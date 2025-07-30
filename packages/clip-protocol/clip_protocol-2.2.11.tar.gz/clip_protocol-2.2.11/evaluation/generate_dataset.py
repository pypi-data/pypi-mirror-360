import pandas as pd
import random
import string

base_n = 5000
N = [3000, 4000, 5000, 6000, 7000]  # Dataset sizes
num_aois = 4                        # Number of Areas of Interest
num_users = 50                      # Number of users

#aoi_percentages = [0.7, 0.1, 0.01, 0.19]
#aoi_percentages = [0.4, 0.2, 0.25, 0.15]
#aoi_percentages = [0.8, 0.13, 0.01, 0.07]
#aoi_percentages = [0.30, 0.20, 0.30, 0.20]
#aoi_percentages = [0.158, 0.316, 0.316, 0.21] poisson lambda=2
aoi_percentages = [0.25, 0.25, 0.25, 0.25] # Uniform distribution

def generate_user_id(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

aois = [f"subevent_{i}" for i in range(num_aois)]

user_ids = [generate_user_id() for _ in range(num_users)]

for n in N:
    records = []

    samples_per_aoi = [int(round(p * n)) for p in aoi_percentages]

    diff = n - sum(samples_per_aoi)
    if diff != 0:
        samples_per_aoi[0] += diff
    
    for aoi, count in zip(aois, samples_per_aoi):
        for _ in range(count):
            user_id = random.choice(user_ids)
            records.append((user_id, aoi))
        

    df = pd.DataFrame(records, columns=["user_id", "aoi_hit"])
    df = df.sample(frac=1).reset_index(drop=True)
    df.to_excel(f'datasets-article/aoi-hits-d4-{n}.xlsx', index=False)