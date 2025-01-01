import betfairlightweight
import pandas as pd
import json
import datetime as dt

from bz2 import BZ2Decompressor
from betfair_login_config import SESSION_TOKEN, APPLICATION_ID, APPLICATION_NAME, APPLICATION_KEY, CERTS_PATH, CREDENTIALS_PATH
from tqdm import tqdm

with open(CREDENTIALS_PATH, 'r') as f:
    cred = json.load(f)
    my_username = cred['username']
    my_password = cred['password']
    my_app_key = cred['app_key']

trading = betfairlightweight.APIClient(username=my_username,
                                       password=my_password,
                                       app_key=my_app_key,
                                       certs=CERTS_PATH)

trading.login()

def downloadHistoricOdds(
    sport="Soccer",
    plan="Basic Plan",
    from_day=1,
    from_month=11,
    from_year=2024,
    to_day=1,
    to_month=12,
    to_year=2024
):
    """
        Method to download historic odds files

        Returns
        -----------
        fileList (list[str]): a list of string representing names of the sports markets
    """
    fileList = trading.historic.get_file_list(
        sport,
        plan,
        from_day,
        from_month,
        from_year,
        to_day,
        to_month,
        to_year,
        market_types_collection=["MATCH_ODDS"],
        countries_collection=["ES"],
    )

    for file in fileList:
        download = trading.historic.download_file(file_path=file)

    return fileList


def decompressHistoricOdds(fileList):
    """
        Method to decompress the historic odds files

        Returns
        ----------
        decompressedFileList (list[str]): list of decompressed file names
    """

    decompressedFileList = []
    for i in tqdm(range(len(fileList))):
        filename = fileList[i]
        filename = filename.split('/')[-1]
        decompressedFilename = filename + '.decompressed'
        with open(decompressedFilename, 'wb') as decompressedFile, open(filename, 'rb') as file:
            decompressor = BZ2Decompressor()
            for data in iter(lambda : file.read(100 * 1024), b''):
                decompressedFile.write(decompressor.decompress(data))
        decompressedFileList.append(decompressedFilename)
    return decompressedFileList


def processOddsHistory(decrompressedFilePath):
    """
        Method to take the path of a decompressed odds data file as the input
        Produce the odds information data frame
        
        Parameters
        -----------
        decompressedFilePath (str): relative path of the decompressed odds file
        
        Returns
        -----------
        fileName (str): name and time of the event
        oddsDf (str): dataframe with all the minute-by-minute odds information on the specific football market
    """
    
    with open(decrompressedFilePath, 'r') as f:
        contents = f.readlines()
        
    matchInfo = json.loads(contents[0])['mc'][0]['marketDefinition']

    assert matchInfo['marketType'] == 'MATCH_ODDS'

    options = matchInfo['runners']
    matchTime = matchInfo['marketTime']
    matchTime = dt.datetime.strptime(matchTime, "%Y-%m-%dT%H:%M:%S.%fZ")

    homeTeam = options[0]['name']
    homeTeamSelectionId = options[0]['id']

    awayTeam = options[1]['name']
    awayTeamSelectionId = options[1]['id']

    assert options[2]['name'] == 'The Draw'
    drawId = options[2]['id']

    eventName = matchInfo['eventName']
    eventDate = matchTime.date()
    csvName = "%s_%s.csv" % (eventDate.strftime('%Y-%m-%d'), eventName)
    
    
    idToSelection = {
        homeTeamSelectionId: homeTeam,
        awayTeamSelectionId: awayTeam,
        drawId: "Draw"
    }
    
    # Extract odds history
    records = []

    for content in contents[1:]:
        try:
            content = json.loads(content)
            assert "rc" in content["mc"][0]
            timestamp = content["pt"]
            oddsInfo = content["mc"][0]["rc"]
            for info in oddsInfo:
                selectionId = info["id"]
                selection = idToSelection[selectionId]
                odds = info["ltp"]
                record = {
                    "timestamp": timestamp,
                    "selection": selection,
                    "odds": odds
                }
                records.append(record)
        except Exception:
            pass
        
    oddsDf = pd.DataFrame.from_records(records)
    
    # timestamp is in ms by default, need to convert to s
    oddsDf['timestamp'] = oddsDf['timestamp'].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
    
    # In play status
    oddsDf['inplay'] = oddsDf['timestamp'] >= matchTime
    
    return csvName, oddsDf

