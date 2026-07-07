from game2dboard import Board
from tkinter import messagebox


class TicTacTorus(Board):

    def __init__(self, topology="standard"):
        """Initializes a Tic Tac Torus game board."""
        super().__init__(3, 3)
        self.title = "Tic Tac Torus"
        self.cell_size = 200
        self.topology = topology
        self.cell_color = "white"
        self.turn = 1
        self.on_mouse_click = self.mouse_fn
        self._canvas.bind("<Button-3>", self._on_right_click)
        self.set_neighbors(topology)
        self._margin = 10
        self.draw_boundary_arrows()
        self.show()


    def set_neighbors(self, topology):
        """Sets the neighbor mappings based on the specified topology."""
        # set standard rules which apply to all topologies
        self.right = [1, 2, None, 4, 5, None, 7, 8, None] # right neighbor of each cell
        self.up = [None, None, None, 0, 1, 2, 3, 4, 5] # up neighbor of each cell

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
            raise ValueError("Invalid topology. Choose 'standard','cylinder','mobius strip','torus','klein bottle', or 'projective plane'.")


    def draw_boundary_arrow(self, side, color, orientation = "+"):
        """Draw a single colored arrow on the board boundary."""
        # set some parameters to control the arrow's position and appearance
        start_ratio=0.33
        end_ratio=0.67
        width=4

        # find the coordinates of the arrow's start and end points based on the side of the board
        left = self.margin/2
        top = self.margin/2
        right = self._canvas_width - self.margin/2
        bottom = self._canvas_height - self.margin/2

        if side == "top":
            x1 = left + int((right - left) * start_ratio)
            y1 = top
            x2 = left + int((right - left) * end_ratio)
            y2 = top
            if orientation == "-":
                x1, x2 = x2, x1
        elif side == "bottom":
            x1 = left + int((right - left) * start_ratio)
            y1 = bottom
            x2 = left + int((right - left) * end_ratio)
            y2 = bottom
            if orientation == "-":
                x1, x2 = x2, x1
        elif side == "left":
            x1 = left
            y1 = top + int((bottom - top) * end_ratio)
            x2 = left
            y2 = top + int((bottom - top) * start_ratio)
            if orientation == "-":
                y1, y2 = y2, y1
        elif side == "right":
            x1 = right
            y1 = top + int((bottom - top) * end_ratio)
            x2 = right
            y2 = top + int((bottom - top) * start_ratio)
            if orientation == "-":
                y1, y2 = y2, y1
        else:
            raise ValueError("side must be 'top', 'bottom', 'left', or 'right'.")

        arrow_id = self._canvas.create_line(
            x1, y1, x2, y2,
            fill=color,
            width=width,
            arrow="last",
            arrowshape=(6, 12, 4),
            capstyle="round",
            smooth=False,
        )
        self._canvas.tag_raise(arrow_id)

    def draw_boundary_arrows(self, arrows=None):
        """Draw a set of example arrows around the board boundary."""
        if self.topology == "cylinder":
            arrows = [
                ("left", "blue", "+"),
                ("right", "blue", "+"),
            ]
        elif self.topology == "mobius strip":
            arrows = [
                ("left", "blue", "-"),
                ("right", "blue", "+"),
            ]
        elif self.topology == "torus":
            arrows = [
                ("left", "blue", "+"),
                ("right", "blue", "+"),
                ("top", "red", "+"),
                ("bottom", "red", "+"),
            ]
        elif self.topology == "klein bottle":
            arrows = [
                ("left", "blue", "-"),
                ("right", "blue", "+"),
                ("top", "red", "+"),
                ("bottom", "red", "+"),
            ]
        elif self.topology == "projective plane":
            arrows = [
                ("left", "blue", "-"),
                ("right", "blue", "+"),
                ("top", "red", "+"),
                ("bottom", "red", "-"),
            ]
        

        for side, color, orientation in arrows:
            self.draw_boundary_arrow(side, color, orientation)

    def idx(self, idx):
        """Returns the value of the cell at the given index."""
        row = idx // 3
        col = idx % 3
        return self[row][col]


    def _on_right_click(self, event):
        """Handle right-click events by reporting the clicked board cell."""
        rc = self._xy2rc(event.x, event.y)
        if rc is not None:
            row, col = rc
            self[row][col] = None  # Reset the cell to None on right-click

    def mouse_fn(self, btn, row, col):    # mouse callback function    
        """Handles mouse click events on the game board. Updates the board state based on the current player's 
        turn and checks for a winner."""
        if self[row][col] is not None:
            return
        
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

ng = TicTacTorus(topology="projective plane")  


