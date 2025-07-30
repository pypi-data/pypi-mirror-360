import psycopg2
import json

def setup_database(conn):
    """ Create tables based on the provided table creation scripts """
    cur = conn.cursor()
    tables = get_insert_list()
    try:
        for table in tables:
            cur.execute(table['table'])
        conn.commit()
    except psycopg2.Error as e:
        print("An error occurred while setting up the database tables:", e)
        conn.rollback()
    finally:
        cur.close()

def get_insert_list():
    """ Return a list of dictionaries defining SQL table creation and insertion commands """
    return [{'tableName': 'dnc_db',
             'columnSearch': 'uid',
             'insertName': 'user_info',
             'type': 'dnc_opt_out',
             'searchQuery': 'SELECT user_info FROM dnc_db WHERE uid = %s;',
             'insertQuery': 'INSERT INTO dnc_db (uid, user_info) VALUES (%s, %s)',
             'table': 'CREATE TABLE IF NOT EXISTS dnc_db (id SERIAL PRIMARY KEY,uid TEXT UNIQUE NOT NULL,user_info JSONB NOT NULL);'},
            {'tableName': 'live_transfers_db',
             'columnSearch': 'uid',
             'insertName': 'lt_lead',
             'type': 'live_transfer_data',
             'searchQuery': 'SELECT lt_lead FROM live_transfers_db WHERE uid = %s;',
             'insertQuery': 'INSERT INTO live_transfers_db (uid, lt_lead) VALUES (%s, %s)',
             'table': 'CREATE TABLE IF NOT EXISTS live_transfers_db (id SERIAL PRIMARY KEY,uid TEXT UNIQUE NOT NULL,lt_lead JSONB NOT NULL);'},
            {'tableName': 'leads_db',
             'columnSearch': 'uid',
             'insertName': 'lead_info',
             'type': 'leads_info_db',
             'searchQuery': 'SELECT lead_info FROM leads_db WHERE uid = %s;',
             'insertQuery': 'INSERT INTO leads_db (uid, lead_info) VALUES (%s, %s)',
             'table': 'CREATE TABLE IF NOT EXISTS leads_db (id SERIAL PRIMARY KEY,uid TEXT UNIQUE NOT NULL,lead_info JSONB NOT NULL);'}]

def main():
    """ Main function to manage the database setup and operations """
    conn = connect_db()
    if conn:
        setup_database(conn)
        # Example to insert data into 'gettxlog'
        cur = conn.cursor()
        try:
            insert_data = ('signature_value', json.dumps({'some': 'data'}))
            cur.execute("INSERT INTO gettxlog (signature, log_data) VALUES (%s, %s)", insert_data)
            conn.commit()
        except psycopg2.Error as e:
            print("Failed to insert data:", e)
            conn.rollback()
        finally:
            cur.close()
        conn.close()

if __name__ == "__main__":
    main()
