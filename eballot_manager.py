import sqlite3
import csv
import glob

def csv_to_db():
    """
    Finds csv file in folder and outputs .db file with same data
    """
    # Create database for data manipulation
    connection = sqlite3.connect("eballot-data.db")
    cur = connection.cursor()

    csv_targets = glob.glob("*.csv")
    if len(csv_targets) == 1:
        # Assign the name of the CSV file to a variable
        csv_filename = csv_targets[0]

    with open(csv_filename) as csv_file:
        read_csv = csv.reader(csv_file, delimiter=",") # comma is default delimiter
        header = next(read_csv)
        global to_db
        to_db = []
        request = f"""
            CREATE TABLE IF NOT EXISTS eballot (
                {
                    ', '.join(['"'+col+'" TEXT' for col in header])
                }
            )
            """
        cur.execute(request)

        # Insert table data into .db
        for row in read_csv:
            placeholders = ', '.join(['?' for _ in row])
            insert_query = f"INSERT INTO eballot VALUES ({placeholders})"
            cur.execute(insert_query, row)
    
    # Commit changes and close the database connection
    connection.commit()
    connection.close()


if __name__ == "__main__":
    csv_to_db()