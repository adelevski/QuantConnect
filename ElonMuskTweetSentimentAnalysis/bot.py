class Algo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2012, 12, 1)
        self.SetEndDate(2021, 3, 22)
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

            if score == 5:
                self.SetHoldings(self.tsla, 1)
            elif score == 1:
                self.SetHoldings(self.tsla, -1)
            
            if score == 1 or score == 5:
                self.Log("Score: " + str(score) + ", Tweet: " + content)
    
    def ExitPositions(self):
        self.Liquidate()

class MuskTweet(PythonData):

    def GetSource(self, config, date, isLive):
        source = "https://downgit.github.io/#/home?url=https://github.com/adelevski/QuantConnect/blob/main/ElonMuskTweetSentimentAnalysis/data/(Final)ElonMuskTweets.csv"
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
            scores = data[2]
            
            words_of_interest = ["tsla", "tesla", "model", "cybertruck", "supercharger", "roadster", "battery" "lithium", "motor"]
            of_interest = False
            
            for word in words_of_interest:
                if word in content:
                    tweet.Value = max([(i,s) for i,s in enumerate(scores)], key=lambda x: x[1])[0]
                    of_interest = True
                    break
                
            if not of_interest:
                tweet.Value = 3
                
            tweet["Tweet"] = str(content)
        
        except ValueError:
            return None

        return tweet