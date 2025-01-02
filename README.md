# football_fair
Gather football data from odds to team stats - a potential research project on sports trading.

## Problem Statement
Sports betting market is never as efficient as the financial market. An interesting phenomenon is
that in markets of football games (especially in European leagues like Premier League, La Liga),
large volumes tend to go to the favorite team, increasing the price and lowering the odds. To
further prove this is more than just confirmation bias, detailed statistical analysis is required.

## Methodology
Betfair provides free historical odds data associated with timestamps. The basic plan includes
odds data per minutes. Such time series data can be visualized to see which teams are likely to
have bigger volume in favor a few hours before their games. The intuition collected from the
experience is that teams like Real Madrid, Barcelona and Man City are usually the favored one,
and likely to have more money under the corresponding selections. To start with a PoC, these
teams are investigated.

The target is to predict the odds right before the game, based on the odds shown in the market
before (eg. 6 hours or 12 hours before the game) plus the available features for the teams.
Alternatively, sentiment analysis could also help with the prediction. However, a purely data-driven
solution will be implemented at the early stage.

## Input data (X)
• Game and player stats on the two teams involved in the match (stats are available on
API-Football, La Liga Official Website, etc)

## Label (Y)
Odds on a selection at the start of the game (using timestamp, and game starting time, to locate
the corresponding price)
With all the available input data, we could use XGBoost as a baseline model to train, and see how
difficult it is to predict the target variable. Alternatively, the target of the prediction could be a
binary indicator of whether the odd falls by 5% (or any other threshold).

## Workflow
Once the model is trained and validated, it will be running on a server. A model can be re-trained
or updated daily to learn the latest data. The inference takes place at 3 hours before the match
and tells if the odds will decrease by 5%. If the prediction is positive, a bet will be placed
automatically by the server on the selection. When profit reaches 5% or when the match starts
(either condition is reached), the bet will be cashed out. To reduce the risk of impacting the
market, the stake will not exceed £500 on a single selection.
Instead of automation, human work could be easily incorporated by email notification. The server
can always send an email to notify the user of a positive prediction. This could involve more
human intervention and avoid technical issues. However, human work could dramatically increase
the risk of entering an actual bet. The ultimate goal of the system is to reduce human work to a
minimum.
