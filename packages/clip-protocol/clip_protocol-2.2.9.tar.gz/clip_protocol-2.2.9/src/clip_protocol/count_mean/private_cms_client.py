import random
import numpy as np
from sympy import primerange
import pandas as pd
from rich.progress import Progress
from numba import njit
from concurrent.futures import ThreadPoolExecutor

from clip_protocol.utils.utils import generate_hash_functions

@njit
def bernoulli_vector(epsilon, m):
    b = np.random.binomial(1, (np.exp(epsilon/2)) / ((np.exp(epsilon/2)) + 1), m)
    return 2 * b - 1

@njit
def update_sketch_matrix(M, v, j, epsilon, k, m):
    c_e = (np.exp(epsilon/2)+1) / ((np.exp(epsilon/2))-1)
    x = k * ((c_e/2) * v + (1/2) * np.ones_like(v))
    for i in range (m):
        M[j,i] += x[i]

class privateCMSClient:
    def __init__(self, epsilon, k, m, df):
        self.df = df
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = self.df['value'].tolist()
        self.domain = self.df['value'].unique().tolist()
        self.N = len(self.dataset)

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # List to store the privatized matrices
        self.client_matrix = []

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.H, self.coefs = generate_hash_functions(self.k, p, 3, self.m)

    def client(self, d):
        j = random.randint(0, self.k-1)
        v = np.full(self.m, -1)
        selected_hash = self.H[j]
        v[selected_hash(d)] = 1
        b = bernoulli_vector(self.epsilon, self.m)
        v_aux = v * b
        return v_aux, j

    def estimate_client(self,d):
        sum_aux = 0
        for i in range(self.k):
            selected_hash = self.H[i]
            sum_aux += self.M[i, selected_hash(d)]
        f_estimated = (self.m/(self.m-1))*((sum_aux/self.k)-(self.N/self.m))
        return f_estimated
    
    def execute_client(self):
        privatized_data = []

        data_with_users = list(zip(self.df['value'].tolist(), self.df['user'].tolist()))
        
        def process(d_u):
            d, user = d_u
            v_aux, j = self.client(d)
            return (v_aux, j, user)
        
        with Progress() as progress:
            bar = progress.add_task("Processing client data", total=len(data_with_users))
            with ThreadPoolExecutor() as executor:
                for result in executor.map(process, data_with_users):
                    privatized_data.append(result)
                    progress.update(bar, advance=1)
        self.client_matrix = privatized_data
        return privatized_data
    
    def server_simulator(self,privatized_data):
        with Progress() as progress:
            bar = progress.add_task('Update sketch matrix', total=len(privatized_data))
            
            for v, j, _ in privatized_data:
                update_sketch_matrix(self.M, v, j, self.epsilon, self.k, self.m)
                progress.update(bar, advance=1)

            bar = progress.add_task('Estimate frequencies', total=len(self.domain))
            F_estimated = {}
            for x in self.domain:
                F_estimated[x] = self.estimate_client(x)
                progress.update(bar, advance=1)

        return F_estimated, self.coefs

def run_private_cms_client(k, m, e, df):
    """
    Runs the privatized Count-Min Sketch algorithm and displays the results.

    Args:
        k (int): Number of hash functions.
        m (int): Size of the sketch matrix.
        e (float): Privacy parameter.
        df (DataFrame): Dataset to be processed.

    Returns:
        tuple: A tuple containing the hash functions, the results table, the error table, the privatized data, and the estimated frequency DataFrame.
    """
    # Initialize the private Count-Mean Sketch
    PCMS = privateCMSClient(e, k, m, df)

    # Client side: process the private data
    privatized_data = PCMS.execute_client()

    # Simulate the server side
    f_estimated, coefs = PCMS.server_simulator(privatized_data)

    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    return coefs, privatized_data, df_estimated