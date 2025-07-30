import numpy as np
import pandas as pd
from tabulate import tabulate

def compute_error_table(real_freq, estimated_freq, p):
    # Turn both into dictionaries {element: frequency}
    real_num_freq = dict(zip(real_freq['Element'], real_freq['Frequency']))
    estimated_num_freq = dict(zip(estimated_freq['Element'], estimated_freq['Frequency']))

    N = sum(real_num_freq.values())

    # Join both dictionaries to get all elements
    all_elements = set(real_num_freq.keys()).union(estimated_num_freq.keys())

    # Calculate error
    errors = [
        abs(real_num_freq.get(key, 0) - estimated_num_freq.get(key, 0))
        for key in all_elements
    ]

    mean_error = np.mean(errors)
    mse = np.mean([(real_num_freq.get(key, 0) - estimated_num_freq.get(key, 0)) ** 2 
                  for key in all_elements])
    mae = np.mean([abs(real_num_freq.get(key, 0) - estimated_num_freq.get(key, 0)) 
                  for key in all_elements])
    lp = np.sum([abs(real_num_freq.get(key, 0) - estimated_num_freq.get(key, 0)) ** p 
                  for key in all_elements]) ** (1/p)

    error_table = [
        ['MAE', f"{mae:.2f}"],
        ['MSE', f"{mse:.2f}"],
        ['RMSE', f"{np.sqrt(mse):.2f}"],
        ['Lρ Norm', f"{lp:.2f}"],
        ['Percentage Error', f"{(mean_error / N) * 100:.2f}%"]
    ]
    return error_table

def display_error_table(real_freq, estimated_freq, p):
    table = compute_error_table(real_freq, estimated_freq, p)
    print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))


def calculate_lp(real_freq, estimated_freq, p):
    real_num_freq = dict(zip(real_freq['Element'], real_freq['Frequency']))
    estimated_num_freq = dict(zip(estimated_freq['Element'], estimated_freq['Frequency']))

    all_elements = set(real_num_freq.keys()).union(estimated_num_freq.keys())

    lp = np.sum([abs(real_num_freq.get(key, 0) - estimated_num_freq.get(key, 0)) ** p 
                  for key in all_elements]) ** (1/p)
    return lp