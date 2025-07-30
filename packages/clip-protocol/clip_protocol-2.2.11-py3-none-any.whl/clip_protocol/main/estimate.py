import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from clip_protocol.utils.utils import load_agregate_json, load_mask_json

class Estimation:
    def __init__(self, df=None):
        self.sketch_by_user = df if df is not None else load_agregate_json()
        self.k, self.m, self.epsilon, self.hashes, self.method, _ = load_mask_json()
    
    def estimate_element(self, d, M, N):
        """Estimates the frequency of an element in the dataset."""
        return (self.m / (self.m - 1)) * (1 / self.k * np.sum([M[i, self.hashes[i](d)] for i in range(self.k)]) - N / self.m)
    
    def query_all_users_event(self, event):
        print(f"\n📊 Estimated frequency of '{event}' per user:\n")
        for user_id, user_data in self.sketch_by_user.items():
            M = np.array(user_data["M"])
            N = user_data["N"]
            est = self.estimate_element(event, M, N)
            if est < 0:
                est = 0
            print(f"🧑 User {user_id}: {est:.4f}")

def run_estimate(df=None):
    estimation = Estimation(df=df)
    event = str(input("Enter the event to estimate or q' to quit: "))
    while event != "q":
        estimation.query_all_users_event(event)
        event = str(input("Enter the event to estimate or q' to quit: "))

if __name__ == "__main__":
    run_estimate()