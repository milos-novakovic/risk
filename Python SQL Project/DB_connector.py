import duckdb

def DB_connector(pos, hist_price):
    # Create / connect to DuckDB database file (this will create .duckdb file)
    con = duckdb.connect("commodity_data.duckdb")
    
    # Write the tables into the DB
    con.execute("CREATE OR REPLACE TABLE positions AS SELECT * FROM pos")
    con.execute("CREATE OR REPLACE TABLE historical_prices AS SELECT * FROM hist_price")

    # Read the same tables and compare with the initial to ensure writing correctness
    if (con.execute("SELECT * FROM positions").df().equals(pos)) and (con.execute("SELECT * FROM historical_prices").df().equals(hist_price)):
        print("Data successfully loaded into DuckDB.")
    else:
        print("There was an error loading into DuckDB.")

    # Table column types
    for table_name in con.execute("SHOW TABLES").df()['name'].to_list():
        print(f"In table {table_name} columns are:")
        print(con.execute(f"DESCRIBE {table_name}").df().to_string(), end='\n\n')
    con.close()