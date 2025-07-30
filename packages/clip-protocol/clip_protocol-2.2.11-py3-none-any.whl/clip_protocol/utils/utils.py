import numpy as np
import pandas as pd
import random
import json
import os
import pickle
import hashlib
from appdirs import user_data_dir

APP_NAME = "clip_protocol"
DATA_DIR = user_data_dir(APP_NAME)
CONFIG_FILE = os.path.join(DATA_DIR, "setup_config.json")
CONFIG_MASK = os.path.join(DATA_DIR, "mask_config.json")
CONFIG_AGREGATE = os.path.join(DATA_DIR, "sketch_by_user")
PRIVATIZED_DATASET = os.path.join(DATA_DIR, "privatized_dataset.csv")
os.makedirs(DATA_DIR, exist_ok=True)

def save_setup_json(setup_instance):
    config = {
        "k": setup_instance.k,
        "m": setup_instance.m,
        "e_ref": setup_instance.e_ref,
        "n_trials": setup_instance.n_trials,
        "events_names": setup_instance.events_names,
        "privacy_method": setup_instance.privacy_method,
        "error_metric": setup_instance.error_metric,
        "error_value": setup_instance.error_value,
        "tolerance": setup_instance.tolerance,
        "p": setup_instance.p if hasattr(setup_instance, 'p') else None,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
        print("✅ Setup configuration saved")

def load_setup_json():
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return config["k"], config["m"], config["e_ref"], config["n_trials"], config["events_names"], config["privacy_method"], config["error_metric"], config["error_value"], config["tolerance"], config["p"]

def save_mask_json(mask_instance, e, coeffs, privatized_dataset, privacy_method):
    config = {
        "k": mask_instance.k,
        "m": mask_instance.m,
        "e": e,
        "hash": coeffs,
        "privacy_method": str(mask_instance.privacy_method),
    }
    converted_data = []
    if privacy_method == "PCMeS":
        for v, j, u in privatized_dataset:
            v_str = " ".join(map(str, v.tolist()))
            converted_data.append([v_str, j, u])
    elif privacy_method == "PHCMS":
        for w, j, l, u in privatized_dataset:
            converted_data.append([w, j, l, u])

    df = pd.DataFrame(converted_data)
    df.to_csv(PRIVATIZED_DATASET, index=False)

    with open(CONFIG_MASK, "w") as f:
        json.dump(config, f)
        print("✅ Mask configuration saved")

def load_mask_json():
    with open(CONFIG_MASK, "r") as f:
        config = json.load(f)
    
    hash_params = config["hash"]
    hash_functions = rebuild_hash_functions(hash_params)

    df = pd.read_csv(PRIVATIZED_DATASET)

    return config["k"], config["m"], config["e"], hash_functions, config["privacy_method"], df

def save_agregate_json(agregate_instance):
    with open(CONFIG_AGREGATE, "wb") as f:
        pickle.dump(agregate_instance.sketch_by_user, f)
    print("✅ Agregate configuration saved")

def load_agregate_json():
    with open(CONFIG_AGREGATE, "rb") as f:
        sketch_by_user = pickle.load(f)
    return sketch_by_user

def deterministic_hash(x):
    return int(hashlib.sha256(str(x).encode('utf-8')).hexdigest(), 16)

def generate_hash_functions(k, p, c, m):
    hash_functions = []
    coeffs = []
    functions_params = {}

    for _ in range(k):
        coefficients = [random.randint(1, p - 1) for _ in range(c)]
        hash_func = lambda x, coeffs=coefficients, p=p: (sum((coeffs[i] * (deterministic_hash(x) ** i)) % p for i in range(c)) % p) % m
        hash_functions.append(hash_func)
        coeffs.append(coefficients)
    
    functions_params = {
        "coefficients": coeffs,
        "p": p,
        "m": m,
        "c": c
    }
    return hash_functions, functions_params

def rebuild_hash_functions(functions_params):
    hash_functions = []
    hash_coeffs = functions_params["coefficients"]
    p = functions_params["p"]
    m = functions_params["m"]
    c = functions_params["c"]
    for coeffs in hash_coeffs:
        hash_func = lambda x, coeffs=coeffs, p=p: (sum((coeffs[i] * (deterministic_hash(x) ** i)) % p for i in range(c)) % p) % m
        hash_functions.append(hash_func)
    return hash_functions

def display_results(real_freq: pd.DataFrame, estimated_freq: dict):
    real_num_freq = dict(zip(real_freq['Element'], real_freq['Frequency']))

    N = sum(real_num_freq.values())

    real_percent_freq = {k: (v * 100 / N) for k, v in real_num_freq.items()}
    estimated_freq_dict = dict(zip(estimated_freq['Element'], estimated_freq['Frequency']))

    data_table = []
    for element in estimated_freq_dict:
        if element in estimated_freq_dict:
            real_count = real_num_freq[element]
            real_percent = real_percent_freq[element]
            estimated_count = estimated_freq_dict[element]
            estimated_percent = (estimated_count / N) * 100
            diff = abs(real_count - estimated_count)
            
            if real_count > 0:
                percent_error = (abs(real_count - estimated_count) / real_count) * 100
            else:
                percent_error = 0.0
            
            data_table.append([
                element, 
                real_count, 
                f"{real_percent:.3f}%", 
                f"{estimated_count:.2f}", 
                f"{estimated_percent:.3f}%", 
                f"{diff:.2f}", 
                f"{percent_error:.2f}%"
            ])
    return data_table

def get_real_frequency(df):
    count = df['value'].value_counts().reset_index()
    count.columns = ['Element', 'Frequency']
    return count