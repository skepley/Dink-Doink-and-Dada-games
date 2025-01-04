"""
Implementation of the classic game mastermind
   
    Author: Shane Kepley
    email: shnkepley@gmail.com
    Date: 12/18/2024; Last revision: 12/18/2024
"""
from rich.console import Console
import readchar

CONSOLE_WIDTH = 40
GAME_SIZE = 6
CENTER_OFFSET = (CONSOLE_WIDTH - GAME_SIZE) // 2
console = Console(width=CONSOLE_WIDTH)

PEG = "●"  # Unicode filled dot
PEG_KEYS = ['1', '2', '3', '4', '5', '6']
PEG_COLORS = dict(zip(PEG_KEYS, ['red', 'blue', 'cyan', 'orange1', 'white', 'purple']))
PEGS = dict(zip(PEG_KEYS, [PEG for key in PEG_KEYS]))


def set_board(size):
    """Set up a game by choosing a pin configuration"""

    solution_as_list = []
    styled_solution = [' ' * CENTER_OFFSET]
    refresh_screen([], ())
    console.print(f"Choose a secret sequence of {GAME_SIZE} dots")
    while len(solution_as_list) < size:
        char = readchar.readkey()
        if char == 'x1b':  # ESC key
            print("\nExiting...")
            break1
        elif char == '\x08':  # backspace key
            refresh_screen([], ())
            console.print(f"Choose a secret sequence of {GAME_SIZE} dots")

            try:
                solution_as_list.pop()
                styled_solution.pop()
            except IndexError:
                pass
            console.print("".join(styled_solution))
        elif char in PEG_KEYS:
            refresh_screen([], ())
            console.print(f"Choose a secret sequence of {GAME_SIZE} dots")
            solution_as_list.append(char)
            style = f"{PEG_COLORS[char]} on black"
            styled_solution.append(f"[{style}]{PEGS[char]}[/]")
            console.print("".join(styled_solution))
    return tuple(solution_as_list)


def input_guess(guessList, solution):
    """Allow the player to make their next guess at the solution"""

    input_size = len(solution)
    new_guess = []
    styled_guess = [' ' * CENTER_OFFSET]
    refresh_screen(guessList, solution)

    while len(new_guess) < input_size:
        char = readchar.readkey()
        if char == 'x1b':  # ESC key
            print("\nExiting...")
            break
        elif char == '\x08':  # backspace key
            refresh_screen(guessList, solution)
            try:
                new_guess.pop()
                styled_guess.pop()
            except IndexError:
                pass
            console.print("".join(styled_guess))
        elif char in PEG_KEYS:
            refresh_screen(guessList, solution)
            new_guess.append(char)
            style = f"{PEG_COLORS[char]} on black"
            styled_guess.append(f"[{style}]{PEGS[char]}[/]")
            console.print("".join(styled_guess))
    return tuple(new_guess)


def parse_guess(guess, solution):
    """Execute a single guess of the solution"""
    guess_as_list = list(guess)  # mutable copy
    solutionList = list(solution)
    highlights = ['black' for j in range(len(guess_as_list))]  # initialize output
    # first pass to highlight greens
    for (idx, pin) in enumerate(guess_as_list):
        if solutionList[idx] == pin:
            solutionList[idx] = -2  # remove pin from the solution but insert a placeholder
            guess_as_list[idx] = -1  # leave a placeholder in the guess
            highlights[idx] = 'green'

    # next pass to highlight yellows
    for (idx, pin) in enumerate(guess_as_list):
        if pin in solutionList:
            solutionList.pop(solutionList.index(pin))
            highlights[idx] = 'yellow'

    return highlights


def refresh_screen(guessList, solution):
    """Update the screen based on the most recent guess"""

    console.clear()
    console.rule(":leafy_green: MASTERMIND :leafy_green:")
    print_key()
    for guess in guessList:
        print_guess(guess, solution)
    return


def print_guess(guess, solution):
    """Print a guess to the screen"""

    highlights = parse_guess(guess, solution)
    styled_guess = [' ' * CENTER_OFFSET]
    for idx, key in enumerate(guess):
        style = f"{PEG_COLORS[key]} on {highlights[idx]}"
        styled_guess.append(f"[{style}]{PEG}[/]")
    console.print("".join(styled_guess))
    return styled_guess


def print_key():
    """Print a table with the key-peg pairs used for playing the game"""

    for key in PEG_KEYS:
        console.print(f"{key} = {PEGS[key]}", style=PEG_COLORS[key])


def print_peg(key, highlight):
    """Print a single peg to the screen"""
    console.print(PEG, style=(PEG_COLORS[key] + ' on ' + highlight), end="")
    return


def main():
    """The main scope and loop for running a single instance of mastermind"""

    set_board()
    # main loop
    solved = True
    nGuess = 0

    while not solved:
        parse_guess()
        refresh_screen()


if __name__ == "__main__":
    guess = ()
    guessList = []
    solution = set_board(GAME_SIZE)
    while guess != solution:
        guess = input_guess(guessList, solution)
        guessList.append(guess)
