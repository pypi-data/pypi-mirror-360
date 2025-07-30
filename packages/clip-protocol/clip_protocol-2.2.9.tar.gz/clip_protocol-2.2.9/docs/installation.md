
#  Installation
Setting up the **CLiP Protocol** on your device is simple and quick!

## 📦 Install via PyPI
Run the following command to install:
```
pip install clip-protocol
```
> 📎 Note: You can also view the package on [PyPI](https://pypi.org/project/clip-protocol/).

## ⚙️ Usage
Once installed, you can execute the following commands to run the privacy adjustment methods:

### Setup
Prepares your dataset for the CLiP workflow.
This step **formats** and **validates** your input data for the next phases.

```
setup -d <dataset>
```

-  `<dataset>`: Path to the input dataset in `.xlsx` format.

### Mask
Applies **personalized local differential privacy** to your dataset.
This command **privatizes** the data based on individual privacy budgets.

```
mask -d <dataset> -o <output>
```

-  `<dataset>`: Path to the input dataset you want to privatize.
- `output`: Path to where the privatized dataset will be saved.

> 📎 Note: After masking, a new `.csv` file will be created containing the privatized data.

*The `output` variable is optional, if it is not needed to save the privatized data you can skip it*

### Aggregation
Combines the privatized data points into **frequency sketches**.
This command **updates the server-side structures** needed for final analysis.
```
agregate
```
This command updates the frequency sketches based on the privatized inputs.
### Estimation
Estimates the **true frequencies** from the aggregated privatized data.
This command **answers frequency** queries based on the collected sketches.
```
estimate
```

### Clear
Use this command when it is needed to delete all data saved from the previous steps.
```
clip_clear
```

## Important Notes
- ✅ Ensure that dataset paths are correct and accessible.

- 🛡️ Make sure you have permission to read/write at the specified locations.

- 📄 The mask step will output a .csv file containing the privatized version of your dataset.