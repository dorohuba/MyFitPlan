import ttkbootstrap as ttk
import re

class UserManager:
    def __init__(self, app):
        self.app = app
        self.vezeteknev = None
        self.keresztnev = None
        self.email = None
        self.jelszo = None

    def is_valid_email(self, email):
        """
        Email cím formátum ellenőrzése reguláris kifejezéssel.
        
        Args:
            email: Ellenőrizendő email cím
            
        Returns:
            bool: True ha valid a formátum, False ha nem
        """
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def login_or_register(self):
        """
        Megjeleníti a bejelentkezős vagy regisztrációs oldalt:
        - Bejelentkezés gomb
        - Regisztráció gomb
        - Bezárás gomb       
        """
        
        udv = ttk.Labelframe(self.app.root,
                             labelwidget=ttk.Label(self.app.root, text="Üdv!", font=("Colibri", 20), style="Custom.TLabelframe.Label"),
                             bootstyle="light")
        udv.place(relx=0.5, rely=0.5, anchor=ttk.CENTER)

        ttk.Button(udv,
                   text="Bejelentkezés",
                   style="lightbutton.TButton",
                   command=self.login_page,
                   width=15,
                   cursor="hand2",
                   takefocus=False).grid(row=0, column=0, columnspan=2, padx=30, pady=(35,0), sticky="snew")
        
        ttk.Button(udv,
                   text="Regisztráció",
                   style="lightbutton.TButton",
                   command=self.register_data_1,
                   width=15,
                   cursor="hand2",
                   takefocus=False).grid(row=1, column=0, padx=(30, 15), pady=(35, 35), sticky="snew")

        ttk.Button(udv,
                   text="Bezárás",
                   style="lightbutton.TButton",
                   command=self.app.root.quit,
                   width=15,
                   cursor="hand2",
                   takefocus=False).grid(row=1, column=1, padx=(15, 30), pady=(35, 35), sticky="snew"),

    # REGISZTRÁCIÓ----------------------
    # 1

    def label_box(self, text="Töltsd ki az adatokat!"):
        """
        Regisztrációs/bejelentkező doboz létrehozása.
        
        Args:
            text: A doboz címkéjének szövege
        """
        self.label_widget = ttk.Label(self.app.root, 
                                      text=text, 
                                      font=("Colibri", 20), 
                                      style="Custom.TLabelframe.Label")
        
        self.register = ttk.Labelframe(self.app.root,
                                      labelwidget=self.label_widget, 
                                      bootstyle="light")
        self.register.place(relx=0.5, rely=0.5, anchor=ttk.CENTER)

    def register_data_1(self):
        """
        Regisztráció első lépésének felülete.
        
        Megjelenít egy űrlapot a következő mezőkkel:
        - Vezetéknév
        - Keresztnév
        - Email cím
        - Jelszó
        - Jelszó megerősítése
        
        A felület tartalmaz egy "Tovább" és egy "Vissza" gombot.
        """
        self.app.clear_screen()
        self.app.screen_stack.append(self.login_or_register)
        
        self.label_box()

        ttk.Label(self.register,text="Vezetéknév", font=("Colibri", 12), style="Custom.TLabel").grid(row=0, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.veznev_input = ttk.Entry(self.register, font=("Colibri", 18), bootstyle="warning")
        self.veznev_input.grid(row=1, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(self.register, text="Keresztnév", font=("Colibri", 12), style="Custom.TLabel").grid(row=2, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.kernev_input = ttk.Entry(self.register, font=("Colibri", 18), bootstyle="warning", )
        self.kernev_input.grid(row=3, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(self.register, text="Email cím", font=("Colibri", 12), style="Custom.TLabel").grid(row=4, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.email_input = ttk.Entry(self.register, font=("Colibri", 18), bootstyle="warning")
        self.email_input.grid(row=5, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(self.register, text="Jelszó", font=("Colibri", 12), style="Custom.TLabel").grid(row=6, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.jelszo_input = ttk.Entry(self.register, show="*", font=("Colibri", 18), bootstyle="warning")
        self.jelszo_input.grid(row=7, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(self.register, text="Jelszó megerősítése", font=("Colibri", 12), style="Custom.TLabel").grid(row=8, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.jelszo_megerosites_input = ttk.Entry(self.register, show="*", font=("Colibri", 18), bootstyle="warning")
        self.jelszo_megerosites_input.grid(row=9, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Button(self.register,
                   text="Tovább",
                   command=self.registration_1,
                   style="lightbutton.TButton",
                   width=8,
                   cursor="hand2",
                   takefocus=False).grid(row=10, column=0, padx=(30, 30), pady=(30, 25), sticky="sn")
        ttk.Button(self.register,
                   text="Vissza",
                   command=self.app.back,
                   style="darkbutton.TButton",
                   width=8,
                   cursor="hand2",
                   takefocus=False).grid(row=11, column=0, padx=(30, 30), pady=(10, 35), sticky="sn")


    def registration_1(self):
        """
        Regisztráció első lépésének feldolgozása.

        Bekéri és ellenőrzi az alapvető felhasználói adatokat:
        - vezetéknév
        - keresztnév
        - email (ellenőrzi, hogy nem létezik-e már)
        - jelszó és jelszó megerősítés
        """
        veznev = self.veznev_input.get()
        kernev = self.kernev_input.get()
        email = self.email_input.get()
        jelszo = self.jelszo_input.get()
        jelszo_megerosites = self.jelszo_megerosites_input.get()

        if not veznev or not kernev or not email or not jelszo or not jelszo_megerosites:
            self.app.custom_messagebox("Hiányzó adatok", "Kérlek, töltsd ki az összes mezőt!")
            return

        if not self.is_valid_email(email):
            self.app.custom_messagebox("Hibás email", "Kérlek, adj meg egy érvényes email címet!")
            return

        if jelszo != jelszo_megerosites:
            self.app.custom_messagebox("Hibás jelszó", "A jelszavak nem egyeznek!")
            return

        self.app.db_cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
        existing_email = self.app.db_cursor.fetchone()
        
        if existing_email:
            self.app.custom_messagebox("Hiba", "Ez az email cím már regisztrálva van!")
            return

        self.vezeteknev = veznev
        self.keresztnev = kernev
        self.email = email
        self.jelszo = jelszo
        self.app.clear_screen()
        self.register_data_2()


    # 2

    def register_data_2(self):
        """
        Regisztráció második lépésének felülete.

        Bekéri a felhasználó fizikai adatait:
        - életkor
        - magasság
        - testsúly
        - nem
        - aktivitási szint
        """
        self.app.screen_stack.append(self.register_data_1)
        
        self.label_box()

        vcmd = (self.app.root.register(str.isdigit), '%P')

        ttk.Label(self.register, text="Életkor", font=("Colibri", 12), style="Custom.TLabel").grid(row=0, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.eletkor_input = ttk.Entry(self.register, font=("Colibri", 18), bootstyle="warning", validate='key', validatecommand=vcmd)
        self.eletkor_input.grid(row=1, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(self.register, text="Magasság (cm)", font=("Colibri", 12), style="Custom.TLabel").grid(row=2, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.magassag_input = ttk.Entry(self.register, font=("Colibri", 18), bootstyle="warning", validate='key', validatecommand=vcmd)
        self.magassag_input.grid(row=3, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(self.register, text="Testsúly (kg)", font=("Colibri", 12), style="Custom.TLabel").grid(row=4, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.testsuly_input = ttk.Entry(self.register, font=("Colibri", 18), bootstyle="warning", validate='key', validatecommand=vcmd)
        self.testsuly_input.grid(row=5, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(self.register, text="Nem", font=("Colibri", 12), style="Custom.TLabel").grid(row=6, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        goals = ["Férfi", "Nő"]
        self.default_value = ttk.StringVar(self.register)
        self.default_value.set("")
        self.nem_input = ttk.Combobox(self.register, textvariable=self.default_value, values=goals, state="readonly", font=("Colibri", 18), bootstyle="warning")
        self.nem_input.grid(row=7, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")
        self.nem_input.configure(width=19)

        ttk.Label(self.register, text="Aktivitás", font=("Colibri", 12), style="Custom.TLabel").grid(row=8, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        goals = ["Csekély", "Mérsékelt", "Közepes", "Átlagon felüli", "Nagyon magas"]
        self.default_value = ttk.StringVar(self.register)
        self.default_value.set("")
        self.aktivitas_input = ttk.Combobox(self.register, textvariable=self.default_value, values=goals, state="readonly", font=("Colibri", 18), bootstyle="warning")
        self.aktivitas_input.grid(row=9, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")
        self.aktivitas_input.configure(width=19)

        ttk.Button(self.register,
                   text="Regisztráció",
                   command=self.registration_2,
                   style="lightbutton.TButton",
                   width=10,
                   cursor="hand2",
                   takefocus=False).grid(row=10, column=0, padx=(30, 30), pady=(30, 25), sticky="sn")
        ttk.Button(self.register,
                   text="Vissza",
                   command=self.app.back,
                   style="darkbutton.TButton",
                   width=8,
                   cursor="hand2",
                   takefocus=False).grid(row=11, column=0, padx=(30, 30), pady=(10, 35), sticky="sn")

    def registration_2(self):
        """
        Regisztráció második lépésének feldolgozása.
        
        Ellenőrzi és elmenti az adatbázisba a felhasználó fizikai adatait:
        - életkor
        - magasság
        - testsúly
        - nem
        - aktivitási szint
        
        Sikeres mentés esetén átirányít a bejelentkező oldalra.
        """
        eletkor = self.eletkor_input.get()
        magassag = self.magassag_input.get()
        testsuly = self.testsuly_input.get()
        nem = self.nem_input.get()
        aktivitas = self.aktivitas_input.get()

        if not eletkor or not magassag or not testsuly or not nem or not aktivitas:
            self.app.custom_messagebox("Hiányzó adatok", "Kérlek, töltsd ki az összes mezőt!")
            return

        try:
            self.app.db_cursor.execute('''
                INSERT INTO users (vezeteknev, keresztnev, email, jelszo, eletkor, magassag, testsuly, nem, aktivitas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.vezeteknev, self.keresztnev, self.email, self.jelszo, eletkor, magassag, testsuly, nem, aktivitas))
            self.app.db_connection.commit()
            self.app.custom_messagebox("Sikeres regisztráció", "A regisztráció sikeres volt!", login=True)

        except Exception as e:
            self.app.custom_messagebox("Hiba", f"Hiba történt: {e}")


    # BEJELENTKEZÉS ----------------------

    def login_page(self):
        """
        Bejelentkező oldal megjelenítése.
        
        Tartalmaz:
        - Email cím beviteli mező
        - Jelszó beviteli mező (rejtett)
        - Tovább gomb a bejelentkezéshez
        - Vissza gomb a kezdőoldalra
        
        A bejelentkezési adatokat a login_check függvény ellenőrzi.
        """
        self.app.clear_screen()
        self.app.screen_stack.append(self.login_or_register)
        self.label_box()
        self.label_widget.configure(text="Jelentkezz be!")

        ttk.Label(self.register, text="Email cím", font=("Colibri", 12), style="Custom.TLabel").grid(row=0, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.email_input_login = ttk.Entry(self.register, font=("Colibri", 18), bootstyle="warning")
        self.email_input_login.grid(row=1, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Label(self.register, text="Jelszó", font=("Colibri", 12), style="Custom.TLabel").grid(row=2, column=0, padx=(30, 30), pady=(15, 5), sticky="sw")
        self.jelszo_input_login = ttk.Entry(self.register, show="*", font=("Colibri", 18), bootstyle="warning")
        self.jelszo_input_login.grid(row=3, column=0, padx=(30, 30), pady=(0, 20), sticky="nw")

        ttk.Button(self.register, text="Tovább", command=self.login_check, style="lightbutton.TButton", width=8, cursor="hand2", takefocus=False).grid(row=4, column=0, padx=(30, 30), pady=(30, 25), sticky="sn")
        ttk.Button(self.register, text="Vissza", command=self.app.back, style="darkbutton.TButton", width=8, cursor="hand2", takefocus=False).grid(row=5, column=0, padx=(30, 30), pady=(10, 35), sticky="sn")

    def login_check(self):
        """
        Bejelentkezési adatok ellenőrzése.

        Ellenőrzi:
        - Az email cím és jelszó páros létezik-e az adatbázisban
        - A megadott adatok helyesek-e
        
        Sikeres bejelentkezés esetén:
        - Elmenti a bejelentkezett felhasználó adatait
        - Átirányít a főoldalra
        
        Sikertelen bejelentkezés esetén hibaüzenetet jelenít meg.
        """
        email = self.email_input_login.get()
        jelszo = self.jelszo_input_login.get()

        self.app.db_cursor.execute('SELECT * FROM users WHERE email = ? AND jelszo = ?', (email, jelszo))
        user = self.app.db_cursor.fetchone()

        if user:
            self.app.logged_in_user = email
            self.app.user_id = user[0]
            self.app.custom_messagebox("Sikeres bejelentkezés", "Sikeres bejelentkezés!", diet=True)
        else:
            self.app.custom_messagebox("Hibás bejelentkezés", "Az email cím vagy jelszó nem helyes!")

    def profile_page(self):
        """
        Profil oldal megjelenítése.
        
        Megjeleníti a felhasználó adatait:
        - Személyes adatok (vezetéknév, keresztnév)
        - Fizikai adatok (kor, magasság, súly)
        - Aktivitási szint
        
        Lehetőséget ad az adatok módosítására és mentésére.
        """
        self.app.clear_screen()
        self.app.load_navigation_bar()

        self.app.db_cursor.execute(
            'SELECT vezeteknev, keresztnev, email, eletkor, magassag, testsuly, nem, aktivitas FROM users WHERE email = ?', 
            (self.app.logged_in_user,)
            )
        user_data = self.app.db_cursor.fetchone()

        if user_data:
            vezeteknev, keresztnev, email, eletkor, magassag, testsuly, nem, aktivitas = user_data

            user_info_frame = ttk.Labelframe(
                self.app.root,
                labelwidget=ttk.Label(self.app.root,
                                      text="Felhasználói adatok",
                                      font=("Colibri", 20),
                                      style="Custom.TLabelframe.Label"),
                                      bootstyle="light")
            user_info_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            fields = {"Vezetéknév": vezeteknev,
                      "Keresztnév": keresztnev,
                      "Életkor": eletkor,
                      "Magasság (cm)": magassag,
                      "Testsúly (kg)": testsuly,}

            original_data = fields.copy()
            original_data["Aktivitás"] = aktivitas

            self.entries = {}
            self.activity_combobox = None

            for idx, (label_text, default_value) in enumerate(fields.items()):
                ttk.Label(user_info_frame,
                          text=label_text,
                          font=("Colibri", 14)).grid(row=idx, column=0, padx=20, pady=10, sticky="w")

                entry_var = ttk.StringVar(value=default_value)
                entry = ttk.Entry(user_info_frame,
                                  font=("Colibri", 14),
                                  width=20,
                                  textvariable=entry_var,
                                  state='readonly')
                entry.grid(row=idx, column=1, padx=20, pady=10, sticky="we")

                self.entries[label_text] = (entry, entry_var)

            ttk.Label(user_info_frame,
                      text="Aktivitás",
                      font=("Colibri", 14)).grid(row=len(fields) + 1, column=0, padx=20, pady=10, sticky="w")

            activity_var = ttk.StringVar(value=aktivitas)
            activity_entry = ttk.Entry(user_info_frame,
                                       font=("Colibri", 14),
                                       width=20,
                                       textvariable=activity_var,
                                       state='readonly')
            activity_entry.grid(row=len(fields) + 1, column=1, padx=20, pady=10, sticky="we")
            self.entries["Aktivitás"] = (activity_entry, activity_var)

            def enable_editing():
                for entry, _ in self.entries.values():
                    entry.config(state='normal')
                activity_entry.grid_forget()

                self.activity_combobox = ttk.Combobox(user_info_frame,
                                                      font=("Colibri", 14),
                                                      width=18,
                                                      textvariable=activity_var,
                                                      state='readonly',
                                                      values=list(self.app.activity_factors.keys()))
                self.activity_combobox.grid(row=len(fields) + 1, column=1, padx=20, pady=10, sticky="we")

                self.entries["Aktivitás"] = (self.activity_combobox, activity_var)

                modify_button.grid_forget()
                save_button.grid(row=len(fields) + 2, column=1, pady=20, padx=20, sticky="e")
                cancel_button.grid(row=len(fields) + 2, column=0, pady=20, padx=20, sticky="w")

            modify_button = ttk.Button(user_info_frame,
                                       text="Módosítás",
                                       style="darkbutton.TButton",
                                       command=enable_editing,
                                       cursor="hand2",
                                       takefocus=False)
            modify_button.grid(row=len(fields) + 2, column=0, pady=20, padx=20, sticky="w")

            def save_changes():
                updated_data = {label: var.get() for label, (entry, var) in self.entries.items()}

                if not (updated_data["Életkor"].isdigit() and
                        updated_data["Magasság (cm)"].isdigit() and
                        updated_data["Testsúly (kg)"].isdigit()):
                    self.app.custom_messagebox("Hiba", "Érvénytelen adatokat adtál meg!", profile=True)
                    return

                self.app.db_cursor.execute(""" 
                    UPDATE users 
                    SET vezeteknev = ?, keresztnev = ?, eletkor = ?, 
                        magassag = ?, testsuly = ?, aktivitas = ? 
                    WHERE email = ? 
                """, (
                    updated_data["Vezetéknév"],
                    updated_data["Keresztnév"],
                    updated_data["Életkor"],
                    updated_data["Magasság (cm)"],
                    updated_data["Testsúly (kg)"],
                    updated_data["Aktivitás"],
                    email
                ))
                self.app.db_connection.commit()
                self.app.custom_messagebox("Siker", "Az adatok sikeresen frissültek!", profile=True)

            save_button = ttk.Button(user_info_frame,
                                     text="Mentés",
                                     style="darkbutton.TButton",
                                     command=save_changes,
                                     cursor="hand2",
                                     takefocus=False)
            save_button.grid_forget()

            def cancel_changes():
                for label, (entry, var) in self.entries.items():
                    var.set(original_data[label])
                    entry.config(state='readonly')

                if self.activity_combobox:
                    self.activity_combobox.grid_forget()
                    
                    activity_entry = ttk.Entry(user_info_frame,
                                               font=("Colibri", 14),
                                               width=20,
                                               textvariable=self.entries["Aktivitás"][1],
                                               state='readonly')
                    activity_entry.grid(row=len(fields) + 1, column=1, padx=20, pady=10, sticky="w")

                    self.entries["Aktivitás"] = (activity_entry, self.entries["Aktivitás"][1])

                save_button.grid_forget()
                cancel_button.grid_forget()
                modify_button.grid(row=len(fields) + 2, column=0, pady=20, padx=20, sticky="w") 
            cancel_button = ttk.Button(user_info_frame,
                                       text="Mégse",
                                       style="darkbutton.TButton",
                                       command=cancel_changes,
                                       cursor="hand2",
                                       takefocus=False)
            cancel_button.grid_forget()

    def logout(self):
        """
        Kijelentkezés kezelése.
        - Törli a képernyőt
        - Nullázza a bejelentkezett felhasználó adatait
        - Megjeleníti a bejelentkező képernyőt
        """
        self.app.clear_screen()
        self.app.logged_in_user = None
        self.app.user_id = None
        self.login_or_register()