"""
A multiplication exam for Jason to pass and earn a trip to Monkey town.

    Output: output
    Other files required: none

    Author: Shane Kepley
    Email: shnkeply@gmail.com
    Date: 12/30/2024
"""

import argparse
from datetime import date
from rich.console import Console
from random import shuffle, sample
import timeit
import dill
from functools import reduce
import readchar

# parse inputs and set up user and challenge
parser = argparse.ArgumentParser()
parser.add_argument("user", type=str,
                    help="identify a username for saving and resuming challenges")
parser.add_argument("level", type=int,
                    help="set the maximum term to appear in sum/product for the challenge")
args = parser.parse_args()
username = args.user
challenge_level = args.level


def load_player(playername: str):
    """Load a players saved data or create a new player"""

    # load score array or set a new one for new users
    try:
        with open(playername + '.dat', 'rb') as file:
            player = dill.load(file)
    except FileNotFoundError:
        player = Player(playername)

    return player


class Player:
    """A class for storing player information and scores"""

    def __init__(self, playername: str):
        """Build a new player"""

        self.playername = playername
        self.max_level = 4


class Game:
    """A class for holding the state of a game and methods required for playing it"""

    def __init__(self, operation: str, level: int):
        self.gameover = False
        self.num_error = 0
        self.problem_set = self.generate_problem_set(operation, level)
        self.nRemaining = len(self.problem_set)

    def generate_problem_set(self, operation: str, level: int):
        """Generate the problem set for this game instance"""

        if operation == 'sum':
            self.symbol = '+'
            operation_function = lambda summands: sum(summands)
            term_list = [sample((i, j), 2) for i in range(challenge_level) for j in range(i, challenge_level)]

        elif operation == 'product':
            self.symbol = 'x'
            operation_function = lambda factors: reduce(lambda x, y: x * y, factors)
            term_list = [sample((i, j), 2) for i in range(1, challenge_level + 1) for j in
                         range(i, challenge_level + 1)]

        for term in term_list:
            term.append(operation_function(term))
        shuffle(term_list)
        return term_list

    def play(self):
        """main loop for the game"""

        while not self.gameover:
            try:
                terms = self.problem_set.pop()
                self.num_error += self.pose_problem(terms)

            except IndexError:  # we have finished all problems
                self.gameover = True

    def pose_problem(self, problem_tuple):
        """Ask a single problem and parse the answer"""

        terms = problem_tuple[:-1]
        solution = problem_tuple[-1]  # true solution
        nErrors = 0
        solved = False
        while not solved:
            console.clear()
            console.print(f"Remaining problems: {self.nRemaining}")
            console.print('\n' * 2)
            console.print(f"{terms[0]} {self.symbol} {terms[1]} = ", end="")
            answer = input()

            if answer == 'q':  # user wants to stop the session
                self.problem_set.append(terms)  # put this problem back onto the stack
                return 'q'

            else:
                try:
                    answer = int(answer)  # convert answer to integer
                    if solution != answer:
                        nErrors += 1
                    else:
                        solved = True
                except ValueError:  # answer was not an integer or the letter q
                    pass
        self.nRemaining -= 1
        return nErrors


class Record:
    """Record stats for a single multiplication challenge"""

    def __init__(self, playername, operation, level):
        """instantiate a new record"""

        self.playername = playername
        self.operation = operation
        self.level = level
        self.problem_set = operation.problem_set
        self.nRemaining = len(self.problem_set)
        self.date = date.today().strftime("%d%m%y")  # current date in ddmmyy format
        self.num_errors = 0
        self.elapsed_time = 0
        self.completed = False

    def __repr__(self):
        """How to print records"""

        # minutes = self.elapsed_time // 60
        # seconds = self.elapsed_time - 60 * minutes
        # return f"Elapsed time: {minutes} minutes and {seconds} seconds\n" \
        #        f"Errors: {self.errors}"

        return f"{self.elapsed_time} seconds with {self.num_errors} mistakes"


def set_mode():
    """Set challenge mode"""

    modes = {'P': 'practice', 'C': 'challenge', 'R': 'resume'}
    modeKey = ''
    while modeKey not in modes.keys():  # mode is either practice, challenge, or resume
        console.clear()
        console.print('Choose a challenge mode')
        console.print("(P)ractice\n(C)hallenge\n(R)esume")
        modeKey = input().upper()
    return modes[modeKey]


def set_operation():
    """Set math operation (challenge mode)"""

    operations = {'M': 'product', 'S': 'sum'}
    operationKey = ''
    while operationKey not in operations.keys():
        console.clear()
        console.print('Choose a challenge type:')
        console.print(f"(M)ultiplications\n(S)ums")
        operationKey = input().upper()
    return operations[operationKey]


console = Console(width=80)
# challenge_mode = set_mode()
# operation = set_operation()
operation = 'product'
game = Game(operation, challenge_level)
game.play()

# # load score array or set a new one for new users
# try:
#     with open(username + '_score.dat', 'rb') as file:
#         scoreData = dill.load(file)
# except FileNotFoundError:
#     scoreData = []

# start the challenge
# if challenge_mode == 'resume':
#     record = scoreData.pop()
# else:
#     record = Record(username, operation, challenge_level)
# in_session = True
# start_time = timeit.default_timer()
# while in_session:
#     p_result = record.pose_problem()
#     if p_result == 'q':  # user quit/paused their challenge
#         in_session = False
#     else:
#         record.num_errors += p_result

# # add timing and completion information to the record
# record.elapsed_time += round(timeit.default_timer() - start_time, 2)
# if record.nRemaining == 0:
#     record.completed = True
# console.print(f"Challenge complete in {record}")
# console.print(f"Target is {5 * challenge_level * (challenge_level + 1) // 2} seconds with 0 mistakes")
#
# # save challenge record
# if challenge_mode in ['challenge', 'resume']:
#     scoreData.append(record)
#     with open(username + '_score.dat', 'wb') as file:
#         dill.dump(scoreData, file)
