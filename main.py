import tkinter as tk
from sudoku_game import SudokuGame

if __name__ == "__main__":
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop()
