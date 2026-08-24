import tkinter as tk
from tkinter import messagebox
import json
import time
import os
from sudoku_generator import SudokuGenerator


class SudokuGame:
    # Основной класс игры с графическим интерфейсом

    def __init__(self, root):
        self.root = root
        self.root.title("Судоку")
        self.root.configure(bg='#F5F3EF')  # Спокойный бежевый фон

        # Игровые данные
        self.generator = SudokuGenerator()
        self.puzzle = []  # Головоломка (с нулями на месте пропусков)
        self.solution = []  # Правильное решение (полное поле)
        self.board = []  # Текущее состояние доски (меняется игроком)
        self.fixed_cells = set()  # Клетки, которые нельзя менять (исходные)

        self.selected_row = None
        self.selected_col = None
        self.difficulty = "medium"

        # Таймер
        self.timer_running = False
        self.start_time = None
        self.timer_id = None

        # Интерфейс
        self.cell_size = 50  # Размер одной клетки в пикселях

        self._create_widgets()
        self.new_game()

    def _create_widgets(self):
        # Создаёт все элементы интерфейса (кнопки, метки, поле)
        # Верхняя панель с таймером и кнопками
        top_frame = tk.Frame(self.root, bg='#F5F3EF')
        top_frame.pack(pady=10)

        # Таймер
        self.timer_label = tk.Label(
            top_frame, text="00:00", font=('Helvetica', 14),
            bg='#F5F3EF', fg='#7F8C8D'
        )
        self.timer_label.pack(side=tk.LEFT, padx=20)

        # Кнопка новой игры
        new_btn = tk.Button(
            top_frame, text="Новая игра", font=('Helvetica', 10),
            bg='#B0BEC5', fg='white', relief=tk.FLAT,
            padx=15, pady=5, command=self.new_game
        )
        new_btn.pack(side=tk.LEFT, padx=5)

        # Выпадающее меню выбора сложности
        self.difficulty_var = tk.StringVar(value="Средне")
        difficulty_menu = tk.OptionMenu(
            top_frame, self.difficulty_var,
            "Легко", "Средне", "Сложно",
            command=self.change_difficulty
        )
        difficulty_menu.config(
            bg='#B0BEC5', fg='white', relief=tk.FLAT,
            font=('Helvetica', 10)
        )
        difficulty_menu.pack(side=tk.LEFT, padx=5)

        # Кнопка показа рекордов
        records_btn = tk.Button(
            top_frame, text="Рекорды", font=('Helvetica', 10),
            bg='#A8B5A5', fg='white', relief=tk.FLAT,
            padx=15, pady=5, command=self.show_records
        )
        records_btn.pack(side=tk.LEFT, padx=5)

        # Поле для рисования сетки и цифр
        self.canvas = tk.Canvas(
            self.root, width=450, height=450,
            bg='white', highlightthickness=0
        )
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)  # Обработка кликов

        # Панель счётчиков оставшихся цифр
        counters_frame = tk.Frame(self.root, bg='#F5F3EF')
        counters_frame.pack(pady=5)

        self.counters_label = tk.Label(
            counters_frame, text="", font=('Helvetica', 10),
            bg='#F5F3EF', fg='#2C3E50'
        )
        self.counters_label.pack()

        # Нижняя панель с информационными сообщениями
        bottom_frame = tk.Frame(self.root, bg='#F5F3EF')
        bottom_frame.pack(pady=10)

        self.status_label = tk.Label(
            bottom_frame, text="", font=('Helvetica', 9),
            bg='#F5F3EF', fg='#7F8C8D'
        )
        self.status_label.pack()

        # Привязка клавиатуры (цифры, стрелки, удаление)
        self.root.bind("<Key>", self.on_keypress)

    def show_records(self):
        # Показывает окно с лучшими временами для каждой сложности
        records = self.load_records()

        # Создаём новое окно
        records_window = tk.Toplevel(self.root)
        records_window.title("Лучшие времена")
        records_window.configure(bg='#F5F3EF')
        records_window.resizable(False, False)

        # Центрируем окно относительно главного
        window_width = 300
        window_height = 200
        screen_width = records_window.winfo_screenwidth()
        screen_height = records_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        records_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Заголовок
        title_label = tk.Label(
            records_window, text="Лучшие результаты",
            font=('Helvetica', 12, 'bold'),
            bg='#F5F3EF', fg='#2C3E50'
        )
        title_label.pack(pady=15)

        # Таблица с рекордами
        frame = tk.Frame(records_window, bg='#F5F3EF')
        frame.pack(pady=10)

        # Названия сложностей
        labels = [
            ("Легко:", records.get('easy')),
            ("Средне:", records.get('medium')),
            ("Сложно:", records.get('hard'))
        ]

        for i, (diff_name, time_value) in enumerate(labels):
            # Название сложности
            diff_label = tk.Label(
                frame, text=diff_name, font=('Helvetica', 11),
                bg='#F5F3EF', fg='#2C3E50', width=10, anchor='w'
            )
            diff_label.grid(row=i, column=0, padx=10, pady=5, sticky='w')

            # Время
            if time_value is not None and time_value > 0:
                time_text = self._format_time(time_value)
                time_label = tk.Label(
                    frame, text=time_text, font=('Helvetica', 11),
                    bg='#F5F3EF', fg='#1F618D', width=10, anchor='w'
                )
            else:
                time_label = tk.Label(
                    frame, text="---", font=('Helvetica', 11),
                    bg='#F5F3EF', fg='#7F8C8D', width=10, anchor='w'
                )
            time_label.grid(row=i, column=1, padx=10, pady=5, sticky='w')

        # Кнопка закрытия
        close_btn = tk.Button(
            records_window, text="Закрыть", font=('Helvetica', 10),
            bg='#B0BEC5', fg='white', relief=tk.FLAT,
            padx=20, pady=5, command=records_window.destroy
        )
        close_btn.pack(pady=15)

    def load_records(self):
        # Загружает рекорды из JSON файла
        filename = "sudoku_records.json"
        default_records = {'easy': None, 'medium': None, 'hard': None}

        # Проверка на наличие файла
        if not os.path.exists(filename):
            return default_records

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                records = json.load(f)
                # Проверяем, что все ключи есть
                for key in default_records:
                    if key not in records:
                        records[key] = None
                return records
        except (json.JSONDecodeError, IOError):
            return default_records

    def new_game(self):
        # Начинает новую игру с текущей выбранной сложностью
        self.stop_timer()

        diff_map = {"Легко": "easy", "Средне": "medium", "Сложно": "hard"}
        self.difficulty = diff_map[self.difficulty_var.get()]

        # Генерируем головоломку и правильное решение
        self.puzzle, self.solution = self.generator.generate_puzzle(self.difficulty)
        self.board = [row[:] for row in self.puzzle]  # Копируем поле

        # Запоминаем, какие клетки были изначально заполнены (их нельзя менять)
        self.fixed_cells.clear()
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] != 0:
                    self.fixed_cells.add((i, j))

        # Сбрасываем выделение и таймер
        self.selected_row = None
        self.selected_col = None
        self.timer_running = False
        self.start_time = None

        self.update_display()
        self.status_label.config(text="Игра начата! Нажмите на клетку и введите цифру.")

    def change_difficulty(self, _):
        # Изменяет сложность (вызывается при выборе в меню)
        self.new_game()

    def update_display(self):
        # Обновляет отображение поля и счётчиков
        self._draw_board()
        self._update_counters()
        self._check_victory()

    def _is_move_correct(self, row, col, num):
        # Проверяет, соответствует ли введённая цифра правильному решению
        if num == 0:
            return True
        return self.solution[row][col] == num

    def _draw_board(self):
        # Рисует игровое поле: сетку, цифры, цветовую подсветку
        self.canvas.delete("all")

        # Находим все неправильные клетки (несовпадающие с решением)
        errors = self._find_errors()

        # Рисуем каждую клетку
        for i in range(9):
            for j in range(9):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Определяем цвет фона клетки
                if (i, j) == (self.selected_row, self.selected_col):
                    fill = '#E8E0D0'  # Выделенная клетка
                elif (i, j) in errors:
                    fill = '#F1948A'  # Красный фон для неправильных цифр
                else:
                    fill = '#FFFFFF'  # Обычная клетка

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

                # Рисуем цифру, если клетка не пустая
                num = self.board[i][j]
                if num != 0:
                    if (i, j) in self.fixed_cells:
                        color = '#000000'  # Исходные цифры - ЧЁРНЫЕ
                    else:
                        if self._is_move_correct(i, j, num):
                            color = '#27AE60'  # Правильные - ЗЕЛЁНЫЕ
                        else:
                            color = '#E74C3C'  # Неправильные - КРАСНЫЕ

                    self.canvas.create_text(
                        x1 + self.cell_size // 2,
                        y1 + self.cell_size // 2,
                        text=str(num), font=('Helvetica', 18), fill=color
                    )

        # Рисуем линии сетки (утолщённые линии для квадратов 3x3)
        for i in range(10):
            width = 2 if i % 3 == 0 else 1
            x = i * self.cell_size
            y = i * self.cell_size
            self.canvas.create_line(x, 0, x, 450, fill='#D5C8B5', width=width)
            self.canvas.create_line(0, y, 450, y, fill='#D5C8B5', width=width)

    def _find_errors(self):
        # Находит все неправильные клетки (не совпадающие с решением)
        errors = set()

        for i in range(9):
            for j in range(9):
                num = self.board[i][j]
                if num != 0 and (i, j) not in self.fixed_cells:
                    if not self._is_move_correct(i, j, num):
                        errors.add((i, j))

        return errors

    def _update_counters(self):
        # Обновляет счётчики: сколько ещё осталось поставить каждой цифры
        # Считаем, сколько правильных цифр уже стоит (не исходных)
        placed_correct = {num: 0 for num in range(1, 10)}

        for i in range(9):
            for j in range(9):
                num = self.board[i][j]
                if num != 0 and (i, j) not in self.fixed_cells:
                    if self._is_move_correct(i, j, num):
                        placed_correct[num] += 1

        # Сколько всего должно быть каждой цифры (всего 9 штук)
        needed = {num: 9 for num in range(1, 10)}

        # Вычитаем исходные цифры (из головоломки)
        for i in range(9):
            for j in range(9):
                num = self.puzzle[i][j]
                if num != 0:
                    needed[num] -= 1

        # Вычитаем уже правильно поставленные пользователем
        for num in range(1, 10):
            needed[num] -= placed_correct[num]

        # Формируем текст для отображения
        parts = []
        for num in range(1, 10):
            if needed[num] > 0:
                parts.append(f"{num}→{needed[num]}")

        if parts:
            self.counters_label.config(text="Осталось добавить: " + "  ".join(parts))
        else:
            self.counters_label.config(text="Все цифры расставлены правильно!")

    def _check_victory(self):
        # Проверяет, выиграл ли игрок (все клетки заполнены и совпадают с решением)
        complete = True
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0 or self.board[i][j] != self.solution[i][j]:
                    complete = False
                    break
            if not complete:
                break

        if complete:
            self.stop_timer()
            elapsed = self._get_elapsed_time()

            self._save_record(elapsed)

            messagebox.showinfo(
                "Поздравляем!",
                f"Вы решили судоку за {self._format_time(elapsed)}!"
            )
            self.status_label.config(text=f"ПОБЕДА! Время: {self._format_time(elapsed)}")

    def on_click(self, event):
        # Обработка клика мыши по полю: выделяем выбранную клетку
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if 0 <= row < 9 and 0 <= col < 9:
            if (row, col) not in self.fixed_cells:
                self.selected_row = row
                self.selected_col = col
                self.status_label.config(text=f"Выбрана клетка ({row + 1}, {col + 1})")
            else:
                self.selected_row = None
                self.selected_col = None
                self.status_label.config(text="Нельзя изменять исходные цифры")

            self.update_display()

    def on_keypress(self, event):
        # Обработка нажатия клавиш:
        # - Цифры 1-9: попытка поставить цифру (ставится всегда, но цвет меняется)
        # - BackSpace/Delete: удаление цифры
        # - Стрелки: навигация по полю
        if self.selected_row is None or self.selected_col is None:
            return

        if (self.selected_row, self.selected_col) in self.fixed_cells:
            self.status_label.config(text="Нельзя изменять исходные цифры")
            return

        # Запускаем таймер при первом действии
        if not self.timer_running:
            self.start_timer()

        # Обработка ввода цифр 1-9
        if event.char.isdigit() and 1 <= int(event.char) <= 9:
            num = int(event.char)

            # Всегда ставим введённую цифру в клетку
            self.board[self.selected_row][self.selected_col] = num

            # Проверяем, правильная ли цифра
            if self.solution[self.selected_row][self.selected_col] == num:
                self.status_label.config(text=f"Правильно! Цифра {num}")
            else:
                correct_num = self.solution[self.selected_row][self.selected_col]
                self.status_label.config(
                    text=f"Неверно! В этой клетке должна быть цифра {correct_num}"
                )

            self.update_display()

        # Удаление цифры
        elif event.keysym in ('BackSpace', 'Delete'):
            self.board[self.selected_row][self.selected_col] = 0
            self.status_label.config(text="Цифра удалена")
            self.update_display()

        # Навигация стрелками
        elif event.keysym == 'Up' and self.selected_row > 0:
            self.selected_row -= 1
            self.update_display()
        elif event.keysym == 'Down' and self.selected_row < 8:
            self.selected_row += 1
            self.update_display()
        elif event.keysym == 'Left' and self.selected_col > 0:
            self.selected_col -= 1
            self.update_display()
        elif event.keysym == 'Right' and self.selected_col < 8:
            self.selected_col += 1
            self.update_display()

    def start_timer(self):
        # Запускает таймер
        self.timer_running = True
        self.start_time = time.time()
        self._update_timer()

    def stop_timer(self):
        # Останавливает таймер
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def _update_timer(self):
        # Обновляет отображение таймера каждую секунду
        if self.timer_running:
            elapsed = self._get_elapsed_time()
            self.timer_label.config(text=self._format_time(elapsed))
            self.timer_id = self.root.after(1000, self._update_timer)

    def _get_elapsed_time(self):
        # Возвращает прошедшее время в секундах
        if self.start_time is None:
            return 0
        return int(time.time() - self.start_time)

    @staticmethod
    def _format_time(seconds):
        # Форматирует время в формат ММ:СС
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def _save_record(self, elapsed):
        # Сохраняет рекорд времени в JSON файл
        filename = "sudoku_records.json"
        records = {}

        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    records = json.load(f)
            except:
                pass

        best = records.get(self.difficulty)
        if best is None or elapsed < best:
            records[self.difficulty] = elapsed
            with open(filename, 'w') as f:
                json.dump(records, f, indent=2)
            self.status_label.config(
                text=f"Новый рекорд для сложности {self.difficulty_var.get()}!"
            )