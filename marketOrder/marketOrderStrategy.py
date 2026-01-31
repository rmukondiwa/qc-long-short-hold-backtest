# region imports
from AlgorithmImports import *
# endregion

class BuyAndHoldMarketOrder(QCAlgorithm):

    def Initialize(self):
        # Backtest strategy daily from 6/1/2024 to 6/1/2025.
        self.SetStartDate(2024,6,1)
        self.SetEndDate(2025,6,1)

        # Starting Capital 1,000,000
        self.SetCash(1000000)

        # Add equities (daily)
        self.goog = self.AddEquity("GOOG", Resolution.Daily).Symbol
        self.amzn = self.AddEquity("AMZN", Resolution.Daily).Symbol

        #Place trades once
        self.traded = False

        # if we lose more the 100k, we exit
        self.starting_value = None
        self.max_loss = 100000

    def OnData(self, data: Slice):
        # Need both bars before doing anything
        if not data.ContainsKey(self.goog) or not data.ContainsKey(self.amzn):
            return

        # Get the starting portfolio value on first usable trading day
        if self.starting_value is None:
            self.starting_value = self.Portfolio.TotalPortfolioValue

        # Immediately long/short once (first trading day we get data)
        if not self.traded:
            self.MarketOrder(self.goog, 3000) # long 3,000 GOOG
            self.MarketOrder(self.amzn, -4000) # short 4,000 AMZN
            self.traded = True
            self.Log(f"Entered positions on {self.Time.date()}")

        # Check every day: exit all positions if loss > 100000
        current_value = self.Portfolio.TotalPortfolioValue
        pnl = current_value - self.starting_value

        if pnl <= -self.max_loss:
            self.Liquidate()
            self.traded = True


        