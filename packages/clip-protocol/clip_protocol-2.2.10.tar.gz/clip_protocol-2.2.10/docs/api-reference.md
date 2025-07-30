
# API Reference

## setup
```python
class Setup:
    def __init__(self, df)
```
Initializes the Setup instance.

Parameters:

- `df` (*pd.DataFrame*). The test dataset

```python
def ask_values(self)
```
Prompts the user to input configuration parameters.

Returns:

- `events_names` (list): Name of the columns in the dataset to be filtered. Two columns must be selected
    - One that contains the users name (later on they will be pseudonymize)
    - One that contains the event information we want to do estimations
- `privacy_method` (str): Name of the privacy method that will be used to privatized the dataset (Only can be PCMeS or PHCMS)
- `error_metric` (str): Name of the metric we wil use to calculate the error (Only can be MSE, Lp Norm or RMSE)
- `error_value` (float): Value of the maximun error we want our data to have (in decimal). For example, if we want a 2% maximun error, 0.02 must be written.
- `tolerance` (float): Value of the tolerance of the error it is needed.

```python
def filter_dataframe(self)
```
Filters the input DataFrame based on the selected event columns.

Returns:
- `pd.DataFrame`: The filtered DataFrame.

```python
def run_command(self, e, k, m)
```
Executes the selected privacy-preserving algorithm with the given parameters.

Parameters:

- `e`(float): Privacy budget (epsilon).
- `k` (int): Number of hash functions.
- `m` (int): Number of buckets.

Returns: 
- `error_table` (table). Table of all the parameters of error
- `df_estimated` (table). Table with the estimated frecuency of the events.

```python
def optimize_k_m(self, er=150)
```
Optimizes the parameters k and m using Optuna.

Parameters:

- `er` (float, optional): Initial reference value for epsilon. Default is 150.

Returns:
- `er`(float): Privacy budget (epsilon) of reference for the next stage.
- `k` (int): Number of hash functions.
- `m` (int): Number of buckets.

```python
def minimize_epsilon(self, k, m)
```
Minimizes the privacy budget (`epsilon`) while satisfying the defined error constraint.

Parameters:

- `k` (int): Number of hash functions.
- `m` (int): Number of buckets.

Returns:

- `e` (int): Optimal epsilon value.

## mask
```python
class Mask:
    def __init__(self, privacy_level, df):
```
Initializes the Mask instance by loading configuration parameters.

Parameters:

- `privacy_level` (str): Privacy level identifier.
- `df` (pd.DataFrame): The input dataset.

```python
def filter_dataframe(self)
```
Filters the input DataFrame based on previously selected event columns and pseudonymizes the user identifiers.
Returns:

- `pd.DataFrame`: The filtered and pseudonymized DataFrame.

```python
def calculate_metrics(self, f_estimated, f_real)
```
Calculates the evaluation metrics between estimated and real frequencies.
Parameters:

- `f_estimated` (pd.DataFrame): Estimated frequency distribution.
- `f_real` (pd.DataFrame): Real frequency distribution.

Returns:

- Placeholder for metric value calculation.

```python
def pseudonimize(self, user_name)
```
Takes a user's name as input and returns a pseudonymized version by hashing the name using the SHA-256 algorithm and truncating it to the first 10 characters.

Input:

- User's name (`user_name`).

Output:

- A 10-character pseudonymized hash of the user's name.

```python
 def optimize_e(self)
```
Optimizes the privacy parameter ϵ using Optuna to minimize the error between real and estimated frequencies while ensuring the selected privacy level is met. It returns the best ϵ value that achieves the desired privacy error threshold.
Input

- None (uses class attributes like `privacy_level`, `error_value`, and `tolerance`).

Output:

- The best optimized ϵ, privatized data, and associated coefficients.


## aggregate
```python
def update_sketch_matrix(M, k, e, privacy_method, data_point)
```
Updates the sketch matrix based on the privatized data using either the "PCMeS" or "PHCMS" privacy method. It processes the given data point and modifies the matrix accordingly.

Input:

- `M`: The sketch matrix.
- `k`: Parameter used in matrix updates.
- `e`: Privacy parameter.
- `privacy_method`: The privacy method to apply ("PCMeS" or "PHCMS").
- `data_point`: Data point used to update the matrix (could be vector, index, or weight).

Output:

- The updated sketch matrix (`M`).

```python
class Agregate:
    def __init__(self):
```
This is the constructor for the Agregate class. It loads the necessary privacy parameters and dataset for aggregation, initializing an empty dictionary to store user-specific sketches.

Output: 

- Initializes the Agregate instance with privacy settings and an empty dictionary for user sketches.

```python
def compute_data(self, user_data):
```
Computes a sketch matrix for a given user's data. It iterates over the user data and updates the sketch matrix using the specified privacy method. The progress of the operation is displayed.

Input: 

- `user_data`: Data related to a specific user.

Output: 

- A tuple with the user's ID and the computed sketch matrix (`M`) along with the number of data points (`N`).

```python
def agregate_per_user(self)
```
Aggregates sketches for all users in the dataset by processing their data with the compute_data function. It stores the resulting sketches in a dictionary.

Output: 

- A dictionary (`sketch_by_user`) mapping user IDs to their computed sketches.

## estimate
```python
class Estimation:
    def __init__(self):
```
Constructor for the Estimation class. It loads the necessary aggregated data (`sketch_by_user`) and privacy settings (`k`, `m`, `epsilon`, `hashes`, `method`) from JSON files to initialize the estimation process.

Output: 

- Initializes the Estimation instance with user sketches and privacy settings.

```python
def estimate_element(self, d, M, N)
```
Estimates the frequency of an element d in the dataset using the sketch matrix `M` and the number of data points `N`. The estimation is based on a formula involving the privacy settings.

Input:

- `d`: The element whose frequency is to be estimated.
- `M`: The sketch matrix for a user.
- `N`: The number of data points for the user.

Output: 
- The estimated frequency of the element `d` for the user.

```python
def query_all_users_event(self, event):
```
Estimates the frequency of an event for each user in the dataset. It prints the estimated frequency for each user by calling the `estimate_element` method.

Input: 

- `event`: The event (element) whose frequency needs to be estimated.

Output: 

- Prints the estimated frequency of the event for each user.

```python
def run_estimate()
```
Initializes the Estimation instance and prompts the user to input an event. It continuously estimates the frequency of the event for all users until the user decides to quit by entering "q".

## utils
```python
def save_setup_json(setup_instance)
```
Saves the initial setup configuration to a JSON file (`setup_config.json`), including parameters like `k`, `m`, `epsilon`, event names, privacy method, error metrics, tolerance, and p.

Input:

- `setup_instance`: Object containing the setup parameters.

Output: JSON configuration file saved.

```python
def load_setup_json()
```
Loads the setup configuration from the previously saved JSON file.

Output: Tuple with `k`, `m`, `epsilon`, `events_names`, `privacy_method`, `error_metric`, `error_value`, `tolerance` and `p`.

```python
def save_mask_json(mask_instance, e, coeffs, privatized_dataset)
```
Saves the mask configuration and the privatized dataset to disk (`mask_config.json` and `privatized_dataset.csv`).

Input:

- `mask_instance`: Mask configuration instance.
- `e`: Epsilon value.
- `coeffs`: Hash function coefficients.
- `privatized_dataset`: Privatized dataset.

Output: JSON and CSV files saved.

```python
def load_mask_json()
```

Loads the mask configuration, rebuilds the hash functions, and loads the privatized dataset.

Output: Tuple with`k`, `m`, `e`, rebuilt hash functions, `privacy_method`, and the dataset as a DataFrame.

```python
def save_agregate_json(agregate_instance)
```
Saves the user sketch aggregation object to a binary file (sketch_by_user).

Input:

- `agregate_instance`: Instance containing the user sketches.

```python
def load_agregate_json()
```
Loads the user sketch aggregation object from the binary file.

Output: Loaded sketch_by_user object.

```python
def deterministic_hash(x)
```
Generates a deterministic hash of an element using SHA-256, returning it as an integer.

Input:

- `x`: Element to be hashed.

Output: Deterministic hash as an integer.

```python
def generate_hash_functions(k, p, c, m)
```
Generates `k` hash functions based on random coefficients over a finite field defined by `p`, mapped to `m`.

Input:

- `k`: Number of hash functions.

- `p`: Large prime number for modular operations.

- `c`: Polynomial degree.

- `m`: Output range.

Output:

- List of hash functions.
- Dictionary with function parameters.

```python
def rebuild_hash_functions(functions_params)
```
Rebuilds hash functions from their stored coefficients and parameters.

Input:

- `functions_params`: Dictionary with `coefficients`, `p`, `m`, and `c`.

Output:

- List of rebuilt hash functions.

```python
def display_results(real_freq: pd.DataFrame, estimated_freq: dict)
```
Displays real vs estimated frequencies of elements, including absolute differences and percentage errors.

Input:

- `real_freq`: DataFrame with real frequencies.

- `estimated_freq`: Dictionary with estimated frequencies.

Output:

- List of tabulated results with real count, real percentage, estimated count, estimated percentage, difference, and percent error.

```python
def get_real_frequency(df)
```
Computes the real frequency of each element in a DataFrame.

Input:

- `df`: DataFrame containing a value column.

Output:

- DataFrame with columns Element and Frequency.


## 📎 Notes
- Make sure that your input file does not have incorrectly named columns (e.g., `Unnamed: 0`).

- Pseudonymization is applied using simple hashing.