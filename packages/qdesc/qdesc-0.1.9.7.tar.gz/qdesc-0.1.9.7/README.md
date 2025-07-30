# <font face = 'Impact' color = '#274472' >  qdesc : Quick and Easy Descriptive Analysis </font>
![QDesc](https://raw.githubusercontent.com/Dcroix/qdesc/refs/heads/main/QDesc%20logo.png)

![Package Version](https://img.shields.io/badge/version-0.1.9.6-pink)
![Downloads](https://pepy.tech/badge/qdesc)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
[![DOI](https://zenodo.org/badge/990715642.svg)](https://doi.org/10.5281/zenodo.15834554)
![License: GPL v3.0](https://img.shields.io/badge/license-GPL%20v3.0-blue)

## <font face = 'Calibri' color = '#274472' >  Installation </font>
```sh
pip install qdesc
```

## <font face = 'Calibri' color = '#274472' >  Overview </font>
Qdesc is a package for quick and easy descriptive analysis. It is a powerful Python package designed for quick and easy descriptive analysis of quantitative data. It provides essential statistics like mean and standard deviation for normal distribution and median and raw median absolute deviation for skewed data. With built-in functions for frequency distributions, users can effortlessly analyze categorical variables and export results to a spreadsheet. The package also includes a normality check dashboard, featuring Anderson-Darling statistics and visualizations like histograms and Q-Q plots. Whether you're handling structured datasets or exploring statistical trends, qdesc streamlines the process with efficiency and clarity.

## <font face = 'Calibri' color = '#274472' >  Creating a sample dataframe</font>
```python
import pandas as pd
import numpy as np

# Create sample data
data = {
    "Age": np.random.randint(18, 60, size=15),  # Continuous variable
    "Salary": np.random.randint(30000, 120000, size=15),  # Continuous variable
    "Department": np.random.choice(["HR", "Finance", "IT", "Marketing"], size=15),  # Categorical variable
    "Gender": np.random.choice(["Male", "Female"], size=15),  # Categorical variable
}
# Create DataFrame
df = pd.DataFrame(data)
```
## <font face = 'Calibri' color = '#274472' >  qd.desc Function</font>
The function qd.desc(df) generates the following statistics:
* count - number of observations
* mean - measure of central tendency for normal distribution	
* std - measure of spread for normal distribution
* median - measure of central tendency for skewed distributions or those with outliers
* MAD - measure of spread for skewed distributions or those with outliers; this is manual Median Absolute Deviation (MAD) which is more robust when dealing with non-normal distributions.
* min - lowest observed value
* max - highest observed value	
* AD_stat	- Anderson - Darling Statistic
* 5% crit_value - critical value for a 5% Significance Level	
* 1% crit_value - critical value for a 1% Significance Level

```python
import qdesc as qd
qd.desc(df)

| Variable | Count | Mean  | Std Dev | Median | MAD   | Min   | Max    | AD Stat | 5% Crit Value |
|----------|-------|-------|---------|--------|-------|-------|--------|---------|---------------|
| Age      | 15.0  | 37.87 | 13.51   | 38.0   | 12.0  | 20.0  | 59.0   | 0.41    | 0.68          |
| Salary   | 15.0  | 72724 | 29483   | 67660  | 26311 | 34168 | 119590 | 0.40    | 0.68          |
```

## <font face = 'Calibri' color = '#274472' >  qd.grp_desc Function</font>
This function, qd.grp_desc(df, "Continuous Var", "Group Var") creates a table for descriptive statistics similar to the qd.desc function but has the measures
presented for each level of the grouping variable. It allows one to check whether these measures, for each group, are approximately normal or not. Combining it
with qd.normcheck_dashboard allows one to decide on the appropriate measure of central tendency and spread.

```python
import qdesc as qd
qd.grp_desc(df, "Salary", "Gender")

| Gender  | Count | Mean  -   | Std Dev   | Median   | MAD      | Min    | Max     | AD Stat | 5% Crit Value |
|---------|-------|-----------|-----------|----------|----------|--------|---------|---------|---------------|
| Female  | 7     | 84,871.14 | 32,350.37 | 93,971.0 | 25,619.0 | 40,476 | 119,590 | 0.36    | 0.74          |
| Male    | 8     | 62,096.12 | 23,766.82 | 60,347.0 | 14,278.5 | 34,168 | 106,281 | 0.24    | 0.71          |
```

## <font face = 'Calibri' color = '#274472' >  qd.freqdist Function</font>
Run the function qd.freqdist(df, "Variable Name") to easily create a frequency distribution for your chosen categorical variable with the following:
* Variable Levels (i.e., for Sex Variable: Male and Female)
* Counts - the number of observations
* Percentage - percentage of observations from total.

```python
import qdesc as qd
qd.freqdist(df, "Department")

| Department | Count | Percentage |
|------------|-------|------------|
| IT         | 5     | 33.33     |
| HR         | 5     | 33.33     |
| Marketing  | 3     | 20.00     |
| Finance    | 2     | 13.33     |
```

## <font face = 'Calibri' color = '#274472' >  qd.freqdist_a Function</font>
Run the function qd.freqdist_a(df, ascending = FALSE) to easily create frequency distribution tables, arranged in descending manner (default) or ascending (TRUE), for all the categorical variables in your data frame. The resulting table will include columns such as:
* Variable levels (i.e., for Satisfaction: Very Low, Low, Moderate, High, Very High) 
* Counts - the number of observations
* Percentage - percentage of observations from total.

```python
import qdesc as qd
qd.freqdist_a(df)

| Column     | Value     | Count | Percentage |
|------------|----------|-------|------------|
| Department | IT       | 5     | 33.33%     |
| Department | HR       | 5     | 33.33%     |
| Department | Marketing| 3     | 20.00%     |
| Department | Finance  | 2     | 13.33%     |
| Gender     | Male     | 8     | 53.33%     |
| Gender     | Female   | 7     | 46.67%     |
```

## <font face = 'Calibri' color = '#274472' >  qd.freqdist_to_excel Function</font>
Run the function qd.freqdist_to_excel(df, "Filename.xlsx", ascending = FALSE ) to easily create frequency distribution tables, arranged in descending manner (default) or ascending (TRUE), for all  the categorical variables in your data frame and SAVED as separate sheets in the .xlsx File. The resulting table will include columns such as:
* Variable levels (i.e., for Satisfaction: Very Low, Low, Moderate, High, Very High) 
* Counts - the number of observations
* Percentage - percentage of observations from total.

```python
import qdesc as qd
qd.freqdist_to_excel(df, "Results.xlsx")

Frequency distributions written to Results.xlsx
```

## <font face = 'Calibri' color = '#274472' >  qd.normcheck_dashboard Function</font>
Run the function qd.normcheck_dashboard(df) to efficiently check each numeric variable for normality of its distribution. It will compute the Anderson-Darling statistic and create visualizations (i.e., qq-plot, histogram, and boxplots) for checking whether the distribution is approximately normal.

```python
import qdesc as qd
qd.normcheck_dashboard(df)
```
![Descriptive Statistics](https://raw.githubusercontent.com/Dcroix/qdesc/refs/heads/main/qd.normcheck_dashboard.png)


## <font face = 'Calibri' color = '#3D5B59' >  License</font>
This project is licensed under the GPL-3 License. See the LICENSE file for more details.

## <font face = 'Calibri' color = '#3D5B59' >  Acknowledgements</font>
Acknowledgement of the libraries used by this package...

### <font face = 'Calibri' color = '#3D5B59' >  Pandas</font>
Pandas is distributed under the BSD 3-Clause License, pandas is developed by Pandas contributors. Copyright (c) 2008-2024, the pandas development team All rights reserved.
### <font face = 'Calibri' color = '#3D5B59' >  Numpy</font>
NumPy is distributed under the BSD 3-Clause License, numpy is developed by NumPy contributors. Copyright (c) 2005-2024, NumPy Developers. All rights reserved.
### <font face = 'Calibri' color = '#3D5B59' >  SciPy</font>
SciPy is distributed under the BSD License, scipy is developed by SciPy contributors. Copyright (c) 2001-2024, SciPy Developers. All rights reserved.





