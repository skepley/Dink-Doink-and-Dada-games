# TicTacTorus

TicTacTorus is a twist on the classic Tic-Tac-Toe game based on the article found here: 
https://chalkdustmagazine.com/features/topological-tic-tac-toe/

In short, the board is allowed to have different mathematical topologies such as a cylinder or torus. This means some edges of the board are identified with other edges so moves can wrap around and create new winning possibilities.

## How to Play
1. Download the game and install game2dboard library
2. Run the game using Python:
   - `python tic_tac_torus.py topology` where topology is one of {standard, cylinder, torus, "mobius strip", "projective plane", "klein bottle"}.
2. The game starts with an empty board.
3. Players take turns placing their symbol (`X` or `O`) on the board with left click starting with `X`.
4. The goal is to get three of your symbols in a row, column, or diagonal.
5. Because the board wraps around the edges, some lines can connect across the borders.

## Notes

- The game is meant to be played by two players.
- Try to think strategically, since wraparound moves can make threats which are harder for your opponent to notice or even make double threats which guarantee a win on next move. 
- Some topologies have a guaranteed win for the starting player. Try to figure out which topologies have a win and what the winning strategy is. 
