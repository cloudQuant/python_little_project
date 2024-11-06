"""This is for all the code used to interact with the AlphaVantage API
and the SQLite database. Remember that the API relies on a key that is
stored in your `.env` file and imported via the `config` module.
"""

import sqlite3

import pandas as pd
import requests
from config import settings


class AlphaVantageAPI:
    def __init__(self, alpha_api_key):
        self.__api_key = alpha_api_key

    def get_daily(self, ticker, output_size="full"):
        import requests
        url = (f"https://learn-api.wqu.edu/1/data-services/alpha-vantage/query?"
               "function=TIME_SERIES_DAILY"
               f"&outputsize={output_size}"
               f"&datatype=json"
               f"&symbol={ticker}"
               f"&apikey={settings.alpha_api_key}"
               )

        # Send request to API (8.1.6)
        try:
            response = requests.get(url)

            # Extract JSON data from response (8.1.10)
            response_data = response.json()

            # Read data into DataFrame (8.1.12 & 8.1.13)
            stock_data = response_data['Time Series (Daily)']
            df = pd.DataFrame(stock_data).T

            # Convert `df_ambuja` index to `DatetimeIndex`
            df.index = pd.to_datetime(df.index)

            # Name index "date"
            df.index.name = "date"
            # Remove numbering from `df_ambuja` column names
            df.columns = [i.split(". ")[1] for i in df.columns]

            df = df.astype("float")
        except Exception as e:
            print(e)
            df = pd.DataFrame()

        # Return DataFrame
        return df


class SQLRepository:
    def __init__(self, connection):
        self.connection = connection

    def insert_table(self, table_name, records, if_exists="fail"):

        """Insert DataFrame into SQLite database as table

        Parameters
        ----------
        table_name : str
        records : pd.DataFrame
        if_exists : str, optional
            How to behave if the table already exists.

            - 'fail': Raise a ValueError.
            - 'replace': Drop the table before inserting new values.
            - 'append': Insert new values to the existing table.

            Dafault: 'fail'

        Returns
        -------
        dict
            Dictionary has two keys:

            - 'transaction_successful', followed by bool
            - 'records_inserted', followed by int
        """

        # Validate if_exists parameter
        if if_exists not in ["fail", "replace", "append"]:
            raise ValueError("Invalid value for if_exists. Choose from 'fail', 'replace', or 'append'.")

        # Check if the table exists
        cursor = self.connection.cursor()
        # cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        # table_exists = cursor.fetchone() is not None
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        tables = [i[1] for i in tables]
        table_exists = table_name in tables
        if table_exists:
            if if_exists == "fail":
                raise ValueError(f"Table '{table_name}' already exists.")
            elif if_exists == "replace":
                cursor.execute(f"DROP TABLE IF EXISTS '{table_name}' ")
            elif if_exists == "append":
                # Check for duplicates if appending
                existing_records = pd.read_sql_query(f"SELECT * FROM '{table_name}'", self.connection)
                print(existing_records.head())
                # Identify records that are not already in the table
                new_records = records[
                    ~records.index.isin(existing_records.set_index(existing_records.columns[0]).index)]

                # Update records with only non-duplicates
                records = new_records

        # Insert the DataFrame into the SQLite table
        # Insert the DataFrame into the SQLite table, only if records are non-empty
        if not records.empty:
            records.to_sql(table_name, self.connection, if_exists="append", index=True)
        else:
            print("没有新的待追加的数据")

        # Commit the transaction
        self.connection.commit()

        # Get the number of records inserted
        cursor.execute(f"SELECT COUNT(*) FROM '{table_name}' ")
        records_inserted = cursor.fetchone()[0]

        return {
            'transaction_successful': True,
            'records_inserted': records_inserted
        }

    def read_table(self, table_name, limit=None):

        """Read table from database.

        Parameters
        ----------
        table_name : str
            Name of table in SQLite database.
        limit : int, None, optional
            Number of most recent records to retrieve. If `None`, all
            records are retrieved. By default, `None`.

        Returns
        -------
        pd.DataFrame
            Index is DatetimeIndex "date". Columns are 'open', 'high',
            'low', 'close', and 'volume'. All columns are numeric.
        """
        # Create SQL query (with optional limit)
        if limit is None:
            query = f"SELECT * FROM '{table_name}' "
        else:
            query = f"SELECT * FROM '{table_name}' ORDER BY date DESC LIMIT {limit}"

        # Retrieve data, read into DataFrame
        df = pd.read_sql_query(query, self.connection)

        # Set the index to 'date' and convert it to DatetimeIndex
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Ensure all columns are numeric
        df = df.astype("float64")
        return df