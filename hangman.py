from rich.console import Console

# console.print("Hello, [bold red]Rich[/] :snake:")
console = Console(width=40)


def get_word():
    console.clear()
    console.rule(":leafy_green: Hangman :leafy_green:")
    word = input('Choose the secret word: ')
    return word.upper()


def play(word):
    word_completion = "_" * len(word)
    # remove spaces
    word_as_list = list(word_completion)
    indices = [i for i, letter in enumerate(word) if letter == ' ']
    for idx in indices:
        word_as_list[idx] = ' '
    word_completion = "".join(word_as_list)
    guessed = False
    quit = False
    guessed_letter = []
    tries = 7
    console.clear()
    console.print('Guess the word to stop the hangman!')
    console.print(display_hangman(tries))
    console.print('Secret word: ' + word_completion)
    print('\n')
    while not guessed and tries > 0:
        console.print("Previous guesses: " + ', '.join(sorted(guessed_letter)))
        guess = input("Please guess a single letter or a {0} letter word: ".format(len(word))).upper()
        console.clear()
        console.rule(":leafy_green: Hangman :leafy_green:")

        if guess in guessed_letter:
            console.print("You already guessed the letter", guess)

        elif len(guess) == 1 and guess.isalpha():
            guessed_letter.append(guess)
            if guess in word:
                console.print("Good guess, {0} is in the secret word!".format(guess))
                word_as_list = list(word_completion)
                indices = [i for i, letter in enumerate(word) if letter == guess]
                for idx in indices:
                    word_as_list[idx] = guess
                word_completion = "".join(word_as_list)
                if '_' not in word_completion:
                    guessed = True
            else:
                console.print("Tough luck, {0} is not in the secret word.".format(guess))
                tries -= 1

        elif guess == "QUIT":
            tries = 0
            quit = True

        elif len(guess) == len(word):
            if guess == word:
                word_completion = word
                guessed = True
            else:
                tries -= 1
                console.print("Sorry {0} is not the secret word".format(guess))

        else:
            console.print("Not a valid letter or word")

        console.print(display_hangman(tries))
        console.print('Secret word: ' + word_completion)
        console.print('\n')

    if quit:
        console.clear()
        console.print('Game aborted')
    elif guessed:
        console.clear()
        console.print('Congratulations, the word was ' + word + '. You win the game!')
    else:
        console.clear()
        console.print("Sorry you ran out of tries. The correct word was: " + word)


def display_hangman(tries):
    stages = [  # final state: head, torso, both arms, and both legs
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     / \\
           -
        """,
        # head, torso, both arms, and one leg
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |     / 
           -
        """,
        # head, torso, and both arms
        """
           --------
           |      |
           |      O
           |     \\|/
           |      |
           |      
           -
        """,
        # head, torso, and one arm
        """
           --------
           |      |
           |      O
           |     \\|
           |      |
           |     
           -
        """,
        # head and upper and lower torso
        """
           --------
           |      |
           |      O
           |      |
           |      |
           |     
           -
        """,
        # head and upper torso
        """
           --------
           |      |
           |      O
           |      |
           |      
           |     
           -
        """,
        # head
        """
           --------
           |      |
           |      O
           |    
           |      
           |     
           -
        """,
        # initial empty state
        """
           --------
           |      |
           |      
           |    
           |      
           |     
           -
        """
    ]
    return stages[tries]


def main():
    word = get_word()
    play(word)
    while input("Play again? (Y/N) ").upper() == 'Y':
        word = get_word()
        play(word)


if __name__ == "__main__":
    main()
