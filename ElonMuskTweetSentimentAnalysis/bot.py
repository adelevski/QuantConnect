class Algo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2012, 12, 1)
        self.SetEndDate(2017, 1, 1)
        self.SetCash(100000)

        self.tsla = self.AddEquity("TSLA", Resolution.Minute).Symbol
        self.musk = self.AddData(MuskTweet, "MUSKTWTS", Resolution.Minute).Symbol

        self.Schedule.On(self.DateRules.EveryDay(self.tsla),
                         self.TimeRules.BeforeMarketClose(self.tsla, 15),
                         self.ExitPositions)

    def OnData(self, data):
        if self.musk in data:
            index, score = data[self.musk].Value
            content = data[self.musk].Tweet

            if index == 5 and score > 1:
                self.SetHoldings(self.tsla, 1)
            elif index == 1 and score > 1:
                self.SetHoldings(self.tsla, -1)
            
            if (score > 1) and (index == 1 or index == 5):
                self.Log("Index/Score: " + str(index) + "/" + str(score) + ", Tweet: " + content)
    
    def ExitPositions(self):
        self.Liquidate()

class MuskTweet(PythonData):

    def GetSource(self, config, date, isLive):
        source = "https://www.dropbox.com/s/q2ruax0rn8466bi/%28Final%29ElonMuskTweets.csv?dl=1"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile)

    def Reader(self, config, line, date, isLive):
        if not (line.strip() and line[0].isdigit()):
            return None

        data = line.split('"')
        tweet = MuskTweet()

        try:
            tweet.Symbol = config.Symbol
            tweet.Time = datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=1)
            content = data[1].lower()
            nums = data[2].split("[")[1].split("]")[0].split[","]
            scores = [float(num) for num in nums]
            
            words_of_interest = ["tsla", "tesla", "model", "cybertruck", "supercharger", "roadster", "battery" "lithium", "motor"]
            of_interest = False
            
            for word in words_of_interest:
                if word in content:
                    tweet.Value = max([(i+1,s) for i,s in enumerate(scores)], key=lambda x: x[1])
                    of_interest = True
                    break
                
            if not of_interest:
                tweet.Value = (3, 0)
                
            tweet["Tweet"] = str(content)
        
        except ValueError:
            return None

        return tweet