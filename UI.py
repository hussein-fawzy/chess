board_segments = [[],   [[], "|     |", "|  *  |", "| *** |", "|  *  |", "| *** |"],
						[[], "|*****|", "| *** |", "| *** |", "| *** |", "|*****|"],
						[[], "|**** |", "|***  |", "|*    |", "|*    |", "|*****|"],
						[[], "|  *  |", "| *** |", "|  *  |", "| *** |", "|*****|"],
						[[], "|  *  |", "| *** |", "| *Q* |", "| *** |", "|*****|"],
						[[], "| ^ ^ |", "| *** |", "| *K* |", "| *** |", "|*****|"]]

default_char = "*"
colors = ["=", "."] #[black char, white char]

def print_board(board, top_color = 0, last_move = []):
	if last_move == []:
		last_move = [-1, -1]

	print("-" * 56)

	for i in range(0, 64, 8): 		#board squares loop. loops by a whole row
		for k in range(6): 			#lines per row loop
			for j in range(i, i+8):	#squares per row loop
				if k == 0:
					if j == last_move[0] or j == last_move[1]:
						print("|->" + str(j).rjust(3) + "|", end = "")
					else:
						print("|" + str(j).rjust(5) + "|", end = "")
				else:
					if board[j] == 0:
						print("|     |", end = "")
					elif board[j] < 7:
						print(board_segments[board[j]][k].replace(default_char, colors[top_color]), end = "")
					else:
						print(board_segments[board[j] - 6][k].replace(default_char, colors[not top_color]), end = "")

			print("")
		
		print("-" * 56)
