from sympy import primerange
import random
import numpy as np
from rich.progress import Progress
import pandas as pd
from numba import njit
from concurrent.futures import ThreadPoolExecutor

from clip_protocol.utils.utils import generate_hash_functions

def hadamard_matrix(n):
    if n == 1:
        return np.array([[1]])
    else:
        h_half = hadamard_matrix(n // 2)
        return np.block([[h_half, h_half], [h_half, -h_half]])

@njit
def update_sketch_matrix(epsilon, k, M, w, j, l):
    c_e = (np.exp(epsilon/2)+1) / ((np.exp(epsilon/2))-1)
    x = k * c_e * w
    M[j,l] =  M[j,l] + x


def traspose_M(M, H):
    return M @ np.transpose(H)

class privateHCMSClient:
    def __init__(self, epsilon, k, m, df):
        self.df = df
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = self.df['value'].tolist()
        self.domain = self.df['value'].unique().tolist()
        self.H = hadamard_matrix(self.m)
        self.N = len(self.dataset)

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # List to store the privatized matrices
        self.client_matrix = []

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.hashes, self.coeffs = generate_hash_functions(self.k, p, 3, self.m)

    def client(self,d):
        j = random.randint(0, self.k - 1)
        v = np.full(self.m, 0)
        selected_hash = self.hashes[j]
        v[selected_hash(d)] = 1
        w = np.dot(self.H, v)
        l = random.randint(0, self.m-1)

        P_active = np.exp(self.epsilon) / (np.exp(self.epsilon) + 1)
        if random.random() <= P_active:
            b = 1
        else:
            b = -1
        return b * w[l],j,l

    def estimate_client(self, d):
        return (self.m / (self.m-1)) * (1/self.k * np.sum([self.M[i,self.hashes[i](d)] for i in range(self.k)]) - self.N/self.m)
    
    def execute_client(self):
        privatized_data = []

        data_with_users = list(zip(self.df['value'].tolist(), self.df['user'].tolist()))

        def process(d_u):
            d, user = d_u
            w, j, l = self.client(d)
            return (w, j, l, user)
        
        with Progress() as progress:
            task = progress.add_task('Processing client data', total=len(data_with_users))
            with ThreadPoolExecutor() as executor:
                for result in executor.map(process, data_with_users):
                    privatized_data.append(result)
                    progress.update(task, advance=1)
        self.client_matrix = privatized_data
        return privatized_data

    def server_simulator(self, privatized_data):
        with Progress() as progress:
            task = progress.add_task('[cyan]Update sketch matrix', total=len(privatized_data))
            for v, j, w, _ in privatized_data:
                update_sketch_matrix(self.epsilon, self.k, self.M, v, j, w)
                progress.update(task, advance=1)

            # Transpose the matrix
            self.M = traspose_M(self.M, self.H)

            # Estimate the frequencies
            F_estimated = {}
            task = progress.add_task('[cyan]Obtaining histogram of estimated frequencies', total=len(self.domain))
            for x in self.domain:
                F_estimated[x] = self.estimate_client(x)
                progress.update(task, advance=1)
        return F_estimated, self.coeffs
    
def run_private_hcms_client(k, m, e, df):
    """
    Runs the private Count-Min Sketch client, processes the data, and estimates frequencies on the server.

    Args:
        k (int): The number of hash functions.
        m (int): The size of the sketch matrix.
        e (float): The privacy parameter epsilon for differential privacy.
        df (pandas.DataFrame): The dataset in DataFrame format.

    Returns:
        tuple: A tuple containing the hash functions, data table, error table, privatized data, and the estimated frequencies.
    """
    # Initialize the client 
    client = privateHCMSClient(e, k, m, df)

    # Client side: process the private data
    privatized_data = client.execute_client()

    # Simulate the server side
    f_estimated, coeffs = client.server_simulator(privatized_data)
    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    return coeffs, privatized_data, df_estimated


  
