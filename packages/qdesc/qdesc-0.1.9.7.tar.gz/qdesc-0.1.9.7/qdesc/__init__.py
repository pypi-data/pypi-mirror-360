

def desc(df):
    import pandas as pd
    import numpy as np
    from scipy.stats import anderson
    x = np.round(df.describe().T,2)
    x = x.iloc[:, [0,1,2,5,3,7]]
    x.rename(columns={'50%': 'median'}, inplace=True)
    mad_values = {}
    # computes the manual mad which is more robust to outliers and non-normal distributions
    for column in df.select_dtypes(include=[np.number]):
        median = np.median(df[column])
        abs_deviation = np.abs(df[column] - median)
        mad = np.median(abs_deviation)
        mad_values[column] = mad
    mad_df = pd.DataFrame(list(mad_values.items()), columns=['Variable', 'MAD'])
    mad_df.set_index('Variable', inplace=True)
    results = {}
    # Loop through each column to test only continuous variables (numeric columns)
    for column in df.select_dtypes(include=[np.number]):  # Only continuous variables
        result = anderson(df[column])
        statistic = result.statistic
        critical_values = result.critical_values
        # Only select the 5% levels
        selected_critical_values = {
            '5% crit_value': critical_values[2]
        }
        # Store the results in a dictionary
        results[column] = {
            'AD_stat': statistic,
            **selected_critical_values  # Add critical values for 5%
        }
    # Convert the results dictionary into a DataFrame
    anderson_df = pd.DataFrame.from_dict(results, orient='index')
    xl = x.iloc[:, :4]
    xr = x.iloc[:, 4:]
    x_df = np.round(pd.concat([xl, mad_df, xr, anderson_df], axis=1),2)
    return x_df


def grp_desc(df, numeric_col, group_col):
    import pandas as pd
    import numpy as np
    from scipy.stats import median_abs_deviation, anderson
    results = []
    for group, group_df in df.groupby(group_col):
        data = group_df[numeric_col].dropna()
        if len(data) < 2:
            # Not enough data for stats like std or AD test
            stats = {
                group_col: group,
                'count': len(data),
                'mean': np.nan,
                'std': np.nan,
                'median': np.nan,
                'mad': np.nan,
                'min': np.nan,
                'max': np.nan,
                'anderson_stat': np.nan,
                'crit_5%': np.nan
            }
        else:
            ad_result = anderson(data, dist='norm')
            stats = {
                group_col: group,
                'count': len(data),
                'mean': data.mean(),
                'std': data.std(),
                'median': data.median(),
                'mad': median_abs_deviation(data),
                'min': data.min(),
                'max': data.max(),
                'AD_stat': ad_result.statistic,
                'crit_5%': ad_result.critical_values[2],  # 5% is the third value
            }
        results.append(stats)
    return np.round(pd.DataFrame(results),2)

def freqdist(df, column_name):
    import pandas as pd
    import numpy as np
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")
    
    if df[column_name].dtype not in ['object', 'category']:
        raise ValueError(f"Column '{column_name}' is not a categorical column.")
    
    freq_dist = df[column_name].value_counts().reset_index()
    freq_dist.columns = [column_name, 'Count']
    freq_dist['Percentage'] = np.round((freq_dist['Count'] / len(df)) * 100,2)
    return freq_dist


def freqdist_a(df, ascending=False):
    import pandas as pd
    import numpy as np
    results = []  
    for column in df.select_dtypes(include=['object', 'category']).columns:
        frequency_table = df[column].value_counts()
        percentage_table = np.round(df[column].value_counts(normalize=True) * 100,2)

        distribution = pd.DataFrame({
            'Column': column,
            'Value': frequency_table.index,
            'Count': frequency_table.values,
            'Percentage': percentage_table.values
        })
        distribution = distribution.sort_values(by='Percentage', ascending=ascending)
        results.append(distribution)
    final_df = pd.concat(results, ignore_index=True)
    return final_df

def clean_sheet_name(name):
    import re
    # Remove invalid characters
    name = re.sub(r'[:\\/?*\[\]]', '', name)
    # Limit to 31 characters
    name = name.strip()[:31]
    return name

def freqdist_to_excel(df, output_path, sort_by='Percentage', ascending=False, top_n=None):
    import pandas as pd
    import numpy as np
    used_names = set()
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        for column in df.select_dtypes(include=['object', 'category']).columns:
            frequency_table = df[column].value_counts()
            percentage_table = df[column].value_counts(normalize=True) * 100

            distribution = pd.DataFrame({
                'Value': frequency_table.index,
                'Count': frequency_table.values,
                'Percentage': percentage_table.values
            })
            distribution = distribution.sort_values(by=sort_by, ascending=ascending)
            if top_n is not None:
                distribution = distribution.head(top_n)
            # Generate safe sheet name
            base_name = clean_sheet_name(column)
            sheet_name = base_name
            count = 1
            while sheet_name.lower() in used_names:
                sheet_name = f"{base_name[:28]}_{count}"  # stay within 31 char limit
                count += 1
            used_names.add(sheet_name.lower())
            distribution.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Frequency distributions written to {output_path}")

def normcheck_dashboard(df, significance_level=0.05, figsize=(18, 5)):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import statsmodels.api as sm
    from scipy.stats import anderson
    import math
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        print("No numeric columns to analyze.")
        return
    for col in numeric_cols:
        data = df[col].dropna()
        print(f"\n--- Variable: {col} ---")
        if len(data) < 8:
            print("Not enough data to perform Anderson-Darling test or meaningful plots.")
            continue
        # Anderson-Darling Test
        test_result = anderson(data, dist='norm')
        stat = test_result.statistic
        sig_levels = test_result.significance_level
        crit_values = test_result.critical_values
        level_diff = [abs(sl - (significance_level * 100)) for sl in sig_levels]
        closest_index = level_diff.index(min(level_diff))
        used_sig = sig_levels[closest_index]
        crit_val = crit_values[closest_index]
        decision = "Fail to Reject Null" if stat <= crit_val else "Reject Null"
        # Print Summary
        print(f"  Anderson-Darling Statistic : {stat:.4f}")
        print(f"  Critical Value (@ {used_sig}%) : {crit_val:.4f}")
        print(f"  Decision : {decision}")
        # Plots (QQ, Histogram, Boxplot)
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        # QQ Plot
        sm.qqplot(data, line='s', ax=axes[0])
        axes[0].set_title(f"QQ Plot - {col}")
        # Histogram (No KDE)
        sns.histplot(data, bins=30, kde=False, color='gray', alpha=0.3, ax=axes[1])
        axes[1].set_title(f"Histogram - {col}")
        # Boxplot
        sns.boxplot(x=data, ax=axes[2], color='lightblue')
        axes[2].set_title(f"Boxplot - {col}")
        axes[2].set_xlabel(col)
        plt.suptitle(f"Normality Assessment - {col}", fontsize=14, y=1.05)
        plt.tight_layout()
        plt.show()
