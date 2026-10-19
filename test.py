import random
import tkinter as tk


COLS = 10
ROWS = 20
CELL = 60
BOARD_WIDTH = COLS * CELL
BOARD_HEIGHT = ROWS * CELL

BACKGROUND = "#111820"
PANEL = "#1b2730"
GRID = "#263640"
TEXT = "#edf3f4"
MUTED = "#9aabb2"

PIECES = {
	"I": ("#50d8c7", ((0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0))),
	"O": ("#f2c14e", ((0, 0, 0, 0), (0, 1, 1, 0), (0, 1, 1, 0), (0, 0, 0, 0))),
	"T": ("#b28dff", ((0, 0, 0, 0), (1, 1, 1, 0), (0, 1, 0, 0), (0, 0, 0, 0))),
	"S": ("#7bd88f", ((0, 0, 0, 0), (0, 1, 1, 0), (1, 1, 0, 0), (0, 0, 0, 0))),
	"Z": ("#ff7272", ((0, 0, 0, 0), (1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 0, 0))),
	"J": ("#69a9ff", ((0, 0, 0, 0), (1, 0, 0, 0), (1, 1, 1, 0), (0, 0, 0, 0))),
	"L": ("#ff9e5e", ((0, 0, 0, 0), (0, 0, 1, 0), (1, 1, 1, 0), (0, 0, 0, 0))),
}


class Tetris:
	def __init__(self, root):
		self.root = root
		self.cell = min(CELL, max(18, (root.winfo_screenheight() - 260) // ROWS))
		self.board_width = COLS * self.cell
		self.board_height = ROWS * self.cell
		self.preview_width = self.cell * 5
		self.preview_height = self.cell * 4
		self.root.title("俄罗斯方块")
		self.root.configure(bg=BACKGROUND)
		self.root.resizable(False, False)
		self.root.bind_all("<KeyPress>", self.on_key)

		shell = tk.Frame(root, bg=BACKGROUND, padx=22, pady=20)
		shell.pack()

		tk.Label(
			shell,
			text="俄罗斯方块",
			bg=BACKGROUND,
			fg=TEXT,
			font=("Microsoft YaHei UI", 20, "bold"),
		).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

		self.canvas = tk.Canvas(
			shell,
			width=self.board_width,
			height=self.board_height,
			bg="#0d141a",
			highlightthickness=1,
			highlightbackground=GRID,
		)
		self.canvas.grid(row=1, column=0, rowspan=2, sticky="n")

		sidebar = tk.Frame(shell, bg=BACKGROUND, width=170)
		sidebar.grid(row=1, column=1, sticky="n", padx=(18, 0))
		sidebar.grid_propagate(False)

		self.score_var = tk.StringVar()
		self.lines_var = tk.StringVar()
		self.level_var = tk.StringVar()
		for label, variable in (
			("分数", self.score_var),
			("消除行数", self.lines_var),
			("等级", self.level_var),
		):
			block = tk.Frame(sidebar, bg=PANEL, padx=12, pady=9)
			block.pack(fill="x", pady=(0, 8))
			tk.Label(block, text=label, bg=PANEL, fg=MUTED, font=("Microsoft YaHei UI", 9)).pack(anchor="w")
			tk.Label(block, textvariable=variable, bg=PANEL, fg=TEXT, font=("Microsoft YaHei UI", 18, "bold")).pack(anchor="w")

		tk.Label(
			sidebar,
			text="下一个",
			bg=BACKGROUND,
			fg=MUTED,
			font=("Microsoft YaHei UI", 10, "bold"),
		).pack(anchor="w", pady=(8, 6))
		self.preview = tk.Canvas(sidebar, width=self.preview_width, height=self.preview_height, bg=PANEL, highlightthickness=0)
		self.preview.pack(anchor="w")

		self.status_var = tk.StringVar(value="")
		tk.Label(
			sidebar,
			textvariable=self.status_var,
			bg=BACKGROUND,
			fg="#50d8c7",
			font=("Microsoft YaHei UI", 10, "bold"),
			justify="left",
		).pack(anchor="w", pady=(12, 6))

		controls = tk.Frame(shell, bg=BACKGROUND)
		controls.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(14, 0))
		tk.Label(
			controls,
			text="← → 移动    ↑ 旋转    ↓ 加速下落    空格 硬降    P 暂停    R 重开",
			bg=BACKGROUND,
			fg=MUTED,
			font=("Microsoft YaHei UI", 9),
		).pack(anchor="w")

		self.reset()
		self.tick()
		self.root.update_idletasks()
		x = max(0, (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2)
		y = max(0, (self.root.winfo_screenheight() - self.root.winfo_height()) // 2)
		self.root.geometry(f"+{x}+{y}")

	def reset(self):
		self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
		self.score = 0
		self.lines = 0
		self.paused = False
		self.game_over = False
		self.bag = []
		self.queue = [self.take_piece() for _ in range(3)]
		self.spawn_piece()
		self.update_stats()
		self.draw()

	def take_piece(self):
		if not self.bag:
			self.bag = list(PIECES)
			random.shuffle(self.bag)
		return self.bag.pop()

	def spawn_piece(self):
		name = self.queue.pop(0)
		self.queue.append(self.take_piece())
		color, shape = PIECES[name]
		self.current = [name, color, [list(row) for row in shape], 3, 0]
		if not self.valid(self.current[2], self.current[3], self.current[4]):
			self.game_over = True

	def valid(self, shape, x, y):
		for row_index, row in enumerate(shape):
			for col_index, filled in enumerate(row):
				if not filled:
					continue
				board_x = x + col_index
				board_y = y + row_index
				if board_x < 0 or board_x >= COLS or board_y >= ROWS:
					return False
				if board_y >= 0 and self.board[board_y][board_x] is not None:
					return False
		return True

	def on_key(self, event):
		key = event.keysym.lower()
		if key == "r":
			self.reset()
			return
		if key == "p" and not self.game_over:
			self.paused = not self.paused
			self.draw()
			return
		if self.paused or self.game_over:
			return

		if key in ("left", "a"):
			self.move(-1, 0)
		elif key in ("right", "d"):
			self.move(1, 0)
		elif key in ("down", "s"):
			if self.move(0, 1):
				self.score += 1
				self.update_stats()
		elif key in ("up", "x"):
			self.rotate()
		elif key == "space":
			self.hard_drop()

	def move(self, dx, dy):
		_, _, shape, x, y = self.current
		if self.valid(shape, x + dx, y + dy):
			self.current[3] += dx
			self.current[4] += dy
			self.draw()
			return True
		if dy:
			self.lock_piece()
		return False

	def rotate(self):
		_, _, shape, x, y = self.current
		rotated = [list(row) for row in zip(*shape[::-1])]
		for offset in (0, -1, 1, -2, 2):
			if self.valid(rotated, x + offset, y):
				self.current[2] = rotated
				self.current[3] += offset
				self.draw()
				return

	def hard_drop(self):
		while self.valid(self.current[2], self.current[3], self.current[4] + 1):
			self.current[4] += 1
			self.score += 2
		self.lock_piece()

	def lock_piece(self):
		_, color, shape, x, y = self.current
		for row_index, row in enumerate(shape):
			for col_index, filled in enumerate(row):
				board_y = y + row_index
				if filled and board_y >= 0:
					self.board[board_y][x + col_index] = color

		remaining = [row for row in self.board if any(cell is None for cell in row)]
		cleared = ROWS - len(remaining)
		self.board = [[None for _ in range(COLS)] for _ in range(cleared)] + remaining
		if cleared:
			self.lines += cleared
			self.score += (0, 100, 300, 500, 800)[cleared] * self.level
			self.update_stats()
		self.spawn_piece()
		self.draw()

	@property
	def level(self):
		return self.lines // 10 + 1

	def update_stats(self):
		self.score_var.set(f"{self.score:06d}")
		self.lines_var.set(str(self.lines))
		self.level_var.set(str(self.level))

	def draw_block(self, x, y, color):
		size = self.cell
		inset = max(2, size // 15)
		left = x * size + inset
		top = y * size + inset
		self.canvas.create_rectangle(
			left,
			top,
			left + size - inset * 2,
			top + size - inset * 2,
			fill=color,
			outline="",
		)
		self.canvas.create_line(left + 2, top + 2, left + size - inset * 2 - 2, top + 2, fill="#ffffff", width=1)

	def draw(self):
		self.canvas.delete("all")
		for row in range(ROWS):
			for col in range(COLS):
				self.canvas.create_rectangle(
					col * self.cell,
					row * self.cell,
					(col + 1) * self.cell,
					(row + 1) * self.cell,
					outline=GRID,
				)
				color = self.board[row][col]
				if color:
					self.draw_block(col, row, color)

		if not self.game_over:
			_, color, shape, x, y = self.current
			ghost_y = y
			while self.valid(shape, x, ghost_y + 1):
				ghost_y += 1
			for row_index, row in enumerate(shape):
				for col_index, filled in enumerate(row):
					if filled:
						self.canvas.create_rectangle(
							(x + col_index) * self.cell + max(3, self.cell // 10),
							(ghost_y + row_index) * self.cell + max(3, self.cell // 10),
							(x + col_index + 1) * self.cell - max(3, self.cell // 10),
							(ghost_y + row_index + 1) * self.cell - max(3, self.cell // 10),
							outline=color,
							dash=(3, 3),
						)
						self.draw_block(x + col_index, y + row_index, color)

		self.draw_preview()
		if self.paused or self.game_over:
			message = "游戏结束\n请按 R 重新开始" if self.game_over else "已暂停\n按 P 继续"
			self.canvas.create_rectangle(
				self.cell,
				self.board_height // 2 - self.cell * 3 // 2,
				self.board_width - self.cell,
				self.board_height // 2 + self.cell * 3 // 2,
				fill=BACKGROUND,
				outline="#50d8c7",
				width=max(1, self.cell // 15),
			)
			self.canvas.create_text(
				self.board_width // 2,
				self.board_height // 2,
				text=message,
				fill=TEXT,
				font=("Microsoft YaHei UI", max(14, self.cell // 2), "bold"),
				justify="center",
			)
		self.status_var.set("游戏结束，按 R 重开" if self.game_over else "P 暂停 / 继续\nR 重新开始")

	def draw_preview(self):
		self.preview.delete("all")
		name = self.queue[0]
		color, shape = PIECES[name]
		cells = [(row, col) for row, values in enumerate(shape) for col, filled in enumerate(values) if filled]
		min_row = min(row for row, _ in cells)
		max_row = max(row for row, _ in cells)
		min_col = min(col for _, col in cells)
		max_col = max(col for _, col in cells)
		size = max(14, self.cell * 3 // 4)
		offset_x = (self.preview_width - (max_col - min_col + 1) * size) // 2
		offset_y = (self.preview_height - (max_row - min_row + 1) * size) // 2
		for row, col in cells:
			left = offset_x + (col - min_col) * size
			top = offset_y + (row - min_row) * size
			self.preview.create_rectangle(left + 2, top + 2, left + size - 2, top + size - 2, fill=color, outline="")

	def tick(self):
		if not self.paused and not self.game_over:
			self.move(0, 1)
		delay = max(90, 550 - (self.level - 1) * 45)
		self.root.after(delay, self.tick)


if __name__ == "__main__":
	window = tk.Tk()
	Tetris(window)
	window.mainloop()