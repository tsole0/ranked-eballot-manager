import sqlite3
import csv
import glob
from math import ceil

# Create database for data manipulation
connection = sqlite3.connect("eballot-data.db")
cur = connection.cursor()

DEBUG = True #Toggle DEBUG mode

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
    return eval(tally_result, round_number) # Start the election adjudication loop

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
    Determine if exists winner, and who. Prints process for easy auditing.
    :param results: The list containing amount of votes to evaluate. Must only include lists of form [candidate name, number of votes]
    :param round_number: The number of the current round of voting.
    """
    total_votes = sum(result[1] for result in results)
    num_to_win = ceil(total_votes / 2) # The number of votes needed to win in this round of voting (simple majority)
    print(f"Begin round {round_number}.")

    outcome_percentages = [] # Initialize list of candidates and their percentages of first choice votes
    exists_winner = False # Nobody has yet won the election

    # Determine if there is a winner

    for result in results:
        candidate_percentage = round(result[1] / total_votes, 4) * 100 # Returns candidates percentage to two decimal places
        outcome_percentages.append((result[0], candidate_percentage)) # Stores result in outcome_percentages
        if result[1] >= num_to_win:
            exists_winner = True
        else:
            pass
    
    print(outcome_percentages)
    
    if exists_winner is True:
        return winner()
    else:
        print(f"No person has majority.")
        return new_round(round_number)

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
    
    print(f"{lowest[0]} has the least amount of votes and is eliminated.\n")

    query = f"""
    SELECT ROWID
    FROM eballot
    WHERE "{lowest[0]}" = 1;
    """
    cur.execute(query)
    rowids = [rowid[0] for rowid in cur.fetchall()] # Gets the row IDs of all 1's in the lowest-scoring candidate's column

    for rowid in rowids:
        lowest_nonprimary_vote = 99999 # Initialize as an arbitrarily high number that ensures any (resonable) # of candidates can be considered
        row = extract_row(rowid)
        for vote in row:
            if vote > 1 and vote < lowest_nonprimary_vote:
                lowest_nonprimary_vote = vote
        row = list(map(lambda cell : cell if cell!=1 else 0, row)) # Replaces 1 with 0 in row
        row = list(map(lambda cell : cell if cell!=lowest_nonprimary_vote else 1, row)) # Replaces next lowest value with 1
        if DEBUG is True:
            print("DEBUG: ", row)
        
        # Update SQL table
        update_sql(rowid, row)

    round_number += 1

    return eval(tally(1), round_number)

def extract_row(rowid: int):
    """
    Extract a row from the SQL database.
    :param rowid: The ROWID (row ID) of the column you wish to extract
    """
    row = [] # Initialize row to be returned later
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
        single_vote = int(cur.fetchone()[0])
        row.append(single_vote)
        row = [int(vote) for vote in row] # Ensure all values are Python ints
    return row

def update_sql(rowid: int, values: list):
    """
    Update a row in the SQL database.
    :param rowid: The ROWID (row ID) of the column you wish to update
    :param values: The values of the data with which you wish to update this row
    """
    cur.execute(f"PRAGMA table_info(eballot)")
    index = 0 # Index of the list that we will indicate which item from the list will be used to update data
    columns = cur.fetchall()
    for column in columns:
        column_name = column[1]
        query = f"""
            UPDATE eballot
            SET "{column_name}" = '{values[index]}'
            WHERE ROWID = {rowid};
        """
        cur.execute(query)
        index += 1

def winner():
    return None

if __name__ == "__main__":
    csv_to_db()
    ranked_choice()
    # Commit changes and close the database connection
    connection.commit()
    connection.close()
    