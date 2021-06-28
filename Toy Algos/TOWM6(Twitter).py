# Preprocessing
import pandas as pd
import re

# import csv to pandas dataframe
df = pd.read_csv("data_elonmusk.csv", encoding='latin1') # encoding = 'iso-8859-1' or encoding = 'cp1252'

# select time and tweet columns
df = df[["Time", "Tweet"]]

# reverse order
df = df[::-1].reset_index(drop = True)

# remove all URLs (replaces with {URL} placeholder)
for i in range(len(df)):
    if "http" in df["Tweet"][i]:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|[?:%[0-9a-fA-F][0-9a-fA-F]))+', df["Tweet"][i])

        for url in urls:
            df["Tweet"][i] = df["Tweet"][i].replace(url, '{URL}')

# export dataframe to csv
df.to_csv("MuskTweetsPreProcessed.csv", index=False)

# Quant Connect
from nltk.sentiment import SentimentIntensityAnalyzer

class Algo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2012, 11, 1)
        self.SetEndDate(2017, 1, 1)
        self.SetCash(100000)

        self.tsla = self.AddEquity("TSLA", Resolution.Minute).Symbol
        self.musk = self.AddData(MuskTweet, "MUSKTWTS", Resolution.Minute).Symbol

        self.Schedule.On(self.DateRules.EveryDay(self.tsla),
                        self.TimeRules.BeforeMarketClose(self.tsla, 15),
                        self.ExitPositions)

    def OnData(self, data):
        if self.musk in data:
            score = data[self.musk].Value
            content = data[self.musk].Tweet

            if score > 0.5:
                self.SetHoldings(self.tsla, 1)
            elif score < -0.5:
                self.SetHoldings(self.tsla, -1)
            
            if abs(score) > 0.5:
                self.Log("Score: " + str(score) + ", Tweet: " + content)
    
    def ExitPositions(self):
        self.Liquidate()

class MuskTweet(PythonData):

    sia = SentimentIntensityAnalyzer()

    def GetSource(self, config, date, isLive):
        source = "https://www.dropbox.com/s/ovnsrgg1fou1y0r/MuskTweetsPreProcessed.csv?dl=1"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile)

    def Reader(self, config, line, date, isLive):
        if not (line.strip() and line[0].isdigit()):
            return None

        data = line.split(",")
        tweet = MuskTweet()

        try:
            tweet.Symbol = config.Symbol
            tweet.Time = datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=1)
            content = data[1].lower()

            if "tsla" in content or "tesla" in content:
                tweet.Value = self.sia.polarity_scores(content)["compound"]
            else:
                tweet.Value = 0

            tweet["Tweet"] = str(content)
        
        except ValueError:
            return None

        return tweet


