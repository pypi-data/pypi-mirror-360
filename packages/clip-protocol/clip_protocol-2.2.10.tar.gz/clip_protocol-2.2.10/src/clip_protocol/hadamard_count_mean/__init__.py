"""
This subpackage contains implementations of algorithms for calculating private count means
using the Hadamard Count-Mean-Sketch (HCMS) approach. The Hadamard transform is used to
efficiently encode and perturb data, ensuring differential privacy while maintaining data
utility. This subpackage includes both client-side and server-side implementations for
privacy-preserving data aggregation.

Modules:
- private_hcms_client.py: Contains the client-side logic for perturbing data using the Hadamard transform.
- private_hcms_server.py: Implements the server-side logic for aggregating and analyzing perturbed data.

Main Functions:
- execute_client: Simulates the client side of the privatized Count-Min Sketch for all elements in the dataset.
- server_simulator: Simulates the server side of the privatized Count-Min Sketch, processes the privatized data, and estimates frequencies.
- update_sketch_matrix: Updates the sketch matrix based on the privatized data received from the client.
- estimate_client: Estimates the frequency of an element based on the private CMS sketch matrix.
"""