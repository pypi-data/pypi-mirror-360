"""
This subpackage contains implementations of algorithms for calculating private count means
using the Count-Mean-Sketch (CMS) approach. The Count-Mean-Sketch is a probabilistic data
structure that allows for efficient frequency estimation while providing differential privacy
guarantees. This subpackage includes both client-side and server-side implementations for
privacy-preserving data aggregation.

Modules:
- cms_client_mean.py: Implements the client-side logic for generating private count means.
- private_cms_client.py: Contains the client-side logic for perturbing data before sending it to the server.
- private_cms_server.py: Implements the server-side logic for aggregating and analyzing perturbed data.

Main Functions:
- execute_client: Simulates the client side of the privatized Count-Min Sketch for all elements in the dataset.
- server_simulator: Simulates the server side of the privatized Count-Min Sketch, processes the privatized data, and estimates frequencies.
- update_sketch_matrix: Updates the sketch matrix based on the privatized data received from the client.
- estimate_client: Estimates the frequency of an element based on the private CMS sketch matrix.
"""