from game2dboard import Board
from tkinter import messagebox


class TicTacTorus(Board):

    def __init__(self, topology="euclidean"):
        """Initializes a Tic Tac Torus game board."""
        super().__init__(3, 3)
        self.title = "Tic Tac Torus"
        self.cell_size = 120
        self.topology = topology
        self.cell_color = "white"
        self.turn = 1
        self.on_mouse_click = self.mouse_fn
        self.set_neighbors(topology)
        self.show()

    def set_neighbors(self, topology):
        """Sets the neighbor mappings based on the specified topology."""
        # set standard rules which apply to all topologies
        self.right = [1, 2, None, 4, 5, None, 7, 8, None] # right neighbor of each cell
        self.up = [None, None, None, 0, 1, 2, 3, 4, 5] # up neighbor of each cell

        # use the following to verify the diagonals are set properly for the euclidean topology
        # self.diagonal = [None, None, None, 1, 2, None, 4, 5, None] # up-right diagonal neighbor of each cell
        # self.diagonal2 = [None, None, None, None, 0, 1, None, 3, 4] # up-left diagonal neighbor of each cell

        def set_diagonal_neighbors():
            """Sets the diagonal neighbor mappings for the topology given the up/right neighbor mappings."""
            self.diagonal = [None] * 9
            self.diagonal2 = [None] * 9
            left_neighbors = [None] * 9
            for cell in range(9):
                for cell2 in range(9):
                    if self.right[cell2] == cell:
                        left_neighbors[cell] = cell2
                        break
                    
            for cell in range(9):
                u1 = self.up[cell]
                if u1 is not None:
                    self.diagonal[cell] = self.right[u1]  # up-right diagonal neighbor
                    self.diagonal2[cell] = left_neighbors[u1]  # up-left diagonal neighbor


        if topology == "cylinder":
            self.right = [1, 2, 0, 4, 5, 3, 7, 8, 6] # right neighbor of each cell
            set_diagonal_neighbors()

        elif topology == "mobius strip":
            self.right = [1, 2, 6, 4, 5, 3, 7, 8, 0]
            set_diagonal_neighbors()

        elif topology == "torus":
            self.right = [1, 2, 0, 4, 5, 3, 7, 8, 6]
            self.up = [6, 7, 8, 0, 1, 2, 3, 4, 5]
            set_diagonal_neighbors()

        elif topology == "klein bottle":
            self.right = [1, 2, 6, 4, 5, 3, 7, 8, 0]
            self.up = [6, 7, 8, 0, 1, 2, 3, 4, 5]
            set_diagonal_neighbors()

        elif topology == "projective plane":
            self.right = [1, 2, 0, 4, 5, 3, 7, 8, 6]
            self.up = [6, 7, 8, 0, 1, 2, 3, 4, 5]
            set_diagonal_neighbors()

        else:
            raise ValueError("Invalid topology. Choose 'euclidean','cylinder','mobius strip','torus','klein bottle', or 'projective plane'.")


    def idx(self, idx):
        """Returns the value of the cell at the given index."""
        row = idx // 3
        col = idx % 3
        return self[row][col]


    def mouse_fn(self, btn, row, col):    # mouse callback function    
        """Handles mouse click events on the game board. Updates the board state based on the current player's 
        turn and checks for a winner."""
        if self.turn %2:
            self[row][col] = 1
        else:
            self[row][col] = 0

        winning_line = self._get_winning_line()
        if winning_line is not None:
            self._highlight_line(winning_line)
            if self.turn %2:
                self.winner = 'X'
            else:
                self.winner = 'O'
            if messagebox.askyesno("Tic Tac Torus", f"Game over! {self.winner} is the winner!\nRestart?"):
                self.setup_game()
                return
            else:
                self.close()
            return

        self.turn += 1

    def setup_game(self):
        """Sets up the game board for a new game."""
        for row in range(3):
            for col in range(3):
                self[row][col] = None
        self._reset_cell_backgrounds()
        self.turn = 1
        self.winner = None

    def _reset_cell_backgrounds(self):
        """Restore the default background color on all cells."""
        for row in range(3):
            for col in range(3):
                self._cells[row][col].bgcolor = self.cell_color

    def _highlight_line(self, line, color='gold'):
        """Highlight the given winning line of cell indices."""
        for idx in line:
            row = idx // 3
            col = idx % 3
            self._cells[row][col].bgcolor = color

    def _get_winning_line(self):
        """Return the winning line indices if there is a winner, otherwise None."""
        def triple_equal(a, b, c):
            if a is None or b is None or c is None:
                return False
            va = self.idx(a)
            vb = self.idx(b)
            vc = self.idx(c)
            return va is not None and va == vb == vc

        for cell in range(9):
            v = self.idx(cell)
            if v is None:
                continue

            r1 = self.right[cell]
            r2 = None
            if r1 is not None:
                r2 = self.right[r1]
            if triple_equal(cell, r1, r2):
                return [cell, r1, r2]

            u1 = self.up[cell]
            u2 = None
            if u1 is not None:
                u2 = self.up[u1]
            if triple_equal(cell, u1, u2):
                return [cell, u1, u2]

            d1 = self.diagonal[cell]
            d2 = None
            if d1 is not None:
                d2 = self.diagonal[d1]
            if triple_equal(cell, d1, d2):
                return [cell, d1, d2]

            od1 = self.diagonal2[cell]
            od2 = None
            if od1 is not None:
                od2 = self.diagonal2[od1]
            if triple_equal(cell, od1, od2):
                return [cell, od1, od2]

        return None

    def game_over(self):
        """Checks if the game is over and returns the winner (1 or 0) or None if the game is not over."""
        winning_line = self._get_winning_line()
        if winning_line is not None:
            return self.idx(winning_line[0])
        return None

ng = TicTacTorus(topology="klein bottle")  
