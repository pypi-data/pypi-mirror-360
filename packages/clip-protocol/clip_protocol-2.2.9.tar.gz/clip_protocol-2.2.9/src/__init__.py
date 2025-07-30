"""
This module initializes the Local_Privacy package and specifies the core imports
necessary for utilizing its local differential privacy functionalities.

The Local_Privacy package provides a suite of differential privacy algorithms 
designed to safeguard user data privacy while preserving the utility of aggregated 
data. These algorithms are organized into distinct modules and subpackages to ensure 
ease of use, flexibility, and scalability.

Core Modules:
- `individual_method.py`: Implements the differential privacy algorithm for single-user datasets.
- `general_method.py`: Implements the differential privacy algorithm for multi-user datasets.

Subpackages:
- `private_count_mean`: Contains algorithms for performing private mean calculations on count data.
- `private_hadamard_count_mean`: Implements private mean calculation algorithms utilizing the Hadamard transform.
"""
