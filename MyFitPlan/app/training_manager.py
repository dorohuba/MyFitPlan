import ttkbootstrap as ttk
import sqlite3

class TrainingManager:
    def __init__(self, app):
        self.app = app
        self.current_day = None
        self.day_buttons = []
        self.training_table = None
        self.day_selector_frame = None
        self.delete_day_btn = None
        self.training_frame = None

    def training_page(self):
        """
        Edzésterv oldal megjelenítése.
        Tartalmaz:
        - napválasztó gombokat
        - nap hozzáadása és törlése gombot
        - gyakorlatok táblázatát
        - gyakorlat hozzáadása és törlése gombokat
        """
        self.app.clear_screen()
        self.app.load_navigation_bar()

        button_container = ttk.Frame(self.app.root)
        button_container.place(relx=0.5, rely=0.20, anchor="center", relwidth=0.8)

        self.day_selector_frame = ttk.Frame(button_container)
        self.day_selector_frame.pack(side="left")

        self.delete_day_btn = ttk.Button(button_container,
                                         text="Nap törlése",
                                         style="darkbutton.TButton",
                                         command=self.delete_current_day,
                                         cursor="hand2",
                                         takefocus=False)
        self.delete_day_btn.pack(pady=10, side="right")

        self.app.db_cursor.execute("""SELECT day_name FROM training_days WHERE user_id = ?""",
                                  (self.app.user_id,))
        days = [row[0] for row in self.app.db_cursor.fetchall()]
        
        days.append("+ Új nap")

        self.day_buttons = []
        first_day = None if not days or days[0] == "+ Új nap" else days[0]

        for day in days:
            initial_style = "darkbutton.TButton" if day == "+ Új nap" else (
                "selected.TButton" if day == first_day else "words.TButton")
            
            btn = ttk.Button(self.day_selector_frame,
                             text=day,
                             style=initial_style,
                             command=lambda d=day: self.select_training_day(d) if d != "+ Új nap" else self.add_new_day(),
                             cursor="hand2",
                             takefocus=False)
            btn.pack(side="left", padx=10, pady=10)
            self.day_buttons.append(btn)

        self.training_frame = ttk.Frame(self.app.root,
                                        style="Frameborder.TFrame")
        self.training_frame.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.8, relheight=0.6)

        table_border_frame = ttk.Frame(self.training_frame,
                                       style="Frameborder.TFrame")
        table_border_frame.pack(fill="both", expand=True, padx=2, pady=2)

        columns = ("Gyakorlat", "Sorozat", "Ismétlés", "Súly (kg)", "Kellékek", "Nehézség", "Leírás")

        self.training_table = ttk.Treeview(table_border_frame,
                                           columns=columns,
                                           show="headings",
                                           style="Custom.Treeview")
        
        column_widths = {"Gyakorlat": 150,
                         "Sorozat": 70,
                         "Ismétlés": 70,
                         "Súly (kg)": 70,
                         "Kellékek": 150,
                         "Nehézség": 100,
                         "Leírás": 200}
        
        for col in columns:
            self.training_table.heading(col, text=col, anchor="center")
            self.training_table.column(col, anchor="center", width=column_widths[col])
        
        self.training_table.pack(fill="both", expand=True)

        button_frame = ttk.Frame(self.app.root)
        button_frame.place(relx=0.09, rely=0.87)

        ttk.Button(button_frame, 
                   text="Gyakorlat hozzáadása", 
                   style="darkbutton.TButton",
                   command=self.add_exercise,
                   cursor="hand2",
                   takefocus=False).grid(row=0, column=0, padx=20)

        ttk.Button(button_frame, 
                   text="Gyakorlat törlése", 
                   style="darkbutton.TButton",
                   command=self.delete_exercise,
                   cursor="hand2",
                   takefocus=False).grid(row=0, column=1, padx=20)

        if first_day:
            self.current_day = first_day
            self.load_training_plan(first_day)
        else:
            self.current_day = None

    def add_new_day(self):
        """
        Új edzésnap hozzáadása.
        
        Felugró ablakban bekéri az új nap nevét.
        Korlátozások:
        - Maximum 7 nap hozható létre
        - A nap neve maximum 10 karakter lehet
        - Nem lehet két azonos nevű nap
        
        Az új nap elmentődik az adatbázisba.
        """
        MAX_DAYS = 7
        MAX_CHAR_LENGTH = 10
        
        current_days = len([btn for btn in self.day_buttons if btn['text'] != "+ Új nap"])
        
        if current_days >= MAX_DAYS:
            self.app.custom_messagebox("Hiba", "Maximum 7 napot lehet létrehozni!")
            return

        popup = ttk.Toplevel()
        popup.title("Új nap hozzáadása")
        popup.geometry("400x200")
        
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        ttk.Label(popup, text=f"Nap neve (max {MAX_CHAR_LENGTH} karakter):", 
                 font=("Colibri", 12), style="Custom.TLabel").pack(pady=(20,5))
        
        def validate_length(P):
            return len(P) <= MAX_CHAR_LENGTH

        vcmd = (popup.register(validate_length), '%P')
        day_input = ttk.Entry(popup, 
                             font=("Colibri", 12), 
                             bootstyle="warning", 
                             width=30,
                             validate='key',
                             validatecommand=vcmd)
        day_input.pack(pady=(0,20))

        def save_new_day():
            day_name = day_input.get().strip()
            if not day_name:
                self.app.custom_messagebox("Hiba", "Kérlek, add meg a nap nevét!")
                return

            if len(day_name) > MAX_CHAR_LENGTH:
                self.app.custom_messagebox("Hiba", f"A nap neve nem lehet hosszabb {MAX_CHAR_LENGTH} karakternél!")
                return

            self.app.db_cursor.execute("""SELECT day_name FROM training_days WHERE user_id = ? AND day_name = ?""",
                                      (self.app.user_id, day_name))

            if self.app.db_cursor.fetchone():
                self.app.custom_messagebox("Hiba", "Már létezik ilyen nevű nap!")
                return

            try:
                self.app.db_cursor.execute("""
                    INSERT INTO training_days (user_id, day_name)
                    VALUES (?, ?)
                """, (self.app.user_id, day_name))
                self.app.db_connection.commit()
            except sqlite3.Error:
                self.app.custom_messagebox("Hiba", "Nem sikerült menteni az új napot!")
                return

            for btn in self.day_buttons:
                btn.destroy()
            self.day_buttons.clear()

            self.app.db_cursor.execute("""SELECT day_name FROM training_days WHERE user_id = ? ORDER BY day_name""",
                                      (self.app.user_id,))
            days = [row[0] for row in self.app.db_cursor.fetchall()]
            days.append("+ Új nap")

            for day in days:
                btn = ttk.Button(self.day_selector_frame,
                                 text=day,
                                 style="words.TButton" if day != "+ Új nap" else "darkbutton.TButton",
                                 command=lambda d=day: self.select_training_day(d) if d != "+ Új nap" else self.add_new_day(),
                                 cursor="hand2",
                                 takefocus=False)
                btn.pack(side="left", padx=10, pady=10)
                self.day_buttons.append(btn)
            
            popup.destroy()
            self.select_training_day(day_name)

        ttk.Button(popup,
                   text="Mentés",
                   style="darkbutton.TButton", 
                   command=save_new_day,
                   cursor="hand2",
                   takefocus=False).pack(pady=20)

    def select_training_day(self, day):
        """
        Edzésnap kiválasztása.
        Betölti a kiválasztott nap gyakorlatait.
        A kiválasztott nap gombja narancssárga háttérrel jelenik meg.
        """
        if day == "+ Új nap":
            self.add_new_day()
            return

        for btn in self.day_buttons:
            if btn['text'] != "+ Új nap":
                btn.configure(style="words.TButton")
        
        for btn in self.day_buttons:
            if btn['text'] == day:
                btn.configure(style="selected.TButton")
                break

        self.current_day = day
        self.app.db_cursor.execute(
            "SELECT id FROM training_days WHERE user_id = ? AND day_name = ?",
            (self.app.user_id, day))
        
        self.load_training_plan(day)

    def add_exercise(self):
        """
        Új gyakorlat hozzáadása az aktuális edzésnaphoz.
        - Izomcsoport választás
        - Gyakorlat választás az adatbázisból
        - Sorozat, ismétlés és súly megadása
        """
        if not self.current_day:
            self.app.custom_messagebox("Hiba", "Kérlek, először válassz vagy hozz létre egy napot!")
            return

        popup = ttk.Toplevel()
        popup.title("Gyakorlat hozzáadása")
        popup.geometry("800x500")
        
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        
        muscle_groups = ['bicepsz', 'comb', 'has', 'hát', 'kardió', 'mell', 
                        'far', 'tricepsz', 'vádli', 'váll']

        ttk.Label(popup,
                  text="Izomcsoport:",
                  font=("Colibri", 12),
                  style="Custom.TLabel").pack(pady=5)
        muscle_group_var = ttk.StringVar(popup)
        muscle_group_combo = ttk.Combobox(popup,
                                          textvariable=muscle_group_var,
                                          values=muscle_groups, 
                                          state="readonly",
                                          font=("Colibri", 12),
                                          bootstyle="warning",
                                          width=30)
        muscle_group_combo.pack(pady=(0,15))

        ttk.Label(popup,
                  text="Gyakorlat:",
                  font=("Colibri", 12),
                  style="Custom.TLabel").pack(pady=5)
        exercise_var = ttk.StringVar(popup)
        exercise_combo = ttk.Combobox(popup,
                                      textvariable=exercise_var,
                                      state="readonly", 
                                      font=("Colibri", 12),
                                      bootstyle="warning",
                                      width=50)
        exercise_combo.pack(pady=(0,15))

        info_frame = ttk.Frame(popup)
        info_frame.pack(pady=10, fill="x", padx=20)
        
        equipment_label = ttk.Label(info_frame,
                                    text="",
                                    font=("Colibri", 10),
                                    style="Custom.TLabel")
        equipment_label.pack()
        difficulty_label = ttk.Label(info_frame,
                                     text="",
                                     font=("Colibri", 10),
                                     style="Custom.TLabel")
        difficulty_label.pack()
        description_label = ttk.Label(info_frame,
                                      text="",
                                      font=("Colibri", 10),
                                      style="Custom.TLabel",
                                      wraplength=700)
        description_label.pack()

        input_frame = ttk.Frame(popup)
        input_frame.pack(pady=20)

        def validate_number(P):
            if P == "":
                return True
            if P.isdigit() and int(P) <= 99999:
                return True
            return False

        def validate_decimal(P):
            if P == "":
                return True
            try:
                float_val = float(P)
                if float_val <= 99999:
                    return True
                return False
            except ValueError:
                return False

        vcmd_number = (popup.register(validate_number), '%P')
        vcmd_decimal = (popup.register(validate_decimal), '%P')

        ttk.Label(input_frame, text="Sorozat:", font=("Colibri", 12), style="Custom.TLabel").grid(row=0, column=0, padx=5)
        sets_input = ttk.Spinbox(input_frame, 
                                 to=99999,
                                 font=("Colibri", 12),
                                 bootstyle="warning",
                                 width=10,
                                 validate="key",
                                 validatecommand=vcmd_number)
        sets_input.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Ismétlés:", font=("Colibri", 12), style="Custom.TLabel").grid(row=0, column=2, padx=5)
        reps_input = ttk.Spinbox(input_frame,
                                 to=99999,
                                 font=("Colibri", 12),
                                 bootstyle="warning",
                                 width=10,
                                 validate="key",
                                 validatecommand=vcmd_number)
        reps_input.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Súly:", font=("Colibri", 12), style="Custom.TLabel").grid(row=0, column=4, padx=5)
        weight_input = ttk.Entry(input_frame,
                                 font=("Colibri", 12),
                                 bootstyle="warning",
                                 width=10,
                                 validate="key",
                                 validatecommand=vcmd_decimal)
        weight_input.grid(row=0, column=5, padx=5)

        def update_exercises(*args):
            selected_group = muscle_group_var.get()
            self.app.db_cursor.execute(f"""
                SELECT [Gyakorlat neve], [Szükséges eszközök], [Nehézségi szint] 
                FROM {selected_group}
            """)
            exercises = self.app.db_cursor.fetchall()
            exercise_combo['values'] = [f"{ex[0]} | {ex[1]} | {ex[2]}" for ex in exercises]
        
        def update_info(*args):
            if not exercise_var.get():
                return
            exercise_name = exercise_var.get().split(" | ")[0]
            selected_group = muscle_group_var.get()
            self.app.db_cursor.execute(f"""
                SELECT [Szükséges eszközök], [Nehézségi szint], Leírás 
                FROM {selected_group} 
                WHERE [Gyakorlat neve] = ?
            """, (exercise_name,))
            info = self.app.db_cursor.fetchone()
            if info:
                equipment_label.config(text=f"Kellékek: {info[0]}")
                difficulty_label.config(text=f"Nehézség: {info[1]}")
                description_label.config(text=f"Leírás: {info[2]}")

        muscle_group_combo.bind('<<ComboboxSelected>>', update_exercises)
        exercise_combo.bind('<<ComboboxSelected>>', update_info)

        def validate_and_add():
            if not exercise_var.get():
                self.app.custom_messagebox("Hiányzó adatok", "Kérlek, válassz ki egy gyakorlatot!")
                return

            try:
                weight = float(weight_input.get()) if weight_input.get() else None
                sets = int(sets_input.get()) if sets_input.get() else None
                reps = int(reps_input.get()) if reps_input.get() else None
            except ValueError:
                self.app.custom_messagebox("Hibás adat", "A megadott értékeknek számoknak kell lenniük!")
                return

            exercise_name = exercise_var.get().split(" | ")[0]
            selected_group = muscle_group_var.get()
            
            try:
                self.app.db_cursor.execute(f"""
                    SELECT [Szükséges eszközök], [Nehézségi szint], [Leírás]
                    FROM "{selected_group}" 
                    WHERE [Gyakorlat neve] = ?
                """, (exercise_name,))
                
                info = self.app.db_cursor.fetchone()
                if not info:
                    self.app.custom_messagebox("Hiba", "A gyakorlat nem található az adatbázisban!")
                    return

                self.app.db_cursor.execute("""
                    SELECT id FROM training_days 
                    WHERE user_id = ? AND day_name = ?
                """, (self.app.user_id, self.current_day))
                
                day_result = self.app.db_cursor.fetchone()
                if not day_result:
                    self.app.custom_messagebox("Hiba", "A kiválasztott nap nem található!")
                    return
                    
                day_id = day_result[0]

                sets_to_insert = sets if sets is not None else ""
                reps_to_insert = reps if reps is not None else ""
                weight_to_insert = weight if weight is not None else ""

                self.app.db_cursor.execute("""
                    INSERT INTO exercises (
                        day_id, exercise_name, sets, reps, weight, 
                        equipment, difficulty, description
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (day_id, exercise_name, sets_to_insert, reps_to_insert, weight_to_insert,
                      info[0], info[1], info[2]))
                
                self.app.db_connection.commit()
                self.load_training_plan(self.current_day)
                popup.destroy()
                
            except sqlite3.Error as e:
                self.app.custom_messagebox("Hiba", f"Adatbázis hiba történt: {str(e)}")
                return

        ttk.Button(popup,
                   text="Hozzáadás",
                   style="darkbutton.TButton", 
                   command=validate_and_add,
                   cursor="hand2",
                   takefocus=False).pack(pady=20)

    def delete_exercise(self):
        """
        Kiválasztott gyakorlat törlése.
        
        Ellenőrzi, hogy van-e kiválasztott gyakorlat,
        majd törli azt az adatbázisból és a táblázatból.
        Megerősítő üzenetet jelenít meg sikeres törlés esetén.
        """
        selected_items = self.training_table.selection()
        if not selected_items:
            self.app.custom_messagebox("Hiba", "Kérlek, válassz ki egy gyakorlatot a törléshez!")
            return
        
        for selected_item in selected_items:
            values = self.training_table.item(selected_item)['values']
            
            self.app.db_cursor.execute("""SELECT id FROM training_days WHERE user_id = ? AND day_name = ?""",
                                      (self.app.user_id, self.current_day))
            day_id_result = self.app.db_cursor.fetchone()
            
            if not day_id_result:
                self.app.custom_messagebox("Hiba", "Nem található a kiválasztott nap!")
                return
            day_id = day_id_result[0]

            self.app.db_cursor.execute("""DELETE FROM exercises WHERE day_id = ? AND exercise_name = ? AND sets = ? AND reps = ? AND weight = ?""",
                                      (day_id, values[0], values[1], values[2], values[3]))
            self.app.db_connection.commit()
            
            self.training_table.delete(selected_item)

    def load_training_plan(self, day):
        """
        Edzésterv betöltése a kiválasztott naphoz.
        
        Args:
            day: A kiválasztott nap neve
        
        Betölti az adatbázisból a naphoz tartozó gyakorlatokat
        és megjeleníti őket a táblázatban a részletes információkkal együtt.
        """
        for item in self.training_table.get_children():
            self.training_table.delete(item)
        
        self.app.db_cursor.execute("""SELECT id FROM training_days WHERE user_id = ? AND day_name = ?""",
                                  (self.app.user_id, day))
        
        result = self.app.db_cursor.fetchone()
        if result is None:
            return
        
        day_id = result[0]
        
        self.app.db_cursor.execute("""SELECT exercise_name, sets, reps, weight, equipment, difficulty, description FROM exercises WHERE day_id = ?""",
            (day_id,))
        
        for row in self.app.db_cursor.fetchall():
            self.training_table.insert("", "end", values=row)

    def delete_current_day(self):
        """
        Aktuálisan kiválasztott edzésnap törlése.
        
        Megerősítést kér a felhasználótól, majd:
        - Törli a naphoz tartozó összes gyakorlatot
        - Törli magát a napot az adatbázisból
        - Eltávolítja a nap gombját a felületről
        - Törli a táblázat tartalmát
        
        Sikeres törlés után megerősítő üzenetet jelenít meg.
        """
        if not self.current_day or self.current_day == "+ Új nap":
            self.app.custom_messagebox("Hiba", "Nincs kiválasztott nap!")
            return

        confirm_window = ttk.Toplevel(self.app.root)
        confirm_window.title("Megerősítés")
        screen_width = self.app.root.winfo_screenwidth()
        screen_height = self.app.root.winfo_screenheight()
        window_width = 600
        window_height = 200
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height / 2 - window_height / 2)
        confirm_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
        confirm_window.grab_set()

        ttk.Label(confirm_window, 
                 text=f"Biztosan törölni szeretnéd a(z) {self.current_day} napot?",
                 font=("Colibri", 15),
                 bootstyle="secondary").pack(pady=50)

        button_frame = ttk.Frame(confirm_window)
        button_frame.pack(pady=10)

        def confirm_delete():
            self.app.db_cursor.execute("""SELECT id FROM training_days WHERE user_id = ? AND day_name = ?""",
                                      (self.app.user_id, self.current_day))
            day_id = self.app.db_cursor.fetchone()[0]

            self.app.db_cursor.execute("DELETE FROM exercises WHERE day_id = ?", (day_id,))
            
            self.app.db_cursor.execute("DELETE FROM training_days WHERE id = ?", (day_id,))
            self.app.db_connection.commit()

            for btn in self.day_buttons:
                if btn['text'] == self.current_day:
                    btn.destroy()
                    self.day_buttons.remove(btn)
                    break

            for item in self.training_table.get_children():
                self.training_table.delete(item)

            self.current_day = None
            confirm_window.destroy()
            self.app.custom_messagebox("Sikeres törlés", "A nap sikeresen törölve!")

        ttk.Button(button_frame,
                   text="Igen",
                   style="lightbutton.TButton",
                   cursor="hand2",
                   takefocus=False,
                   command=confirm_delete).pack(side="left", padx=10)

        ttk.Button(button_frame,
                   text="Nem",
                   style="lightbutton.TButton",
                   cursor="hand2",
                   takefocus=False,
                   command=confirm_window.destroy).pack(side="right", padx=10)