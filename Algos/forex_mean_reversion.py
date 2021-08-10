
from System.Drawing import Color

class ForexBollingerBandBot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)
        self.pair = self.AddForex("EURUSD", Resolution.Daily, Market.Oanda).Symbol
        self.bb = self.BB(self.pair, 20, 2)
        
        stockPlot = Chart('Trade Plot')
        stockPlot.AddSeries(Series('Buy', SeriesType.Scatter, '$', 
                            Color.Green, ScatterMarkerSymbol.Triangle))
        stockPlot.AddSeries(Series('Sell', SeriesType.Scatter, '$', 
                            Color.Red, ScatterMarkerSymbol.TriangleDown))
        stockPlot.AddSeries(Series('Liquidate', SeriesType.Scatter, '$', 
                            Color.Blue, ScatterMarkerSymbol.Diamond))
        self.AddChart(stockPlot)

    def OnData(self, data):
        if not self.bb.IsReady:
            return
        
        price = data[self.pair].Price
        
        self.Plot("Trade Plot", "Price", price)
        self.Plot("Trade Plot", "MiddleBand", self.bb.MiddleBand.Current.Value)
        self.Plot("Trade Plot", "UpperBand", self.bb.UpperBand.Current.Value)
        self.Plot("Trade Plot", "LowerBand", self.bb.LowerBand.Current.Value)
        
        if not self.Portfolio.Invested:
            if self.bb.LowerBand.Current.Value > price:
                self.SetHoldings(self.pair, 1)
                self.Plot("Trade Plot", "Buy", price)
            elif self.bb.UpperBand.Current.Value < price:
                self.SetHoldings(self.pair, -1)
                self.Plot("Trade Plot", "Sell", price)
        else:
            if self.Portfolio[self.pair].IsLong:
                if self.bb.MiddleBand.Current.Value < price:
                    self.Liquidate()
                    self.Plot("Trade Plot", "Liquidate", price)
            elif self.bb.MiddleBand.Current.Value > price:
                self.Liquidate()    
                self.Plot("Trade Plot", "Liquidate", price)