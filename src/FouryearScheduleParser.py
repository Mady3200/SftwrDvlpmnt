import pandas as pd

def load_csv_schedule(csv_path, header_row):
    """
    Load a CSV file into a pandas DataFrame.

    Parameters:
    csv_path (str): The file path to the CSV file.
    header_row (int): The row number to use as the column names.

    Returns:
    pd.DataFrame: The loaded DataFrame.
    """
    df_4year = pd.read_csv(csv_path, header=header_row)
    return df_4year

if __name__ == "__main__":
    df_4year = load_csv_schedule(r"..\inputs_new\fouryear.csv", 0)