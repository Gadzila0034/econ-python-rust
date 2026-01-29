import tkinter as tk
from tkinter import ttk, messagebox
import re
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    from rust_stats import group_stats
    RUST_AVAILABLE = True
    print("✅ Rust модуль доступен")
except ImportError:
    RUST_AVAILABLE = False
    print("⚠️ Rust модуль не найден, будет использоваться Python версия")
    # Резервная Python реализация (обновленная для совместимости)

class StatisticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Статистический анализатор")
        self.root.geometry("1600x900")
        
        self.data = []
        self.current_result = None
        
        self.create_layout()
        
    def create_layout(self):
        # 1. Верхний заголовок
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            header,
            text="📊 Анализатор вариационных рядов",
            font=("Arial", 16, "bold")
        ).pack()
        
        # 2. Основной контейнер (левая панель + таблица)
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Левая панель (30% ширины)
        left_panel = ttk.LabelFrame(main_container, text="Управление и ввод", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # ПРАВАЯ ЧАСТЬ - только контейнер
        right_container = ttk.Frame(main_container)
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Создаем панель сумм ТОЛЬКО ОДИН РАЗ
        self.table_top_frame = ttk.LabelFrame(right_container, text="Суммы столбцов", padding="5")
        self.table_top_frame.pack(fill=tk.X, pady=(0, 5))

        # Создаем панель таблицы
        self.table_panel = ttk.LabelFrame(right_container, text="Вариационный ряд", padding="10")
        self.table_panel.pack(fill=tk.BOTH, expand=True)
        
        # 3. Нижняя панель для гистограммы
        self.plot_frame = ttk.LabelFrame(self.root, text="Гистограмма", padding="10")
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Сохраняем ссылки на панели
        self.left_panel = left_panel
        
        # Заполняем панели
        self.fill_left_panel()
        self.fill_table_top()
        self.fill_table_panel()
        
    def fill_left_panel(self):
        """Заполняет левую панель"""
        # Очищаем панель
        for widget in self.left_panel.winfo_children():
            widget.destroy()
        
        # 1. Кнопка загрузки данных (заглушка)
        ttk.Button(
            self.left_panel,
            text="Загрузить данные",
            width=20
        ).pack(pady=5)
        
        # 2. Поле для ввода данных
        ttk.Button(
            self.left_panel,
            text="Вставить данные",
            width=20,
            command=self.open_data_input
        ).pack(pady=5)

        ttk.Button(
            self.left_panel,
            text="Сгенерировать тест",
            width=20,
            command=self.generate_test_data
        ).pack(pady=10)
        
        # Кнопка расчета
        self.calc_button = ttk.Button(
            self.left_panel,
            text="Рассчитать",
            width=20,
            command=self.calculate_statistics
        )
        self.calc_button.pack(pady=20)
        
        # Кнопка для медиан и мод
        self.median_mode_button = ttk.Button(
            self.left_panel,
            text="Медианы и Моды",
            width=20,
            command=self.show_medians_modes
        )
        self.median_mode_button.pack(pady=5)
        
        # 4. Статус Rust
        ttk.Separator(self.left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        rust_status = "✅ Rust модуль доступен" if RUST_AVAILABLE else "⚠️ Python версия"
        ttk.Label(self.left_panel, text=rust_status, 
                 font=("Arial", 9, "italic")).pack()
        
        # 5. Основные статистики
        ttk.Separator(self.left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        stats_label = ttk.Label(
            self.left_panel, 
            text="ОСНОВНЫЕ СТАТИСТИКИ",
            font=("Arial", 11, "bold")
        )
        stats_label.pack(pady=(0, 10))

        self.fill_stats()
        
    def fill_stats(self):
        """Создает и отображает статистики в левой панели"""
        all_stats = [
            ("Среднее (x̄):", "среднее", "---"),
            ("Сумма Ni:", "sum_ni", "---"),
            ("Сумма Xi*Ni:", "sum_xi_ni", "---"),
            ("Сумма |Xi-Xср|*Ni:", "sum_abs", "---"),
            ("Сумма (Xi-Xср)²*Ni:", "sum_squared", "---"),
            ("Сумма (Xi-Xср)³*Ni:", "sum_cubed", "---"),
            ("Сумма (Xi-Xср)⁴*Ni:", "sum_fourth", "---"),
            ("Дисперсия (D):", "дисперсия", "---"),
            ("Стандартное отклонение (σ):", "стандартное_отклонение", "---"),
            ("Среднее линейное отклонение (L):", "среднее_линейное_отклонение", "---"),
            ("Коэффициент вариации (V%):", "коэффициент_вариации", "---"),
            ("Асимметрия (Ka):", "асимметрия", "---"),
            ("Эксцесс (E):", "эксцесс", "---"),
        ]
        
        self.stats_labels = {}

        for label_text, key, default_value in all_stats:
            # Создаем фрейм для одной статистики
            frame = ttk.Frame(self.left_panel)
            frame.pack(fill=tk.X, pady=3, padx=5)

            # Название статистики
            ttk.Label(frame,
                text=label_text, 
                width=30, 
                anchor="w",
                font=("Arial", 9)
            ).pack(side=tk.LEFT)

            # Значение статистики
            value_label = ttk.Label(
                frame, 
                text=default_value, 
                font=("Arial", 9, "bold"),
                foreground="blue"
            )
            value_label.pack(side=tk.LEFT, padx=(10, 0))

            # Сохраняем ссылку на метку значения
            self.stats_labels[key] = value_label
            
        # Добавляем статусную строку
        ttk.Separator(self.left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        self.status_label = ttk.Label(
            self.left_panel, 
            text="Готов к работе",
            font=("Arial", 9)
        )
        self.status_label.pack()
        
    def fill_table_top(self):
        """Создает панель сумм НАД таблицей (вызывается один раз!)"""
        # Очищаем фрейм
        for widget in self.table_top_frame.winfo_children():
            widget.destroy()

        sums_frame = ttk.Frame(self.table_top_frame)
        sums_frame.pack(side=tk.LEFT)

        columns = ["ni", "xi", "si", "xi_ni", "wi", "pi", 
           "abs_dev_ni", "sq_dev_ni", "cub_dev_ni", "fourth_dev_ni"]
        column_names = {
            "ni": "Σni",
            "xi": "Σxi", 
            "si": "Σsi",
            "xi_ni": "Σ(xi·ni)",
            "wi": "Σwi",
            "pi": "Σpi, %",
            "abs_dev_ni": "Σ|xi-x̄|·ni",
            "sq_dev_ni": "Σ(xi-x̄)²·ni",
            "cub_dev_ni": "Σ(xi-x̄)³·ni",
            "fourth_dev_ni": "Σ(xi-x̄)⁴·ni"
        }

        self.sum_labels = {}

        for i, col in enumerate(columns):
            frame = ttk.Frame(sums_frame)
            frame.pack(side=tk.LEFT, padx=15)

            ttk.Label(
                frame, 
                text=column_names[col],
                font=("Arial", 10, "bold")
            ).pack()

            value_label = ttk.Label(
                frame,
                text="0.00",
                font=("Arial", 11, "bold"),
                foreground="darkgreen"
            )
            value_label.pack()
            self.sum_labels[col] = value_label

    def fill_table_panel(self):
        """Заполняет панель таблицы (БЕЗ панели сумм!)"""
        # Очищаем панель
        for widget in self.table_panel.winfo_children():
            widget.destroy()
        
        # Создаем таблицу (Treeview) с прокруткой
        table_container = ttk.Frame(self.table_panel)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("interval", "ni", "xi", "si", "xi_ni", "wi", "pi", 
           "xi_minus_mean", "abs_dev_ni", "sq_dev_ni", "cub_dev_ni", "fourth_dev_ni")
        
        self.table = ttk.Treeview(
            table_container, 
            columns=columns, 
            show="headings", 
            height=15
        )
        
        headings = {
            "interval": "Интервал",
            "ni": "ni",
            "xi": "xi",
            "si": "si",
            "xi_ni": "xi·ni",
            "wi": "wi",
            "pi": "pi, %",
            "xi_minus_mean": "xi-x̄",
            "abs_dev_ni": "|xi-x̄|·ni",
            "sq_dev_ni": "(xi-x̄)²·ni",
            "cub_dev_ni": "(xi-x̄)³·ni",
            "fourth_dev_ni": "(xi-x̄)⁴·ni"
        }

        for col, text in headings.items():
            self.table.heading(col, text=text)
        
        # Настраиваем ширину колонок
        col_config = {
            "interval": {"width": 120, "anchor": "center"},
            "ni": {"width": 60, "anchor": "center"},
            "xi": {"width": 70, "anchor": "center"},
            "si": {"width": 70, "anchor": "center"},
            "xi_ni": {"width": 80, "anchor": "center"},
            "wi": {"width": 70, "anchor": "center"},
            "pi": {"width": 80, "anchor": "center"},
            "xi_minus_mean": {"width": 80, "anchor": "center"},
            "abs_dev_ni": {"width": 90, "anchor": "center"},
            "sq_dev_ni": {"width": 100, "anchor": "center"},
            "cub_dev_ni": {"width": 100, "anchor": "center"},
            "fourth_dev_ni": {"width": 100, "anchor": "center"}
        }
        
        for col, config in col_config.items():
            self.table.column(col, **config)

        
        for col in self.table['columns']:
            self.table.heading(col, anchor='center')
            self.table.column(col, stretch=False)
    
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)

        # Размещаем
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def open_data_input(self):
        """Открывает окно для ввода данных"""
        input_window = tk.Toplevel(self.root)
        input_window.title("Ввод данных")
        input_window.geometry("500x400")
        input_window.transient(self.root)  # Связываем с главным окном

        # Инструкция
        instruction = """Введите числа в любом формате:
        
        • Через запятую: 10, 20, 30
        • Через пробел: 10 20 30
        • С новой строки
        • Десятичные дроби: 72.2 или 72,2
        • С разделителями тысяч: 1,234.56 или 1.234,56

        📋 Можно вставить из буфера обмена: Ctrl+V"""
        
        ttk.Label(input_window, text=instruction, justify=tk.LEFT).pack(pady=10)
        
        # Поле ввода с улучшенной поддержкой
        text_frame = ttk.Frame(input_window)
        text_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Текстовое поле с прокруткой
        text_area = tk.Text(text_frame, height=10, width=50, font=("Courier", 10))
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Улучшенная поддержка Ctrl+V
        def paste_text(event=None):
            try:
                text_area.insert(tk.INSERT, input_window.clipboard_get())
                return "break"  # Предотвращаем стандартное поведение
            except:
                pass
        
        # Привязываем горячие клавиши
        text_area.bind("<Control-v>", paste_text)
        text_area.bind("<Control-V>", paste_text)  # Для Caps Lock
        
        # Пример данных
        text_area.insert("1.0", "100.5, 120.3, 115.8, 130.2, 125.6\n")
        text_area.insert("end", "110.9, 95.7, 105.4, 140.1, 135.0\n")
        text_area.insert("end", "128.7, 118.4, 122.9, 132.5, 127.8\n")
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(input_window)
        button_frame.pack(pady=10)
        
        def process_data():
            """Обрабатывает введенные данные"""
            text = text_area.get("1.0", tk.END).strip()
            numbers = self.parse_numbers_advanced(text)

            if numbers:
                self.data = numbers
                messagebox.showinfo(
                    "Успех", 
                    f"✅ Загружено {len(numbers)} чисел\n"
                    f"📊 Диапазон: [{min(numbers):.2f}, {max(numbers):.2f}]\n"
                    f"📈 Примерное среднее: {sum(numbers)/len(numbers):.2f}"
                )
                input_window.destroy()
                    
                # Обновляем статус
                self.update_status(f"Загружено {len(numbers)} чисел")
            else:
                messagebox.showerror("Ошибка", "Не найдено корректных чисел!")
        
        def clear_field():
            """Очищает поле ввода"""
            text_area.delete("1.0", tk.END)
        
        # Кнопки
        ttk.Button(button_frame, text="📋 Вставить пример", 
                  command=lambda: text_area.insert(tk.END, "72.5, 85.3, 90.1, 88.7, 95.2\n")).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="🗑️ Очистить", 
                  command=clear_field).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="✅ Загрузить", 
                  command=process_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="❌ Отмена", 
                  command=input_window.destroy).pack(side=tk.LEFT, padx=2)
        
        # Фокус на поле ввода
        text_area.focus_set()
        
        # Закрытие по Escape
        input_window.bind("<Escape>", lambda e: input_window.destroy())
        
        # Центрируем окно
        input_window.update_idletasks()
        x = (input_window.winfo_screenwidth() - input_window.winfo_width()) // 2
        y = (input_window.winfo_screenheight() - input_window.winfo_height()) // 2
        input_window.geometry(f"+{x}+{y}")
        
    def parse_numbers_advanced(self, text):
        """Парсит числа из текста с поддержкой разных форматов"""
        numbers = []
        
        # Удаляем комментарии и лишние символы
        text = re.sub(r'[^\d\s,\-+.]', ' ', text)
        
        # Ищем все возможные числовые последовательности
        pattern = r'[-+]?\d{1,3}(?:[,\s.]?\d{3})*(?:[.,]\d+)?'
        
        for match in re.finditer(pattern, text):
            token = match.group().strip()
            
            # Преобразуем в число
            num = self.convert_to_float(token)
            if num is not None:
                numbers.append(num)
        
        return numbers
    
    def convert_to_float(self, token):
        """Конвертирует строку в float, поддерживая разные форматы"""
        token = token.replace(' ', '').replace('\t', '')
        
        if not token:
            return None
        
        # Если есть и точка и запятая
        if ',' in token and '.' in token:
            # Определяем десятичный разделитель по последнему
            if token.rfind(',') > token.rfind('.'):
                normalized = token.replace('.', '').replace(',', '.')
            else:
                normalized = token.replace(',', '')
        elif ',' in token:
            # Только запятые
            if token.count(',') == 1:
                normalized = token.replace(',', '.')
            else:
                # Несколько запятых - предполагаем разделители тысяч
                normalized = token.replace(',', '')
        else:
            normalized = token
        
        try:
            return float(normalized)
        except ValueError:
            return None
            
    def update_status(self, message):
        """Обновляет статус в интерфейсе"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            
    def calculate_statistics(self):
        """Основная функция расчета - вызывает Rust модуль"""
        try:
            # Получаем данные из текстового поля (если было окно ввода)
            if not self.data:
                messagebox.showwarning("Нет данных", "Введите данные для анализа")
                return
            
            # Вызываем Rust модуль
            print(f"📊 Передаем в Rust: {len(self.data)} чисел")
            result = group_stats(self.data)
            
            # Сохраняем результат
            self.current_result = result
            
            # Обновляем все компоненты интерфейса
            self.update_table_with_results()
            self.update_stats_with_results()
            self.update_sums_with_results()
            
            # Обновляем гистограмму
            self.update_histogram(result)
            
            # Обновляем статус
            self.update_status(f"✅ Рассчитано! {len(self.data)} точек")
            
            messagebox.showinfo(
                "Успех!",
                f"📊 Статистики рассчитаны!\n"
                f"📈 Интервалов: {len(result.intervals)}\n"
                f"📐 Среднее: {result.mean:.4f}"
            )
            
        except Exception as e:
            messagebox.showerror("Ошибка расчета", f"Ошибка: {str(e)}")
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            
    def update_table_with_results(self):
        """Обновляет таблицу результатами из Rust"""
        if not self.current_result:
            print("❌ Нет результатов для отображения")
            return
        
        result = self.current_result
        
        # Проверяем наличие необходимых полей
        if not hasattr(result, 'intervals'):
            print("❌ У результата нет поля 'intervals'")
            return
        
        print(f"🔄 Обновляю таблицу: {len(result.intervals)} строк")
        
        # 1. Очищаем старые данные
        for item in self.table.get_children():
            self.table.delete(item)
        
        # 2. Получаем все данные из Rust
        intervals = result.intervals
        ni = result.ni if hasattr(result, 'ni') else [0] * len(intervals)
        xi = result.xi if hasattr(result, 'xi') else [0.0] * len(intervals)
        si = result.si if hasattr(result, 'si') else [0] * len(intervals)
        xi_ni = result.xi_ni if hasattr(result, 'xi_ni') else [0.0] * len(intervals)
        
        # Дополнительные данные из Rust
        xi_minus_mean = result.xi_minus_mean if hasattr(result, 'xi_minus_mean') else [0.0] * len(intervals)
        abs_xi_minus_mean_ni = result.abs_xi_minus_mean_ni if hasattr(result, 'abs_xi_minus_mean_ni') else [0.0] * len(intervals)
        squared_xi_minus_mean_ni = result.squared_xi_minus_mean_ni if hasattr(result, 'squared_xi_minus_mean_ni') else [0.0] * len(intervals)
        cubed_xi_minus_mean_ni = result.cubed_xi_minus_mean_ni if hasattr(result, 'cubed_xi_minus_mean_ni') else [0.0] * len(intervals)
        fourth_power_xi_minus_mean_ni = result.fourth_power_xi_minus_mean_ni if hasattr(result, 'fourth_power_xi_minus_mean_ni') else [0.0] * len(intervals)
        
        # 3. Рассчитываем общее количество данных
        total_n = len(self.data)
        
        # 4. Заполняем таблицу новыми данными
        for i in range(len(intervals)):
            # Проверяем что есть данные для текущей строки
            if i < len(ni) and i < len(xi):
                start, end = intervals[i]
                
                # Рассчитываем относительные частоты (wi и pi)
                wi_value = ni[i] / total_n if total_n > 0 else 0
                pi_value = wi_value * 100  # в процентах
                
                # Получаем значения отклонений из Rust (с проверкой длины)
                xi_minus_mean_val = xi_minus_mean[i] if i < len(xi_minus_mean) else 0
                abs_dev_val = abs_xi_minus_mean_ni[i] if i < len(abs_xi_minus_mean_ni) else 0
                sq_dev_val = squared_xi_minus_mean_ni[i] if i < len(squared_xi_minus_mean_ni) else 0
                cub_dev_val = cubed_xi_minus_mean_ni[i] if i < len(cubed_xi_minus_mean_ni) else 0
                fourth_dev_val = fourth_power_xi_minus_mean_ni[i] if i < len(fourth_power_xi_minus_mean_ni) else 0
                
                # Вставляем строку со ВСЕМИ 12 колонками
                self.table.insert("", "end", values=(
                    f"[{start:.2f}, {end:.2f}]",    # 1. Интервал
                    f"{ni[i]}",                      # 2. ni (частота)
                    f"{xi[i]:.4f}",                  # 3. xi (средняя точка)
                    f"{si[i]}",                      # 4. si (накопленная частота)
                    f"{xi_ni[i]:.4f}",               # 5. xi·ni
                    f"{wi_value:.4f}",               # 6. wi (относительная частота)
                    f"{pi_value:.2f}%",              # 7. pi, % (процентная частота)
                    f"{xi_minus_mean_val:.4f}",      # 8. xi - x̄
                    f"{abs_dev_val:.4f}",            # 9. |xi-x̄|·ni
                    f"{sq_dev_val:.4f}",             # 10. (xi-x̄)²·ni
                    f"{cub_dev_val:.4f}",            # 11. (xi-x̄)³·ni
                    f"{fourth_dev_val:.4f}"          # 12. (xi-x̄)⁴·ni
                ))
        
        print(f"✅ Таблица обновлена: {len(intervals)} строк")
    
    def update_stats_with_results(self):
        """Обновляет статистики результатами из Rust"""
        if not self.current_result:
            print("❌ Нет результатов для статистик")
            return
        
        result = self.current_result
        print("🔄 Обновляю статистики...")
        
        # Сопоставление ключей статистик с полями из Rust
        stats_mapping = {
            "среднее": f"{result.mean:.4f}",
            "sum_ni": f"{result.sum_ni:.0f}",
            "sum_xi_ni": f"{result.sum_xi_ni:.4f}",
            "sum_abs": f"{result.sum_abs:.4f}",
            "sum_squared": f"{result.sum_squared:.4f}",
            "sum_cubed": f"{result.sum_cubed:.4f}",
            "sum_fourth": f"{result.sum_fourth:.4f}",
            "дисперсия": f"{result.variance:.4f}",
            "стандартное_отклонение": f"{result.std:.4f}",
            "среднее_линейное_отклонение": f"{result.mean_linear_dev:.4f}",
            "коэффициент_вариации": f"{result.variation_coef:.2f}%",
            "асимметрия": f"{result.asymmetry:.4f}",
            "эксцесс": f"{result.excess:.4f}",
        }
        
        # Обновляем каждую статистику
        updated_count = 0
        for key, value in stats_mapping.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=value)
                updated_count += 1
        
        print(f"✅ Обновлено {updated_count} статистик")
        
    def update_sums_with_results(self):
        """Обновляет суммы столбцов над таблицей"""
        if not self.current_result:
            print("❌ Нет результатов для сумм")
            return
        
        result = self.current_result
        print("🔄 Обновляю суммы...")
        
        # Проверяем что self.sum_labels существует
        if not hasattr(self, 'sum_labels') or not self.sum_labels:
            print("⚠️ sum_labels не инициализированы")
            return
        
        # Получаем xi и вычисляем сумму
        xi_sum = sum(result.xi) if hasattr(result, 'xi') and result.xi else 0.0
        
        # Получаем последнее значение si (общую сумму)
        si_total = result.si[-1] if hasattr(result, 'si') and result.si else 0
        
        # Рассчитываем суммы
        sums = {
            "ni": f"{result.sum_ni:.0f}",
            "xi": f"{xi_sum:.4f}",
            "si": f"{si_total}",
            "xi_ni": f"{result.sum_xi_ni:.4f}",
            "wi": "1.0000",  # Σwi всегда = 1
            "pi": "100.00%", # Σpi всегда = 100%
            "abs_dev_ni": f"{result.sum_abs:.4f}",
            "sq_dev_ni": f"{result.sum_squared:.4f}",
            "cub_dev_ni": f"{result.sum_cubed:.4f}",
            "fourth_dev_ni": f"{result.sum_fourth:.4f}"
        }
        
        # Обновляем отображение
        for col, value in sums.items():
            if col in self.sum_labels:
                self.sum_labels[col].config(text=value)
                print(f"  ✅ Σ{col}: {value}")
        
        print(f"✅ Обновлены суммы")
    
    def update_histogram(self, result):
        """Обновляет гистограмму с медианами и модами"""
        try:
            # Очищаем предыдущий график
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            
            # Проверяем наличие данных
            if not hasattr(result, 'intervals') or not hasattr(result, 'frequencies'):
                print("⚠️ Нет данных для гистограммы")
                return
            
            intervals = result.intervals
            frequencies = result.ni if hasattr(result, 'ni') else []
            
            if not intervals or not frequencies:
                print("⚠️ Пустые данные для гистограммы")
                return
            
            # Создаем новый график
            fig = Figure(figsize=(10, 5))
            ax = fig.add_subplot(111)
            
            # Преобразуем интервалы для matplotlib
            bins = [intervals[0][0]] + [upper for (_, upper) in intervals]
            
            # Создаем данные для гистограммы
            all_data = []
            midpoints = []
            for i, ((start, end)) in enumerate(intervals):
                if i < len(frequencies):
                    # Добавляем средние точки интервалов с учетом частоты
                    midpoint = (start + end) / 2
                    all_data.extend([midpoint] * frequencies[i])
                    midpoints.append(midpoint)
            
            if not all_data:
                print("⚠️ Нет данных для построения гистограммы")
                return
            
            # Гистограмма
            ax.hist(all_data, bins=bins, edgecolor='black', alpha=0.7, 
                   label=f'Частота (N={sum(frequencies)})', color='skyblue')
            
            # Добавляем медианы
            if hasattr(result, 'medians') and result.medians:
                medians = result.medians
                for i, median in enumerate(medians):
                    if i < len(frequencies):
                        # Рисуем вертикальную линию для медианы
                        ax.axvline(x=median, color='red', linestyle='--', 
                                 alpha=0.6, label='Медиана' if i == 0 else '')
            
            # Добавляем моды
            if hasattr(result, 'modes') and result.modes:
                modes = result.modes
                for i, mode in enumerate(modes):
                    if i < len(frequencies):
                        # Рисуем вертикальную линию для моды
                        ax.axvline(x=mode, color='green', linestyle=':', 
                                 alpha=0.6, label='Мода' if i == 0 else '')
            
            ax.set_xlabel('Значения')
            ax.set_ylabel('Частота')
            ax.set_title('Гистограмма распределения с медианами и модами')
            
            # Убираем дублирование легенды
            handles, labels = ax.get_legend_handles_labels()
            unique_labels = []
            unique_handles = []
            for handle, label in zip(handles, labels):
                if label not in unique_labels:
                    unique_labels.append(label)
                    unique_handles.append(handle)
            
            if unique_labels:
                ax.legend(unique_handles, unique_labels)
            
            ax.grid(True, alpha=0.3)
            
            # Встраиваем в Tkinter
            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Добавляем подпись
            stats_text = f"Среднее: {result.mean:.2f} | σ: {result.std:.2f} | N: {len(self.data)}"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            print("✅ Гистограмма построена")
            
        except Exception as e:
            print(f"❌ Ошибка при построении гистограммы: {e}")
            import traceback
            traceback.print_exc()
    
    def show_medians_modes(self):
        """Показывает медианы и моды (если есть результат)"""
        if not self.current_result:
            messagebox.showinfo("Нет данных", 
                               "Сначала выполните расчет, нажав кнопку 'Рассчитать'")
            return
        
        try:
            # Создаем новое окно
            mm_window = tk.Toplevel(self.root)
            mm_window.title("Медианы и Моды")
            mm_window.geometry("600x400")
            
            # Создаем Notebook для вкладок
            notebook = ttk.Notebook(mm_window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Вкладка медиан
            median_frame = ttk.Frame(notebook)
            notebook.add(median_frame, text="Медианы по интервалам")
            
            # Таблица для медиан
            median_tree = ttk.Treeview(median_frame, 
                                     columns=('interval', 'midpoint', 'median'), 
                                     show='headings', height=15)
            
            median_tree.heading('interval', text='Интервал')
            median_tree.heading('midpoint', text='Середина (xi)')
            median_tree.heading('median', text='Медиана')
            
            median_tree.column('interval', width=200)
            median_tree.column('midpoint', width=150)
            median_tree.column('median', width=150)
            
            # Заполняем данными
            result = self.current_result
            intervals = result.intervals
            medians = result.medians if hasattr(result, 'medians') else []
            xi = result.xi if hasattr(result, 'xi') else []
            
            for i in range(min(len(intervals), len(medians), len(xi))):
                start, end = intervals[i]
                interval_str = f"{start:.2f} - {end:.2f}"
                midpoint_val = xi[i] if i < len(xi) else (start + end) / 2
                median_val = medians[i]
                
                median_tree.insert('', 'end', 
                                 values=(interval_str, 
                                         f"{midpoint_val:.4f}", 
                                         f"{median_val:.4f}"))
            
            scrollbar = ttk.Scrollbar(median_frame, orient="vertical", 
                                     command=median_tree.yview)
            median_tree.configure(yscrollcommand=scrollbar.set)
            
            median_tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Вкладка мод
            mode_frame = ttk.Frame(notebook)
            notebook.add(mode_frame, text="Моды по интервалам")
            
            # Таблица для мод
            mode_tree = ttk.Treeview(mode_frame, 
                                   columns=('interval', 'midpoint', 'mode'), 
                                   show='headings', height=15)
            
            mode_tree.heading('interval', text='Интервал')
            mode_tree.heading('midpoint', text='Середина (xi)')
            mode_tree.heading('mode', text='Мода')
            
            mode_tree.column('interval', width=200)
            mode_tree.column('midpoint', width=150)
            mode_tree.column('mode', width=150)
            
            # Заполняем данными
            modes = result.modes if hasattr(result, 'modes') else []
            
            for i in range(min(len(intervals), len(modes), len(xi))):
                start, end = intervals[i]
                interval_str = f"{start:.2f} - {end:.2f}"
                midpoint_val = xi[i] if i < len(xi) else (start + end) / 2
                mode_val = modes[i]
                
                mode_tree.insert('', 'end', 
                               values=(interval_str, 
                                       f"{midpoint_val:.4f}", 
                                       f"{mode_val:.4f}"))
            
            scrollbar2 = ttk.Scrollbar(mode_frame, orient="vertical", 
                                      command=mode_tree.yview)
            mode_tree.configure(yscrollcommand=scrollbar2.set)
            
            mode_tree.pack(side='left', fill='both', expand=True)
            scrollbar2.pack(side='right', fill='y')
            
            # Кнопка закрытия
            close_btn = ttk.Button(mm_window, text="Закрыть", 
                                  command=mm_window.destroy)
            close_btn.pack(pady=10)
            
            # Общая информация
            info_frame = ttk.Frame(mm_window)
            info_frame.pack(fill='x', padx=10, pady=5)
            
            if hasattr(result, 'mean') and hasattr(result, 'std'):
                ttk.Label(info_frame, 
                         text=f"Среднее: {result.mean:.4f} | Стандартное отклонение: {result.std:.4f} | N: {len(self.data)}",
                         font=("Arial", 9, "italic")).pack()
            
            print("✅ Окно медиан и мод открыто")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть медианы и моды: {str(e)}")
            print(f"❌ Ошибка при открытии окна медиан и мод: {e}")
    
    def generate_test_data(self):
        """Генерирует тестовые данные для проверки"""
        self.data = []
        for _ in range(100000):
            # Нормальное распределение
            value = random.normalvariate(100, 20)
            # Ограничиваем диапазон 50-150
            value = max(50, min(150, value))
            # Округляем до 1 знака после запятой
            self.data.append(round(value, 1))
        
        # Обновляем статус
        self.update_status(f"Сгенерировано {len(self.data)} чисел")
        
        # Показываем информацию о данных
        messagebox.showinfo(
            "Тестовые данные сгенерированы",
            f"✅ Сгенерировано {len(self.data)} чисел\n"
            f"📊 Диапазон: [{min(self.data):.1f}, {max(self.data):.1f}]\n"
            f"📈 Среднее: {sum(self.data)/len(self.data):.2f}\n"
            f"📐 Стандартное отклонение: ~20"
        )
        
        print(f"📊 Сгенерировано {len(self.data)} тестовых чисел")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = StatisticsApp(root)
    root.mainloop()