from Board import Board
from Constants import CHECK_MATE_SCORE, DRAW_SCORE
from TimeLog import start_sample, end_sample

# Piece square tables #############################################################################
#weight of each piece on each square on the board
pawn_table = 	[0,  0,  0,  0,  0,  0,  0,  0,
				50, 50, 50, 50, 50, 50, 50, 50,
				10, 10, 20, 30, 30, 20, 10, 10,
				 5,  5, 10, 27, 27, 10,  5,  5,
				 0,  0,  0, 25, 25,  0,  0,  0,
				 0,  5,  0, 10, 10,  0,  5,  0,
				 5, 10, 10,-25,-25, 10, 10,  10,
				 0,  0,  0,  0,  0,  0,  0,  0]
				 
knight_table = 	[-50,-40,-30,-30,-30,-30,-40,-50,
				-40,-20,  0,  0,  0,  0,-20,-40,
				-30,  0, 10, 15, 15, 10,  0,-30,
				-30,  5, 15, 20, 20, 15,  5,-30,
				-30,  0, 15, 20, 20, 15,  0,-30,
				-40,  5, 20, 15, 15, 20,  5,-40,
				-40,-20,  0,  0,  0,  0,-20,-40,
				-50,-40,-20,-30,-30,-20,-40,-50]
				
bishop_table = 	[-20,-10,-10,-10,-10,-10,-10,-20,
				-10,  0,  0,  0,  0,  0,  0, -10,
				-10,  0,  5, 10, 10,  5,  0, -10,
				-10,  5,  5, 10, 10,  5,  5, -10,
				-10,  0, 10, 10, 10, 10,  0,- 10,
				-10, 10, 10,-10,-10, 10, 10, -10,
				-10, 10,  0, -5, -5,  0, 10,-10,
				-20,-10,-35,-10,-10,-35,-10,-20]
				
king_table = 	[-30, -40, -40, -50, -50, -40, -40, -30,
				 -30, -40, -40, -50, -50, -40, -40, -30,
				 -30, -40, -40, -50, -50, -40, -40, -30,
				 -30, -40, -40, -50, -50, -40, -40, -30,
				 -20, -30, -30, -40, -40, -30, -30, -20,
				 -10, -20, -20, -20, -20, -20, -20, -10,
				  20,  20,   0,   0,   0,   0,  20,  20,
				  20,  30,  10,   0,   0,  10,  30,  20]

pawn_table_end_game = [0,  0,  0,  0,  0,  0,  0,  0,
						50, 50, 50, 50, 50, 50, 50, 50,
						40, 40, 40, 40, 40, 40, 40, 40,
						30, 30, 30, 30, 30, 30, 30, 30,
						20, 20, 20, 20, 20, 20, 20, 20,
						10, 10, 10, 10, 10, 10, 10, 10,
						 0,  0,  0,  0,  0,  0,  0,  0,
						 0,  0,  0,  0,  0,  0,  0,  0]

				 
# Pieces valid moves ##############################################################################
#numbers to be added or subtracted form a piece's location to obtain its valid moves
top_pawn_moves = [7, 8, 9, 16]
bottom_pawn_moves = [-7, -8, -9, -16]
knight_moves = [-17, -15, -10, -6, 6, 10, 15, 17]
bishop_moves = [9, 18, 27, 36, 45, 54, 63, -9, -18, -27, -36, -45, -54, -63, 7, 14, 21, 28, 35, 42, 49, 56, -7, -14, -21, -28, -35, -42, -49, -56]
rook_moves = [1, 2, 3, 4, 5, 6, 7, -1, -2, -3, -4, -5, -6, -7, 8, 16, 24, 32, 40, 48, 56, -8, -16, -24, -32, -40, -48, -56]
queen_moves = bishop_moves + rook_moves
king_moves = [-1, 1, -8, 8, -7, 7, -9, 9, 2, -2]

pieces_moves = [[], top_pawn_moves, rook_moves, knight_moves, bishop_moves, queen_moves, king_moves, bottom_pawn_moves]


#return square color of position (p) (0:black, 1:white)
def position_color(p):
	rank = int(p/8)
	file = p%8
	
	return (rank%2 == file%2)
	
#check to see if the pieces at p1 and p2 are for the same player
def is_same_type(p1, p2, board):
	if (board[p1] > 0 and board[p1] < 7 and board[p2] > 0 and board[p2] < 7) or (board[p1] > 6 and board[p2] > 6):
		return 1
		
	return 0
	
#check if the diagonal between (f) and (t) is clear
def is_clear_diag(f, t, board):
	#return false if not a diagonal
	file_f = f%8
	file_t = t%8
	
	if abs(int(f/8) - int(t/8)) != abs(file_f - file_t):
		return 0
		
	#set start and end position
	if f < t:
		start = f
		end = t
		
		if file_f < file_t: #if start is to the left of end
			delta = 9 #one row down and one columt right
		else:
			delta = 7 #one row down and one columt left
	else:
		start = t
		end = f
		
		if file_t < file_f: #if start is to the left of end
			delta = 9 #one row down and one columt right
		else:
			delta = 7 #one row down and one columt left
	
	
	#check if diagonal is clear
	start += delta
	while start < end:
		if board[start] != 0:
			return 0
			
		start += delta
		
	return 1

#check if the horizontal line between (f) and (t) is clear
def is_clear_h_line(f, t, board):
	#return false if not a horizontal line
	if int(f/8) != int(t/8):
		return 0
		
	#set start and end position
	if f < t:
		start = f
		end = t
	else:
		start = t
		end = f
	
	#check if horizontal line is clear
	start += 1
	while start < end:
		if board[start] != 0:
			return 0
			
		start += 1
		
	return 1
	
#check if the vertical line between (f) and (t) is clear
def is_clear_v_line(f, t, board):
	#return false if not a horizontal line
	if f%8 != t%8:
		return 0
		
	#set start and end position
	if f < t:
		start = f
		end = t
	else:
		start = t
		end = f
	
	#check if horizontal line is clear
	start += 8
	while start < end:
		if board[start] != 0:
			return 0
			
		start += 8
		
	return 1

#check if a move is valid
def is_valid_move(board, piece, f, t, ignore_same_color = False, ignore_empty_f = False, ignore_turn = True):
	#ignore_same_color = False -> Allow a player to take (eat) itself

	if t > 63 or t < 0 or f > 63 or f < 0:
		return 0
		
	if (ignore_empty_f == False and board.arr[f] == 0) or (ignore_same_color == False and is_same_type(f, t, board.arr)) or (ignore_turn == False and board.turn != (not board.arr[f] < 7)):
		return 0
	
	#pawns
	if piece == 1:
		rank_f = int(f/8)
		
		if (((t == f + 7 or t == f + 9) and int(t/8) == rank_f + 1 and (board.arr[t] != 0 or (board.arr[t] == 0 and board.sides[1][5] == t%8 and rank_f == 4))) 
		or (t == f + 8 and board.arr[t] == 0) 
		or (rank_f == 1 and t == f + 16 and board.arr[f + 8] == 0 and board.arr[t] == 0)):
			return 1
	elif piece == 7:
		rank_f = int(f/8)
		
		if (((t == f - 7 or t == f - 9) and int(t/8) == rank_f - 1 and (board.arr[t] != 0 or (board.arr[t] == 0 and board.sides[0][5] == t%8 and rank_f == 3)))
		or (t == f - 8 and board.arr[t] == 0)
		or (rank_f == 6 and t == f - 16 and board.arr[f - 8] == 0 and board.arr[t] == 0)):
			return 1
	
	#knights
	elif piece == 3 or piece == 9:
		file_f = f%8
		rank_f = int(f/8)
		file_t = t%8
		rank_t = int(t/8)
	
		if (abs(rank_t - rank_f) == 2 and abs(file_t - file_f) == 1) or (abs(rank_t - rank_f) == 1 and abs(file_t - file_f) == 2):
			return 1
			
	#bishops
	elif piece == 4 or piece == 10:
		return is_clear_diag(f, t, board.arr)

	#rooks
	elif piece == 2 or piece == 8:
		return is_clear_h_line(f, t, board.arr) or is_clear_v_line(f, t, board.arr)
			
	#queens
	elif piece == 5 or piece == 11:
		return is_clear_h_line(f, t, board.arr) or is_clear_v_line(f, t, board.arr) or is_clear_diag(f, t, board.arr)
			
	#kings
	elif piece == 6:
		rank_f = int(f/8)
		rank_t = int(t/8)
		
		if ((t == f+7 or t == f+8 or t == f+9) and rank_t == rank_f+1) or ((t == f-7 or t == f-8 or t == f-9) and rank_t == rank_f-1) or ((t == f+1 or t == f-1) and rank_t == rank_f):
			return 1
		
		#check castling
		if board.sides[0][2] == 0 and rank_t == rank_f:
			if board.sides[0][0] == 1:
				if t == f-2 and board.sides[0][3] == 0 and board.arr[f-1] == 0 and board.arr[f-2] == 0 and not is_threatened(board, 0, 1, t+1) and not is_threatened(board, 0, 1, board.sides[0][7]):
					return 1
				elif t == f+2 and board.sides[0][4] == 0 and board.arr[f+1] == 0 and board.arr[f+2] == 0 and board.arr[f+3] == 0 and not is_threatened(board, 0, 1, t-1) and not is_threatened(board, 0, 1, board.sides[0][7]):
					return 1
			else:
				if t == f+2 and board.sides[0][3] == 0 and board.arr[f+1] == 0 and board.arr[f+2] == 0 and not is_threatened(board, 0, 1, t-1) and not is_threatened(board, 0, 1, board.sides[0][7]):
					return 1
				elif t == f-2 and board.sides[0][4] == 0 and board.arr[f-1] == 0 and board.arr[f-2] == 0 and board.arr[f-3] == 0 and not is_threatened(board, 0, 1, t+1) and not is_threatened(board, 0, 1, board.sides[0][7]):
					return 1
	elif piece == 12:
		rank_f = int(f/8)
		rank_t = int(t/8)
		
		if ((t == f+7 or t == f+8 or t == f+9) and rank_t == rank_f+1) or ((t == f-7 or t == f-8 or t == f-9) and rank_t == rank_f-1) or ((t == f+1 or t == f-1) and rank_t == rank_f):
			return 1
			
		if board.sides[1][2] == 0 and rank_t == rank_f:
			if board.sides[1][0] == 1:
				if t == f+2 and board.sides[1][3] == 0 and board.arr[f+1] == 0 and board.arr[f+2] == 0 and not is_threatened(board, 1, 0, t-1) and not is_threatened(board, 1, 0, board.sides[1][7]):
					return 1
				elif t == f-2 and board.sides[1][4] == 0 and board.arr[f-1] == 0 and board.arr[f-2] == 0 and board.arr[f-3] == 0 and not is_threatened(board, 1, 0, t+1) and not is_threatened(board, 1, 0, board.sides[1][7]):
					return 1
			else:
				if t == f-2 and board.sides[1][3] == 0 and board.arr[f-1] == 0 and board.arr[f-2] == 0 and not is_threatened(board, 1, 0, t+1) and not is_threatened(board, 1, 0, board.sides[1][7]):
					return 1
				elif t == f+2 and board.sides[1][4] == 0 and board.arr[f+1] == 0 and board.arr[f+2] == 0 and board.arr[f+3] == 0 and not is_threatened(board, 1, 0, t-1) and not is_threatened(board, 1, 0, board.sides[1][7]):
					return 1
	
	return 0

def _move_piece(f, t, board, turn, check_valid_move = True):
	#return false if wrong turn
	if (board.arr[f] < 7 and turn != 0) or (board.arr[f] > 6 and turn != 1):
		return 0

	#exit if invalid move
	if check_valid_move and not is_valid_move(board, board.arr[f], f, t):
		return 0
	
	if turn == 1:
		#en_passant
		if board.arr[f] == 7 and (t == f-7 or t == f-9) and int(t/8) == int(f/8)-1 and board.arr[t] == 0:
			board.remove_piece(t+8)
				
		#king castling
		if board.sides[1][0] == 1:
			if board.arr[f] == 12 and t == f+2: #short
				board.move_piece(t+1, t-1) #move rook to correct position
				board.set_bottom_short_castled()

			if board.arr[f] == 12 and t == f-2: #long
				board.move_piece(t-2, t+1) #move rook to correct position
				board.set_bottom_long_castled()
		else:
			if board.arr[f] == 12 and t == f+2: #long
				board.move_piece(t+2, t-1) #move rook to correct position
				board.set_bottom_long_castled()

			if board.arr[f] == 12 and t == f-2: #short
				board.move_piece(t-1, t+1) #move rook to correct position
				board.set_bottom_short_castled()
				
		#promote pawn to queens
		if board.arr[f] == 7 and int(t/8) == 0:
			board.remove_piece(f)
			board.set_piece(11, f)
		
		board.move_piece(f, t)
	else:
		#en_passant
		if board.arr[f] == 1 and (t == f+7 or t == f+9) and int(t/8) == int(f/8)+1 and board.arr[t] == 0:
			board.remove_piece(t-8)
			
		#king castling
		if board.sides[0][0] == 0:
			if board.arr[f] == 6 and t == f+2: #short
				board.move_piece(t+1, t-1) #move rook to correct position
				board.set_top_short_castled()
				
			if board.arr[f] == 6 and t == f-2: #long
				board.move_piece(t-2, t+1) #move rook to correct position
				board.set_top_long_castled()
		else:
			if board.arr[f] == 6 and t == f+2: #long
				board.move_piece(t+2, t-1) #move rook to correct position
				board.set_top_long_castled()
				
			if board.arr[f] == 6 and t == f-2: #short
				board.move_piece(t-1, t+1) #move rook to correct position
				board.set_top_short_castled()
			
		#promote pawn to queens
		if board.arr[f] == 1 and int(t/8) == 7:
			board.remove_piece(f)
			board.set_piece(5, f)
		
		board.move_piece(f, t)
	
	return 1
		
#return the number of valid moves for player
def valid_moves_count(board, player, opponent):
	count = 0
	count_with_king_safety = 0
	
	for p in board.sides[player][6]:
		if board.arr[p] < 8:
			piece_moves = pieces_moves[board.arr[p]]
		else:
			piece_moves = pieces_moves[board.arr[p] - 6]
		
		for j in piece_moves:
			to_pos = j+p
			if is_valid_move(board, board.arr[p], p, to_pos):
				count += 1
				
				if king_clear_after_move(board, player, opponent, p, to_pos):
					count_with_king_safety += 1
		
	return [count, count_with_king_safety]

#insert move into moves_arr to keep moves_arr sorted ([lowest attacker, highest victim] to [highest attacker, lowest victim])
def insert_sorted_move(moves_arr, move, board):
	length = len(moves_arr)

	priority_0 = piece_priority(None, board.arr[move[0]])
	priority_1 = piece_priority(None, board.arr[move[1]])

	for i in range(length):
		if priority_0 <= piece_priority(None, board.arr[moves_arr[i][0]]):
			for j in range(i, length):
				if board.arr[moves_arr[j][0]] == board.arr[moves_arr[j][1]]:
					if priority_1 >= piece_priority(None, board.arr[moves_arr[j][1]]):
						moves_arr.insert(j, move)
						return
				else:
					moves_arr.insert(j, move)
					return

	#if it was not added, add it to the end
	moves_arr.append(move)

#insert a position to pos_arr according to piece priority at pos (descending order)
def insert_sorted_position(pos_arr, pos, board):
	pos_priority = piece_priority(None, board.arr[pos]) #priority of piece at pos

	for i in range(len(pos_arr)):
		if pos_priority >= piece_priority(None, board.arr[pos_arr[i]]):
			pos_arr.insert(i, pos)
			return

	#if it was not added, add it to the end
	pos_arr.append(pos)

#return a list of valid moves for player (sorted by importance of move)
def sorted_valid_moves(board, player, opponent, best_moves = []):
	# start_sample("sorted_valid_moves")
	
	ppp = board.sides[player][6][:] #player_pieces_positions

	#put middle pawns first
	adds = 0

	length = len(ppp)
	i = 0
	while i < length:
		if board.arr[ppp[i]] == 1 or board.arr[ppp[i]] == 7:
			file = ppp[i] % 8
			if file == 3 or file == 4:
				ppp.insert(0, ppp[i])
				del ppp[i + 1]

				adds += 1
				if adds == 2: #if two pawns are added (the two middle pawns), no need to continue
					break

		i += 1

	#add pieces' moves
	moves = []

	for p in ppp:
		if board.arr[p] < 8:
			piece_moves = pieces_moves[board.arr[p]]
		else:
			piece_moves = pieces_moves[board.arr[p] - 6]
			
		for j in piece_moves:
			to_pos = j + p
			
			if is_valid_move(board, board.arr[p], p, to_pos) and king_clear_after_move(board, player, opponent, p, to_pos):
				moves.append([p, to_pos])

	#filter attacking moves
	sorted_attack_moves = []
	
	length = len(moves)
	i = 0
	while i < length:
		if board.arr[moves[i][1]] != 0: #if there is an opponent in the "to" position (attacking move)
			insert_sorted_move(sorted_attack_moves, moves[i], board)

			del moves[i]
			length -= 1
		else:
			i += 1
			
	#insert attacking moves to the beginning
	moves = sorted_attack_moves + moves

	#insert best moves to the beginning
	valid_best_moves = []

	for m in best_moves:
		if m in moves: #this move is valid since all moves in the list "moves" are valid
			moves.remove(m)
			valid_best_moves.append(m)

	moves = valid_best_moves + moves
	
	#add en-passant
	# if board.sides[opponent][5] != 0:
	# 	for pp in board.sides[player][6]:
	# 		if board.arr[pp] == 1: #top pawn
	# 			rank = int(pp/8)
	# 			if rank == 4: #only continue if the pawn's rank is 4 (can attack with en-passant)
	# 				file = pp % 8
	# 				if board.sides[opponent][5] == file + 1 and king_clear_after_move(board, player, opponent, pp, pp + 9): #no need to check if the move is valid as the if conditions ensure a valid en-passant
	# 					moves.append([pp, pp + 9])
	# 				elif board.sides[opponent][5] == file - 1 and king_clear_after_move(board, player, opponent, pp, pp + 7):
	# 					moves.append([pp, pp + 7])
	# 		elif board.arr[pp] == 7: #bottom pawn
	# 			rank = int(pp/8)
	# 			if rank == 3: #only continue if the pawn's rank is 3 (can attack with en-passant)
	# 				file = pp % 8
	# 				if board.sides[opponent][5] == file + 1 and king_clear_after_move(board, player, opponent, pp, pp - 7):
	# 					moves.append([pp, pp - 7])
	# 				elif board.sides[opponent][5] == file - 1 and king_clear_after_move(board, player, opponent, pp, pp - 9):
	# 					moves.append([pp, pp - 9])

	# end_sample("sorted_valid_moves")

	return moves
	
def is_quite_move(board, player, opponent, f, t):
	#check if the move is quite before it is made

	if board.arr[t] != 0: #attacking move
		return False

	elif is_threatened(board, opponent, player, board.sides[opponent][7]): #king check
		return False

	elif board.sides[opponent][5] == t%8 and ((board.arr[f] == 1 and int(f/8) == 4) or (board.arr[f] == 7 and int(f/8) == 3)): #en-passant
		return False
	
	elif (board.arr[f] == 1 and int(f/8) == 7) or (board.arr[f] == 7 and int(f/8) == 0): #promotion
		return False

	return True
	
#return position value for piece of type (piece)
def piece_value(piece, p, game_phase):
	if game_phase < 10:
		#pawns
		if piece == 1:
			return pawn_table[63 - p]
		elif piece == 7:
			return pawn_table[p]
			
		#knights
		elif piece == 3:
			return knight_table[63 - p]
		elif piece == 9:
			return knight_table[p]
			
		#bishopt
		elif piece == 4:
			return bishop_table[63 - p]
		elif piece == 10:
			return bishop_table[p]
			
		#kings
		elif piece == 6:
			return king_table[63 - p]
		elif piece == 12:
			return king_table[p]
		
		#queens and rooks
		else:
			return 0
	else:
		#pawns
		if piece == 1:
			return pawn_table_end_game[63 - p]
		elif piece == 7:
			return pawn_table_end_game[p]

		#queens, rooks, bishops and knights
		else:
			return 0
		
#return priority according to piece type and position
def piece_priority(board, piece, p = -1, game_phase = -1):
	#pawn
	if piece == 1:
		#if positional priority is not required return original piece priority
		if p == -1:
			return 1

		piece_rank = int(p/8)
		promote_p = p + (7 - piece_rank)*8
		
		if is_clear_v_line(p, promote_p, board.arr):
			if (game_phase >= 10 and piece_rank > 1) or piece_rank > 4:
				return piece_rank - 1
			else:
				return 1
		else:
			if (game_phase >= 10 and piece_rank > 2) or piece_rank > 4:
				return piece_rank - 2
			else:
				return 1
	elif piece == 7:
		if p == -1:
			return 1

		piece_rank = int(p/8)
		promote_p = p - piece_rank*8
		
		if is_clear_v_line(p, promote_p, board.arr):
			if (game_phase >= 10 and piece_rank < 6) or piece_rank < 3:
				return (6 - piece_rank) #(7 - piece_rank - 1)
			else:
				return 1
		else:
			if (game_phase >= 10 and piece_rank < 5) or piece_rank < 3:
				return (5 - piece_rank) #(7 - piece_rank - 2)
			else:
				return 1
			
	#rook
	elif piece == 2 or piece == 8:
		return 10
		
	#knight
	elif piece == 3 or piece == 9:
		return 4
		
	#bishop
	elif piece == 4 or piece == 10:
		return 6
		
	#queen
	elif piece == 5 or piece == 11:
		return 18
		
	#king
	elif piece == 6 or piece == 12:
		return 0
		
	else:
		return 0

#return the sum of least priorities of pieces at (pieces_positions)
def sum_priorities(board, pieces_positions, game_phase, count = -1):
	if count == 0:
		return 0
		
	priorities = [0] * len(pieces_positions)
	sum = 0
	
	for i in range(len(pieces_positions)):
		priorities[i] = piece_priority(board, board.arr[pieces_positions[i]], pieces_positions[i], game_phase)
	
	if count == -1:
		for i in range(len(pieces_positions)):
			sum += priorities[i]
	else:
		priorities.sort()
		
		if count <= len(pieces_positions):
			items_count = count
		else:
			items_count = len(pieces_positions)
			
		for i in range(items_count):
			sum += priorities[i]
	
	return sum

#return four arrays representing player and opponent attacks and defences
def defences_attacks_lists(board, player, opponent):
	attacked_by_player = [[]] * 64		#player pieces that are attacking opponent pieces at each board position
	defended_by_opponent = [[]] * 64	#opponent pieces that are defending opponent pieces at each board position
	
	attacked_by_opponent = [[]] * 64	#opponent pieces that are attacking player pieces at each board position
	defended_by_player = [[]] * 64		#player pieces that are defending player pieces at each board position

	player_is_top = board.sides[player][6][0] < 7
	opponent_is_top = not player_is_top

	for p in board.sides[player][6]:
		if board.arr[p] < 8:
			piece_moves = pieces_moves[board.arr[p]]
		else:
			piece_moves = pieces_moves[board.arr[p] - 6]

		for j in piece_moves:
			to_pos = j + p

			if to_pos < 0 or to_pos > 63:
				continue

			#player defending himself
			if ((player_is_top and board.arr[to_pos] > 0 and board.arr[to_pos] < 7)
			or (player_is_top == False and board.arr[to_pos] > 6)):
				if is_valid_move(board, board.arr[p], p, to_pos, ignore_same_color = True) and king_clear_after_move(board, player, opponent, p, to_pos):
						defended_by_player[to_pos] = defended_by_player[to_pos] + [p]

			#player attacking opponent
			elif ((player_is_top and board.arr[to_pos] > 6)
			or (player_is_top == False and board.arr[to_pos] > 0 and board.arr[to_pos] < 7)):
				if is_valid_move(board, board.arr[p], p, to_pos) and king_clear_after_move(board, player, opponent, p, to_pos):
						attacked_by_player[to_pos] = attacked_by_player[to_pos] + [p]

	for p in board.sides[opponent][6]:
		if board.arr[p] < 8:
			piece_moves = pieces_moves[board.arr[p]]
		else:
			piece_moves = pieces_moves[board.arr[p] - 6]
			
		for j in piece_moves:
			to_pos = j + p

			if to_pos < 0 or to_pos > 63:
				continue

			#opponent defending himself
			if ((opponent_is_top and board.arr[to_pos] > 0 and board.arr[to_pos] < 7)
			or (opponent_is_top == False and board.arr[to_pos] > 6)):
				if is_valid_move(board, board.arr[p], p, to_pos, ignore_same_color = True) and king_clear_after_move(board, opponent, player, p, to_pos):
						defended_by_opponent[to_pos] = defended_by_opponent[to_pos] + [p]

			#opponent attacking player
			elif ((opponent_is_top and board.arr[to_pos] > 6)
			or (opponent_is_top == False and board.arr[to_pos] > 0 and board.arr[to_pos] < 7)):
				if is_valid_move(board, board.arr[p], p, to_pos) and king_clear_after_move(board, opponent, player, p, to_pos):
						attacked_by_opponent[to_pos] = attacked_by_opponent[to_pos] + [p]

	return attacked_by_player, defended_by_opponent, attacked_by_opponent, defended_by_player

#return True if player's piece at position (t) is threatened by opponent. return False otherwise
def is_threatened(board, player, opponent, t):
	might_be_en_passant = ((board.arr[t] == 1 and board.arr[t-8] == 0) or (board.arr[t] == 7 and board.arr[t+8] == 0)) and board.sides[player][5] == t%8
	
	for p in board.sides[opponent][6]:
		if board.arr[p] < 8:
			piece_moves = pieces_moves[board.arr[p]]
		else:
			piece_moves = pieces_moves[board.arr[p] - 6]
			
		if (t - p) in piece_moves and is_valid_move(board, board.arr[p], p, t):
			return True
		elif might_be_en_passant:
			if board.arr[p] == 1 and (t + 8 - p) in piece_moves and is_valid_move(board, board.arr[p], p, t + 8):
				return True
			elif board.arr[p] == 7 and (t - 8 - p) in piece_moves and is_valid_move(board, board.arr[p], p, t - 8):
				return True
				
	return False

#return True if player's king is safe after move. False otherwise
def king_clear_after_move(board, player, opponent, f, t):
	#is en_passant?. These are not all en-passant conditions buf if they are valid then it might be en-passant move
	#is castling?. These are not all castling conditions buf if they are valid then it might be a catsling move
	#only check en_passant and castling because these moves involve changing squares other than "f" and "t"
	if (((board.arr[f] == 1 or board.arr[f] == 7) and board.sides[opponent][5] == t%8)
	or ((board.arr[f] == 6 or board.arr[f] == 12) and board.sides[player][2] == 0 and (board.sides[player][3] == 0 or board.sides[player][4] == 0))):
		tmp_board = Board(replica = True)
		tmp_board.replicate(board)

		_move_piece(f, t, tmp_board, player, check_valid_move = False)

		return (not is_threatened(tmp_board, player, opponent, tmp_board.sides[player][7]))
	else:
		king_move = (board.arr[f] == 6 or board.arr[f] == 12)

		#board.sides[opponent][6] will be used for the is_threatened call (needs to be updated)
		opponent_piece = False
		if t in board.sides[opponent][6]:
			opponent_piece = True
			board.sides[opponent][6].remove(t)

		tmp_board_t = board.arr[t]
		board.arr[t] = board.arr[f]
		board.arr[f] = 0

		#update king position if it moved (this board variable needs to be updated as it will be used for the is_threatened call)
		if king_move:
			board.sides[player][7] = t

		clear = not is_threatened(board, player, opponent, board.sides[player][7])

		board.arr[f] = board.arr[t]
		board.arr[t] = tmp_board_t

		#restore opponent's piece at "t" (if any)
		if opponent_piece:
			board.sides[opponent][6].append(t)

		#restore king position if it moved
		if king_move:
			board.sides[player][7] = f

		return clear

#return a weight representing how much a draw is in favor for player
def draw_weight(board, player, opponent, game_phase):
	player_pieces_priorities = 0
	opponent_pieces_priorities = 0
	
	player_pieces_count = len(board.sides[player][6])
	opponent_pieces_count = len(board.sides[opponent][6])
	
	for p in board.sides[player][6]:
		player_pieces_priorities += piece_priority(board, board.arr[p], p, game_phase)
			
	for p in board.sides[opponent][6]:
		opponent_pieces_priorities += piece_priority(board, board.arr[p], p, game_phase)
		
	weight = (player_pieces_priorities - opponent_pieces_priorities) * 6
	weight += player_pieces_count - opponent_pieces_count
	
	if weight < 0:
		return DRAW_SCORE
	else:
		return (-DRAW_SCORE)

#return the equivalent index of "i" if the board is rotated
def rotated_index(i):
	# return 63 - ( ((int(i/8) + 1) * 8 - 1) - (i % 8) ) #mirrored_board
	return 63 - i
	
#return a weight representing how much the board is in favor for player
def evaluate_board(board, player, opponent, turn, game_phase):
	start_sample("evaluate_board")

	weight = 0
		
	# Check for check mate ########################################################################
	if turn == player and is_threatened(board, player, opponent, board.sides[player][7]):
		player_valid_moves = valid_moves_count(board, player, opponent)
		if player_valid_moves[1] == 0:
			return (-CHECK_MATE_SCORE)
		
	if turn == opponent and is_threatened(board, opponent, player, board.sides[opponent][7]):
		opponent_valid_moves = valid_moves_count(board, opponent, player)
		if opponent_valid_moves[1] == 0:
			return (CHECK_MATE_SCORE)
	
	
	# Factor for players' and opponents' piece position values ####################################
	player_position_value = 0
	opponent_position_value = 0
	
	for p in board.sides[player][6]:
		player_position_value += piece_value(board.arr[p], p, game_phase)
			
	for p in board.sides[opponent][6]:
		opponent_position_value += piece_value(board.arr[p], p, game_phase)

	if game_phase < 5:
		weight += (player_position_value - opponent_position_value) * 2
	else:
		weight += player_position_value - opponent_position_value
	

	# Factor for players' and opponents' piece priorities and count ###############################
	player_pieces_priorities = 0
	opponent_pieces_priorities = 0
	
	player_pieces_count = len(board.sides[player][6])
	opponent_pieces_count = len(board.sides[opponent][6])
	
	for p in board.sides[player][6]:
		player_pieces_priorities += piece_priority(board, board.arr[p], p, game_phase)
			
	for p in board.sides[opponent][6]:
		opponent_pieces_priorities += piece_priority(board, board.arr[p], p, game_phase)
	
	weight += (player_pieces_priorities - opponent_pieces_priorities) * 250
	weight += (player_pieces_count - opponent_pieces_count) * 100
	
	
	# Find opponents' and players' pieces positions to be used for further evaluation #############
	player_pawn_files = []
	player_knights_positions = []
	player_bishops_positions = []
	opponent_pawn_files = []
	opponent_knights_positions = []
	opponent_bishops_positions = []
	
	for p in board.sides[player][6]:
		if board.arr[p] == 1 or board.arr[p] == 7:
			player_pawn_files.append(p % 8)
		elif board.arr[p] == 3 or board.arr[p] == 9:
			player_knights_positions.append(p)
		elif board.arr[p] == 4 or board.arr[p] == 10:
			player_bishops_positions.append(p)
	
	for p in board.sides[opponent][6]:
		if board.arr[p] == 1 or board.arr[p] == 7:
			opponent_pawn_files.append(p % 8)
		elif board.arr[p] == 3 or board.arr[p] == 9:
			opponent_knights_positions.append(p)
		elif board.arr[p] == 4 or board.arr[p] == 10:
			opponent_bishops_positions.append(p)
			

	# Factor for bishops count and pieces positions ###############################################
	player_bishop_weight = 0
	opponent_bishop_weight = 0
	
	bishops_count = len(player_bishops_positions)
	if bishops_count > 1:
		player_bishop_weight += 150
	elif bishops_count == 1:
		bishop_color = position_color(player_bishops_positions[0])
		
		for p in board.sides[opponent][6]:
			if position_color(p) != bishop_color:
				if p != board.sides[opponent][7]:
					opponent_bishop_weight += 25
				else:
					opponent_bishop_weight += 50
	
	bishops_count = len(opponent_bishops_positions)
	if bishops_count > 1:
		opponent_bishop_weight += 150
	elif bishops_count == 1:
		bishop_color = position_color(opponent_bishops_positions[0])
		
		for p in board.sides[player][6]:
			if position_color(p) != bishop_color:
				if p != board.sides[player][7]:
					player_bishop_weight += 25
				else:
					player_bishop_weight += 50

	weight += player_bishop_weight - opponent_bishop_weight
	

	# Factor for knights on edge ##################################################################
	player_knight_weight = 0
	opponent_knight_weight = 0
	
	for p in player_knights_positions:
		knight_file = p%8
		
		if knight_file == 0 or knight_file == 8:
			player_knight_weight -= 50
		else:
			knight_rank = int(p/8)
			
			if knight_rank == 0 or knight_rank == 8:
				player_knight_weight -= 50
		
	for p in opponent_knights_positions:
		knight_file = p%8
		
		if knight_file == 0 or knight_file == 8:
			opponent_knight_weight -= 50
		else:
			knight_rank = int(p/8)
			
			if knight_rank == 0 or knight_rank == 8:
				opponent_knight_weight -= 50
	
	weight += player_knight_weight - opponent_knight_weight
	

	# Factor for pawns structure ##################################################################
	player_pawn_structure = 0
	opponent_pawn_structure = 0
	
	for i, f in enumerate(player_pawn_files):
		#penalty for double pawns
		if f in player_pawn_files[i+1:]:
			player_pawn_structure -= 50
			
		#penalty for isolated pawns
		if f == 0:
			if (f+1) not in player_pawn_files:
				player_pawn_structure -= 60
		elif f == 7:
			if (f-1) not in player_pawn_files:
				player_pawn_structure -= 60
		else:
			if (f+1) not in player_pawn_files:
				player_pawn_structure -= 30

			if (f-1) not in player_pawn_files:
				player_pawn_structure -= 30
				
	for i, f in enumerate(opponent_pawn_files):
		if f in opponent_pawn_files[i+1:]:
			opponent_pawn_structure -= 50
			
		if f == 0:
			if (f+1) not in opponent_pawn_files:
				opponent_pawn_structure -= 60
		elif f == 7:
			if (f-1) not in opponent_pawn_files:
				opponent_pawn_structure -= 60
		else:
			if (f+1) not in opponent_pawn_files: 
				opponent_pawn_structure -= 30
			
			if (f-1) not in opponent_pawn_files:
				opponent_pawn_structure -= 30

	weight += player_pawn_structure - opponent_pawn_structure
	
	
	# Factor for attacks and defences #############################################################
	player_defence_value = 0
	opponent_defence_value = 0

	attacked_by_player, defended_by_opponent, attacked_by_opponent, defended_by_player = defences_attacks_lists(board, player, opponent)
		
	for p in board.sides[player][6]:
		if len(attacked_by_opponent[p]) > 0 and board.sides[player][7] != p:
			
			#if player's turn, remove attackers that are not protected as they can be eliminated immediatly
			if turn == player:
				for attacker in attacked_by_opponent[p][:]:
					if len(attacked_by_player[attacker]) > 0 and len(defended_by_opponent[attacker]) == 0:
						attacked_by_opponent[p].remove(attacker)
						
				if len(attacked_by_opponent[p]) == 0:
					continue
					
			player_defence = sum_priorities(board, attacked_by_opponent[p], game_phase, count = len(defended_by_player[p])) - (piece_priority(board, board.arr[p], p, game_phase) + sum_priorities(board, defended_by_player[p], game_phase, count = len(attacked_by_opponent[p]) - 1))
			
			#player defence accounts only for losing positions so it doesn't encourage being in a position where the player would gain advantage if the opponent takes the piece at position p (assuming the opponent is not stupid)
			if player_defence < 0:
				if turn == player:
					player_defence *= 2
				else:
					player_defence *= 48
			else:
				player_defence = 0
				
			#penalty if number of attacking pieces is greater than number of defending pieces (+1 for the attacked piece)
			if len(attacked_by_opponent[p]) >= len(defended_by_player[p]) + 1:
				player_defence -= 8*piece_priority(board, board.arr[p], p, game_phase)
		
			player_defence_value += player_defence
		
		#penalty if undefended piece
		if board.sides[player][7] != p and len(defended_by_player[p]) == 0:
			player_defence_value -= piece_priority(board, board.arr[p], p, game_phase)
		
	for p in board.sides[opponent][6]:
		if len(attacked_by_player[p]) > 0 and board.sides[opponent][7] != p:
			
			if turn == opponent:
				for attacker in attacked_by_player[p][:]:
					if len(attacked_by_opponent[attacker]) > 0 and len(defended_by_player[attacker]) == 0:
						attacked_by_player[p].remove(attacker)
						
				if len(attacked_by_player[p]) == 0:
					continue
				
			opponent_defence = sum_priorities(board, attacked_by_player[p], game_phase, count = len(defended_by_opponent[p])) - (piece_priority(board, board.arr[p], p, game_phase) + sum_priorities(board, defended_by_opponent[p], game_phase, count = len(attacked_by_player[p]) - 1))
			
			if opponent_defence < 0:
				if turn == opponent:
					opponent_defence *= 2
				else:
					opponent_defence *= 48
			else:
				opponent_defence = 0
			
			if len(attacked_by_player[p]) >= len(defended_by_opponent[p]) + 1:
				opponent_defence -= 8*piece_priority(board, board.arr[p], p, game_phase)
					
			opponent_defence_value += opponent_defence
		
		if board.sides[opponent][7] != p and len(defended_by_opponent[p]) == 1:
			opponent_defence_value -= piece_priority(board, board.arr[p], p, game_phase)
	
	weight += (player_defence_value - opponent_defence_value) * 4
	

	# Factor for player's and opponent's king safety ##############################################
	player_king_safety = 0
	opponent_king_safety = 0
	
	if board.sides[player][1] > 0:
		player_king_safety += 250
	
	if game_phase < 10:
		if board.sides[player][1] > 0:
			#check king protection pawns and bishops
			if player == 0:
				pawn_pos = board.sides[player][7] + 8
				if board.arr[pawn_pos] != 1 and board.arr[pawn_pos] != 4:
					player_king_safety -= 80
				
				pawn_pos = board.sides[player][7] + 7
				if int(pawn_pos/8) == int(board.sides[player][7]/8)+1 and board.arr[pawn_pos] != 1:
					player_king_safety -= 40
					
				pawn_pos = board.sides[player][7] + 9
				if int(pawn_pos/8) == int(board.sides[player][7]/8)+1 and board.arr[pawn_pos] != 1:
					player_king_safety -= 40
			else:
				pawn_pos = board.sides[player][7] - 8
				if board.arr[pawn_pos] != 7 and board.arr[pawn_pos] != 10:
					player_king_safety -= 80
				
				pawn_pos = board.sides[player][7] - 7
				if int(pawn_pos/8) == int(board.sides[player][7]/8)-1 and board.arr[pawn_pos] != 7:
					player_king_safety -= 40
					
				pawn_pos = board.sides[player][7] - 9
				if int(pawn_pos/8) == int(board.sides[player][7]/8)-1 and board.arr[pawn_pos] != 7:
					player_king_safety -= 40
		elif board.sides[player][2] == 0: #if not castled and can castle, check castling protection pawns
			if board.sides[player][4] == 0:
				if player == 0:
					if board.sides[player][0] == 1:
						castling_pawns = [13, 14, 15]
					else:
						castling_pawns = [8, 9, 10]
						
					for p in castling_pawns:
						if board.arr[p] != 1:
							player_king_safety -= 30
				else:
					if board.sides[player][0] == 1:
						castling_pawns = [48, 49, 50]
					else:
						castling_pawns = [52, 54, 55]
						
					for p in castling_pawns:
						if board.arr[p] != 7:
							player_king_safety -= 30
						
			if board.sides[player][3] == 0:
				if player == 0:
					if board.sides[player][0] == 1:
						castling_pawns = [8, 9, 10]
					else:
						castling_pawns = [13, 14, 15]
						
					for p in castling_pawns:
						if board.arr[p] != 1:
							player_king_safety -= 30
				else:
					if board.sides[player][0] == 1:
						castling_pawns = [52, 54, 55]
					else:
						castling_pawns = [48, 49, 50]
						
					for p in castling_pawns:
						if board.arr[p] != 7:
							player_king_safety -= 30
		
		#penalty for disabled castling
		if board.sides[player][1] == 0:
			if board.sides[player][2] == 1:
				player_king_safety -= 200
			else:
				if board.sides[player][4] == 1:
					player_king_safety -= 80
				if board.sides[player][3] == 1:
					player_king_safety -= 120
	
	#remove king attackers that are not protected
	for attacker in attacked_by_opponent[board.sides[player][7]][:]:
		if len(attacked_by_player[attacker]) > 0 and len(defended_by_opponent[attacker]) == 0:
			attacked_by_opponent[board.sides[player][7]].remove(attacker)
		
	if len(attacked_by_opponent[board.sides[player][7]]) > 0:
		player_king_safety -= 50
	
	if board.sides[opponent][1] > 0:
		opponent_king_safety += 250
		
	if game_phase < 10:
		if board.sides[opponent][1] > 0:
			if opponent == 0:
				pawn_pos = board.sides[opponent][7] + 8
				if board.arr[pawn_pos] != 1 and board.arr[pawn_pos] != 4:
					opponent_king_safety -= 80
				
				pawn_pos = board.sides[opponent][7] + 7
				if int(pawn_pos/8) == int(board.sides[opponent][7]/8)+1 and board.arr[pawn_pos] != 1:
					opponent_king_safety -= 40
					
				pawn_pos = board.sides[opponent][7] + 9
				if int(pawn_pos/8) == int(board.sides[opponent][7]/8)+1 and board.arr[pawn_pos] != 1:
					opponent_king_safety -= 40
			else:
				pawn_pos = board.sides[opponent][7] - 8
				if board.arr[pawn_pos] != 7 and board.arr[pawn_pos] != 10:
					opponent_king_safety -= 80
				
				pawn_pos = board.sides[opponent][7] - 7
				if int(pawn_pos/8) == int(board.sides[opponent][7]/8)-1 and board.arr[pawn_pos] != 7:
					opponent_king_safety -= 40
					
				pawn_pos = board.sides[opponent][7] - 9
				if int(pawn_pos/8) == int(board.sides[opponent][7]/8)-1 and board.arr[pawn_pos] != 7:
					opponent_king_safety -= 40
		elif board.sides[opponent][2] == 0:
			if board.sides[opponent][4] == 0:
				if opponent == 0:
					if board.sides[opponent][0] == 1:
						castling_pawns = [13, 14, 15]
					else:
						castling_pawns = [8, 9, 10]
						
					for p in castling_pawns:
						if board.arr[p] != 1:
							opponent_king_safety -= 30
				else:
					if board.sides[opponent][0] == 1:
						castling_pawns = [48, 49, 50]
					else:
						castling_pawns = [52, 54, 55]
						
					for p in castling_pawns:
						if board.arr[p] != 7:
							opponent_king_safety -= 30
						
			if board.sides[opponent][3] == 0:
				if opponent == 0:
					if board.sides[opponent][0] == 1:
						castling_pawns = [8, 9, 10]
					else:
						castling_pawns = [13, 14, 15]
						
					for p in castling_pawns:
						if board.arr[p] != 1:
							opponent_king_safety -= 30
				else:
					if board.sides[opponent][0] == 1:
						castling_pawns = [52, 54, 55]
					else:
						castling_pawns = [48, 49, 50]
						
					for p in castling_pawns:
						if board.arr[p] != 7:
							opponent_king_safety -= 30
			
		if board.sides[opponent][1] == 0:
			if board.sides[opponent][2] == 1:
				opponent_king_safety -= 200
			else:
				if board.sides[opponent][4] == 1:
					opponent_king_safety -= 80
				if board.sides[opponent][3] == 1:
					opponent_king_safety -= 120
						
	for attacker in attacked_by_player[board.sides[opponent][7]][:]:
		if len(attacked_by_opponent[attacker]) > 0 and len(defended_by_player[attacker]) == 0:
			attacked_by_player[board.sides[opponent][7]].remove(attacker)
			
	if len(attacked_by_player[board.sides[opponent][7]]) > 0:
		opponent_king_safety -= 50
	

	weight += player_king_safety - opponent_king_safety
	
	end_sample("evaluate_board")

	return weight
