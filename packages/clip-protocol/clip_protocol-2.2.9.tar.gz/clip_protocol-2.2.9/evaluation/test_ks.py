import pandas as pd
import numpy as np
from scipy.stats import chisquare, poisson, uniform

# Carga datos
df_5000 = pd.read_excel('datasets-article/aoi-hits-d1-3000.xlsx')

df_5000['aoi_hit'] = df_5000['aoi_hit'].replace({
    'subevent_0': 0,
    'subevent_1': 1,
    'subevent_2': 2,
    'subevent_3': 3
}).astype(int)

counts = np.bincount(df_5000['aoi_hit'], minlength=4)
#counts = [790, 1580, 1580, 1050] # para poisson

print("Counts (observed):", counts)

# Parámetro lambda
lambda_poisson = 2

# Calcula probabilidades Poisson para valores 0..3
probs = poisson.pmf(np.arange(4), mu=lambda_poisson)
#probs = uniform.pdf(np.arange(4), loc=0, scale=4)  # Distribución uniforme para 0..3

# Normaliza para que sumen 1 solo en esos valores
probs = probs / probs.sum()

# Calcula esperados según la distribución teórica
expected = probs * sum(counts)

# Test chi-cuadrado
stat, pvalue = chisquare(counts, f_exp=expected)

print(f"Chi2 statistic: {stat:.4f}")
print(f"P-value: {pvalue:.4f}")