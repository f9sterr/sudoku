
import random
import copy


class SudokuGenerator:

    def __init__(self):
        self.size = 9

    def generate_complete(self):
        # Начинаем с пустого поля
        board = [[0 for _ in range(9)] for _ in range(9)]

        # Заполняем диагональные квадраты 3x3, тк они независимы
        for i in range(0, 9, 3):
            self._fill_box(board, i, i)

        # Заполняем остальные клетки
        self._solve(board)
        return board

    def _fill_box(self, board, row, col):
        nums = list(range(1, 10))
        random.shuffle(nums)
        index = 0
        for i in range(3):
            for j in range(3):
                board[row + i][col + j] = nums[index]
                index += 1

    def _solve(self, board):
        empty = self._find_empty(board)
        if not empty:
            return True
        # Создаём список чисел 1-9 и перемешиваем для случайности
        row, col = empty
        nums = list(range(1, 10))
        random.shuffle(nums)

        for num in nums:
            if self._is_valid(board, num, row, col):
                board[row][col] = num
                if self._solve(board):
                    return True
                board[row][col] = 0
        return False

    def _find_empty(self, board):
        #Находит пустую клетку
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None

    def _is_valid(self, board, num, row, col):
        #Проверяет, можно ли поставить число
        # Проверка строки
        for j in range(9):
            if board[row][j] == num:
                return False

        # Проверка столбца
        for i in range(9):
            if board[i][col] == num:
                return False

        # Проверка квадрата 3x3
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if board[box_row + i][box_col + j] == num:
                    return False

        return True

    def generate_puzzle(self, difficulty):
       #Создаёт головоломку с заданной сложностью.
        # Количество удаляемых клеток
        holes = {
            'easy': 45,
            'medium': 55,
            'hard': 65
        }.get(difficulty, 55)

        # Генерируем полное решение
        solution = self.generate_complete()

        # Создаём копию и удаляем клетки
        puzzle = copy.deepcopy(solution)
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)

        for i in range(holes):
            r, c = cells[i]
            puzzle[r][c] = 0

        return puzzle, solution

    def check_conflict(self, board, row, col, num):
        #Проверяет, есть ли конфликт при размещении числа.
        if num == 0:
            return False

        # Временно убираем текущее значение для проверки
        original = board[row][col]
        board[row][col] = 0

        conflict = not self._is_valid(board, num, row, col)

        board[row][col] = original
        return conflict

    def is_complete(self, board):
        # Проверяем, что нет пустых клеток
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return False

        # Проверяем корректность
        for i in range(9):
            for j in range(9):
                num = board[i][j]
                if self.check_conflict(board, i, j, num):
                    return False
        return True