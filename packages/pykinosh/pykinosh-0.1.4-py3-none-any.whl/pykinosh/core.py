# -*- coding: utf-8 -*-
"""
Created on Sun Jun 29 08:05:31 2025

@author: DELL
"""

import pandas as pd
from sqlalchemy import create_engine
#import numpy as np


def pull_data(sheet_id, to_csv=False):
    """Pulls data from googlesheets or online excel files and creates
    DataFrames from each sheet. It also exports as CSV.

    Parameters
    ----------
    sheet_id : str, the unique id of the sheet
        
    to_csv : bool, True or False
        Returns CSV files if True and returns DataFrames otherwise. (Default value = False)

    Returns
    -------
    It returns either a CSV file or multiple DataFrames depending `to_csv` parameter 
    
    """
       
    global df_names
    try:
        #Establishing the connection
        xlsx = pd.ExcelFile(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx")
        
        #Extracting sheets into a list
        df_names = []
        sheet_names = xlsx.sheet_names
        
        
        if to_csv == True:
            for sheet in sheet_names:
                df_name = f"{sheet.lower().strip().replace(' ','_')}_df"
                globals()[df_name] = pd.read_excel(xlsx, sheet_name = sheet)
                df_names.append(df_name)
                globals()[df_name].to_csv(f"{df_name}.csv", index=False)
        elif to_csv == False:
            for sheet in sheet_names:
                df_name = f"{sheet.lower().strip().replace(' ','_')}_df"
                df_names.append(df_name)
                globals()[df_name] = pd.read_excel(xlsx, sheet_name = sheet)
            
            print(f"The following DataFrames have been created: {df_names}")
        
    except Exception as e:
        print(f"An error occured: {e}.")
        
#CONNECTING TO THE SQL SERVER
def connect_db(dbms, database_name, username, password=None, port=None, to_csv=False):
    """
    It connects to RDBMS and returns dataframes for each table in the database.
    It supports MysQL, PostgreSQL, SQLServer.
    
    Parameters
    ----------
    dbms :takes in a string. Particularly one of three values - `sqlserver`,`postgresql`,`mysql`
        
    database_name : takes in a string.
        This is the name of the database to be conncected.
    username : takes in a string.
        This is the username of the database. Default is `root` for mysql and `postgres` for postgreSQL.
    password :
         (Default value = None)
    port : The port for the localhost. It takes in an integer if necessary. Default is 5432 for postgreSQL
         (Default value = None)

    Returns
    -------
    DataFrames for as many tables that are in the database
    """
    global table_list
    global table_df
    table_df = []
    if to_csv == False:
        if dbms == "sqlserver":
            if password == None:
                #Without Password
                connection_uri = f"mssql+pyodbc://@{username}\\SQLEXPRESS/{database_name}"f"?driver=ODBC+Driver+17+for+SQL+Server"f"&trusted_connection=yes"
                engine = create_engine(connection_uri)
                
                table_list = pd.read_sql(f"SELECT * FROM {database_name}.INFORMATION_SCHEMA.TABLES;", connection_uri)["TABLE_NAME"].to_list()[:-1]
                for table in table_list:
                    table_name = f"{table.lower()}_df"
                    globals()[table_name] = pd.read_sql(f"SELECT * FROM {table}", engine)
                    table_df.append(table_name)
                print(f"These are the tables available in the {database_name} database: {table_list}.")
                print(f"The following DataFrames have been created: {table_df}.")
            else:
                #With Password
                connection_uri = f"mssql+pyodbc://{username}:{password}@{username}\\SQLEXPRESS/{database_name}"f"?driver=ODBC+Driver+17+for+SQL+Server"
                engine = create_engine(connection_uri)
                
                table_list = pd.read_sql(f"SELECT * FROM {database_name}.INFORMATION_SCHEMA.TABLES;", connection_uri)["TABLE_NAME"].to_list()[:-1]
                table_df = []
                for table in table_list:
                    table_name = f"{table.lower()}_df"
                    globals()[table_name] = pd.read_sql(f"SELECT * FROM {table}", engine)
                    table_df.append(table_name)
                print(f"These are the tables available in the {database_name} database: {table_list}.")
    
        
            
        elif dbms == "postgres":
            connection_uri = (f"postgresql+psycopg2://{username}:{password}@localhost:{port}/{database_name}")
            engine = create_engine(connection_uri)
            
            table_list = pd.read_sql("""SELECT tablename
                            FROM pg_catalog.pg_tables
                            WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
                            """, engine)['tablename'].to_list()
            for table in table_list:
                table_name = f"{table.lower()}_df"
                globals()[table_name] = pd.read_sql(f"SELECT * FROM {table}", engine)
                table_df.append(table_name)
            print(f"These are the tables available in the {database_name} database: {table_list}.")
            print(f"The following DataFrames have been created: {table_df}.")
        
        elif dbms == "mysql":
            connection_uri = (f"mysql+mysqlconnector://{username}:{password}@localhost/{database_name}")
            engine = create_engine(connection_uri)
            
            table_list = pd.read_sql("SHOW TABLES", con=engine)[f"Tables_in_{database_name}"].to_list()
            for table in table_list:
                table_name = f"{table.lower()}_df"
                globals()[table_name] = pd.read_sql(f"SELECT * FROM {table}", engine)
                table_df.append(table_name)
            print(f"These are the tables available in the {database_name} database: {table_list}.")
            print(f"The following DataFrames have been created: {table_df}.")
        else:
            print(f"This package does not support {dbms} dbms of SQL for now. Look out for future updates.")
            
    elif to_csv == True:
        if dbms == "sqlserver":
            if password == None:
                #Without Password
                connection_uri = f"mssql+pyodbc://@{username}\\SQLEXPRESS/{database_name}"f"?driver=ODBC+Driver+17+for+SQL+Server"f"&trusted_connection=yes"
                engine = create_engine(connection_uri)
                
                table_list = pd.read_sql(f"SELECT * FROM {database_name}.INFORMATION_SCHEMA.TABLES;", connection_uri)["TABLE_NAME"].to_list()[:-1]
                for table in table_list:
                    table_name = f"{table.lower()}_df"
                    globals()[table_name] = pd.read_sql(f"SELECT * FROM {table}", engine)
                    table_df.append(table_name)
                    globals()[table_name].to_csv(f"{table_name}.csv", index=False)
                print(f"These are the tables available in the {database_name} database: {table_list}.")
                print(f"The following DataFrames have been created: {table_df}.")
            else:
                #With Password
                connection_uri = f"mssql+pyodbc://{username}:{password}@{username}\\SQLEXPRESS/{database_name}"f"?driver=ODBC+Driver+17+for+SQL+Server"
                engine = create_engine(connection_uri)
                
                table_list = pd.read_sql(f"SELECT * FROM {database_name}.INFORMATION_SCHEMA.TABLES;", connection_uri)["TABLE_NAME"].to_list()[:-1]
                table_df = []
                for table in table_list:
                    table_name = f"{table.lower()}_df"
                    globals()[table_name] = pd.read_sql(f"SELECT * FROM {table}", engine)
                    table_df.append(table_name)
                    globals()[table_name].to_csv(f"{table_name}.csv", index=False)
                print(f"These are the tables available in the {database_name} database: {table_list}.")
    
        
            
        elif dbms == "postgres":
            connection_uri = (f"postgresql+psycopg2://{username}:{password}@localhost:{port}/{database_name}")
            engine = create_engine(connection_uri)
            
            table_list = pd.read_sql("""SELECT tablename
                            FROM pg_catalog.pg_tables
                            WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
                            """, engine)['tablename'].to_list()
            for table in table_list:
                table_name = f"{table.lower()}_df"
                globals()[table_name] = pd.read_sql(f"SELECT * FROM {table}", engine)
                table_df.append(table_name)
                globals()[table_name].to_csv(f"{table_name}.csv", index=False)
            print(f"These are the tables available in the {database_name} database: {table_list}.")
            print(f"The following DataFrames have been created: {table_df}.")
        
        elif dbms == "mysql":
            connection_uri = (f"mysql+mysqlconnector://{username}:{password}@localhost/{database_name}")
            engine = create_engine(connection_uri)
            
            table_list = pd.read_sql("SHOW TABLES", con=engine)[f"Tables_in_{database_name}"].to_list()
            for table in table_list:
                table_name = f"{table.lower()}_df"
                globals()[table_name] = pd.read_sql(f"SELECT * FROM {table}", engine)
                table_df.append(table_name)
                globals()[table_name].to_csv(f"{table_name}.csv", index=False)
            print(f"These are the tables available in the {database_name} database: {table_list}.")
            print(f"The following DataFrames have been created: {table_df}.")
        else:
            print(f"This package does not support {dbms} dbms of SQL for now. Look out for future updates.")