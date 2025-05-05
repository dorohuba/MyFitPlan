import ttkbootstrap as ttk
from datetime import datetime
import re

class DietManager:
    def __init__(self, app):
        self.app = app
        self.meter = None
        self.breakfast_table = None
        self.lunch_table = None
        self.dinner_table = None
        self.other_table = None
        self.date_entry = None
        self.food_input = None
        self.custom_food_entry = None
        self.amount_label = None

    def add_food(self, target_table):
        """Étel hozzáadása funkció"""
        popup = ttk.Toplevel()
        popup.title("Étel hozzáadása")
        popup.geometry("860x200")
        
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        self.app.db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in self.app.db_cursor.fetchall() if row[0] in ['Alkoholos italok', 'Gabonafélék és hüvelyesek', 'Gyümölcsök', 
                      'Halfélék', 'Húsfélék', 'Italok', 'Olajok', 'Szénhidrátok', 'Tejtermékek és tojások', 'Zöldségek']]
        table_names.append("Egyéni")

        ttk.Label(popup,
                  text="Típus",
                  font=("Colibri", 12),
                  style="Custom.TLabel").grid(row=1, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        meal_type_var = ttk.StringVar(popup)
        meal_type_input = ttk.Combobox(popup,
                                       textvariable=meal_type_var,
                                       values=table_names,
                                       state="readonly",
                                       font=("Colibri", 18),
                                       bootstyle="warning",
                                       width=15)
        meal_type_input.grid(row=2, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(popup, text="Étel",
                  font=("Colibri", 12),
                  style="Custom.TLabel").grid(row=1, column=1, padx=(30, 30), pady=(15, 5), sticky="sw")
        food_var = ttk.StringVar(popup)
        self.food_input = ttk.Combobox(popup,
                                  textvariable=food_var,
                                  values=[],
                                  state="readonly",
                                  font=("Colibri", 18),
                                  bootstyle="warning",
                                  width=15)
        self.food_input.grid(row=2, column=1, padx=(30, 30), pady=(0, 20), sticky="nw")

        self.custom_food_entry = ttk.Entry(popup,
                                      font=("Colibri", 18),
                                      bootstyle="warning",
                                      width=16)
        self.custom_food_entry.grid(row=2, column=1, padx=(30, 30), pady=(0, 20), sticky="nw")
        self.custom_food_entry.grid_remove()

        self.amount_label = ttk.Label(popup,
                                 text="Mennyiség (g/ml)",
                                 font=("Colibri", 12),
                                 style="Custom.TLabel")
        self.amount_label.grid(row=1, column=2, padx=(30, 30), pady=(15, 5), sticky="sw")
        amount_input = ttk.Spinbox(popup,
                                   from_=0,
                                   to=10000,
                                   font=("Colibri", 18),
                                   bootstyle="warning",
                                   width=15)
        amount_input.grid(row=2, column=2, padx=(30, 30), pady=(0, 20), sticky="nw")
        amount_input.configure(validate="key")
        amount_input['validatecommand'] = (popup.register(lambda text: text.isdigit()), '%P')

        def validate_inputs():
            if not meal_type_var.get():
                self.app.custom_messagebox("Hiányzó adatok", "Kérlek, válassz egy típust!")
                return False
                
            if meal_type_var.get() == "Egyéni":
                if not self.custom_food_entry.get():
                    self.app.custom_messagebox("Hiányzó adatok", "Kérlek, add meg az étel nevét!")
                    return False
                if not amount_input.get().isdigit() or int(amount_input.get()) <= 0:
                    self.app.custom_messagebox("Hiányzó adatok", "Kérlek, adj meg egy érvényes kalória értéket!")
                    return False
            else:
                if not food_var.get():
                    self.app.custom_messagebox("Hiányzó adatok", "Kérlek, válassz egy ételt!")
                    return False
                if not amount_input.get().isdigit() or int(amount_input.get()) <= 0:
                    self.app.custom_messagebox("Hiányzó adatok", "Kérlek, adj meg egy érvényes mennyiséget!")
                    return False
            return True

        meal_type_input.bind("<<ComboboxSelected>>", lambda event: self.load_food_options(event, meal_type_var))

        def add_selected_food():
            if not validate_inputs():
                return

            selected_table = meal_type_var.get()
            amount = amount_input.get()

            if selected_table == "Egyéni":
                food_name = self.custom_food_entry.get()
                calories = int(amount)
                amount_to_save = 0
            else:
                selected_food = food_var.get()
                last_parenthesis_index = selected_food.rfind('(')
                food_name = selected_food[:last_parenthesis_index].strip()
                calories_text = re.search(r'\((.*?)\)', selected_food[last_parenthesis_index:])
                calories_per_100 = int(calories_text.group(1).split()[0])
                calories = round((calories_per_100 / 100 * int(amount)))
                amount_to_save = int(amount)

            target_table.insert("", "end", values=(food_name, f"{calories} kcal", amount_to_save))

            selected_date = self.app.date_entry.entry.get()
            
            self.app.db_cursor.execute("""
                INSERT INTO users_meals (user_id, table_name, food_name, calories, amount, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.app.user_id, 
                  "breakfast_table" if target_table == self.app.breakfast_table else 
                  "lunch_table" if target_table == self.app.lunch_table else 
                  "dinner_table" if target_table == self.app.dinner_table else 
                  "other_table", 
                  food_name, calories, amount_to_save, selected_date))

            self.app.db_connection.commit()
            self.update_meter()
            popup.destroy()

        add_button = ttk.Button(popup,
                                text="Hozzáadás",
                                style="darkbutton.TButton",
                                command=add_selected_food,
                                cursor="hand2",
                                takefocus=False)
        add_button.grid(row=3, column=1, pady=30)

        popup.protocol("WM_DELETE_WINDOW", popup.destroy)

    def load_food_options(self, event, meal_type_var):
        """Étel opciók betöltése"""
        selected_table = meal_type_var.get()
        if selected_table == "Egyéni":
            self.food_input.grid_remove()
            self.custom_food_entry.grid()
            self.amount_label.configure(text="Kalória (kcal)")
        else:
            self.custom_food_entry.grid_remove()
            self.food_input.grid()
            self.amount_label.configure(text="Mennyiség (g/ml)")
            if selected_table:
                unit = "ml" if selected_table in ["Italok", "Alkoholos italok"] else "g"
                self.app.db_cursor.execute(f'SELECT Név, Kalória FROM "{selected_table}";')
                foods = [f"{row[0]} ({row[1]} kcal/100{unit})" for row in self.app.db_cursor.fetchall()]
                self.food_input['values'] = foods

    def diet_page(self):
        """
        Képernyő tisztítása ás étrend oldal megjelenítése.
        
        Tartalmazza:
        - Kalória mérő widget (napi limit és aktuális bevitel)
        - Dátumválasztó a napi étkezések megtekintéséhez
        - Négy étkezési kategória (reggeli, ebéd, vacsora, egyéb)
        - Étkezések hozzáadása gomb minden kategóriához
        
        A kalória mérő színe változik a napi limit függvényében:
        - Világos lila: kevesebb mint 75%
        - Narancssárga: 75-100% között
        - Piros: 100% felett
        """
        self.app.clear_screen()
        self.app.load_navigation_bar()

        self.app.db_cursor.execute(
            'SELECT eletkor, magassag, testsuly, nem, aktivitas FROM users WHERE email = ?', 
            (self.app.logged_in_user,))
        
        user_data = self.app.db_cursor.fetchone()

        if user_data:
            eletkor, magassag, testsuly, nem, aktivitas = user_data
            
            if nem == "Férfi":
                bmr = 10 * int(testsuly) + 6.25 * int(magassag) - 5 * int(eletkor) + 5
            elif nem == "Nő":
                bmr = 10 * int(testsuly) + 6.25 * int(magassag) - 5 * int(eletkor) - 161
            
            self.app.tdee = bmr * self.app.activity_factors.get(aktivitas)

        self.app.meter = ttk.Meter(master=self.app.root,
                                   bootstyle="primary",
                                   subtext=f"Napi max kcal: {int(self.app.tdee)} ",
                                   textfont="Colibri 20",
                                   subtextfont="Colibri 20",
                                   stripethickness=10,
                                   metersize=350,
                                   amounttotal=int(self.app.tdee))
        self.app.meter.place(relx=0.5, rely=0.55, anchor="center")

        box_width = 0.25
        box_height = 0.25
        name_box_height = 0.05
        
        self.app.date_select_frame = ttk.Frame(self.app.root)
        self.app.date_select_frame.place(relx=0.375,
                                 rely=0.21,
                                 relwidth=box_width,
                                 relheight=name_box_height)

        date_select_box = ttk.PanedWindow(self.app.date_select_frame,
                                       orient='horizontal')
        date_select_box.pack(expand=True)

        self.app.date_entry = ttk.DateEntry(self.app.date_select_frame,
                                            bootstyle="warning",
                                            dateformat="%Y-%m-%d",
                                            firstweekday=0)
        date_select_box.add(self.app.date_entry)

        def update_button_click():
            selected_date = self.app.date_entry.entry.get()
            self.load_user_meals(selected_date)
            self.update_meter()

        update_button = ttk.Button(self.app.date_select_frame,
                                   text="Lekérdezés",
                                   command=update_button_click,
                                   style="darkbutton.TButton",
                                   cursor="hand2",
                                   takefocus=False)
        date_select_box.add(update_button)


        self.app.box1 = ttk.Frame(self.app.root,
                                  style="Frameborder.TFrame",
                                  relief="solid",
                                  borderwidth=1)
        self.app.box1.place(relx=0.05, rely=0.27, relwidth=box_width, relheight=box_height)

        self.app.box2 = ttk.Frame(self.app.root, style="Frameborder.TFrame", relief="solid", borderwidth=1)
        self.app.box2.place(relx=0.05,
                            rely=0.67,
                            relwidth=box_width,
                            relheight=box_height)

        self.app.box3 = ttk.Frame(self.app.root,
                                  style="Frameborder.TFrame",
                                  relief="solid",
                                  borderwidth=1)
        self.app.box3.place(relx=0.70,
                            rely=0.27,
                            relwidth=box_width,
                            relheight=box_height)

        self.app.box4 = ttk.Frame(self.app.root,
                                  style="Frameborder.TFrame",
                                  relief="solid",
                                  borderwidth=1)
        self.app.box4.place(relx=0.70,
                            rely=0.67,
                            relwidth=box_width,
                            relheight=box_height)

        for i in range(4):
            self.app.root.grid_columnconfigure(i, weight=1)

        self.app.root.grid_rowconfigure(2, weight=1)

        def create_table(frame, columns, data):
            table = ttk.Treeview(frame,
                                 columns=columns,
                                 show="headings",
                                 style="Custom.Treeview")
            table.pack(expand=True, fill="both", padx=1)

            for col in columns:
                table.heading(col, text=col, anchor="center")
                table.column(col, anchor="center", width=50)

            for row in data:
                table.insert("", "end", values=row)

            table.bind("<Button-1>", lambda e: "break")
            table.bind("<Double-1>", lambda e: "break")

            table['selectmode'] = 'none'

            return table

        

        columns = ("Étel", "Kcal", "g/ml")
        data_breakfast = []
        data_lunch = []
        data_dinner = []
        data_other = []

        self.app.breakfast_table = create_table(self.app.box1, columns, data_breakfast)
        self.app.lunch_table = create_table(self.app.box2, columns, data_lunch)
        self.app.dinner_table = create_table(self.app.box3, columns, data_dinner)
        self.app.other_table = create_table(self.app.box4, columns, data_other)

        self.load_user_meals()

        self.update_meter()

        box_width = 0.25
        box_height = 0.25
        name_box_height = 0.05

        self.app.boxname1 = ttk.Frame(self.app.root,
                                      style="Frameborder.TFrame",
                                      relief="solid",
                                      borderwidth=1)
        self.app.boxname1.place(relx=0.05, rely=0.21, relwidth=box_width, relheight=name_box_height )
        ttk.Label(self.app.boxname1,
                  text="Reggeli",
                  anchor="center",
                  style="meals.TLabel").pack(expand=True)

        self.app.boxname2 = ttk.Frame(self.app.root,
                                      style="Frameborder.TFrame",
                                      relief="solid",
                                      borderwidth=1)
        self.app.boxname2.place(relx=0.05, rely=0.61, relwidth=box_width, relheight=name_box_height)
        ttk.Label(self.app.boxname2,
                  text="Ebéd",
                  anchor="center",
                  style="meals.TLabel").pack(expand=True)

        self.app.boxname3 = ttk.Frame(self.app.root,
                                      style="Frameborder.TFrame",
                                      relief="solid",
                                      borderwidth=1)
        self.app.boxname3.place(relx=0.70, rely=0.21, relwidth=box_width, relheight=name_box_height)
        ttk.Label(self.app.boxname3,
                  text="Vacsora",
                  anchor="center",
                  style="meals.TLabel").pack(expand=True)

        self.app.boxname4 = ttk.Frame(self.app.root,
                                      style="Frameborder.TFrame",
                                      relief="solid",
                                      borderwidth=1)
        self.app.boxname4.place(relx=0.70, rely=0.61, relwidth=box_width, relheight=name_box_height)
        ttk.Label(self.app.boxname4,
                  text="Egyéb",
                  anchor="center",
                  style="meals.TLabel").pack(expand=True)

        details_button1 = ttk.Button(self.app.boxname1,
                                     text="+",
                                     style="darkbutton.TButton", 
                                     cursor="hand2",
                                     takefocus=False,
                                     width=3,
                                     command=lambda: self.add_food(self.app.breakfast_table))
        details_button1.place(relx=0.985, rely=0.5, anchor="e")

        details_button2 = ttk.Button(self.app.boxname2,
                                     text="+",
                                     style="darkbutton.TButton", 
                                     cursor="hand2",
                                     takefocus=False,
                                     width=3,
                                     command=lambda: self.add_food(self.app.lunch_table))
        details_button2.place(relx=0.985, rely=0.5, anchor="e")

        details_button3 = ttk.Button(self.app.boxname3,
                                     text="+",
                                     style="darkbutton.TButton", 
                                     cursor="hand2",
                                     takefocus=False,
                                     width=3,
                                     command=lambda: self.add_food(self.app.dinner_table))
        details_button3.place(relx=0.985, rely=0.5, anchor="e")

        details_button4 = ttk.Button(self.app.boxname4,
                                     text="+",
                                     style="darkbutton.TButton", 
                                     cursor="hand2",
                                     takefocus=False,
                                     width=3,
                                     command=lambda: self.add_food(self.app.other_table))
        details_button4.place(relx=0.985, rely=0.5, anchor="e")


    def load_user_meals(self, selected_date=None):
        """
        Felhasználó étkezéseinek betöltése a kiválasztott dátumra.
        
        Args:
            selected_date: A kiválasztott dátum (alapértelmezett: mai nap)
        
        Minden étkezési kategóriához betölti az adatbázisból:
        - étel neve
        - kalória tartalom
        - mennyiség

        Az "egyéni" kategóriába saját, előre nem definiált ételeket lehet hozzáadni.
        A kalóriát manuálisan kell megadni, a mennyiség pedig ebben az esetben mindíg 0.
        """
        if not selected_date:
            selected_date = datetime.now().strftime("%Y-%m-%d")


        for table in [self.app.breakfast_table, self.app.lunch_table, self.app.dinner_table, self.app.other_table]:
            table.delete(*table.get_children())

        self.app.db_cursor.execute("""SELECT table_name, food_name, calories, amount FROM users_meals WHERE user_id = ? AND date = ?""",
                                  (self.app.user_id, selected_date))
        meals = self.app.db_cursor.fetchall()

        for meal in meals:
            table_name, food_name, calories, amount = meal
            if table_name == "breakfast_table":
                self.app.breakfast_table.insert("", "end", values=(food_name, f"{calories} kcal", amount))
            elif table_name == "lunch_table":
                self.app.lunch_table.insert("", "end", values=(food_name, f"{calories} kcal", amount))
            elif table_name == "dinner_table":
                self.app.dinner_table.insert("", "end", values=(food_name, f"{calories} kcal", amount))
            else:
                self.app.other_table.insert("", "end", values=(food_name, f"{calories} kcal", amount))


    def update_meter(self):
        """
        Kalória mérő widget frissítése.
        
        Kiszámítja az adott napra bevitt összes kalóriát,
        és frissíti a mérő megjelenítését:
        - Beállítja az aktuális értéket
        - Módosítja a színt az értékek alapján
        """
        selected_date = self.app.date_entry.entry.get()
        total_calories = 0

        self.app.db_cursor.execute("""SELECT user_id, calories, date FROM users_meals WHERE user_id = ? AND date = ?""",
                                  (self.app.user_id, selected_date))
        rows = self.app.db_cursor.fetchall()

        for row in rows:
            calories_str = row[1]
            calories = int(calories_str)
            total_calories += calories

        self.app.meter.configure(amountused=total_calories)

        if total_calories >= int(self.app.tdee):
            self.app.meter.configure(bootstyle="danger")
        elif total_calories >= 3 * int(self.app.tdee) / 4:
            self.app.meter.configure(bootstyle="warning")
        else:
            self.app.meter.configure(bootstyle="primary")
