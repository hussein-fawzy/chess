from Engine import ChessEngine, set_search_depth, set_ignore_time_limit, set_search_max_time, hashed_weights
from BoardSupport import rotated_index
from UI import print_board

import TimeLog

#game variables
engine = None

bottom_color = 1
rotated_board = 0

last_move = []

def display_board():
	if engine == None:
		return

	if rotated_board == 0:
		print_board(engine.get_board_arr(), not bottom_color, last_move)
	else:
		print_board(engine.get_rotated_board_arr(), not bottom_color, last_move)

def make_move(f, t):
	global last_move

	#rotate inputs if the board is rotated
	if rotated_board:
		f = rotated_index(f)
		t = rotated_index(t)

	engine.move_piece(f, t)
	
	#print last move
	if len(engine.moves) > 0:
		last_move = engine.moves[-1]

		if rotated_board:
			last_move[0] = rotated_index(last_move[0])
			last_move[1] = rotated_index(last_move[1])

	print("")
	print("move ", last_move)

	display_board()

def play_moves_from_moves_list(moves_list):
	moves_count = len(moves_list)

	for i in range(0, len(moves_list), 2):
		# time.sleep(1) #rest the processor

		print("Move: ", moves_list[i])
		make_move(moves_list[i][0], moves_list[i][1])

		if i < moves_count - 1 and moves_list[i + 1] != engine.moves[-1]:
			print("Move Mismatch")
			break

def play_moves_from_moves_times_list(moves_list):
	moves_count = len(moves_list)

	for i in range(0, moves_count, 2):
		# time.sleep(1) #rest the processor

		move = moves_list[i][0]
		print("Move: ",  move)

		make_move(move[0], move[1])

		if i < moves_count - 1 and moves_list[i + 1][0] != engine.moves[-1]:
			print("Move Mismatch")
			break


if __name__ == "__main__":
	TimeLog.add_channel("sorted_valid_moves")
	TimeLog.add_channel("evaluate_board")

	engine = ChessEngine(bottom_color = bottom_color, enable_auto_play = True)

	if len(engine.moves) > 0:
		last_move = engine.moves[-1]

		if rotated_board:
			last_move[0] = rotated_index(last_move[0])
			last_move[1] = rotated_index(last_move[1])

	display_board()	

	while True:
		try:
			f = input("from: ")
			
			if f == "moves": #player moves
				print(engine.moves)
			elif f == "moves_times": #player moves
				for line in engine.moves_times:
					print(line)

			elif f == "eap": #enable auto play
				engine.set_auto_play(1)
			elif f == "dap": #disable auto play
				engine.set_auto_play(0)

			elif f == "pb": #print board
				display_board()
			elif f.startswith("undo"): #undo moves
				val = f.split(" ")
				val = val[1]
				engine.undo(int(val))
				
				display_board()
			elif f == "endgame":
				break
				
			elif f.startswith("ssd"): #set search depth
				val = f.split(" ")
				val = val[1]
				set_search_depth(int(val))
			elif f.startswith("sitl"): #set ignore time limit
				val = f.split(" ")
				val = val[1]
				set_ignore_time_limit(int(val))
			elif f.startswith("ssmt"): #set searth max time
				val = f.split(" ")
				val = val[1]
				set_search_max_time(int(val))
			elif f == "scores":

				min = 2000000
				max = -2000000
				for s in hashed_weights:
					if s < 2000000 and s > max:
						max = s

					if s > -2000000 and s < min:
						min = s

				print(max, min)
					
			f = int(f)
		except:
			continue
		

		if f < 0 or f > 63:
			continue
		
		try:
			t = int(input("to: "))
		except ValueError:
			continue
		
		if t < 0 or t > 63:
			continue
			
		if t == f:
			continue
		
		make_move(f, t)

		TimeLog.print_stats("sorted_valid_moves")
		TimeLog.reset_channel("sorted_valid_moves")

		TimeLog.print_stats("evaluate_board")
		TimeLog.reset_channel("evaluate_board")
