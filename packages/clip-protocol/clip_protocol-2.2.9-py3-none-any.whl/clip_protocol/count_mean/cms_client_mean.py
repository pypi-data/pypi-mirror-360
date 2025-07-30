import random
import numpy as np
from sympy import primerange
from rich.progress import Progress

from clip_protocol.utils.utils import generate_hash_functions, display_results

class CMSClient:
    """
    A class to represent the Count-Min Sketch (CMS) Client.

    Attributes:
        df: DataFrame containing the dataset.
        k: Number of hash functions used in the CMS.
        m: Size of the sketch matrix.
        dataset: List of values from the dataset.
        domain: Unique values in the dataset.
        N: Total number of elements in the dataset.
        M: Count-Min Sketch matrix.
        H: List of hash functions.
    
    Methods:
        client(d):
            Simulates the client side of the CMS, returning a vector with hash values.
        update_sketch_matrix(d):
            Updates the sketch matrix based on the given element.
        estimate_client(d):
            Estimates the frequency of an element using the CMS sketch matrix.
        server_simulator():
            Simulates the server side of the CMS, processes the data, and estimates frequencies.
    """

    def __init__(self, k, m, df):
        """
        Initializes the CMSClient with the given parameters.
        """
        self.df = df
        self.k = k 
        self.m = m
        self.dataset = self.df['value'].tolist()
        self.domain = self.df['value'].unique().tolist()
        self.N = len(self.dataset)
        
        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.H = generate_hash_functions(self.k,p, 3,self.m)

    def client(self, d):
        """
        Simulates the client side of the Count-Min Sketch.

        Args:
            d (element): The element for which the sketch vector is generated.

        Returns:
            tuple: A tuple containing the sketch vector and the index of the chosen hash function.
        """
        j = random.randint(0, self.k-1)
        v = np.full(self.m, -1)
        selected_hash = self.H[j]
        v[selected_hash(d)] = 1
        return v, j
   
    def update_sketch_matrix(self, d):
        """
        Updates the sketch matrix based on the given element.

        Args:
            d (element): The element to be used for updating the sketch matrix.
        """
        for i in range (self.k):
            selected_hash = self.H[i]
            hash_index = selected_hash(d)
            self.M[i ,hash_index] += 1

    def estimate_client(self,d):
        """
        Estimates the frequency of an element based on the sketch matrix.

        Args:
            d (element): The element whose frequency is estimated.

        Returns:
            float: The estimated frequency of the element.
        """
        mean = 0
        for i in range(self.k):
            selected_hash = self.H[i]
            mean += self.M[i,selected_hash(d)]
        return mean/self.k
    
    def server_simulator(self):
        """
        Simulates the server side of the CMS by processing the dataset 
        and estimating the frequencies of each element.

        Returns:
            dict: A dictionary with the elements and their estimated frequencies.
        """
        with Progress() as progress:
            bar = progress.add_task("[cyan]Processing client data...", total=len(self.dataset))

            for d in self.dataset:
                self.update_sketch_matrix(d)
                progress.update(bar, advance=1)

            F_estimated = {}
            bar = progress.add_task("[cyan]Obtaining histogram of estimated frequencies...", total=len(self.domain))
            for x in self.domain:
                F_estimated[x] = self.estimate_client(x)
                progress.update(bar, advance=1)
        return F_estimated

def run_cms_client_mean(k, m, df):
    """
    Runs the Count-Min Sketch algorithm and displays the results.

    Args:
        k (int): Number of hash functions.
        m (int): Size of the sketch matrix.
        df (DataFrame): Dataset to be processed.

    Returns:
        DataFrame: A table containing the elements and their estimated frequencies.
    """
    # Initialize the CMSClient
    PCMS = CMSClient(k, m, df)

    # Simulate the server side
    f_estimated = PCMS.server_simulator()

    # Show the results
    data_table = display_results(df, f_estimated)

    return data_table




  
