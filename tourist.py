import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

# ==========================================
# 1. ОБЪЕКТНО-ОРИЕНТИРОВАННЫЕ КЛАССЫ (ООП)
# ==========================================

class Attraction:
    def __init__(self, name, category, address, rating, latitude, longitude):
        self.name = name
        self.category = category
        self.address = address
        self.rating = float(rating)
        self.latitude = float(latitude)    # Географическая широта
        self.longitude = float(longitude)  # Географическая долгота

class Route:
    def __init__(self, route_id, name, distance, complexity, route_type, cost, duration):
        self.route_id = route_id
        self.name = name
        self.distance = float(distance)
        self.complexity = complexity
        self.route_type = route_type
        self.cost = float(cost)
        self.duration = float(duration)
        self.attractions = []

    def add_attraction(self, attraction):
        self.attractions.append(attraction)

    def get_average_rating(self):
        if not self.attractions:
            return 0.0
        return round(sum(a.rating for a in self.attractions) / len(self.attractions), 1)


# ==========================================
# 2. ПРОДВИНУТЫЙ МЕНЕДЖЕР БАЗЫ ДАННЫХ (СУБД)
# ==========================================

class DataManager:
    def __init__(self, db_name="travel_directory.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Создание реляционных таблиц с поддержкой ГЕО-координат"""
        db_exists = os.path.exists(self.db_name)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if not db_exists:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    distance REAL,
                    complexity TEXT,
                    route_type TEXT,
                    cost REAL,
                    duration REAL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_id INTEGER,
                    name TEXT NOT NULL,
                    category TEXT,
                    address TEXT,
                    rating REAL,
                    latitude REAL,
                    longitude REAL,
                    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
                )
            ''')

            # 12 туристических маршрутов
            sample_routes = [
                ("Историческая Москва", 5.5, "Легкий", "Пеший", 500, 3.0),
                ("Тайны Кремля и Оружейная палата", 3.0, "Легкий", "Пеший", 1200, 2.5),
                ("Парки и царские усадьбы Юга", 12.0, "Средний", "Автобусный", 300, 5.0),
                ("Мистические улочки Булгакова", 4.5, "Средний", "Пеший", 600, 3.5),
                ("Архитектурный модерн столицы", 6.0, "Легкий", "Автобусный", 450, 4.0),
                ("Живописное Подмосковье", 25.0, "Сложный", "Автобусный", 900, 8.0),
                ("Литературное Переделкино", 8.0, "Средний", "Автобусный", 700, 4.5),
                ("Огни ночного мегаполиса", 30.0, "Легкий", "Автобусный", 1500, 3.0),
                ("Арт-кластеры и дизайн-заводы", 7.0, "Средний", "Пеший", 200, 4.0),
                ("Круиз по Москве-реке", 15.0, "Легкий", "Водный", 1100, 2.0),
                ("Серебряный Бор и каналы", 10.0, "Средний", "Водный", 850, 3.0),
                ("Тайны протоки водохранилищ", 18.0, "Сложный", "Водный", 1600, 5.0)
            ]
            cursor.executemany(
                "INSERT INTO routes (name, distance, complexity, route_type, cost, duration) VALUES (?, ?, ?, ?, ?, ?)", 
                sample_routes
            )
            
            # Реальные географические координаты объектов в Москве для карт
            sample_attractions = [
                (1, "Красная Площадь", "Музей", "ул. Красная Площадь", 5.0, 55.7539, 37.6208),
                (1, "Храм Василия Блаженного", "Архитектура", "ул. Красная Площадь, 7", 4.8, 55.7525, 37.6231),
                (1, "ГУМ", "Архитектура", "Красная площадь, 3", 4.5, 55.7548, 37.6216),
                (2, "Оружейная палата", "Музей", "Территория Кремля", 4.9, 55.7495, 37.6133),
                (2, "Александровский сад", "Парк", "у стен Кремля", 4.7, 55.7521, 37.6146),
                (2, "Колокольня Ивана Великого", "Архитектура", "Кремль", 4.6, 55.7508, 37.6181),
                (3, "Усадьба Царицыно", "Парк", "Дольская ул., 1", 4.9, 55.6152, 37.6821),
                (3, "Усадьба Коломенское", "Парк", "пр-т Андропова, 39", 4.6, 55.6669, 37.6642),
                (4, "Нехорошая квартира", "Музей", "Большая Садовая, 10", 4.8, 55.7669, 37.5944),
                (4, "Патриаршие пруды", "Парк", "Большой Патриарший пер.", 4.5, 55.7648, 37.5925),
                (5, "Особняк Рябушинского", "Архитектура", "Малая Никитская, 6", 4.7, 55.7594, 37.5966),
                (5, "Дом Мельникова", "Архитектура", "Кривоарбатский пер., 10", 4.9, 55.7499, 37.5897),
                (6, "Лосиный Остров", "Природа", "Поперечный просек", 4.4, 55.8263, 37.7922),
                (7, "Дом-музей Пастернака", "Музей", "Переделкино, ул. Павленко, 3", 4.8, 55.6601, 37.3315),
                (7, "Музей Чуковского", "Музей", "Переделкино, ул. Серафимовича", 4.7, 55.6585, 37.3328),
                (8, "Смотровая Воробьевы горы", "Природа", "Университетская площадь", 4.9, 55.7093, 37.5423),
                (8, "Москва-Сити", "Архитектура", "Пресненская наб.", 4.6, 55.7472, 37.5393),
                (9, "Винзавод", "Галерея", "4-й Сыромятнический пер.", 4.5, 55.7569, 37.6622),
                (9, "Флакон", "Галерея", "Большая Новодмитровская, 36", 4.4, 55.8052, 37.5847),
                (10, "Парк Горького (Причал)", "Парк", "Крымский Вал, 9", 4.8, 55.7294, 37.6011),
                (10, "Нескучный сад", "Парк", "Ленинский проспект, 30", 4.7, 55.7172, 37.5889),
                (11, "Живописный мост", "Архитектура", "проспект Маршала Жукова", 4.8, 55.7777, 37.4444),
                (12, "Клязьминское водохранилище", "Природа", "МО, Мытищинский р-н", 4.5, 55.9811, 37.6322)
            ]
            cursor.executemany(
                "INSERT INTO attractions (route_id, name, category, address, rating, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                sample_attractions
            )
            conn.commit()
        conn.close()

    def load_data(self):
        routes_list = []
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, distance, complexity, route_type, cost, duration FROM routes")
        for r_id, name, dist, comp, r_type, cost, dur in cursor.fetchall():
            route_obj = Route(r_id, name, dist, comp, r_type, cost, dur)
            
            cursor.execute("SELECT name, category, address, rating, latitude, longitude FROM attractions WHERE route_id=?", (r_id,))
            for a_name, cat, addr, rat, lat, lon in cursor.fetchall():
                route_obj.add_attraction(Attraction(a_name, cat, addr, rat, lat, lon))
                
            routes_list.append(route_obj)
            
        conn.close()
        return routes_list

    def add_new_route(self, name, distance, complexity, route_type, cost, duration):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO routes (name, distance, complexity, route_type, cost, duration) VALUES (?, ?, ?, ?, ?, ?)",
            (name, distance, complexity, route_type, cost, duration)
        )
        conn.commit()
        conn.close()


# ==========================================
# 3. ЭКСПЕРТНЫЙ ИНТЕРФЕЙС УПРАВЛЕНИЯ (GUI)
# ==========================================

class GUIController:
    def __init__(self, root, data_manager):
        self.root = root
        self.dm = data_manager
        self.root.title("Информационная система: Справочник туристических маршрутов")
        self.root.geometry("1150x600")
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # ------------------ ВЕРХНЯЯ ПАНЕЛЬ ФИЛЬТРОВ ------------------
        filter_frame = ttk.LabelFrame(self.root, text=" Панель фильтрации и сортировки записей ", padding=10)
        filter_frame.pack(fill="x", padx=15, pady=5, side="top")

        ttk.Label(filter_frame, text="Сложность:").grid(row=0, column=0, padx=5, sticky="w")
        self.combo_complexity = ttk.Combobox(filter_frame, values=["Все", "Легкий", "Средний", "Сложный"], state="readonly", width=10)
        self.combo_complexity.set("Все")
        self.combo_complexity.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=2, padx=5, sticky="w")
        self.combo_type = ttk.Combobox(filter_frame, values=["Все", "Пеший", "Автобусный", "Водный"], state="readonly", width=12)
        self.combo_type.set("Все")
        self.combo_type.grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="Макс. цена (руб):").grid(row=0, column=4, padx=5, sticky="w")
        self.entry_price = ttk.Entry(filter_frame, width=10)
        self.entry_price.grid(row=0, column=5, padx=5)

        ttk.Label(filter_frame, text="Сортировать по:").grid(row=0, column=6, padx=10, sticky="w")
        self.combo_sort = ttk.Combobox(filter_frame, values=["Без сортировки", "Цена (Возр.)", "Цена (Убыв.)", "Высокий рейтинг"], state="readonly", width=16)
        self.combo_sort.set("Без сортировки")
        self.combo_sort.grid(row=0, column=7, padx=5)

        ttk.Button(filter_frame, text="Применить", command=self.apply_filters).grid(row=0, column=8, padx=10)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).grid(row=0, column=9, padx=5)

        # ------------------ ЦЕНТРАЛЬНАЯ ТАБЛИЦА ------------------
        table_frame = ttk.Frame(self.root, padding=15)
        table_frame.pack(fill="both", expand=True)

        columns = ("name", "distance", "complexity", "type", "cost", "duration", "rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="Название туристического маршрута")
        self.tree.heading("distance", text="Дистанция (км)")
        self.tree.heading("complexity", text="Сложность")
        self.tree.heading("type", text="Тип пути")
        self.tree.heading("cost", text="Цена (руб)")
        self.tree.heading("duration", text="Время (ч)")
        self.tree.heading("rating", text="Рейтинг")

        self.tree.column("name", width=250, anchor="w")
        self.tree.column("distance", width=100, anchor="center")
        self.tree.column("complexity", width=100, anchor="center")
        self.tree.column("type", width=110, anchor="center")
        self.tree.column("cost", width=90, anchor="center")
        self.tree.column("duration", width=90, anchor="center")
        self.tree.column("rating", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self.open_detail_window)

        # ------------------ НИЖНЯЯ ПАНЕЛЬ ДЕЙСТВИЙ ------------------
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill="x", side="bottom")

        ttk.Button(bottom_frame, text="➕ Добавить новый маршрут", command=self.open_add_route_window).pack(side="left", padx=5)
        
        # НАШ НОВЫЙ БОНУСНЫЙ БУТТОН КАРТЫ:
        ttk.Button(bottom_frame, text="🗺️ Показать маршрут на карте", command=self.open_map_window).pack(side="left", padx=10)
        
        ttk.Button(bottom_frame, text="📊 Сформировать аналитический отчет", command=self.draw_advanced_charts).pack(side="right", padx=10)
        ttk.Label(bottom_frame, text="💡 Совет: Выберите строку и нажмите кнопку карты для вывода GPS пути", font=("Arial", 9, "italic")).pack(side="left", padx=10)

    def refresh_table(self, data_list=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        routes_to_show = data_list if data_list is not None else self.dm.load_data()
        for r in routes_to_show:
            self.tree.insert("", "end", values=(
                r.name, r.distance, r.complexity, r.route_type, r.cost, r.duration, r.get_average_rating()
            ))

    def apply_filters(self):
        all_routes = self.dm.load_data()
        filtered = []
        comp_crit = self.combo_complexity.get()
        type_crit = self.combo_type.get()
        price_crit = self.entry_price.get().strip()
        sort_crit = self.combo_sort.get()

        max_price = float('inf')
        if price_crit:
            try:
                max_price = float(price_crit)
                if max_price < 0: raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Стоимость должна быть положительным числом!")
                return

        for r in all_routes:
            if comp_crit != "Все" and r.complexity != comp_crit: continue
            if type_crit != "Все" and r.route_type != type_crit: continue
            if r.cost > max_price: continue
            filtered.append(r)

        if sort_crit == "Цена (Возр.)": filtered.sort(key=lambda x: x.cost)
        elif sort_crit == "Цена (Убыв.)": filtered.sort(key=lambda x: x.cost, reverse=True)
        elif sort_crit == "Высокий рейтинг": filtered.sort(key=lambda x: x.get_average_rating(), reverse=True)
            
        self.refresh_table(filtered)

    def reset_filters(self):
        self.combo_complexity.set("Все")
        self.combo_type.set("Все")
        self.combo_sort.set("Без сортировки")
        self.entry_price.delete(0, tk.END)
        self.refresh_table()

    # ------------------ ИНТЕГРАЦИЯ ИНТЕРАКТИВНОЙ КАРТЫ GPS ------------------
    def open_map_window(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите маршрут из таблицы, чтобы увидеть его на карте!")
            return
            
        values = self.tree.item(selected_item, "values")
        route_name = values[0]
        
        all_routes = self.dm.load_data()
        selected_route = next((r for r in all_routes if r.name == route_name), None)
        
        if not selected_route or not selected_route.attractions:
            messagebox.showinfo("Информация", "Для этого маршрута пока нет точек с GPS координатами.")
            return

        # Импортируем карту
        import tkintermapview

        # Создаем дочернее модальное окно для карты
        map_win = tk.Toplevel(self.root)
        map_win.title(f"Географическая карта: {selected_route.name}")
        map_win.geometry("850x600")
        map_win.transient(self.root)
        map_win.grab_set()

        # Инициализируем виджет карты на весь экран окна
        map_widget = tkintermapview.TkinterMapView(map_win, width=850, height=600, corner_radius=0)
        map_widget.pack(fill="both", expand=True)

        # Вычисляем среднюю координату центра для автоматической фокусировки камеры
        avg_lat = sum(a.latitude for a in selected_route.attractions) / len(selected_route.attractions)
        avg_lon = sum(a.longitude for a in selected_route.attractions) / len(selected_route.attractions)
        
        map_widget.set_position(avg_lat, avg_lon)
        map_widget.set_zoom(13) # Оптимальный городской масштаб zoom

        # Цикл расстановки маркеров и сохранения координат для трека пути
        path_coordinates = []
        for i, attr in enumerate(selected_route.attractions, start=1):
            map_widget.set_marker(
                attr.latitude, 
                attr.longitude, 
                text=f"{i}. {attr.name} [{attr.category}]"
            )
            path_coordinates.append((attr.latitude, attr.longitude))
            
        # Если точек больше 1, автоматически рисуем соединительную линию трека (маршрутную линию)
        if len(path_coordinates) > 1:
            map_widget.set_path(path_coordinates, color="#1f77b4", width=3)

    # ------------------ ОКНО ДЕТАЛИЗАЦИИ ОБЪЕКТА ------------------
    def open_detail_window(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        values = self.tree.item(selected_item, "values")
        route_name = values[0]
        
        all_routes = self.dm.load_data()
        selected_route = next((r for r in all_routes if r.name == route_name), None)
        if not selected_route: return

        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"Детали маршрута: {selected_route.name}")
        detail_win.geometry("600x400")
        detail_win.transient(self.root)
        detail_win.grab_set()

        info_txt = f"Маршрут: {selected_route.name}\n" \
                   f"Тип: {selected_route.route_type} | Сложность: {selected_route.complexity}\n" \
                   f"Протяженность: {selected_route.distance} км | Длительность: {selected_route.duration} ч.\n" \
                   f"Базовая стоимость: {selected_route.cost} руб."
        
        tk.Label(detail_win, text=info_txt, justify="left", font=("Arial", 10, "bold"), pady=10).pack(anchor="w", padx=15)
        
        sub_columns = ("name", "cat", "rating", "addr")
        sub_tree = ttk.Treeview(detail_win, columns=sub_columns, show="headings", height=8)
        sub_tree.heading("name", text="Локация")
        sub_tree.heading("cat", text="Категория")
        sub_tree.heading("rating", text="Рейтинг")
        sub_tree.heading("addr", text="Адрес")
        
        sub_tree.column("name", width=150)
        sub_tree.column("cat", width=100, anchor="center")
        sub_tree.column("rating", width=60, anchor="center")
        sub_tree.column("addr", width=240)
        sub_tree.pack(fill="both", expand=True, padx=15, pady=10)

        for a in selected_route.attractions:
            sub_tree.insert("", "end", values=(a.name, a.category, a.rating, a.address))

    # ------------------ ФОРМА ДОБАВЛЕНИЯ ЗАПИСИ (CRUD) ------------------
    def open_add_route_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Добавление новой записи")
        add_win.geometry("400x350")
        add_win.resizable(False, False)
        add_win.transient(self.root)
        add_win.grab_set()

        fields = ["Название:", "Дистанция (км):", "Цена (руб):", "Длительность (часы):"]
        entries = {}
        for idx, text in enumerate(fields):
            tk.Label(add_win, text=text).grid(row=idx, column=0, padx=15, pady=10, sticky="e")
            entry = ttk.Entry(add_win, width=25)
            entry.grid(row=idx, column=1, padx=10, pady=10)
            entries[text] = entry

        tk.Label(add_win, text="Сложность:").grid(row=4, column=0, padx=15, pady=10, sticky="e")
        combo_comp = ttk.Combobox(add_win, values=["Легкий", "Средний", "Сложный"], state="readonly", width=22)
        combo_comp.set("Легкий")
        combo_comp.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(add_win, text="Тип пути:").grid(row=5, column=0, padx=15, pady=10, sticky="e")
        combo_t = ttk.Combobox(add_win, values=["Пеший", "Автобусный", "Водный"], state="readonly", width=22)
        combo_t.set("Пеший")
        combo_t.grid(row=5, column=1, padx=10, pady=10)

        def save_action():
            name = entries["Название:"].get().strip()
            dist = entries["Дистанция (км):"].get().strip()
            price = entries["Цена (руб):"].get().strip()
            dur = entries["Длительность (часы):"].get().strip()

            if not name or not dist or not price or not dur:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            try:
                d_val = float(dist)
                p_val = float(price)
                dur_val = float(dur)
                if d_val <= 0 or p_val < 0 or dur_val <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Числовые параметры введены неверно!")
                return

            self.dm.add_new_route(name, d_val, combo_comp.get(), combo_t.get(), p_val, dur_val)
            messagebox.showinfo("Успех", "Маршрут добавлен в СУБД!")
            add_win.destroy()
            self.refresh_table()

        ttk.Button(add_win, text="💾 Сохранить в СУБД", command=save_action).grid(row=6, column=0, columnspan=2, pady=20)

    # ------------------ ВИЗУАЛИЗАЦИЯ MATPLOTLIB ------------------
    def draw_advanced_charts(self):
        routes = self.dm.load_data()
        if not routes: return

        names = [r.name[:15] + "..." if len(r.name) > 15 else r.name for r in routes]
        costs = [r.cost for r in routes]

        types_count = {"Пеший": 0, "Автобусный": 0, "Водный": 0}
        for r in routes:
            if r.route_type in types_count: types_count[r.route_type] += 1

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        ax1.barh(names, costs, color='#4ba3a5', edgecolor='black')
        ax1.set_xlabel('Стоимость экскурсии (руб.)')
        ax1.set_title('Анализ цен по каталогу маршрутов', fontweight='bold')
        ax1.invert_yaxis()
        ax1.grid(axis='x', linestyle='--', alpha=0.7)

        labels = list(types_count.keys())
        sizes = list(types_count.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops={'edgecolor': 'black'})
        ax2.set_title('Структура видов экскурсионного передвижения', fontweight='bold')

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    manager = DataManager()
    root = tk.Tk()
    app = GUIController(root, manager)
    root.mainloop()