"""
MyFitPlan alkalmazás
-------------------
Egy személyre szabott edzés- és étrendtervező alkalmazás.

Főbb funkciók:
- Felhasználói regisztráció és bejelentkezés
- Személyes profil kezelése
- Étrend követése és napi kalória számolás
- Edzésterv készítése és kezelése
- Gyakorlatok hozzáadása izomcsoportok szerint

Az alkalmazás SQLite adatbázist használ az adatok tárolására.
"""

import ttkbootstrap as ttk
import sqlite3
import os
import sys
from pathlib import Path
from app.user_manager import UserManager
from app.diet_manager import DietManager
from app.training_manager import TrainingManager


def resource_path(relative_path):
    """ 
    Fájlok elérési útjának kezelése.
    
    Args:
        relative_path: A fájl relatív elérési útja
        
    Returns:
        A fájl abszolút elérési útja
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(base_path) == "app":
            base_path = os.path.dirname(base_path)
    return os.path.join(base_path, relative_path)



class MyFitPlan:
    """
    Az alkalmazás fő osztálya, ami kezeli a bejelentkezési és regisztrációs felületet,
    az adatbázis műveleteket, valamint az alkalmazás egyéb funkcióit.
    """
    def __init__(self, root):
        """
        Az alkalmazás inicializálása.
        Beállítja az ablak tulajdonságait, létrehozza az adatbázis kapcsolatot,
        és beállítja a stílusokat.
        """
        self.root = root
        self.root.title("MyFitPlan")
        self.root.state('zoomed')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.root.minsize(screen_width, screen_height)
        self.root.maxsize(screen_width, screen_height)

        self.current_theme = "myfitplan"
        self.root.configure(bg="#090e51")

        self.screen_stack = []

        db_path = resource_path('myfitplan.db')
        self.db_connection = sqlite3.connect(db_path)
        self.db_cursor = self.db_connection.cursor()
        self.create_database()

        self.user_manager = UserManager(self)
        self.meal_manager = DietManager(self)
        self.training_manager = TrainingManager(self)

        self.activity_factors = {"Csekély": 1.2,
                                 "Mérsékelt": 1.375,
                                 "Közepes": 1.55,
                                 "Átlagon felüli": 1.725,
                                 "Nagyon magas": 1.9}

        self.configure_styles()
        self.user_manager.login_or_register()
        self.logged_in_user = None
        self.user_id = None

    def configure_styles(self):
        """Stílusok beállítása"""
        style = ttk.Style()
        style.configure('darkbutton.TButton', background="#09053a", foreground="#8b87dc", 
                        font=("Colibri", 10), relief="solid", borderwidth=1, bordercolor="#ff4e1a")
        style.map('darkbutton.TButton', background=[('active', '#110a6b')], 
                  foreground=[('active', 'white')], relief=[('active', 'solid')])
        style.configure('lightbutton.TButton', background="#09053a", foreground="#8b87dc", font=("Colibri", 15), relief="solid", borderwidth=1, bordercolor="#ff4e1a")
        style.map('lightbutton.TButton', background=[('active', '#110a6b')], foreground=[('active', 'white')], relief=[('active', 'solid')])
        style.configure("Custom.TLabelframe", background="#090e51")
        style.configure("Custom.TLabelframe.Label", background="#090e51", font=("Colibri", 20), foreground="#8b87dc")
        style.configure("Custom.TEntry", fieldbackground="#090e51", highlightthickness=0,)
        style.configure("Custom.TLabel", background="#090e51", foreground="#8b87dc")
        style.configure('Frameborder1.TFrame', borderwidth=0, relief='solid', bordercolor='#ff4e1a', background='#40098d')
        style.configure('Frameborder.TFrame', borderwidth=1, relief='solid', bordercolor='#ff4e1a', background='#09053a')
        style.configure('menubutton.TButton', background='#40098d', borderwidth=1, bordercolor="#ff4e1a", highlightthickness=0, relief="flat")
        style.configure('words.TButton', background='#40098d', font=("Colibri", 14, "bold"), foreground='#8b87dc', borderwidth=0, bordercolor="#ff4e1a", highlightthickness=0)
        style.map('words.TButton', background=[('active', '#09053a')], foreground=[('active', 'white')], relief=[('active', 'flat')])
        style.map('menubutton.TButton', background=[('active', '#40098d')], relief=[('active', 'flat')])
        style.configure("Custom.Treeview", background="#09053a", foreground="#8b87dc", font=("Colibri", 12), borderwidth=1, bordercolor="#ff4e1a", rowheight=20)
        style.configure("Custom.Treeview.Heading", font=("Colibri", 14))
        style.map('Custom.Treeview', bordercolor=[('active', 'grey')])
        style.configure("meals.TLabel", background="#09053a", font=("Colibri", 16), foreground="#8b87dc")
        style.configure('selected.TButton', background='#ff4e1a', font=("Colibri", 14, "bold"), foreground='white', borderwidth=0, bordercolor="#ff4e1a", highlightthickness=0)
        style.map('selected.TButton', background=[('active', '#b02800')], foreground=[('active', '#ffffff')])
        style.configure("Custom.Treeview", background="#09053a", foreground="#8b87dc", font=("Colibri", 12), borderwidth=0, rowheight=20, fieldbackground="#09053a")    
        style.map("Custom.Treeview", background=[('selected', '#09053a')], foreground=[('selected', '#ff4e1a')])
        

    def create_database(self):
        """
        Adatbázis struktúra létrehozása.
        
        Létrehozott táblák:
        - users: Felhasználói adatok tárolása
        - users_meals: Felhasználók étkezéseinek naplózása
        - training_days: Edzésnapok tárolása
        - exercises: Felhasználók által összeállított edzéstervek gyakorlatai
        
        Minden tábla csak akkor jön létre, ha még nem létezik.
        """

        self.db_cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                vezeteknev TEXT NOT NULL,
                keresztnev TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                jelszo TEXT NOT NULL,
                eletkor INTEGER,
                magassag INTEGER,
                testsuly INTEGER,
                nem TEXT,
                aktivitas TEXT
            )
        ''')


        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS users_meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                table_name TEXT NOT NULL,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')


        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                day_name TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, day_name)
            )
        ''')

 
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                weight REAL,
                equipment TEXT,
                difficulty TEXT,
                description TEXT,
                FOREIGN KEY(day_id) REFERENCES training_days(id)
            )
        ''')

        self.db_connection.commit()

    def clear_screen(self):
        """
        Képernyő tartalmának törlése.
        Eltávolít minden widgetet a felületről.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def custom_messagebox(self, title, message, login=False, diet=False, profile=False):
        """
        Egyedi üzenetablak megjelenítése.
        Paraméterek:
        - title: az ablak címe
        - message: megjelenítendő üzenet
        - login: átirányítás a bejelentkező oldalra
        - diet: átirányítás az étrend oldalra
        - profile: átirányítás a profil oldalra
        """
        message_window = ttk.Toplevel(self.root)
        message_window.title(title)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 500
        window_height = 200
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height / 2 - window_height / 2)
        message_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
        message_window.grab_set()

        label = ttk.Label(message_window, text=message,
                          font=("Colibri", 15),
                          bootstyle="secondary")
        label.pack(pady=50)

        rendben = ttk.Button(message_window, text="Rendben",
                             style="lightbutton.TButton",
                             cursor="hand2",
                             takefocus=False,
                             command=lambda: self.close_messagebox(message_window, login, diet, profile))
        rendben.pack(pady=10)

    def back(self):
        """
        Visszalépés az előző képernyőre.
        A screen_stack lista alapján visszanavigál az előző oldalra.
        """
        if self.screen_stack:
            self.clear_screen()
            previous_screen = self.screen_stack.pop()
            previous_screen()

    def close_messagebox(self, message_window, login, diet, profile):
        """
        Üzenetablak bezárása és opcionális átirányítás.
        Az átirányítási paraméterek alapján navigál a megfelelő oldalra.
        """
        message_window.destroy()
        if login==True:
            self.user_manager.login_page()
        if diet==True:
            self.meal_manager.diet_page()
        if profile==True:
            self.user_manager.profile_page()

    def load_navigation_bar(self):
        """
        Navigációs sáv betöltése.
        
        Létrehozza és megjeleníti a felső navigációs sávot:
        - Profil ikon és gomb
        - Étrend ikon és gomb
        - Edzés ikon és gomb
        - Kijelentkezés ikon és gomb
        - Bezárás ikon és gomb
        """
        self.top_frame = ttk.Canvas(self.root, height=110)
        self.top_frame.grid_propagate(False)
        self.top_frame.grid(row=0, column=0, columnspan=5, padx=0, pady=0, sticky="new")

        self.bg1_image = ttk.PhotoImage(file=resource_path("Képek/backg1.png"))
        self.top_frame.create_image(0, 0, image=self.bg1_image, anchor="nw")

        self.bg2_image = ttk.PhotoImage(file=resource_path("Képek/backg2.png"))
        
        self.bg2 = self.top_frame.create_image(self.root.winfo_screenwidth(), 0, image=self.bg2_image, anchor="ne")

        def update_bg2_position(event=None):
            if self.top_frame.winfo_exists():
                try:
                    self.top_frame.coords(self.bg2, self.root.winfo_width(), 0)
                except ttk.TclError:
                    pass

        self.bg_update_binding = self.root.bind('<Configure>', update_bg2_position)
        
        self.profile_icon = ttk.PhotoImage(file=resource_path("Képek/profile.png")).subsample(2)
        self.food_icon = ttk.PhotoImage(file=resource_path("Képek/diet.png")).subsample(2)
        self.weight_icon = ttk.PhotoImage(file=resource_path("Képek/weight.png")).subsample(2)
        self.logout = ttk.PhotoImage(file=resource_path("Képek/logout.png")).subsample(2)
        self.exit = ttk.PhotoImage(file=resource_path("Képek/exit.png")).subsample(2)

        self.left_frame = ttk.Frame(self.top_frame,
                                    style="Frameborder1.TFrame")
        self.left_frame.grid(row=0, column=1, pady=13, padx=50, sticky="ns")

        self.top_frame.grid_columnconfigure(0, weight=0)
        self.top_frame.grid_columnconfigure(1, weight=0)
        self.top_frame.grid_columnconfigure(2, weight=1)
 
        self.profile_button = ttk.Button(self.left_frame,
                                         image=self.profile_icon,
                                         command=self.user_manager.profile_page,
                                         style="menubutton.TButton",
                                         cursor="hand2",
                                         takefocus=False)
        self.profile_button.grid(row=0, column=1, pady=(2,0), padx=2, sticky="nsew")

        self.food_button = ttk.Button(self.left_frame,
                                      image=self.food_icon,
                                      command=self.meal_manager.diet_page,
                                      style="menubutton.TButton",
                                      cursor="hand2",
                                      takefocus=False)
        self.food_button.grid(row=0, column=2, pady=(2,0), padx=2, sticky="nsew")

        self.weight_button = ttk.Button(self.left_frame,
                                        image=self.weight_icon, 
                                        command=self.training_manager.training_page,
                                        style="menubutton.TButton", 
                                        cursor="hand2", 
                                        takefocus=False)
        self.weight_button.grid(row=0, column=3, pady=(2,0), padx=2, sticky="nsew")

        self.logout_button = ttk.Button(self.left_frame, 
                                        image=self.logout, 
                                        command=self.user_manager.logout,
                                        style="menubutton.TButton", 
                                        cursor="hand2", 
                                        takefocus=False)
        self.logout_button.grid(row=0, column=5, pady=(2,0), padx=2, sticky="nsew")

        self.exit_button = ttk.Button(self.left_frame,
                                      image=self.exit,
                                      command=self.root.quit,
                                      style="menubutton.TButton",
                                      cursor="hand2",
                                      takefocus=False)
        self.exit_button.grid(row=0, column=6, pady=(2,0), padx=2, sticky="nsew")

        self.profile_label_button = ttk.Button(self.left_frame,
                                               text="Profil",
                                               command=self.user_manager.profile_page,
                                               style="words.TButton",
                                               cursor="hand2",
                                               takefocus=False)
        self.profile_label_button.grid(row=1, column=1, pady=(0, 2), padx=2, sticky="nsew")

        self.food_label_button = ttk.Button(self.left_frame,
                                            text="Étrend", 
                                            command=self.meal_manager.diet_page,
                                            style="words.TButton", 
                                            cursor="hand2", 
                                            takefocus=False)
        self.food_label_button.grid(row=1, column=2, pady=(0, 2), padx=2, sticky="nsew")

        self.weight_label_button = ttk.Button(self.left_frame,
                                              text="Edzés",
                                              command=self.training_manager.training_page,
                                              style="words.TButton", 
                                              cursor="hand2", 
                                              takefocus=False)
        self.weight_label_button.grid(row=1, column=3, pady=(0, 2), padx=2, sticky="nsew")

        self.logout_label_button = ttk.Button(self.left_frame, 
                                              text="Kijelentkezés", 
                                              command=self.user_manager.logout,
                                              style="words.TButton", 
                                              cursor="hand2", 
                                              takefocus=False)
        self.logout_label_button.grid(row=1, column=5, pady=(0, 2), padx=2, sticky="nsew")

        self.exit_label_button = ttk.Button(self.left_frame, 
                                            text="Bezárás", 
                                            command=self.root.quit,
                                            style="words.TButton", 
                                            cursor="hand2", 
                                            takefocus=False)
        self.exit_label_button.grid(row=1, column=6, pady=(0, 2), padx=2, sticky="nsew")

