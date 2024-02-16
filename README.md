# ranked-eballot-manager

## Functionality

Takes a `.csv` file and runs a ranked choice election on it.

## Election Technical Specifications

The program will run a series of adjudication rounds, during which it will attempt to determine a winner by majority (>50% of the vote). If one does not exist, it will remove the candidate with the least number of first-choice votes. If there is a tie for least number of first-choice votes, a tiebreaking round takes place.

In this tiebreaking round, the Borda method is used. This method is useful for determining which candidates have the most and least *overall* support, instead of just 1st place support.

For each place (1st, 2nd, ect.), numbers are swapped for points, which are summed up. For example, if there are three places, 1st, 2nd, and 3rd, by which candidates can be ranked, then each 1st choice vote will count for 3 points, each 2nd for 2 points, and each 3rd for 1 point. These points are summed up for each candidate in the tiebreaking round, and the person with the least overall score will be eliminated.

This order in which the Borda count takes place is determined before any of the other election processes begin, and thus is not impacted by subsequent rounds of voting.

## Limits of system design

At a (very large) number of rounds, Python will return a stack size error and no more results will be tabulated. However, due to limitations in the implementation of the program, it is likely (although untested) that using a large amount of candidates >450 could lead to stack overflows, causing fatal errors. With this said, it is suggested that this framework be used only for running candidates in real ranked choice elections and not for other uses (i.e. using the program as a sorting algorithm or inputting values other than ranked votes) to avoid edge cases that will return errors.
