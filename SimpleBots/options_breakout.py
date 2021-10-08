class Bot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

        equity = self.AddEquity("MSFT", Resolution.Minute)
        equity.SetDataNormalizationMode(SetDataNormalizationMode.Raw)

        self.equity = equity.Symbol
        self.SetBenchmark(self.equity)

        option = self.AddOption("MSFT", Resolution.Minute)
        option.SetFilter(-3, 3, timedelta(20), timedelta(40))
        
        self.high = self.MAX(self.equity, 21, Resolution.Daily, Field.High)


    def OnData(self, data):
        if not self.high.IsReady:
            return

        option_invested = [x.Key for x in self.Portfolio if x.Value.Invested and x.Value.Type == SecurityType.Option]
        
        if option_invested:
            if self.Time + timedelta(4) > option_invested[0].ID.Date:
                self.Liquidate(option_invested[0], "Too close to expiration")
            return 
        
        if self.Securities[self.equity].Price >= self.high.Current.Value:
            for i in data.OptionChains:
                chains = i.Value
                self.BuyCall(chains)


    def BuyCall(self, chains):
        expiry = sorted(chains, key = lambda x: x.Empty, reverse=True)[0].Expiry
        calls = [i for i in chains if i.Expiry == expiry and i.Right == OptionRight.Call]
        call_contracts = sorted(calls, key = lambda x: abs(x.Strike - x.UnderlyingLastPrice))
        if len(call_contracts) == 0:
            return
        self.call = call_contracts[0]

        quantity = self.Portfolio.TotalPortfolioValue / self.call.AskPrice
        quantity = int(0.05 * quantity / 100)
        self.Buy(self.call.Symbol, quantity)


    def OnOrderEvent(self, orderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        if order.Type == OrderType.OptionExercise:
            self.Liquidate()

        