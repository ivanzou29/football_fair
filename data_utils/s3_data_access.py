import boto3
import pandas as pd
from io import StringIO


s3 = boto3.resource('s3')
# bucket_name = 'betfairex'
# object_key = '2024-01-04_Sevilla v Athletic Bilbao.csv'


def read_csv_from_s3(bucket_name, object_key):
    response = s3.Object(bucket_name, object_key).get()

    s3_contents = response['Body'].read()
    df = pd.read_csv(StringIO(s3_contents.decode('utf-8')))

    return df