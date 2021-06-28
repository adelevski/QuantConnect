class Algo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

        spy = self.AddEquity("SPY", Resolution.Daily)
        # self.AddForex, self.AddFuture..

        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)

        self.spy = spy.Symbol

        self.SetBenchmark("SPY")
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.entryPrice = 0
        self.period = timedelta(31)
        self.nextEntryTime = self.Time

    def OnData(self, data):
        
        if not self.spy in data:
            return

        # 3 different ways to get price
        # price = data.Bars[self.spy].Close
        price = data[self.spy].Close
        # price = self.Securities[self.spy]

        if not self.Portfolio.Invested:
            if self.nextEntryTime <= self.Time:
                # 2 different ways to buy
                self.SetHoldings(self.spy, 1)
                # self.MarketOrder(self.spy, int(self.Portfolio.Cash / price))

                self.Log("BUY SPY @" + str(price))
                self.entryPrice = price

            elif self.entryPrice * 1.1 < price or self.entryPrice * 0.9 > price:
                self.Liquidate(self.spy) 
                self.Log("SELL SPY @" + str(price))

                self.nextEntryTime = self.Time + self.period`
                


   



