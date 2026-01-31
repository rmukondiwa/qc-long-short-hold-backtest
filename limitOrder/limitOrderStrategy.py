# region imports
from AlgorithmImports import *
# endregion

class BuyAndHoldLimitOrder(QCAlgorithm):

    def Initialize(self):
        # Backtest strategy daily from 6/1/2024 to 6/1/2025.
        self.SetStartDate(2024,6,1)
        self.SetEndDate(2025,6,1)

        # Starting Capital 1,000,000
        self.SetCash(1000000)

        # Add equities (daily)
        self.goog = self.AddEquity("GOOG", Resolution.Daily).Symbol
        self.amzn = self.AddEquity("AMZN", Resolution.Daily).Symbol

        # Entry control
        self.first_day_prices_set = False
        self.orders_submitted = False

        # if we lose more the 100k, we exit
        self.starting_value = None
        self.max_loss = 100000
        self.stopped_out = False

    def OnData(self, data: Slice):
        if self.stopped_out:
            return

        # Need both bars before doing anything
        if self.goog not in data.Bars or self.amzn not in data.Bars:
            return

        # Get the starting portfolio value on first usable trading day
        if self.starting_value is None:
            self.starting_value = self.Portfolio.TotalPortfolioValue

        #First Day: store prices and limit order threshold
        if not self.first_day_prices_set:
            self.goog_start = data[self.goog].Close
            self.amzn_start = data[self.amzn].Close

            # 5% thresholds
            self.goog_limit = round(self.goog_start * 0.95, 2)
            self.amzn_limit = round(self.amzn_start * 1.05, 2)

            self.Log(
                f"Day-1 prices: GOOG={self.goog_start:.2f}, "
                f"AMZN={self.amzn_start:.2f} | "
                f"Limits: BUY GOOG @ {self.goog_limit:.2f}, "
                f"SHORT AMZN @ {self.amzn_limit:.2f}"
            )

            self.first_day_prices_set = True
            return

        # Immediately long/short once (first trading day we get data)
        if not self.orders_submitted:
            self.LimitOrder(self.goog, 3000, self.goog_limit) # long 3,000 GOOG
            self.LimitOrder(self.amzn, -4000, self.amzn_limit) # short 4,000 AMZN
            self.orders_submitted = True
            self.Log(f"Entered positions on {self.Time.date()}, conditions met for limit order")

        # Check every day: exit all positions if loss > 100000
        current_value = self.Portfolio.TotalPortfolioValue
        pnl = current_value - self.starting_value
        if pnl <= -self.max_loss:
            self.Liquidate()
            self.stopped_out = True

