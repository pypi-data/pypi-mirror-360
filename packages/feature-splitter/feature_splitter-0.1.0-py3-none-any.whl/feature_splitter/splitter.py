import pandas as pd

def split_df_by_variation(df, n_splits=4, prefix='Client'):
    """Splits a DataFrame into n_splits parts based on sorting by the column with the highest variance.
    Saves each split as a CSV file with filenames like '{prefix}1.csv', '{prefix}2.csv', etc.

    Parameters:
        df (pd.DataFrame): Input DataFrame.
        n_splits (int): Number of parts to split into.
        prefix (str): Prefix for the output CSV files.

    Returns:
        list of pd.DataFrame: List of split DataFrames.
    """
    most_variation_column = df.var().idxmax()
    print(f"The column with the most variation is: {most_variation_column}")

    df_sorted = df.sort_values(by=most_variation_column, ascending=True).reset_index(drop=True)

    split_size = len(df) // n_splits
    dfs = []

    for i in range(n_splits):
        start_idx = i * split_size
        end_idx = (i + 1) * split_size if i < n_splits - 1 else len(df)
        part_df = df_sorted.iloc[start_idx:end_idx]
        dfs.append(part_df)
        part_df.to_csv(f'{prefix}{i+1}.csv', index=False)

    return dfs