import pandas as pd
import numpy as np
from scipy.stats import genpareto

class RiskEngine:
    def __init__(self):
        self.threshold_percentile = 0.10 # Focus on worst 10% of losses

    def calculate_risk_scalar(self, history: list) -> float:
        """
        Calculate a risk scalar (0.0 - 1.0) based on EVT.
        1.0 = Safe (Full Size)
        < 1.0 = Risky (Reduce Size)
        """
        if not history or len(history) < 100:
            return 1.0 # Default to full size if not enough data

        try:
            # 1. Prepare Data
            df = pd.DataFrame(history)
            df['close'] = pd.to_numeric(df['close'])
            
            # Calculate Log Returns
            df['returns'] = np.log(df['close'] / df['close'].shift(1))
            df = df.dropna()
            
            returns = df['returns'].values
            
            # 2. Focus on Left Tail (Losses)
            # We want positive values for losses to fit GPD
            losses = -returns
            
            # Threshold (u) using Peak Over Threshold (POT)
            # We look at the worst 10% of losses
            u = np.percentile(losses, (1 - self.threshold_percentile) * 100)
            
            # Filter excesses (losses > threshold)
            excesses = losses[losses > u] - u
            
            if len(excesses) < 10:
                return 1.0 # Not enough tail data
            
            # 3. Fit GPD
            # shape (xi), loc (mu), scale (sigma)
            xi, mu, sigma = genpareto.fit(excesses)
            
            # 4. Determine Scalar based on Tail Index (xi)
            # xi > 0 means heavy tail (high risk of black swan)
            # xi <= 0 means thin tail (normal/safe)
            
            if xi <= 0:
                return 1.0 # Thin tail, safe
            elif xi < 0.2:
                return 0.9 # Mild risk
            elif xi < 0.4:
                return 0.7 # Moderate risk
            else:
                return 0.5 # High risk (Fat tail)

        except Exception as e:
            print(f"Risk Engine Error: {e}")
            return 1.0 # Fail safe
