import pyodbc

server = 'servername.database.windows.net'
database = 'databasename'
username = 'username'
password = 'password'   
driver= '{ODBC Driver 17 for SQL Server}'


def create_connection(data=None, customer_id=None):
    try:
        with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                if customer_id is not None:
                    value = cursor.execute(f"SELECT * FROM dbo.Customer where CustomerID = {customer_id}")
                row = list(cursor.fetchone())
                return row
    except Exception as e:
        return None
        print("Error:",e)
