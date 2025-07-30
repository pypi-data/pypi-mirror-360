import os
import numpy as np
import pandas as pd
from rich.progress import Progress

from clip_protocol.utils.utils import display_results

class privateHCMSServer:
    """
    A private Hadamard Count-Min Sketch (HCMS) server implementation.
    """
    def __init__(self, epsilon, k, m, df, hashes):
        """
        Initializes the private HCMS server.
        
        :param epsilon: Privacy parameter
        :param k: Number of hash functions
        :param m: Number of columns in the sketch matrix
        :param df: Dataframe containing the dataset
        :param hashes: List of hash functions
        """
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = self.df['value'].tolist()
        self.domain = self.df['value'].unique().tolist()
        self.H = self.hadamard_matrix(self.m)
        self.N = len(self.dataset)
        self.hashes = hashes

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))
    
    def hadamard_matrix(self,n):
        """
        Generates the Hadamard matrix recursively.

        Args:
            n (int): The size of the matrix.

        Returns:
            numpy.ndarray: The generated Hadamard matrix.
        """
        if n == 1:
            return np.array([[1]])
        else:
            # Recursive function to generate the Hadamard matrix
            h_half = self.hadamard_matrix(n // 2)
            h = np.block([[h_half, h_half], [h_half, -h_half]])
        return h

    def update_sketch_matrix(self, w, j, l):
        """
        Updates the sketch matrix with a new data point.
        
        :param w: Weight of the data point
        :param j: Hash function index
        :param l: Hash value
        """
        c_e = (np.exp(self.epsilon/2)+1) / ((np.exp(self.epsilon/2))-1)
        x = self.k * c_e * w
        self.M[j,l] =  self.M[j,l] + x

    def traspose_M(self):
        """
        Applies the Hadamard transformation to the sketch matrix.
        """
        self.M = self.M @ np.transpose(self.H)

    def estimate_server(self,d):
        """
        Estimates the frequency of an element in the dataset.
        
        :param d: Element to estimate
        :return: Estimated frequency
        """
        return (self.m / (self.m-1)) * (1/self.k * np.sum([self.M[i,self.hashes[i](d)] for i in range(self.k)]) - self.N/self.m)

    def execute_server(self, privatized_data):
        """
        Processes the privatized data and estimates frequencies.
        
        :param privatized_data: List of privatized data points
        :return: Dictionary of estimated frequencies
        """
        with Progress() as progress:
            task = progress.add_task('[cyan]Update sketch matrix', total=len(privatized_data))
            for data in privatized_data:
                self.update_sketch_matrix(data[0],data[1],data[2])
                progress.update(task, advance=1)

            # Transpose the matrix
            self.traspose_M()

            # Estimate the frequencies
            F_estimated = {}
            task = progress.add_task('[cyan]Obtaining histogram of estimated frequencies', total=len(self.domain))
            for x in self.domain:
                F_estimated[x] = self.estimate_server(x)
                progress.update(task, advance=1)
        return F_estimated

    def query_server(self, query_element):
        """
        Queries the estimated frequency of an element.
        
        :param query_element: Element to query
        :return: Estimated frequency or a message if the element is not in the domain
        """
        if query_element not in self.domain:
            return "Element not in the domain"
        estimation = self.estimate_server(query_element)
        return estimation

def run_private_hcms_server(k, m, e, df, hashes, privatized_data):
    """
    Runs the private HCMS server pipeline.
    
    :param k: Number of hash functions
    :param m: Number of columns in the sketch matrix
    :param e: Privacy parameter
    :param df: Dataframe containing the dataset
    :param hashes: List of hash functions
    :param privatized_data: List of privatized data points
    """
    # Initialize the server
    server = privateHCMSServer(e, k, m, df, hashes)

    # Save the privatized data
    privatized_data_save = pd.DataFrame(privatized_data)
    
    # Execute the server
    f_estimated = server.execute_server(privatized_data)

    # Show the results
    display_results(df, f_estimated)

    # Query the server
    while True:
        query = input("Enter an element to query the server or 'exit' to finish: ")
        if query.lower() == 'exit':
            break
        estimation = server.query_server(query)
        print(f"The estimated frequency of {query} is {estimation:.2f}")
    
    return privatized_data_save


  
