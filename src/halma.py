# halma part 1
# process: halma is a two-player, turn-based board game played on a square grid

# header files
import tkinter as tk
import tkinter.messagebox as msg

# constants
CELL_SIZE = 60
MARGIN = 40

# ========================================================================== #
#                                GAME LOGIC                                  #
# ========================================================================== #

# class: Logic
# process: logic for the game process
class Logic:

    # method: init
    # process: creates 2D array, places the pieces in the corners
    def __init__(self, size):

        self.size = size

        # create the 2D array, initialize all spaces to zero (empty)
        self.board = [[0 for x in range(size)] for y in range(size)]

        # halves the board size for the pieces initialization
        half = size // 2

        # creates the top triangle, player 1 (GREEN)
        for row in range(half):
            for col in range(half - row):
                self.board[row][col] = 1

        # creates the bottom triangle, player 2 (RED)
        for row in range(half, self.size):
            start_column = self.size - 1 - (row - half)
            for col in range(start_column, self.size):
                self.board[row][col] = 2

    def check_win(self, player):

        half = self.size // 2

        # player one (green) wins
        if player == 1:
            for row in range(half, self.size):
                start_column = self.size - 1 - (row - half)
                for col in range(start_column, self.size):
                    if self.board[row][col] != 1:
                        return False
            return True

        # player two (red) wins
        if player == 2:
            for row in range(half):
                for col in range(half - row):
                    if self.board[row][col] != 2:
                        return False
            return True

    # method: compute_score
    # process: computes the score for each player
    def compute_score(self, player):

        total = 0

        # traverse the board
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player:

                    # check if in enemy camp (full point)
                    if self.in_goal_camp(row, col, player):
                        total += 1

                    # else distance function
                    else:
                        # fractional contribution based on distance
                        dist = self.distance_to_goal(row, col, player)
                        total += 1 / (1 + dist)

        # return the score
        return round(total, 1)

    # method: distance_to_goal
    # process: checks the distance to the goal state
    def distance_to_goal(self, row, col, player):

        half = self.size // 2

        # checks distance for each player
        if player == 1:
            # for the bottom triangle camp
            goal_row, goal_col = self.size - 1, self.size - 1
        else:
            # for the top triangle camp
            goal_row, goal_col = 0, 0

        # returns the absolute distance to the goal
        return abs(goal_row - row) + abs(goal_col - col)

    # method: in_goal_camp
    # process: checks to see if the player is in the goal camp (for scoring)
    def in_goal_camp(self, row, col, player):

        half = self.size // 2

        # player one (green) bottom right triangle
        if player == 1:
            start_col = self.size - 1 - (row - half)
            return row >= half and col >= start_col

        # player two (red) top left triangle
        if player == 2:
            return row < half and col < (half - row)

    # method: in_home_camp
    # process: checks if the position of the piece is in the player's camp (for the blocking rule)
    def in_home_camp(self, row, col, player):

        half = self.size // 2

        # player one (green) top left triangle
        if player == 1:
            return row < half and col < (half - row)

        # player two (red) bottom right triangle
        if player == 2:
            start_column = self.size - 1 - (row - half)
            return row >= half and col >= start_column

    # method: move_piece
    # process: update the board array
    def move_piece(self, from_position, to_position, player):

        # set variables for the coords from and to
        from_row, from_col = from_position
        to_row, to_col = to_position

        # set the old value to zero, new to one
        self.board[from_row][from_col] = 0
        self.board[to_row][to_col] = player

    # method: get_adjacent_moves
    # process: check all 8 directions, return empty places
    def get_adjacent_moves(self, row, col):

        # initialize variables
        moves = []
        directions = [(-1,-1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        # traverse the directions
        for x, y in directions:
            # assign the variables with the next row and col
            next_row, next_col = row + x, col + y

            # append any positions that are empty to list of moves
            if 0 <= next_row < self.size and 0 <= next_col < self.size:
                if self.board[next_row][next_col] == 0:
                    moves.append((next_row, next_col))

        # return list of moves
        return moves

    # method: get_all_jump_moves
    # process: recursive function, made to capture potential chained jumps, and simple jumps
    def get_all_jump_moves(self, row, col, visited=None):

        # base case for the recursion
        if visited is None:
            visited = set()

        # initialize variables
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        moves = set()

        # traverse all the directions
        for x, y in directions:
            # grab the mid positional value
            mid_row, mid_col = row + x, col + y

            # grab the position we would be jumping to
            jump_row, jump_col = row + 2 * x, col + 2 * y

            # check bounds of the board
            if not (0 <= jump_row < self.size and 0 <= jump_col < self.size):
                continue

            # check that it would be a valid jump (mid needs a piece jump needs to be open)
            if self.board[mid_row][mid_col] != 0 and self.board[jump_row][jump_col] == 0:

               # if the jump has not been visited
                if (jump_row, jump_col) not in visited:

                    # add it to the potential moves
                    moves.add((jump_row, jump_col))

                    # mark this visit before recursion
                    new_visited = visited.copy()
                    new_visited.add((jump_row, jump_col))

                    # now call the function to recurse
                    chained = self.get_all_jump_moves(jump_row, jump_col, new_visited)

                    # update moves based on chained
                    moves.update(chained)

        # return the valid chained moves
        return moves

    # method: get_valid_moves
    # process: call functions to get all valid moves
    def get_valid_moves(self, row, col, player):
        # makes the adjacent moves list
        adjacent_moves = self.get_adjacent_moves(row, col)

        # gets all the available jumps in a list (comes in as a set)
        jump_moves = list(self.get_all_jump_moves(row, col))

        # combine both lists
        all_moves = adjacent_moves + jump_moves

        # blocking rule if the player is in home camp
        if self.in_home_camp(row, col, player):
            current_distance = self.distance_to_goal(row, col, player)

            # create new list to hold all valid places (with blocking rule)
            blocking = []

            # traverse the moves we have been provided
            for (x, y) in all_moves:
                new_distance = self.distance_to_goal(x, y, player)

                # only allow forward moves
                if new_distance < current_distance:
                    blocking.append((x, y))

            # return the list
            return blocking

        # else return the other moves
        return all_moves


    # temporary testing for the board logic
    def print_board(self):
        for row in self.board:
            print(row)
        print()

# ========================================================================== #
#                                GUI                                         #
# ========================================================================== #

# class: Halma
# process: class for the gui and tkinter
class Halma:

    # method: init
    # process: initializes tkinter and creates the canvas and board object
    def __init__(self, size=8):
        self.size = size

        # creates the window, adds a title
        self.window = tk.Tk()
        self.window.title("Halma Part One")

        # creating the status bar at the top
        self.status_label = tk.Label(self.window, text="", font=("Arial", 12))
        self.status_label.pack()

        # creates a canvas with a width of board * cell size + margin
        self.canvas = tk.Canvas(
            self.window,
            width = self.size * CELL_SIZE + MARGIN,
            height = self.size * CELL_SIZE + MARGIN)
        self.canvas.pack()

        # attach the board logic
        self.board = Logic(size)

        # add in the turn system
        self.current_player = 1     # player one (green) starts
        self.move_count = 0         # set the move counter

        # add in the timer system
        self.time_limit = 20  # seconds per move (can make this a parameter later)
        self.time_left = self.time_limit
        self.timer_running = False
        self.timer_id = None

        # selection variables
        self.selected_piece = None
        self.valid_moves = []

        # save the last move
        self.last_move_from = None
        self.last_move_to = None

        # score variables
        self.green_score = 0
        self.red_score = 0

        # binds the mouse click
        self.canvas.bind("<Button-1>", self.on_click)

        # initial draw
        self.refresh_window()

        # starts the timer
        self.start_timer()

        # main loop
        self.window.mainloop()

    # method: draw_grid
    # process: draw NxN squares using create_rectangle
    def draw_grid(self):
        # traverse the NxN grid
        for row in range(self.size):
            for col in range(self.size):

                # get the rectangle positions based on position and cell size and margin
                x1 = col * CELL_SIZE + MARGIN
                y1 = row * CELL_SIZE + MARGIN
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                # create the square for the gameboard
                self.canvas.create_rectangle(x1, y1, x2, y2, outline = "black", fill = "beige")

    # method: draw_labels
    # process: draws the labels for row and col in the margins
    def draw_labels(self):

        # alphabetical col labels
        for col in range(self.size):
            x = col * CELL_SIZE + MARGIN + CELL_SIZE // 2
            y = MARGIN // 2

            letter = chr(ord('a') + col)

            self.canvas.create_text(x, y, text=letter, font=("Arial", 12, "bold"))

        # numerical row labels
        for row in range(self.size):
            x = MARGIN // 2
            y = row * CELL_SIZE + MARGIN + CELL_SIZE // 2

            number = str(row + 1)

            self.canvas.create_text(x, y, text=number, font=("Arial", 12, "bold"))

    # method: draw_pieces
    # process: loop through board, if array 1 and a game piece using create_oval
    def draw_pieces(self):

        # traverse the NxN grid
        for row in range(self.size):
            for col in range(self.size):

                # if the board is supposed to have a piece (per the array)
                piece = self.board.board[row][col]

                if piece != 0:
                    # set the values for the oval (add padding to center this)
                    x1 = col * CELL_SIZE + MARGIN + 10
                    y1 = row * CELL_SIZE + MARGIN + 10
                    x2 = x1 + CELL_SIZE - 20
                    y2 = y1 + CELL_SIZE - 20

                    # player one will be green
                    if piece == 1:
                        color = "green"

                    # player two will be red
                    else:
                        color = "red"

                    # if the piece is the selected piece
                    if self.selected_piece == (row, col):
                        # highlight the piece
                        self.canvas.create_oval(x1, y1, x2, y2, outline = "red", fill="orange")

                    # else then make the piece a player piece (depends on 1 or 2)
                    else:
                        self.canvas.create_oval(x1, y1, x2, y2, fill=color)

    # method: draw_highlights
    # process: draws the highlights using create_rectangle
    def draw_highlights(self):

        # for each position in the valid moves
        for (row, col) in self.valid_moves:
            # grab coords for the rectangle creation based on cell size (added margin to this)
            x1 = col * CELL_SIZE + MARGIN
            y1 = row * CELL_SIZE + MARGIN
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            # create a green rectangle using create_rectangle
            self.canvas.create_rectangle(x1, y1, x2, y2, outline = "green", fill = "lightgreen")

    # method: draw_last_move
    # process: function to draw the last move of the player, from where they started to where they ended
    def draw_last_move(self):

        # for the starting pos
        if self.last_move_from:
            self.draw_move_square(self.last_move_from, "grey")

        # for the ending pos
        if self.last_move_to:
            self.draw_move_square(self.last_move_to, "LightYellow3")

    # method: draw_move_square
    # process: function that draws the last move squares, called by draw_last_move
    def draw_move_square(self, pos, color):

        row, col = pos

        # grab the coords for where we are highlighting
        x1 = col * CELL_SIZE + MARGIN
        y1 = row * CELL_SIZE + MARGIN
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        # creates the rectangle
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    # method: on_click
    # process: coverts click to board pos, if clicked piece select piece, if clicked square move piece
    def on_click(self, event):

        # get the click event positions
        row, col = self.get_cell_from_click(event.x, event.y)

        # if the position is a valid move square
        if (row, col) in self.valid_moves:
            from_pos = self.selected_piece
            to_pos = (row, col)

            # store the last move
            self.last_move_from = from_pos
            self.last_move_to = to_pos

            # move the piece in the logic
            self.board.move_piece(from_pos, to_pos, self.current_player)

            # compute the score for each player
            self.green_score = self.board.compute_score(1)
            self.red_score = self.board.compute_score(2)

            # check if player has won (filled camp)
            if self.board.check_win(self.current_player):
                # notify the players
                self.refresh_window()
                self.update_status("GAME OVER")

                # decide who the winner is and display to players, winner and moves
                winner = "GREEN" if self.current_player == 1 else "RED"
                msg.showinfo("Game Over", f"{winner} wins in {self.move_count} moves!")

                # turn off the timer
                self.timer_running = False

                if self.timer_id is not None:
                    self.window.after_cancel(self.timer_id)

                # exit
                return

            # else unselect the piece
            self.selected_piece = None
            # reset the moves
            self.valid_moves = []
            # switch the turn to next player
            self.switch_player()
            # redraw the board
            self.refresh_window()

            # exit
            return

        # if the selection is not the correct player
        if self.board.board[row][col] != self.current_player:
            # notify players
            self.update_status("Invalid Selection")

            # exit
            return

        # if the position is a piece on the board
        if self.board.board[row][col] == self.current_player:
            # make this the selected piece
            self.selected_piece = (row, col)
            # get the valid moves for the piece
            self.valid_moves = self.board.get_valid_moves(row, col, self.current_player)
            # redraw the board with the positions
            self.refresh_window()

    # method: get_cell_from_click
    # process: converts a click to the board position
    def get_cell_from_click(self, x, y):

        # position is the input divided by the cell size
        col = (x - MARGIN) // CELL_SIZE
        row = (y - MARGIN) // CELL_SIZE

        # return position
        return row, col

    # method: refresh_window
    # process: driver function this is called as it clears the canvas, calls draw_grid, draw_pieces, draw_highlights
    def refresh_window(self):

        self.canvas.delete("all")   # clears the canvas
        self.draw_grid()            # draw the grid
        self.draw_labels()          # draw labels
        self.draw_last_move()       # draw the last moves
        self.draw_highlights()      # draw the highlights around selected piece
        self.draw_pieces()          # draw the pieces (canvas.create_oval)
        self.update_status()        # updates the status bar

    # method: start_timer
    # process: starts the timer for turn time limit, calls update timer function
    def start_timer(self):

        # stop previous timer
        if self.timer_id is not None:
            self.window.after_cancel(self.timer_id)

        self.time_left = self.time_limit
        self.timer_running = True

        # updates the timer
        self.update_timer()

    # method: switch_player
    # process: switches the turn to the next player and increases move counter
    def switch_player(self):

        # if player one switch to two, if two switch to one
        self.current_player = 2 if self.current_player == 1 else 1

        # update the moves
        self.move_count += 1

        # restart the timer
        self.start_timer()

    # method: update_status
    # process: makes the label to display at the top of the window with player # and the moves
    def update_status(self, message=""):

        # lists whose turn it is
        player = "GREEN" if self.current_player == 1 else "RED"

        # label for the top formatting, player, move count, time remaining, scores, and a message section
        self.status_label.config(
            text=f"Turn: {player} | Moves: {self.move_count} | "
                 f"Time: {self.time_left}s | "
                 f"Green: {self.green_score} | Red: {self.red_score} | "
                 f"{message}")

    # method: update_timer
    # process: updates the status display and will announce winners
    def update_timer(self):

        # cant update if not timer running
        if not self.timer_running:
            return

        # update status bar
        self.update_status()

        # if time runs out
        if self.time_left <= 0:
            # stop timer
            self.timer_running = False

            # whoever turn it was loses, other player wins
            loser = "GREEN" if self.current_player == 1 else "RED"
            winner = "RED" if self.current_player == 1 else "GREEN"

            # show a pop out message
            msg.showinfo("Time Up!", f"{loser} ran out of time!\n{winner} wins!")

            # cancel the timer
            if self.timer_id is not None:
                self.window.after_cancel(self.timer_id)

            # exit
            return

        # else make timer go down
        self.time_left -= 1

        # call again after 1 second
        self.timer_id = self.window.after(1000, self.update_timer)

# ========================================================================== #
#                                MAIN                                        #
# ========================================================================== #
if __name__ == "__main__":
    Halma(8)