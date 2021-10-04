from nltk.sentiment import SentimentIntensityAnalyzer

class Algo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2012, 12, 1)
        self.SetEndDate(2021, 3, 22)
        self.SetCash(100000)
        
        self.spy = self.AddEquity("SPY", Resolution.Minute).Symbol
        self.tsla = self.AddEquity("TSLA", Resolution.Minute).Symbol
        self.musk = self.AddData(Tweet, "Tweet", Resolution.Minute).Symbol
        

    def OnData(self, data):
        if self.musk in data:
            score = data[self.musk].Value
            content = data[self.musk].Tweet

            if score > 0.5:
                self.SetHoldings(self.tsla, 0.9)
                self.SetHoldings(self.spy, 0.1)
            elif score < -0.5:
                self.SetHoldings(self.tsla, 0.1)
                self.SetHoldings(self.spy, 0.9)
            
            if abs(score) > 0.5:
                self.Log("Score: " + str(score) + ", Tweet: " + content)
    

class Tweet(PythonData):

    sia = SentimentIntensityAnalyzer()

    def GetSource(self, config, date, isLive):
        source = "https://github.com/adelevski/QuantConnect/raw/main/ElonMuskTweetSentimentAnalysis/data/ElonMuskTweetsPreProcessed.csv"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile)

    def Reader(self, config, line, date, isLive):
        if not (line.strip() and line[0].isdigit()):
            return None

        data = line.split(",")
        tweet = Tweet()
        
        words_of_interest = ["tsla", "tesla", "model", "cybertruck", "supercharger"]

        try:
            tweet.Symbol = config.Symbol
            tweet.Time = datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S") + timedelta(seconds=20)
            content = data[1].lower()

            for word in words_of_interest:
                if word in content:
                    tweet.Value = self.sia.polarity_scores(content)["compound"]
                    break
            else:
                tweet.Value = 0

            tweet["Tweet"] = str(content)
        
        except ValueError:
            return None

        return tweet
