"""
Class responsible for storing all the information about the current state, determining the legal moves and keeping a moves log.
"""

class GameState():

    def __init__(self):

        # Board
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        
        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves, 
            'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.en_passant_possible = () # coordinates for the square where en passant capture is possible
        self.current_castling_right = Castle_Rights(True, True, True, True)
        self.castle_rights_log = [Castle_Rights(self.current_castling_right.wks, self.current_castling_right.bks,   self.current_castling_right.wqs, self.current_castling_right.bqs)]


    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move # swap turns
        
        # update king location if moved
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # en passant move
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_col] = '--' # capturing the pawn

        # update en_passant_possible variable 
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2: # only on 2 squares pawn advances
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.end_col)

        else:
            self.en_passant_possible = ()

        # castle move
        if move.is_castle_move:

            if move.end_col - move.start_col == 2: # kingside castle
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1] # moves the rook
                self.board[move.end_row][move.end_col+1] = '--' # erase the old rook

            else: # queenside castle
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2] # moves the rook
                self.board[move.end_row][move.end_col-2] = '--' # erase the old rook

        # update castling rights - whenever it's a king or rook move
        self.update_castle_rights(move)
        self.castle_rights_log.append(Castle_Rights(self.current_castling_right.wks, self.current_castling_right.bks, 
        self.current_castling_right.wqs, self.current_castling_right.bqs))




    def undo_move(self):

        if len(self.move_log) != 0: # make sure move log not empty

            move = self.move_log.pop()

            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move # swap turns back

            # update king location if needed
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            # undo en passant move
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_col] = '--' # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible = (move.end_row, move.end_col)

            # undo a 2 squares pawn advance
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()

            # undo castling rights
            self.castle_rights_log.pop()
            self.current_castling_right = self.castle_rights_log[-1]
 
            # undo castle move
            if move.is_castle_move:

                if move.end_col - move.start_col == 2: # kingside
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = '--'

                else: # queenside
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = '--'



    def update_castle_rights(self, move):

        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        
        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False

        elif move.piece_moved == 'wR':

            if move.start_row == 7:

                if move.start_col == 0: # queen's side
                    self.current_castling_right.wqs = False
                
                elif move.start_col == 7: #  king's side
                    self.current_castling_right.wks = False

        elif move.piece_moved == 'bR':

            if move.start_row == 0:

                if move.start_col == 0: # queen's side
                    self.current_castling_right.bqs = False
                
                elif move.start_col == 7: #  king's side
                    self.current_castling_right.bks = False


    # Considering checks
    
    def get_valid_moves(self):

        for log in self.castle_rights_log:
            print(log.wks, log.wqs, log.bks, log.bqs, end=", ")
        print()

        temp_en_passant_possible = self.en_passant_possible
        temp_castle_rights = Castle_Rights(self.current_castling_right.wks, self.current_castling_right.bks, 
        self.current_castling_right.wqs, self.current_castling_right.bqs) # copy current castling rights

        # generate all possible moves
        moves = self.get_all_possible_moves()

        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)

        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)


        # for each move, make the move
        for i in range(len(moves)-1, -1, -1): # when removing an element from a list go backwards
            
            self.make_move(moves[i])

            # generate all oppostion moves
            # for each of your opponents moves see if they attack your king
            self.white_to_move = not self.white_to_move 

            if self.in_check():
                moves.remove(moves[i]) # if they attack your king not a valid move
            
            self.white_to_move = not self.white_to_move
            self.undo_move()

        if len(moves) == 0: # either checkmate or stalemate

            if self.in_check():
                self.checkmate = True
            
            else: 
                self.stalemate = True
        
        else:
            self.checkmate = False
            self.stalemate = False

        self.en_passant_possible = temp_en_passant_possible
        self.current_castling_right = temp_castle_rights

        return moves


    # determine if current player is in check

    def in_check(self):

        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])

        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])
            

    # determine if the enemy can attack the square r, c

    def square_under_attack(self, r, c):

        self.white_to_move = not self.white_to_move # switch to opponent's turn

        opposition_moves = self.get_all_possible_moves()

        self.white_to_move = not self.white_to_move # switch back

        for move in opposition_moves:

            if move.end_row == r and move.end_col == c: # square is under attack
                return True

        return False

        
    # Without considering checks

    def get_all_possible_moves(self):
        
        moves = []

        for r in range(len(self.board)): # number of rows

            for c in range(len(self.board[r])): # number of columns in given row

                turn = self.board[r][c][0]

                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    
                    piece = self.board[r][c][1]

                    self.move_functions[piece](r, c, moves) # calls appropriate move function based on piece type
        
        return moves
                    
    

    def get_pawn_moves(self, r, c, moves):
        
        if self.white_to_move: # white pawns

            if self.board[r-1][c] == '--': # 1 square move
                
                moves.append(Move((r, c), (r-1, c), self.board))

                if r == 6 and self.board[r-2][c] == '--': # 2 square move
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0: #captures to the left

                if self.board[r-1][c-1][0] == 'b': # black piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))

                elif (r-1, c-1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_en_passant_move = True))

            if c+1 <= 7: # captures to the right

                if self.board[r-1][c+1][0] == 'b': # black piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))

                elif (r-1, c+1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_en_passant_move = True))
        
        else: # black pawns

            if self.board[r+1][c] == '--': # 1 square move
                
                moves.append(Move((r, c),(r+1, c), self.board))

                if r == 1 and self.board[r+2][c] == '--': # 2 square move
                    moves.append(Move((r, c),(r+2, c), self.board))

            if c-1 >= 0: #captures to the left

                if self.board[r+1][c-1][0] == 'w': # white piece to capture
                    moves.append(Move((r, c), (r+1,c-1), self.board))
                
                elif (r+1, c-1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_en_passant_move = True))

            if c+1 <= 7: # captures to the right

                if self.board[r+1][c+1][0] == 'w': # white piece to capture
                    moves.append(Move((r, c), (r+1,c+1), self.board))

                elif (r+1, c+1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_en_passant_move = True))


    def get_rook_moves(self, r, c, moves):
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right
        enemy_color = 'b' if self.white_to_move else 'w'

        for d in directions:
             for i in range(1, 8):

                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8: # on board

                    end_piece = self.board[end_row][end_col]

                    if end_piece == '--': # empty space valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    elif end_piece[0] == enemy_color: # enemy piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break

                    else: # friendly piece invalid
                        break
                
                else: # not on board
                    break


    def get_knight_moves(self, r, c, moves):
        
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'

        for m in  knight_moves:

            end_row = r + m[0]
            end_col = c + m[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8: # on board

                end_piece = self.board[end_row][end_col]

                if end_piece[0] != ally_color: # not an ally piece (enemy piece or empty space)
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    
    def get_bishop_moves(self, r, c, moves):
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.white_to_move else 'w'

        for d in directions:

            for i in range(1, 8):

                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0<= end_col < 8:

                    end_piece = self.board[end_row][end_col]

                    if end_piece == '--': # empty space valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    elif end_piece[0] == enemy_color: # enemy piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break

                    else: # friendly piece invalid
                        break

                else: # not on board
                    break



    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)



    def get_king_moves(self, r, c, moves):
        
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = 'w' if self.white_to_move else 'b'

        for i in range(8):

            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]

            if 0 <= end_row < 8 and 0 <= end_col < 8: 

                end_piece = self.board[end_row][end_col]

                if end_piece[0] != ally_color: # not an ally piece (enemy piece or empty space)
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    # generate all castle moves and add them to the list of moves
    def get_castle_moves(self, r, c, moves):

        if self.square_under_attack(r, c):
            return # can't castle while in check

        if (self.white_to_move and self.current_castling_right.wks) or (not self.white_to_move and self.current_castling_right.bks):
            self.get_kingside_castle_moves(r, c, moves)

        if (self.white_to_move and self.current_castling_right.wqs) or (not self.white_to_move and self.current_castling_right.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):

        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':

            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move = True))


    def get_queenside_castle_moves(self, r, c, moves):

        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3]:

            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move = True))


         

class Castle_Rights():

    def __init__(self, wks, bks, wqs, bqs):

        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():

    # maps keys to values, key: value
    
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_rank = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}


    def __init__(self, start_square, end_square, board, is_en_passant_move = False, is_castle_move = False):

        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7)
        self.is_en_passant_move = is_en_passant_move
        
        if self.is_en_passant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.is_castle_move = is_castle_move

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
    
    # * Overriding the equals method

    def __eq__(self, other):

        if isinstance(other, Move):
            return self.move_id == other.move_id

        return False

    def get_chess_notation(self):
        return self.get_move(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)


    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_rank[r]

    def get_move(self, r, c):
        
        if self.piece_moved[1] == 'p' and self.piece_captured != '--':
            return self.cols_to_files[c] + 'x'

        if self.piece_moved[1] == 'p':
            return ""

        if self.piece_captured != '--':
            return self.piece_moved[1] + 'x'

        return self.piece_moved[1]