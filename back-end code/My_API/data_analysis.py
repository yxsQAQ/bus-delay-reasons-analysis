import pandas as pd


def get_table_names(connection):
    query = "SHOW TABLES;"
    cursor = connection.cursor()
    cursor.execute(query)
    table_names = [table[0] for table in cursor.fetchall()]
    return table_names

def get_data_from_tables(connection, table_names):
    df = pd.DataFrame()
    for table_name in table_names:
        query = f"SELECT * FROM {table_name};"
        table_data = pd.read_sql(query, connection)
        df = df.append(table_data, ignore_index=True)
    return df

def get_statistical_data(data_name, data, dataframe):
    if not data.empty:
        Length_value = len(data)
        median_value = data.median()
        mean_value = data.mean()
        mode_value = data.mode().iloc[0]
        max_value = data.max()
        min_value = data.min()
        variance_value = data.var()
        quartiles_values = data.quantile([0.25, 0.75])
        skewness_value = data.skew()
        kurtosis_value = data.kurtosis()

        new_row = {
            'Name' : data_name,
            'Length': Length_value,
            'Median': median_value,
            'Mean': mean_value,
            'Mode': mode_value,
            'Maximum': max_value,
            'Minimum': min_value,
            'Variance': variance_value,
            'Quartile_0_25': quartiles_values[0.25],
            'Quartile_0_75': quartiles_values[0.75],
            'Skewness': skewness_value,
            'Kurtosis': kurtosis_value
        }

        dataframe = dataframe.append(new_row, ignore_index=True)

        return dataframe