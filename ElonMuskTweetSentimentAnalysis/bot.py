class Algo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2012, 11, 1)
        self.SetEndDate(2017, 1, 1)
        self.SetCash(100000)

        self.tsla = self.AddEquity("TSLA", Resolution.Minute).Symbol
        self.musk = self.AddData(Tweet, "MUSKTWTS", Resolution.Minute).Symbol

        self.Schedule.On(self.DateRules.EveryDay(self.tsla),
                        self.TimeRules.BeforeMarketClose(self.tsla, 15),
                        self.ExitPositions)
                        
        self.tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
        self.model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

    def OnData(self, data):
        if self.musk in data:
            score = data[self.musk].Value
            content = data[self.musk].Tweet

            if score >= 4:
                self.SetHoldings(self.tsla, 1)
            elif score <= 2:
                self.SetHoldings(self.tsla, -1)
            
            if score <= 2 or score >= 4:
                self.Log("Score: " + str(score) + ", Tweet: " + content)
    
    def ExitPositions(self):
        self.Liquidate()

class Tweet(PythonData):

    def GetSource(self, config, date, isLive):
        source = "https://www.dropbox.com/s/ovnsrgg1fou1y0r/MuskTweetsPreProcessed.csv?dl=1"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile)

    def Reader(self, config, line, date, isLive):
        if not (line.strip() and line[0].isdigit()):
            return None

        data = line.split(",")
        tweet = MuskTweet()
        
        words_of_interest = ["tsla", "tesla", "model", "cybertruck", "supercharger"]

        try:
            tweet.Symbol = config.Symbol
            tweet.Time = datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=1)
            content = data[1].lower()

            for word in words_of_interest:
                if word in content:
                    tokens = self.tokenizer.encode(content, return_tensors="pt")
                    result = self.model(tokens)
                    tweet.Value = max([(i+1, r) for i,r in enumerate(result.logits[0])], key=lambda x: x[1])[0]
                    break
                else:
                    tweet.Value = 3

            tweet["Tweet"] = str(content)
        
        except ValueError:
            return None

        return tweet
