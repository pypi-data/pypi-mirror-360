import pandas as pd


def save_table(data, columns, table_name, date, storage):
    # columns number must be equal to data number of columns
    if len(columns) != len(data):
        raise ValueError("columns number must be equal to data number of columns")
    # check if table exists in storage
    # if table exists, append data to table
    # if table does not exist, create table with data
    if table_name in storage.list():
        base_df = storage.read(table_name)

        # Handle pd.DateTimeIndex, converting index to string
        if isinstance(base_df.index, pd.DatetimeIndex):
            base_df.index = base_df.index.strftime("%Y-%m-%d")

        # Check if date already exists in table
        if date in base_df.index:
            base_df.drop(index=date, inplace=True)

        df = pd.concat(
            [pd.DataFrame([data], columns=columns, index=[date]), base_df.loc[:]]
        )
    else:
        # create table with data
        df = pd.DataFrame([data], columns=columns, index=[date])

    # Save DataFrame to storage
    storage.create(data=df, name=table_name)

    return df
