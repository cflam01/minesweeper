from random import randint


class Minesweeper:
    def __init__(self):
        # Game config
        self.__row = 10
        self.__col = 10
        self.__mines = 10
        self.__uncovered = 0

        # Game state flags
        self.__won = False
        self.__game_end = False
        self.__attempts = 0

        # Board shenanigans
        self.__grid = [[0 for _ in range(self.__col)] for _ in range(self.__row)]
        self.__board = [["." for _ in range(self.__col)] for _ in range(self.__row)]

    def __avoid_first_click(self, col, row):
        self.__grid = [[0 for _ in range(self.__col)] for _ in range(self.__row)]
        mine_placements = 0

        while mine_placements < self.__mines:
            mp_col, mp_row = randint(0, self.__col - 1), randint(0, self.__row - 1)
            if self.__grid[mp_row][mp_col] == -1 or (mp_row == row and mp_col == col):
                continue

            self.__grid[mp_row][mp_col] = -1
            mine_placements += 1

        self.__calculate_neighbours()

    def __calculate_neighbours(self):
        for r in range(self.__row):
            for c in range(self.__col):
                if self.__grid[r][c] == -1:
                    continue

                minecount = 0
                for i in range(max(0, r - 1), min(self.__row, r + 2)):
                    for j in range(max(0, c - 1), min(self.__col, c + 2)):
                        if self.__grid[i][j] == -1:
                            minecount += 1

                self.__grid[r][c] = minecount

    def reveal_dots(self):
        # Reveal mines on the game board
        for r in range(self.__row):
            for c in range(self.__col):
                if self.__grid[r][c] == -1:
                    self.__board[r][c] = "X"
        self.__game_end = True

    def display_board(self):
        # Returns a string representation of the current board
        header = "   " + " ".join(str(i) for i in range(self.__col))
        separator = "\n   " + "-" * (self.__col * 2 - 1)
        rows = [f"{r}| " + " ".join(self.__board[r]) for r in range(self.__row)]
        return "Current board:\n\n" + header + separator + "\n" + "\n".join(rows)

    def get_uncovered(self):
        return self.__uncovered

    def get_game_end(self):
        return self.__game_end

    def get_attempts(self):
        return self.__attempts

    def get_board(self):
        return self.__board

    def uncover_dots(self, col, row, player=True):
        # If it's the first move, place the mines avoiding the first click
        if self.__attempts == 0:
            self.__avoid_first_click(col, row)

        # If it's the player uncovering or the thingy that goes through adjacent cells
        if player:
            self.__attempts += 1

        # Return if position is already flagged or uncovered
        if self.__board[row][col] in {"F", " "}:  # Changed "." to " " for uncovered space
            if player:
                self.__attempts -= 1
            return

        # Handle mine uncovering
        if self.__grid[row][col] == -1:
            self.reveal_dots()
            return

        # Handle uncovering number or empty space
        if self.__grid[row][col] > 0:
            self.__board[row][col] = str(self.__grid[row][col])
        else:
            self.__board[row][col] = " "
            # Check and uncover surrounding cells if empty
            for i in range(max(0, row - 1), min(self.__row, row + 2)):
                for j in range(max(0, col - 1), min(self.__col, col + 2)):
                    if self.__board[i][j] == ".":
                        self.uncover_dots(j, i, player=False)

    def win_lose(self):
        self.__uncovered = 0
        for i in range(self.__row):
            for u in range(self.__col):
                if self.__board[i][u] != "." and self.__board[i][u] != "F" \
                        and self.__board[i][u] != "X":
                    self.__uncovered += 1
                if self.__board[i][u] == "X":
                    return self.__won

        # Check if player has uncovered all non-mine spaces
        if self.__row * self.__col - self.__mines == self.__uncovered:
            xloc = 0
            yloc = 0
            for x in self.__grid:
                for y in x:
                    if y == -1:
                        self.__board[xloc][yloc] = "X"
                    yloc += 1
                xloc += 1
                yloc = 0
            self.__won = True
            self.__game_end = True

        return self.__won


def row_or_col(game, selecting_row):
    if selecting_row:
        row_col_prompt = "vertical row number between 0-9 (set of numbers on the left)"
    else:
        row_col_prompt = "horizontal column number between 0-9 (set of numbers at the top)"
    exit_program = ["quit", "stop", "exit"]

    while True:
        selection = input(f"Please enter a {row_col_prompt} - ").casefold()
        if selection in exit_program:
            game.reveal_dots()
            return "quit"

        try:
            selection = int(selection)
            if 0 <= selection <= 9:
                return selection
        except ValueError:
            pass

        print("Invalid input")


def game_options(game):
    # Display remaining dots to uncover
    dots_left = 90 - game.get_uncovered()
    print(f"You have {dots_left} dot{'' if dots_left == 1 else 's'} left to uncover.")

    allowed = {"r", "reveal", "f", "flag", "u", "unflag", "exit", "quit", "stop"}
    while (decision := input("Would you like to reveal (r), flag (f), or unflag (u) a location? - ").casefold()) not in allowed:
        pass

    if decision in {"quit", "exit", "stop"}:
        game.reveal_dots()
        return

    row = row_or_col(game, selecting_row=True)
    col = row_or_col(game, selecting_row=False)
    if row == "quit" or col == "quit":
        return

    board = game.get_board()
    if decision in {"f", "flag"}:
        if board[row][col] != ".":
            if board[row][col] == "F":
                board[row][col] = "."
            else:
                print("This location has already been revealed before!")
        else:
            board[row][col] = "F"

    elif decision in {"u", "unflag"}:
        if board[row][col] == "F":
            board[row][col] = "."
        else:
            print("This location is not flagged!")

    elif decision in {"r", "reveal"}:
        if board[row][col] == ".":
            game.uncover_dots(col, row)
        else:
            print("This location has already been revealed before!")


def main():
    game = Minesweeper()
    won = False
    while not game.get_game_end():
        print(f"Attempt {game.get_attempts() + 1}. {game.display_board()}")
        game_options(game)
        won = game.win_lose()
    print(game.display_board())
    result = "won" if won else "lost"
    print(f"You have {result} Minesweeper!\nTotal attempts: {game.get_attempts()}\nThanks for playing!")


if __name__ == "__main__":
    main()
