import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class DbManager:
    def __init__(self, dbUrl):
        self.dbUrl = dbUrl

    def execute_query(self, query, params=None, fetch=False):
        """Executes a query on the database with optional parameters."""
        try:
            # Establish a connection to the database
            conn = psycopg2.connect(self.dbUrl)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Execute the query with parameters (if provided)
            cursor.execute(query, params)
            
            # Commit if it is a modifying query
            if not fetch:
                conn.commit()
                cursor.close()
                conn.close()
                return f"Query executed successfully: {query}"
            
            # Fetch results if requested (for SELECT queries)
            else:
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result

        except Exception as e:
            return f"An error occurred: {str(e)}"

# Example of how you might use this DbManager
dbManager = DbManager(dbUrl='postgresql://catalyst:catalyst@192.168.0.100:5432/catalyst_data')

# Function to handle user input queries
def query_input_function():
    print("Enter your SQL query (or type 'exit' to quit):")
    while True:
        # Get the user's query
        query = input("SQL> ")
        
        # Exit on 'exit' keyword
        if query.lower() == 'exit':
            break
        
        # Check if it is a SELECT query to fetch results
        fetch = query.strip().lower().startswith("select")
        
        # Execute the query
        result = dbManager.execute_query(query, fetch=fetch)
        
        # Print the results for SELECT queries
        if fetch:
            for row in result:
                print(row)
        else:
            print(result)

# To run the function and accept user input
if __name__ == "__main__":
    query_input_function()
    
