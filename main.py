UNICODE_PIECES = {
    "King": ["\u2654", "\u265A"],
    "Queen": ["\u2655", "\u265B"],
    "Rook": ["\u2656", "\u265C"],
    "Bishop": ["\u2657", "\u265D"],
    "Knight": ["\u2658", "\u265E"],
    "Pawn": ["\u2659", "\u265F\uFE0E"] # uFE0E added for black pawn to prevent
    # it from being emojified.
}

EMPTY_VAL = " "

class Game:

    def __init__(self):
        self.turn_count = 0
        self.captured_white = []
        self.captured_black = []
        self.board = [[EMPTY_VAL] * 8 for _ in range(8)]
        self._set_board()
        self._print_board()
        self._prompt_for_start()

    def _prompt_for_start(self):
        turn = self._get_curr_turn()
        start_input_prompt = "Choose a {} piece to move (square number): ".format(turn)
        start_input = input(start_input_prompt)
        start_coordinates = self._parse_coordinates(start_input)
        if not start_coordinates:
            print("Invalid input. Should be a number on the board.")
            return self._prompt_for_start()
        start_row, start_col = start_coordinates
        piece = self.board[start_row][start_col]
        if piece == EMPTY_VAL or piece.color != turn:
            print("Invalid input. Choose a square with a {} piece.".format(turn))
            return self._prompt_for_start()
        valid_moves = piece.get_valid_moves(self.board, start_row, start_col)
        if not valid_moves:
            type = piece.get_piece_type()
            print("That {} can't move anywhere.".format(type))
            return self._prompt_for_start()
        self._prompt_for_dest(start_row, start_col, piece, valid_moves)

    def _prompt_for_dest(self, start_row, start_col, piece, valid_moves):
        type = piece.get_piece_type()
        end_input_prompt = "Where would you like to move this {}?: ".format(type)
        end_input = input(end_input_prompt)
        end_coordinates = self._parse_coordinates(end_input)
        if not end_coordinates:
            print("Invalid input. Should be a valid number on the board.")
            return self._prompt_for_dest(start_row, start_col, piece, valid_moves)
        end_row, end_col = end_coordinates
        if (end_row, end_col) not in valid_moves:
            print("That {} can't move to {}{}.".format(type, end_row, end_col))
            return self._prompt_for_dest(start_row, start_col, piece, valid_moves)
        self._move_piece(start_row, start_col, end_row, end_col, piece)

    def _parse_coordinates(self, input):
        coordinates = [c for c in input]
        if len(coordinates) != 2:
            return []
        for coordinate in coordinates:
            if not coordinate.isdigit() or not 0 <= int(coordinate) < 8:
                return []
        return [int(digit) for digit in coordinates]

    def _move_piece(self, start_row, start_col, end_row, end_col, piece):
        board = self.board
        board[start_row][start_col] = EMPTY_VAL
        end_occupant = board[end_row][end_col]
        if end_occupant != EMPTY_VAL:
            if end_occupant.get_piece_type() == "King":
                print("Game Over, {} wins!".format(piece.color))
                return
            self._capture_piece(end_occupant)
        board[end_row][end_col] = piece
        self._pawn_swap_check(end_row, end_col, piece)
        self.turn_count += 1
        self._print_board()
        self._prompt_for_start()

    def _pawn_swap_check(self, end_row, end_col, piece):
        if piece.get_piece_type() != "Pawn" or 1 <= end_row <= 6:
            return
        captured = self.captured_white if piece.color == "White" else \
            self.captured_black
        if not captured:
            print("No captured pieces to swap with your pawn.")
            return
        captured_types = [piece.get_piece_type() for piece in captured]
        print("Available Pieces to Swap:")
        for k, v in enumerate(captured_types):
            print("{}: {}".format(k, v))
        choice = input("Which piece would you like? (choose number): ")
        if not self._valid_swap_choice(captured_types, choice):
            print("Invalid choice. Choose a number listed.")
            return self._pawn_swap_check(end_row, end_col, piece)
        swap_in = captured.pop(int(choice))
        captured.append(piece)
        self.board[end_row][end_col] = swap_in

    def _valid_swap_choice(self, captured_types, choice):
        return choice.isdigit() and 0 <= int(choice) < len(captured_types)

    def _capture_piece(self, occupant):
        if occupant.color == "Black":
            self.captured_black.append(occupant)
        else:
            self.captured_white.append(occupant)

    def _get_curr_turn(self):
        return "White" if self.turn_count % 2 == 0 else "Black"

    def _print_board(self):
        print(" ")
        separator = "   |   "
        starting_separator = "  |   "
        space_and_lines = starting_separator + separator.join([EMPTY_VAL] * 8) + "   |"
        horizontal_line = "  " + ("-" * 65)
        print(horizontal_line)
        for row in range(0,8):
            print(space_and_lines)
            label_row = []
            coordinates_row = "  "
            for col in range(0,8):
                occupant = self.board[row][col]
                label_row.append(occupant.uni if occupant != EMPTY_VAL else EMPTY_VAL)
                coordinates_row += "|" + str(row) + str(col) + "     "
            print(starting_separator + separator.join(label_row) + "   |")
            print(coordinates_row + "|")
            print(horizontal_line)
        print(" ")

    def _set_board(self):
        board = self.board
        pieces, pawns = [], []
        for color in ("White", "Black"):
            pieces += [Rook(color), Knight(color), Bishop(color), \
            Queen(color), King(color), Bishop(color), Knight(color), Rook(color)]
            pawns += [Pawn(color)] * 8
        white_pieces, black_pieces = pieces[:8], pieces[8:]
        white_pawns, black_pawns = pawns[:8], pawns[8:]
        board[0] = black_pieces
        board[1] = black_pawns
        board[6] = white_pawns
        board[7] = white_pieces

class Piece:

    def __init__(self, color):
        self.color = color
        self.uni = self._get_uni_val()
        self.non_diagonal_jumps = ((-1, 0), (1, 0), (0, -1), (0, 1))
        self.diagonal_jumps = ((-1, -1), (-1, 1), (1, -1), (1, 1))

    def get_piece_type(self):
        return type(self).__name__

    def _get_uni_val(self):
        type = self.get_piece_type()
        uni_vals = UNICODE_PIECES[type]
        return uni_vals[0] if self.color == "White" else uni_vals[1]

    def _explore_directions(self, board, directions, valid_moves, start_row, start_col):
        for a, b in directions:
            i, j = start_row + a, start_col + b
            while i >= 0 and j >= 0 and i < 8 and j < 8:
                occupant = board[i][j]
                if occupant != EMPTY_VAL and occupant.color != self.color:
                    valid_moves.append((i,j))
                    break
                if occupant != EMPTY_VAL:
                    break
                valid_moves.append((i,j))
                i += a
                j += b

    def _explore_spaces(self, board, possible_spaces, valid_moves, start_row, start_col):
        for a, b in possible_spaces:
            i, j = start_row + a, start_col + b
            if i < 0 or i > 7 or j < 0 or j > 7:
                continue
            occupant = board[i][j]
            if occupant != EMPTY_VAL and occupant.color != self.color:
                valid_moves.append((i, j))
            elif occupant == EMPTY_VAL:
                valid_moves.append((i, j))

class King(Piece):

    def get_valid_moves(self, board, start_row, start_col):
        valid_moves = []
        possible_spaces = self.non_diagonal_jumps + self.diagonal_jumps
        self._explore_spaces(board, possible_spaces, valid_moves, start_row, start_col)
        return valid_moves

class Queen(Piece):

    def get_valid_moves(self, board, start_row, start_col):
        valid_moves = []
        directions = self.non_diagonal_jumps + self.diagonal_jumps
        self._explore_directions(board, directions, valid_moves, start_row, start_col)
        return valid_moves

class Rook(Piece):

    def get_valid_moves(self, board, start_row, start_col):
        valid_moves = []
        directions = self.non_diagonal_jumps
        self._explore_directions(board, directions, valid_moves, start_row, start_col)
        return valid_moves

class Bishop(Piece):

    def get_valid_moves(self, board, start_row, start_col):
        valid_moves = []
        directions = self.diagonal_jumps
        self._explore_directions(board, directions, valid_moves, start_row, start_col)
        return valid_moves

class Knight(Piece):

    def get_valid_moves(self, board, start_row, start_col):
        valid_moves = []
        possible_spaces = ((-2, 1), (-2, -1), (-1, 2), (1, 2), (2, 1), (2, -1), \
            (1, -2), (-1, -2), (-2, -1))
        self._explore_spaces(board, possible_spaces, valid_moves, start_row, start_col)
        return valid_moves

class Pawn(Piece):

    def get_valid_moves(self, board, start_row, start_col):
        valid_moves = []
        direction = -1 if self.color == "White" else 1
        # move a single square forward
        i = start_row + direction
        if 0 <= i < 8 and board[i][start_col] == EMPTY_VAL:
            valid_moves.append((i, start_col))
        # move two squares forward, only possible from starting position
        if (direction == -1 and start_row == 6) or (direction == 1 and start_row == 1):
            i = start_row + (direction * 2)
            if board[i][start_col] == EMPTY_VAL:
                valid_moves.append((i, start_col))
        # diagonal attack moves
        for col_delta in (-1, 1):
            i, j = start_row + direction, start_col + col_delta
            if 0 <= i < 8 and 0 <= j < 8 and board[i][j] != EMPTY_VAL and \
                board[i][j].color != self.color:
                valid_moves.append((i, j))
        return valid_moves

Game()
