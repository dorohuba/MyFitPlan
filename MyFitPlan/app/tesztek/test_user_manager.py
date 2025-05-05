import unittest
from unittest.mock import MagicMock, patch
from app.user_manager import UserManager

class TestUserManager(unittest.TestCase):
    
    def setUp(self):
        """Teszt környezet előkészítése"""
        self.mock_app = MagicMock()
        self.mock_app.screen_stack = MagicMock()
        self.mock_app.clear_screen = MagicMock()
        self.mock_app.root = MagicMock()
        self.user_manager = UserManager(self.mock_app)

    def test_login_or_register(self):
        """Login/Register oldal tesztelése"""
        with patch('ttkbootstrap.Labelframe') as mock_labelframe, \
             patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Button') as mock_button:
            
            mock_frame = MagicMock()
            mock_labelframe.return_value = mock_frame
            
            self.user_manager.login_or_register()
            
            mock_labelframe.assert_called_once()
            self.assertEqual(mock_button.call_count, 3)
            
            button_calls = mock_button.call_args_list
            commands = [call[1]['command'] for call in button_calls]
            
            self.assertIn(self.user_manager.login_page, commands)
            self.assertIn(self.user_manager.register_data_1, commands)
            self.assertIn(self.mock_app.root.quit, commands)

    def test_label_box(self):
        test_text = "Test Label"
        with patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Labelframe') as mock_labelframe:
            
            self.user_manager.label_box(test_text)
            
            mock_label.assert_called_once()
            mock_labelframe.assert_called_once()
            
            label_args = mock_label.call_args[1]
            self.assertEqual(label_args['text'], test_text)

    def test_register_data_1(self):
        """Regisztráció első oldal tesztelése"""
        with patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Entry') as mock_entry, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Labelframe') as mock_labelframe:
            
            self.mock_app.root = MagicMock()
            mock_register = MagicMock()
            mock_labelframe.return_value = mock_register
            
            def mock_label_box(text="Töltsd ki az adatokat!"):
                self.user_manager.register = mock_register
            self.user_manager.label_box = mock_label_box
            
            self.user_manager.register_data_1()
            
            self.mock_app.clear_screen.assert_called_once()
            self.mock_app.screen_stack.append.assert_called_once_with(self.user_manager.login_or_register)
            
            self.assertEqual(mock_label.call_count, 5)
            self.assertEqual(mock_entry.call_count, 5)
            self.assertEqual(mock_button.call_count, 2)

    def test_register_data_2(self):
        """Regisztráció második oldalának tesztelése"""
        with patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Entry') as mock_entry, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Labelframe') as mock_labelframe, \
             patch('ttkbootstrap.Combobox') as mock_combobox:
            
            self.mock_app.root = MagicMock()
            self.mock_app.clear_screen = MagicMock()
            
            mock_register = MagicMock()
            mock_labelframe.return_value = mock_register
            
            def mock_label_box(text="Töltsd ki az adatokat!"):
                self.user_manager.register = mock_register
                
            self.user_manager.label_box = mock_label_box

            self.user_manager.register_data_1 = MagicMock()
            
            self.user_manager.register_data_2()
            
            self.mock_app.screen_stack.append.assert_called_once_with(self.user_manager.register_data_1)
            
            self.assertEqual(mock_label.call_count, 5)
            self.assertEqual(mock_entry.call_count, 3)
            self.assertEqual(mock_combobox.call_count, 2)
            self.assertEqual(mock_button.call_count, 2)

            vcmd_calls = self.mock_app.root.register.call_args_list
            self.assertEqual(len(vcmd_calls), 1)
            self.assertEqual(vcmd_calls[0][0][0], str.isdigit)

    def test_registration_1(self):
        """Regisztráció első lépésének tesztelése"""
        self.user_manager.veznev_input = MagicMock()
        self.user_manager.kernev_input = MagicMock()
        self.user_manager.email_input = MagicMock()
        self.user_manager.jelszo_input = MagicMock()
        self.user_manager.jelszo_megerosites_input = MagicMock()
        
        self.user_manager.register_data_2 = MagicMock()

        #1. Eset: Hiányzó adatok
        self.user_manager.veznev_input.get.return_value = ""
        self.user_manager.registration_1()
        self.mock_app.custom_messagebox.assert_called_with("Hiányzó adatok", "Kérlek, töltsd ki az összes mezőt!")

        #2. Eset: Nem egyező jelszavak
        self.user_manager.veznev_input.get.return_value = "Teszt"
        self.user_manager.kernev_input.get.return_value = "Elek"
        self.user_manager.email_input.get.return_value = "teszt@example.com"
        self.user_manager.jelszo_input.get.return_value = "password123"
        self.user_manager.jelszo_megerosites_input.get.return_value = "password456"
        
        self.user_manager.registration_1()
        self.mock_app.custom_messagebox.assert_called_with("Hibás jelszó", "A jelszavak nem egyeznek!")

        #3. Eset: Létező email
        self.user_manager.jelszo_megerosites_input.get.return_value = "password123"
        self.mock_app.db_cursor.fetchone.return_value = ["teszt@example.com"]
        
        self.user_manager.registration_1()
        self.mock_app.custom_messagebox.assert_called_with("Hiba", "Ez az email cím már regisztrálva van!")

        #4. Eset: Sikeres regisztráció
        self.mock_app.db_cursor.fetchone.return_value = None
        
        self.user_manager.registration_1()
        
        self.assertEqual(self.user_manager.vezeteknev, "Teszt")
        self.assertEqual(self.user_manager.keresztnev, "Elek")
        self.assertEqual(self.user_manager.email, "teszt@example.com")
        self.assertEqual(self.user_manager.jelszo, "password123")
        
        self.mock_app.clear_screen.assert_called()
        self.user_manager.register_data_2.assert_called_once()

    def test_registration_2(self):
        """Regisztráció második lépésének tesztelése"""
        self.user_manager.eletkor_input = MagicMock()
        self.user_manager.magassag_input = MagicMock()
        self.user_manager.testsuly_input = MagicMock()
        self.user_manager.nem_input = MagicMock()
        self.user_manager.aktivitas_input = MagicMock()
        
        self.user_manager.vezeteknev = "Teszt"
        self.user_manager.keresztnev = "Elek"
        self.user_manager.email = "teszt@example.com"
        self.user_manager.jelszo = "password123"

        #1. Eset: Hiányzó adatok
        self.user_manager.eletkor_input.get.return_value = ""
        self.user_manager.registration_2()
        self.mock_app.custom_messagebox.assert_called_with("Hiányzó adatok", "Kérlek, töltsd ki az összes mezőt!")

        #2. Eset: Sikeres regisztráció
        self.user_manager.eletkor_input.get.return_value = "25"
        self.user_manager.magassag_input.get.return_value = "180"
        self.user_manager.testsuly_input.get.return_value = "75"
        self.user_manager.nem_input.get.return_value = "Férfi"
        self.user_manager.aktivitas_input.get.return_value = "Közepes"
        
        self.user_manager.registration_2()
        
        self.mock_app.db_cursor.execute.assert_called_with('''
                INSERT INTO users (vezeteknev, keresztnev, email, jelszo, eletkor, magassag, testsuly, nem, aktivitas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("Teszt", "Elek", "teszt@example.com", "password123", "25", "180", "75", "Férfi", "Közepes"))
        
        self.mock_app.db_connection.commit.assert_called_once()
        self.mock_app.custom_messagebox.assert_called_with("Sikeres regisztráció", "A regisztráció sikeres volt!", login=True)

        #3. Eset: Adatbázis hiba
        self.mock_app.db_cursor.execute.side_effect = Exception("DB Error")
        self.user_manager.registration_2()
        self.mock_app.custom_messagebox.assert_called_with("Hiba", "Hiba történt: DB Error")

    def test_login_page(self):
        """Bejelentkező oldal tesztelése"""
        with patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Entry') as mock_entry, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Labelframe') as mock_labelframe:
            
            self.mock_app.root = MagicMock()
            mock_register = MagicMock()
            mock_labelframe.return_value = mock_register
            
            def mock_label_box(text="Jelentkezz be!"):
                self.user_manager.register = mock_register
                self.user_manager.label_widget = MagicMock()
            self.user_manager.label_box = mock_label_box
            
            self.user_manager.login_page()
            
            self.mock_app.clear_screen.assert_called_once()
            self.mock_app.screen_stack.append.assert_called_once_with(self.user_manager.login_or_register)
            
            self.user_manager.label_widget.configure.assert_called_once_with(text="Jelentkezz be!")
            
            self.assertEqual(mock_label.call_count, 2)
            self.assertEqual(mock_entry.call_count, 2)
            self.assertEqual(mock_button.call_count, 2)

    def test_login_check(self):
        """Bejelentkezés ellenőrzés tesztelése"""
        self.user_manager.email_input_login = MagicMock()
        self.user_manager.jelszo_input_login = MagicMock()
        
        #1. Eset: Sikertelen bejelentkezés
        self.user_manager.email_input_login.get.return_value = "teszt@example.com"
        self.user_manager.jelszo_input_login.get.return_value = "password123"
        self.mock_app.db_cursor.fetchone.return_value = None
        
        self.user_manager.login_check()
        
        self.mock_app.db_cursor.execute.assert_called_with('SELECT * FROM users WHERE email = ? AND jelszo = ?',
                                                           ("teszt@example.com", "password123") )
        self.mock_app.custom_messagebox.assert_called_with("Hibás bejelentkezés", "Az email cím vagy jelszó nem helyes!")
        
        #2. Eset: Sikeres bejelentkezés
        test_user = [1, "Teszt", "Elek", "teszt@example.com", "password123"]
        self.mock_app.db_cursor.fetchone.return_value = test_user
        
        self.user_manager.login_check()
        
        self.assertEqual(self.mock_app.logged_in_user, "teszt@example.com")
        self.assertEqual(self.mock_app.user_id, 1)
        self.mock_app.custom_messagebox.assert_called_with( "Sikeres bejelentkezés", "Sikeres bejelentkezés!", diet=True)

    def test_profile_page(self):
        """Profil oldal tesztelése"""
        with patch('ttkbootstrap.Labelframe') as mock_labelframe, \
             patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Entry') as mock_entry, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Combobox') as mock_combobox, \
             patch('ttkbootstrap.StringVar') as mock_stringvar:
            
            self.mock_app.root = MagicMock()
            self.mock_app.logged_in_user = "teszt@example.com"
            
            initial_data = ["Teszt", "Elek", "teszt@example.com", "25", "180", "75", "Férfi", "Közepes"]
            self.mock_app.db_cursor.fetchone.return_value = initial_data
            
            mock_var = MagicMock()
            mock_stringvar.return_value = mock_var
            mock_entry_instance = MagicMock()
            mock_entry.return_value = mock_entry_instance
            
            self.user_manager.profile_page()
            
            #1. Betöltés tesztelése
            self.mock_app.clear_screen.assert_called_once()
            self.mock_app.load_navigation_bar.assert_called_once()
            
            self.mock_app.db_cursor.execute.assert_called_with(
                'SELECT vezeteknev, keresztnev, email, eletkor, magassag, testsuly, nem, aktivitas FROM users WHERE email = ?',
                ("teszt@example.com",))
            
            mock_labelframe.assert_called()
            self.assertGreater(mock_label.call_count, 0)
            self.assertGreater(mock_entry.call_count, 0)
            self.assertGreater(mock_button.call_count, 0)
            self.assertGreater(mock_stringvar.call_count, 0)
            
            #2. Módosítás tesztelése
            new_data = {"Vezetéknév": "Új",
                        "Keresztnév": "Név",
                        "Életkor": "30",
                        "Magasság (cm)": "185",
                        "Testsúly (kg)": "80",
                        "Aktivitás": "Átlagon felüli"}
            
            self.user_manager.entries = {}
            for field, value in new_data.items():
                entry_mock = MagicMock()
                var_mock = MagicMock()
                var_mock.get.return_value = value
                self.user_manager.entries[field] = (entry_mock, var_mock)
            
            for call in mock_button.call_args_list:
                if call[1].get('text') == 'Mentés':
                    save_function = call[1]['command']
                    save_function()
                    break
            
            expected_sql = """UPDATE users 
                SET vezeteknev = ?, keresztnev = ?, eletkor = ?, magassag = ?, testsuly = ?, aktivitas = ? WHERE email = ?"""
            expected_params = ("Új", "Név", "30", "185", "80", "Átlagon felüli", "teszt@example.com")
            
            calls = self.mock_app.db_cursor.execute.call_args_list
            found = False
            for call in calls:
                normalized_sql = ' '.join(call[0][0].split())
                normalized_expected = ' '.join(expected_sql.split())
                if normalized_sql == normalized_expected and call[0][1] == expected_params:
                    found = True
                    break
            
            self.assertTrue(found, "A várt SQL művelet nem található a hívások között")
            self.mock_app.db_connection.commit.assert_called()
            self.mock_app.custom_messagebox.assert_called_with("Siker", "Az adatok sikeresen frissültek!", profile=True)

    def test_logout(self):
        """Kijelentkezés tesztelése"""
        self.mock_app.logged_in_user = "teszt@example.com"
        self.mock_app.user_id = 1
        
        self.user_manager.login_or_register = MagicMock()
        
        self.user_manager.logout()
        
        self.mock_app.clear_screen.assert_called_once()
        self.assertIsNone(self.mock_app.logged_in_user)
        self.assertIsNone(self.mock_app.user_id)
        self.user_manager.login_or_register.assert_called_once()

    def test_is_valid_email(self):
        """Email cím tesztelése"""
        valid_emails = [
            "teszt@teszt.hu",
            "teszt.elek@teszt.hu",
            "teszt+elek@teszt.hu",
            "teszt123@teszt.gov.hu",
            "teszt.elek-123@sub.teszt.hu"
        ]
        
        invalid_emails = [
            "",
            "teszt",
            "@teszt.hu",
            "teszt@",
            "teszt@.hu",
            "teszt@teszt",
            "teszt@te szt.hu",
            "teszt elek@teszt.hu",
            "teszt@teszt..hu",
            ".teszt@teszt.hu",
        ]

        for email in valid_emails:
            self.assertTrue(
                self.user_manager.is_valid_email(email),
                f"Az email címnek érvényesnek kellene lennie: {email}"
            )

        for email in invalid_emails:
            self.assertFalse(
                self.user_manager.is_valid_email(email),
                f"Az email címnek érvénytelennek kellene lennie: {email}"
            )

if __name__ == '__main__':
    unittest.main()

"""  python -m unittest app/tesztek/test_user_manager.py
     coverage run -m unittest app/tesztek/test_user_manager.py
     coverage report
"""