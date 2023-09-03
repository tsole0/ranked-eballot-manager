import sqlite3
import csv
import glob

# Create database for data manipulation
connection = sqlite3.connect("eballot-data.db")
cur = connection.cursor()

def csv_to_db():
    """
    Finds csv file in folder and outputs .db file with same data
    """

    csv_targets = glob.glob("*.csv")
    if len(csv_targets) == 1:
        # Assign the name of the CSV file to a variable
        csv_filename = csv_targets[0]

    with open(csv_filename) as csv_file:
        read_csv = csv.reader(csv_file, delimiter=",") # comma is default delimiter
        header = next(read_csv)
        cur.execute(f"DROP TABLE IF EXISTS eballot") # clear any existing data
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

def ranked_choice():
    find_replace_dict = {
        "First": "1",
        "Second": "2",
        "Third": "3"
    }
    # Iterate through each table and column, and perform the find-and-replace
    cur.execute(f"PRAGMA table_info(eballot)")
    columns = cur.fetchall()
    for column in columns:
        column_name = column[1]

        for find, replace in find_replace_dict.items():
            update_query = f"UPDATE eballot SET \"{column_name}\" = REPLACE(\"{column_name}\", '{find}', '{replace}');"
            cur.execute(update_query)

    # Remove all but the first character, which should just be a numeral at this point
    for column in columns:
        column_name = column[1]
        update_query = f"""
                UPDATE eballot
                SET \"{column_name}\" = SUBSTR(\"{column_name}\", 1, 1);
                """
        cur.execute(update_query)



if __name__ == "__main__":
    csv_to_db()
    ranked_choice()
    # Commit changes and close the database connection
    connection.commit()
    connection.close()
    