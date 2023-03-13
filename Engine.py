from Board import Board
from BoardSupport import _move_piece, evaluate_board, sorted_valid_moves, is_quite_move, is_threatened, draw_weight, rotated_index
from Constants import INFINITY, EMPTY_SCORE, CHECK_MATE_SCORE
from datetime import datetime

#hashing boards
hashed_boards_count = 10000000
hashed_weights = [EMPTY_SCORE] * hashed_boards_count

#hashing trees
hashed_trees_count = 5000000
hashed_tree_eval_flag = [0] * hashed_trees_count #1: exact tree, 2: pruned tree, 3: tree did not change alpha or beta
hashed_lines = [0] * hashed_trees_count
hashed_scores = [EMPTY_SCORE] * hashed_trees_count

#statistics
eval_count = 0
from_hash_count = 0
tree_eval_count = 0
tree_from_hash_count = 0

reached_depth = 0
prunes = 0

#sorting moves
cut_off_moves = [[], []] #[[player's moves], [opponent's moves]] moves that caused a prune at a certain depth will be used in sorting valid moves (likely to cause another cut off)
best_moves_ID = [[], []] #[[player's moves], [opponent's moves]] contains the best moves found (obtained from iterative deepening). will be used in sorting valid moves

#search control
search_depth = 4 				#the tree will be fully searched to this depth with iterative deepening
max_q_search_depth = 8 			#non-quite moves quiscence search will not go deeper than this depth
nav_all_in_q_search = False		#navigate all moves - not only non-quite moves - when q_search starts (when depth is reached and a non-quite move is found)
ignore_time_limit = 1
search_max_time = 30
search_start_time = 0


def set_search_depth(value):
	global search_depth
	
	search_depth = value

def set_search_max_time(value):
	global search_max_time
	
	search_max_time = value
	
def set_ignore_time_limit(value):
	global ignore_time_limit
	
	ignore_time_limit = value


#get board index from its zobrist key
def board_zobrist_index(board, length):
	return board.zobrist % length
	

#return a weight representing how much the board is in favor for player (from hash or evaluation)
def get_board_score(board, player, opponent, turn, game_phase):
	global eval_count, from_hash_count
	
	#check for the board is hashed
	board_index = board_zobrist_index(board, hashed_boards_count)
	if hashed_weights[board_index] != EMPTY_SCORE:
		from_hash_count += 1

		return hashed_weights[board_index]
	
	#evaluate board	
	weight = evaluate_board(board, player, opponent, turn, game_phase)
	
	#hash the board
	hashed_weights[board_index] = weight
	
	eval_count += 1
	
	return weight

#start tree navigation with Iterative Deepening	
def generate_move_minimax(engine):
	global eval_count, from_hash_count, tree_eval_count, tree_from_hash_count, reached_depth, prunes
	global cut_off_moves, best_moves_ID
	global search_start_time
	
	#init variables
	eval_count = 0
	from_hash_count = 0
	tree_eval_count = 0
	tree_from_hash_count = 0

	reached_depth = 0
	prunes = 0
	
	search_start_time = datetime.now()
	
	cut_off_moves = [[], []]
	best_moves_ID = [[], []]
	
	best_score = -INFINITY
	
	time_1 = 0
	time_2 = 0
	time_factor = 4.0
	
	#start iterative deepening
	for i in range(1, search_depth + 1):
		loop_start_time = datetime.now()

		tmp_minimax_pruning = minimax_pruning(i, i, -INFINITY, INFINITY, engine)
		
		if tmp_minimax_pruning != 0:
			best_moves_line = tmp_minimax_pruning[1]
			best_score = tmp_minimax_pruning[0]
			
			#add best_moves_line to best_moves_ID
			for j, m in enumerate(best_moves_line):
				if j % 2 == 0: #even indices are for player's moves
					if m not in best_moves_ID[0]:
						best_moves_ID[0] += [m]
				else: #odd indices are for opponent's moves
					if m not in best_moves_ID[1]:
						best_moves_ID[1] += [m]

			print("moves line", best_moves_line)
			
			#if search is not complete when returned (game ended? or time over?), no need to continue
			if len(best_moves_line) < i:
				break
		else:
			break
		
		#if check mate, dont continue searching
		if best_score >= CHECK_MATE_SCORE:
			print("check mate in", len(best_moves_line))
			break
			
		#if time is up or little time left, dont continue searching
		if ignore_time_limit == 0:
			if i == 1:
				time_1 = datetime.now() - loop_start_time
			elif i == 2:
				time_2 = datetime.now() - loop_start_time
			else:
				time_1 = time_2
				time_2 = datetime.now() - loop_start_time
				
				if time_1.seconds == 0:
					time_factor = 4.0
				else:
					time_factor = (time_2.seconds + time_2.microseconds/10000000.0) / (time_1.seconds + time_1.microseconds/10000000.0)
					if time_factor < 4:
						time_factor = 4.0
					else:
						print("time factor", time_factor)
				
			search_curr_time = datetime.now() - search_start_time
			if search_curr_time.seconds > search_max_time/time_factor:
				break
	
	print("")
	print("depth", len(best_moves_line))
	print("reached depth", reached_depth, " / ", max_q_search_depth)
	print("")
	print("boards", eval_count, "   ", from_hash_count)
	print("trees", tree_eval_count, "   ", tree_from_hash_count)
	print("prunes", prunes)
	print("")

	return best_moves_line[0]

def minimax_pruning(start_depth, depth, alpha, beta, engine, prev_move = [], check_time = True, q_search = False):
	#top_player is the maximizing player
	#prev_move is the move which lead to calling this function
	
	global tree_eval_count, tree_from_hash_count, reached_depth, prunes
	global cut_off_moves
	
	init_alpha = alpha
	init_beta = beta

	#update max reached depth (for statistics)
	if start_depth > reached_depth:
		reached_depth = start_depth
	
	if depth == 0:
		return [get_board_score(engine.board, 0, 1, engine.turn, engine.game_phase), [prev_move]] #always return the score in favour of the engine (always bottom player)
			

	# check if tree is hashed #####################################################################
	board_index = board_zobrist_index(engine.board, hashed_trees_count)
	if hashed_scores[board_index] != EMPTY_SCORE and len(hashed_lines[board_index]) >= depth:

		#accept hashed tree if it is fully searched or if it pruned and still meets the pruning condition
		#if maximizing move (turn == 0), check that score is greater than beta (meaning that the tree would still be pruned)
		#if minimizing move (turn == 1), check that score is smaller than alpha (meaning that the tree would still be pruned)
		if (hashed_tree_eval_flag[board_index] == 1) or (engine.turn == 0 and hashed_scores[board_index] > beta) or (engine.turn == 1 and hashed_scores[board_index] < alpha):
			tree_from_hash_count += 1
			
			if prev_move != []:
				return [hashed_scores[board_index], [prev_move] + hashed_lines[board_index]]
			else:
				return [hashed_scores[board_index], hashed_lines[board_index]]

	###############################################################################################


	# prepare best moves and generate valid moves #################################################
	curr_depth = start_depth - depth

	if curr_depth % 2 == 0: #even depth means its player's turn. only get player's moves from best_moves_ID and cut_off_moves
		best_moves = best_moves_ID[0] + cut_off_moves[0]
	else: #odd depth means its opponents's turn. only get opponents's moves from best_moves_ID and cut_off_moves
		best_moves = best_moves_ID[1] + cut_off_moves[1]

	valid_moves = sorted_valid_moves(engine.board, engine.turn, not engine.turn,  best_moves = best_moves)
	
	###############################################################################################


	# check if game ended with a checkmate or a draw ##############################################
	if len(valid_moves) == 0:
		if engine.turn == 0:
			if is_threatened(engine.board, 0, 1, engine.board.sides[0][7]):
				return [(-CHECK_MATE_SCORE - depth), [prev_move]]
			else:
				return [draw_weight(engine.board, 0, 1, engine.game_phase), [prev_move]]
		else:
			if is_threatened(engine.board, 1, 0, engine.board.sides[1][7]):
				return [(CHECK_MATE_SCORE + depth), [prev_move]] #(+ depth) so that closer check mates have higher weights
			else:
				return [draw_weight(engine.board, 0, 1, engine.game_phase), [prev_move]]
	
	###############################################################################################
	

	tmp_engine = ChessEngine(enable_auto_play = False, full_init = False, replica_board = True) #temporary instance to manipulate the pieces
	
	tree_eval_flag = 0;
	curr_moves_line = 0
	

	# navigate tree ###############################################################################
	move_made = False #flag to indicate if any of the valid moves is carried out. all moves could be ignored if it is q_search region and all moves are quite

	for tmp_move in valid_moves:

		#check if the time is over
		if check_time and ignore_time_limit == 0:
			search_curr_time = datetime.now() - search_start_time
			if search_curr_time.seconds >= search_max_time:
				return 0
		
		#copy engine parameters
		tmp_engine.replicate(engine)
		
		#check if the move is quite
		quite_move = True

		#if search is about to end and max_q_search_depth is not reached, check if the move is quite
		#also check if max_q_search_depth is not reached and search has turned to a q_search
		if (depth == 1 or q_search) and start_depth < max_q_search_depth:
			quite_move = is_quite_move(tmp_engine.board, tmp_engine.turn, not tmp_engine.turn, tmp_move[0], tmp_move[1])

		#make the move
		if q_search == False or (q_search and not is_quite_move):
			tmp_engine.move_piece(tmp_move[0], tmp_move[1])
			move_made = True

			#if not quite move, go deeper
			if not quite_move:

				#add extra depth that makes the last move an opponent's move
				if start_depth % 2 == 0: #even start depth -> last move is opponent's move
					extra_depth = 2 #add even number to keep the last move an opponent's move
				else:
					extra_depth = 3 #add odd number to make the last move an opponent's move

				#quiscence search depth cannot exceed max_q_search_depth
				#the last move in this case can be for opponent or player depending on max_q_search_depth
				if (start_depth + extra_depth > max_q_search_depth):
					extra_depth = max_q_search_depth - start_depth

				tmp_minimax_pruning = minimax_pruning(start_depth + extra_depth, depth - 1 + extra_depth, alpha, beta, tmp_engine, prev_move = tmp_move, check_time = check_time, q_search = (True and not nav_all_in_q_search) )
			else:
				#pass the q_search parameter to the minimax_pruning call since the search could've reached the q_search region but the current move is a quite move
				#if it's not passed, it could be the q_search region and all the moves will be examined in the next minimax_pruning call
				tmp_minimax_pruning = minimax_pruning(start_depth, depth - 1, alpha, beta, tmp_engine, prev_move = tmp_move, check_time = check_time, q_search = q_search)
			
			#time is over? (child nodes return 0 if time is over)
			if tmp_minimax_pruning == 0:
				return 0
			
			#set initial value for curr_moves_line
			if curr_moves_line == 0:
				curr_moves_line = tmp_minimax_pruning[1]
			
			#update alpha or beta. update curr_moves_line
			if engine.turn == 0:
				tmp_alpha = tmp_minimax_pruning[0]
				if tmp_alpha > alpha:
					alpha = tmp_alpha
					curr_moves_line = tmp_minimax_pruning[1]
			else:
				tmp_beta = tmp_minimax_pruning[0]
				if tmp_beta < beta:
					beta = tmp_beta
					curr_moves_line = tmp_minimax_pruning[1]

			#prune
			if beta <= alpha:
				#save cut-off move
				#curr_depth is created earlier in the function
				if curr_depth % 2 == 0: #even depth means it was player's turn. set as player's move
					if tmp_move not in cut_off_moves[0]:
						cut_off_moves[0] += [tmp_move]
				else: #odd depth means it was opponents's turn. set as opponent's move
					if tmp_move not in cut_off_moves[1]:
						cut_off_moves[1] += [tmp_move]

				prunes += 1
				tree_eval_flag = 2
				break

	#if none of the valid moves was played, return the weight of the current board (as if the final depth is reached)
	if not move_made:
		return [get_board_score(engine.board, 0, 1, engine.turn, engine.game_phase), [prev_move]]
	
	###############################################################################################


	tree_eval_count += 1

	#set eval_flag
	if tree_eval_flag == 0:
		if (engine.turn == 0 and alpha > init_alpha) or (engine.turn == 1 and beta < init_beta):
			tree_eval_flag = 1
		else:
			tree_eval_flag = 3
	

	# hash search result ##########################################################################	
	hashed_tree_eval_flag[board_index] = tree_eval_flag
	hashed_lines[board_index] = curr_moves_line
	if engine.turn == 0:
		hashed_scores[board_index] = alpha
	else:
		hashed_scores[board_index] = beta

	###############################################################################################

	
	#return the result
	if engine.turn == 0:
		if prev_move != []:
			return [alpha, [prev_move] + curr_moves_line]
		else:
			return [alpha, curr_moves_line]
	else:
		if prev_move != []:
			return [beta, [prev_move] + curr_moves_line]
		else:
			return [beta, curr_moves_line]

			
class ChessEngine:
	
	def __init__(self, bottom_color = 1, enable_auto_play = True, replica_board = False, board = "", full_init = True):
		self.board = Board(replica_board, bottom_color)
			
		self.enable_auto_play = enable_auto_play
		
		self.moves_times = [] #array for statistics

		self.moves = []
		self.game_phase = 0 #0: start, 5: middle, 10: end
		
		if full_init:
			if replica_board:
				self.board.replicate(board)
		
			#set turn
			if self.board.sides[1][0] == 1:
				self.turn = 1
				self.board.set_turn(1)
			else:
				self.turn = 0
				self.board.set_turn(0)
			
			#play if computer's turn
			if self.enable_auto_play and self.turn == 0:
				self.make_engine_move()

	def replicate(self, engine):
		self.board.replicate(engine.board)
		self.game_phase = engine.game_phase
		self.set_turn(engine.turn)

	def reset_engine(self):
		bottom_color = self.board.sides[1][0]
		
		self.board = Board()
		
		self.board.sides[0][0] = not bottom_color
		self.board.sides[1][0] = bottom_color

		self.copy_players_to_board()
		
		#set turn
		if self.board.sides[1][0] == 1:
			self.set_turn(1)
		else:
			self.set_turn(0)
			
		self.moves = []
		self.game_phase = 0

	def set_auto_play(self, value):
		self.enable_auto_play = value
		
		if self.turn == 0 and self.enable_auto_play:
			self.make_engine_move()
	

	def get_board_arr(self):
		return self.board.arr
	
	def get_rotated_board_arr(self):
		#a rotated chess board is a mirrored board about the horizontal center line

		rotated_board = [0] * 64
		
		for i in range(64):
			rotated_board[i] = self.board.arr[rotated_index(i)]
			
		return rotated_board
		

	def set_turn(self, turn):
		self.turn = turn
		self.board.set_turn(turn)
	
	def apply_moves(self, moves):
		ap = self.enable_auto_play
		self.enable_auto_play = 0
		
		for move in moves:
			self.move_piece(move[0], move[1])
		
		self.enable_auto_play = ap
		
	def undo(self, n):
		moves = self.moves[:-2*n]
		
		self.reset_engine()
		self.apply_moves(moves)

		#statistics array
		self.moves_times = self.moves_times[:-2*n]
	
	def move_piece(self, f, t):
		if _move_piece(f, t, self.board, self.turn) == 0:
			return 0
		
		self.moves.append([f, t])
				
		#update game_phase
		if len(self.moves) == 6:
			self.game_phase = 5
			self.board.game_phase = self.game_phase
	
		#count number of pawns
		top_player_pawns_count = 0
		bottom_player_pawns_count = 0
		
		for p in self.board.sides[0][6]:
			if self.board.arr[p] == 1 or self.board.arr[p] == 7:
				top_player_pawns_count += 1
		
		for p in self.board.sides[1][6]:
			if self.board.arr[p] == 1 or self.board.arr[p] == 7:
				bottom_player_pawns_count += 1
		
		#check if end game phase		
		if len(self.board.sides[0][6]) - top_player_pawns_count + len(self.board.sides[1][6]) - bottom_player_pawns_count < 7:
			self.game_phase = 10
			self.board.game_phase = self.game_phase
		
		#change turn
		self.set_turn(not self.turn)

		#if computer turn	
		if self.turn == 0 and self.enable_auto_play == True:
			self.make_engine_move()
		

	def generate_move(self):		
		return generate_move_minimax(self)
		
	def make_engine_move(self):
		start = datetime.now()

		computer_move = self.generate_move()

		length = datetime.now() - start
		print("s ", length.seconds, " m ", length.microseconds)
		
		evals = from_hash_count + eval_count
		if evals > 0:
			print("ms/eval ", (length.seconds * 1000.0 + length.microseconds / 1000) / evals)
		
		self.move_piece(computer_move[0], computer_move[1])

		#add to statistics list
		moves_count = len(self.moves)
		moves_times_count = len(self.moves_times)

		if (moves_count == moves_times_count + 2):
			self.moves_times.append([self.moves[-2], 0])
			self.moves_times.append([self.moves[-1], (length.seconds + length.microseconds / 1000000.0)])
		else:
			self.moves_times.append([self.moves[-1], (length.seconds + length.microseconds / 1000000.0)])
