import pandas as pd

def analyze_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Analyzes a pandas DataFrame and returns a summary of key statistics for each column.
    
    Generates a comprehensive analysis of the input DataFrame including data types, 
    missing values, and zero values. The output provides both counts and percentages 
    for better data quality assessment.

    Args
    ----
        df (pd.DataFrame): The DataFrame to be analyzed. Can contain mixed data types.

    Returns
    -------
        pd.DataFrame: A summary DataFrame with the following columns:
            - column: Name of the original DataFrame column
            - type: Data type of each column (as string)
            - n_nan: Count of missing/NaN values
            - perc_nan: Percentage of missing/NaN values (rounded to 2 decimals)
            - n_zeros: Count of zero values (numeric columns only)
            - perc_zeros: Percentage of zero values (numeric columns only, rounded to 2 decimals)

    Notes
    -------
        - For non-numeric columns, zero counts will be shown as 0
        - Percentages are calculated based on total rows in the input DataFrame
        - Missing values in zero-count columns are automatically filled with 0
        - The result DataFrame is returned with a reset index for easier manipulation

    Examples
    -------
        >>> import pandas as pd
        >>> import numpy as np
        >>> df = pd.DataFrame({
        ...     'A': [1, 2, 0, np.nan],
        ...     'B': ['x', 'y', 'z', np.nan],
        ...     'C': [0, 0, 0, 0]
        ... })
        >>> analyze_dataframe(df)
          column   type  n_nan  perc_nan  n_zeros  perc_zeros
        0     A  float64      1     25.0        1       25.00
        1     B   object      1     25.0        0        0.00
        2     C    int64      0      0.0        4      100.00
    """
    # Initialize dictionary to store results
    data = {
        'type': df.dtypes.astype(str),
        'n_nan': df.isna().sum(),
        'perc_nan': (df.isna().mean() * 100).round(2),
        'n_zeros': (df == 0).sum(numeric_only=True),
        'perc_zeros': ((df == 0).mean(numeric_only=True) * 100).round(2),
    }

    # Create final dataframe
    result_df = pd.DataFrame(data)
    result_df.index.name = 'column'

    # Replace NaN with 0 in zero count columns (for non-numeric columns)
    result_df['n_zeros'] = result_df['n_zeros'].fillna(0).astype(int)
    result_df['perc_zeros'] = result_df['perc_zeros'].fillna(0)

    return result_df.reset_index()

def dataframe_to_text(df: pd.DataFrame) -> str:
    """Converts a pandas DataFrame into a formatted markdown-style table string.

    Transforms the DataFrame into a text representation with markdown table syntax,
    including column headers and separator lines. The output is compatible with
    markdown viewers and provides a clean text representation of tabular data.

    Args
    ----
        df (pd.DataFrame): The pandas DataFrame to be converted to text format.
                           Should contain data that can be safely converted to strings.

    Returns
    -------
        str: A markdown-formatted table string representation of the DataFrame,
             with the following structure:
             
             |Column1|Column2|...|
             |---|---|...|
             |value1|value2|...|
             |...|...|...|

    Notes
    -----
        - The function creates a markdown-compatible table with alignment separators
        - All values are converted to strings using default pandas formatting
        - The table includes a header row and separator line automatically
        - Empty DataFrames will return a valid markdown table structure with just headers

    Examples
    --------
        >>> df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})
        >>> print(dataframe_to_text(df))
        |A|B|
        |---|---|
        |1|x|
        |2|y|

        >>> df_empty = pd.DataFrame(columns=['X', 'Y'])
        >>> print(dataframe_to_text(df_empty))
        |X|Y|
        |---|---|
    """
    text = "|"
    for column in df.columns:
        text += f"{column}|"
    text = text[:-1]
    text += "\n|" + "---|" * len(df.columns) + "\n|"

    for index, row in df.iterrows():
        for column in df.columns:
            text += f"{row[column]}|"
        text += "\n"

    return text