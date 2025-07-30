import os
import sys
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from clip_protocol.utils.utils import load_mask_json, save_agregate_json


def update_sketch_matrix(M, k, e, privacy_method, data_point):
    """Updates the sketch matrix based on the privatized data."""
    if privacy_method == "PCMeS":
        v, j = data_point
        v = np.array(v)
        c_e = (np.exp(e / 2) + 1) / (np.exp(e / 2) - 1)
        x = k * ((c_e / 2) * v + (1 / 2) * np.ones_like(v))
        M[j, :] += x
    elif privacy_method == "PHCMS":
        w, j, l = data_point
        c_e = (np.exp(e / 2) + 1) / (np.exp(e / 2) - 1)
        x = k * c_e * w
        M[j, l] += x
    return M

class Agregate:
    def __init__(self):
        self.k, self.m, self.e, _, self.privacy_method, self.private_dataset = load_mask_json()
        self.sketch_by_user = {}

    def compute_data(self, user_data):
        M = np.zeros((self.k, self.m)) # Sketch matrix empty
        with Progress() as progress:
            task = progress.add_task("[cyan]Updating sketch matrix", total=len(user_data))
            for _, row in user_data.iterrows(): # Iterate over the rows of the user data
                    if self.privacy_method == "PCMeS":
                        v = np.array([int(x) for x in row["0"].split()])
                        data = (v, int(row["1"]))
                    elif self.privacy_method == "PHCMS":
                        data = (row["0"], row["1"], row["2"])
                    M = update_sketch_matrix(M, self.k, self.e, self.privacy_method, data)
                    progress.update(task, advance=1)
                
                    if self.privacy_method == "PHCMS":
                        M = M @ np.transpose(self.H)
        user_id = user_data["2"].iloc[0]
        return user_id, {"M": M.tolist(), "N": len(user_data)}
    
    def agregate_per_user(self):
        users = self.private_dataset["2"].unique() # List of all users
        user_groups = [self.private_dataset[self.private_dataset["2"] == user] for user in users] # List of sketches for each user
        sketch_by_user = {}

        for i in range(len(users)):
            user_id, sketch = self.compute_data(user_groups[i])
            sketch_by_user[user_id] = sketch
    
        self.sketch_by_user = sketch_by_user
        
    
def run_agregate():
    agregate_instance = Agregate()
    print("🧑‍🤝‍🧑 Aggregate per user")
    agregate_instance.agregate_per_user()
    save_agregate_json(agregate_instance)

if __name__ == "__main__":
    run_agregate()
