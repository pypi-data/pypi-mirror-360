
import numpy as np
import pandas as pd
import os
from colorama import Fore, Style
from rich.progress import Progress

from clip_protocol.utils.utils import display_results

class privateCMSServer:
    """
    This class represents the server side of the Private Count-Mean Sketch (PCMS).
    It is responsible for updating the sketch matrix and providing frequency estimations.

    Attributes:
        df (pandas.DataFrame): The dataset containing the values.
        epsilon (float): The privacy parameter epsilon.
        k (int): The number of hash functions.
        m (int): The size of the sketch.
        dataset (list): The list of values in the dataset.
        domain (list): The unique values in the dataset.
        N (int): The size of the dataset.
        H (list): The list of hash functions.
        M (numpy.ndarray): The sketch matrix.
    """
    def __init__(self, epsilon, k, m, df, H):
        """
        Initializes the privateCMSServer class with the given parameters.

        Args:
            epsilon (float): The privacy parameter epsilon.
            k (int): The number of hash functions.
            m (int): The size of the sketch.
            df (pandas.DataFrame): The dataset containing the values.
            H (list): The list of hash functions.
        """
        self.df = df
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = self.df['value'].tolist()
        self.domain = self.df['value'].unique().tolist()
        self.N = len(self.dataset)
        self.H = H

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))
    
    def update_sketch_matrix(self,v,j):
        """
        Updates the sketch matrix based on the given privatized data.

        Args:
            v (numpy.ndarray): The privatized vector.
            j (int): The index of the hash function used.
        """
        c_e = (np.exp(self.epsilon/2)+1) / ((np.exp(self.epsilon/2))-1)
        x = self.k * ((c_e/2) * v + (1/2) * np.ones_like(v))
        for i in range (self.m):
            self.M[j,i] += x[i]

    def execute_server(self,privatized_data):
        """
        Executes the server-side operations, including updating the sketch matrix
        and estimating the frequencies.

        Args:
            privatized_data (list): The privatized data from the client.

        Returns:
            dict: A dictionary containing the estimated frequencies for each element.
        """
        with Progress() as progress:
            task = progress.add_task('[cyan]Update sketch matrix', total=len(privatized_data))

            for data in privatized_data:
                self.update_sketch_matrix(data[0],data[1])
                progress.update(task, advance=1)

            F_estimated = {}
            task = progress.add_task('[cyan]Obtaining histogram of estimated frequencies', total=len(self.domain))
            for x in self.domain:
                F_estimated[x] = self.estimate_server(x)
                progress.update(task, advance=1)
                
        return F_estimated

    def estimate_server(self,d):
        """
        Estimates the frequency of an element based on the current sketch matrix.

        Args:
            d (any): The element whose frequency is to be estimated.

        Returns:
            float: The estimated frequency of the element.
        """
        sum_aux = 0
        for i in range(self.k):
            selected_hash = self.H[i]
            sum_aux += self.M[i, selected_hash(d)]
        
        f_estimated = (self.m/(self.m-1))*((sum_aux/self.k)-(self.N/self.m))
        return f_estimated
    
    def query_server(self, query_element):
        """
        Queries the server for the estimated frequency of an element.

        Args:
            query_element (any): The element to query.

        Returns:
            float or str: The estimated frequency of the element, or a message if the element is not in the domain.
        """
        if query_element not in self.domain:
            return "Element not in the domain"
        estimation = self.estimate_server(query_element)
        return estimation
    
def run_private_cms_server(k, m, e, df, H, privatized_data):
    """
    Runs the server-side operations for the Private Count-Mean Sketch, including
    estimating frequencies and querying the server.

    Args:
        k (int): The number of hash functions.
        m (int): The size of the sketch.
        e (float): The privacy parameter epsilon.
        df (pandas.DataFrame): The dataset containing the values.
        H (list): The list of hash functions.
        privatized_data (list): The privatized data from the client.
    """
    #Initialize the server Count-Mean Sketch
    server = privateCMSServer(e, k, m, df, H)

    # Save the privatized data
    privatized_data_save = pd.DataFrame(privatized_data)
    
    # Execute the server
    f_estimated = server.execute_server(privatized_data)

    # Query the server
    while True:
        query = input("Enter a event to query the server or 'exit' to finish: ")
        if query.lower() == 'exit':
            break
        estimation = server.query_server(query)
        print(f"The estimated frequency of {query} is {estimation:.2f}")
    
    return privatized_data_save

def run_private_cms_server_multiuser(k, m, private):
    """
    Runs the server-side operations for the Private Count-Mean Sketch,
    storing a separate server instance for each user.

    Args:
        k (int): The number of hash functions.
        m (int): The size of the sketch.
        e (float): The privacy parameter epsilon.
        df (pandas.DataFrame): The dataset containing the values.
        H (list): The list of hash functions.
        privatized (dict): A dictionary where keys are users and values contain privatized data.

    Returns:
        dict: A dictionary of servers where each user has its own server instance.
    """

    user_servers = {}

    with Progress() as progress:
        task = progress.add_task("[cyan]Initializing servers...", total=len(private))

        for user, data in private.items():
            progress.update(task, advance=1, description=f"[cyan]Processing user {user}...")

            e = data["e"]
            privatized_data = data["privatized_data"]
            H = data["result"]

            df = pd.DataFrame(privatized_data)

            #Initialize the server Count-Mean Sketch
            server = privateCMSServer(e, k, m, df, H)
            
            f_estimated = server.execute_server(privatized_data)
            
            user_servers[user] = server
    
    print(F"✅ {Fore.GREEN}All user servers initialized.{Style.RESET_ALL}")
    
    while True:
        user_query = input("Enter a user to query or 'exit' to finish: ")
        if user_query.lower() == 'exit':
            break
        if user_query not in user_servers:
            raise ValueError(f"❌ {Fore.RED}User '{user_query}' not found.{Style.RESET_ALL}")
        
        event_query = input(f"Enter an event for user {user_query}: ")
        estimation = user_servers[user_query].query_server(event_query)
        print(f"The estimated frequency of '{event_query}' for user '{user_query}' is {estimation:.2f}")

