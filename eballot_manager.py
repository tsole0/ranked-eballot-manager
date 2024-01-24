import sqlite3
import csv
import glob
from math import ceil

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
    
    round_number = 1 # Starts as round 1 of elections
    tally_result = tally(1) # Count first choices
    eval(tally_result, round_number) # Start the election adjudication loop

def tally(place: int):
    """
    Count nth place votes for each candidate (column)
    :param place: The place that will be counted for each candidate.
    """
    cur.execute(f"PRAGMA table_info(eballot)")
    tally_result = []
    columns = cur.fetchall()
    for column in columns:
        column_name = column[1]
        query = f"""
        SELECT COUNT(*) FROM eballot WHERE \"{column_name}\" = '{place}';
        """
        cur.execute(query)
        result = cur.fetchone() # Fetch the result
        tally_result.append([column_name, result[0]]) # Store result as a list in a list
    
    return tally_result

def eval(results: list, round_number: int):
    """
    Determine if winner, and who.
    :param results: The list containing amount of votes to evaluate. Must only include lists of form [candidate name, number of votes]
    :param round_number: The number of the current round of voting.
    """
    num_to_win = ceil(sum((result[1] for result in results)) / 2) # The number of votes needed to win in this round of voting (simple majority)
    
    # Determine if there is a winner
    for result in results:
        if result[1] >= num_to_win:
            winner()
            break
        else:
            new_round(round_number)
            break
        
def new_round(round_number: int):
    """
    'Eliminate' lowest-scoring candidate, then kick back to new evaluation round--
    :param round_number: The number of the current round of voting.
    """
    tally_results = tally(1)
    initial_value = -1
    lowest = [str, initial_value]
    for result in tally_results:
        if result[1] < lowest[1] or lowest[1] == -1:
            lowest = result

    query = f"""
    SELECT ROWID
    FROM eballot
    WHERE "{lowest[0]}" = 1;
    """
    cur.execute(query)
    rowids = [rowid[0] for rowid in cur.fetchall()] # Gets the row IDs of all 1's in the lowest-scoring candidate's column

    for rowid in rowids:
        row = extract_row(rowid)


    round_number += 1

def extract_row(rowid: int):
    """
    Extract a row from the SQL database.
    :param rowid: The ROWID (row ID) of the column you wish to extract
    """
    row = []
    cur.execute(f"PRAGMA table_info(eballot)")
    columns = cur.fetchall()
    for column in columns:
        column_name = column[1]
        query = f"""
            SELECT "{column_name}"
            FROM eballot
            WHERE ROWID = {rowid};
        """
        cur.execute(query)
        row.append(cur.fetchone()[0])
    print(row)







def winner():
    pass




if __name__ == "__main__":
    csv_to_db()
    ranked_choice()
    # Commit changes and close the database connection
    connection.commit()
    connection.close()
    