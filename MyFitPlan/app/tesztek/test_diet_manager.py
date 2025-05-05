import unittest
from unittest.mock import MagicMock, patch
from app.diet_manager import DietManager

class TestDietManager(unittest.TestCase):

    def setUp(self):
        """Teszt környezet előkészítése"""
        self.mock_app = MagicMock()
        self.diet_manager = DietManager(self.mock_app)

    def test_user_data_loading(self):
        """Felhasználó adatainak betöltés tesztelése"""
        self.mock_app.logged_in_user = "teszt@example.com"
        self.mock_app.user_id = 1
        self.mock_app.root = MagicMock()
        self.mock_app.activity_factors = {"Közepes": 1.55}

        def mock_execute(query, *args):
            if 'SELECT eletkor, magassag' in query:
                self.mock_app.db_cursor.fetchone.return_value = ("25", "180", "75", "Férfi", "Közepes")

            else:
                self.mock_app.db_cursor.fetchone.return_value = None
            return self.mock_app.db_cursor

        self.mock_app.db_cursor.execute = MagicMock(side_effect=mock_execute)
        
        with patch('ttkbootstrap.Frame', return_value=MagicMock()) as mock_frame, \
             patch('ttkbootstrap.Meter', return_value=MagicMock()) as mock_meter, \
             patch('ttkbootstrap.Label', return_value=MagicMock()) as mock_label, \
             patch('ttkbootstrap.Treeview', return_value=MagicMock()) as mock_treeview, \
             patch('ttkbootstrap.DateEntry', return_value=MagicMock()) as mock_dateentry, \
             patch('ttkbootstrap.Button', return_value=MagicMock()) as mock_button, \
             patch('ttkbootstrap.PanedWindow', return_value=MagicMock()) as mock_panedwindow:
            
            mock_date_entry = MagicMock()
            mock_date_entry.entry = MagicMock()
            mock_date_entry.entry.get.return_value = "2024-01-01"
            mock_dateentry.return_value = mock_date_entry
            
            self.diet_manager.diet_page()
            
            self.mock_app.db_cursor.execute.assert_any_call(
                'SELECT eletkor, magassag, testsuly, nem, aktivitas FROM users WHERE email = ?', 
                (self.mock_app.logged_in_user,))
            
            expected_bmr = 10 * 75 + 6.25 * 180 - 5 * 25 + 5
            expected_tdee = expected_bmr * 1.55
            self.assertEqual(self.mock_app.tdee, expected_tdee)

    def test_ui_elements(self):
        """UI elemek létrehozásának tesztelése"""
        with patch('ttkbootstrap.Frame') as mock_frame, \
             patch('ttkbootstrap.Meter') as mock_meter, \
             patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Treeview') as mock_treeview, \
             patch('ttkbootstrap.DateEntry') as mock_dateentry, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.PanedWindow') as mock_panedwindow:

            self.mock_app.root = MagicMock()
            self.mock_app.logged_in_user = "teszt@example.com"
            self.mock_app.tdee = 2000
            self.mock_app.db_cursor.fetchone.return_value = ("25", "180", "75", "Férfi", "Közepes")


            mock_meter_instance = MagicMock()
            mock_meter.return_value = mock_meter_instance
            
            self.diet_manager.diet_page()

            self.mock_app.clear_screen.assert_called_once()
            self.mock_app.load_navigation_bar.assert_called_once()

            mock_meter.assert_called_once()
            self.assertGreater(mock_frame.call_count, 0)
            self.assertGreater(mock_label.call_count, 0)
            self.assertEqual(mock_dateentry.call_count, 1)
            self.assertGreater(mock_button.call_count, 0)

    def test_table_creation(self):
        """Táblázatok létrehozásának tesztelése"""
        self.mock_app.root = MagicMock()
        self.mock_app.logged_in_user = "teszt@example.com"
        self.mock_app.db_cursor.fetchone.return_value = ("25", "180", "75", "Férfi", "Közepes")

        
        with patch('ttkbootstrap.Frame', return_value=MagicMock()) as mock_frame, \
             patch('ttkbootstrap.Meter', return_value=MagicMock()) as mock_meter, \
             patch('ttkbootstrap.Label', return_value=MagicMock()) as mock_label, \
             patch('ttkbootstrap.Treeview', return_value=MagicMock()) as mock_treeview, \
             patch('ttkbootstrap.DateEntry', return_value=MagicMock()) as mock_dateentry, \
             patch('ttkbootstrap.Button', return_value=MagicMock()) as mock_button, \
             patch('ttkbootstrap.PanedWindow', return_value=MagicMock()) as mock_panedwindow:
            
            mock_box = MagicMock()
            self.mock_app.box1 = mock_box
            self.mock_app.box2 = mock_box
            self.mock_app.box3 = mock_box
            self.mock_app.box4 = mock_box

            self.diet_manager.diet_page()

            self.assertEqual(mock_treeview.call_count, 4)
            
            calls = mock_treeview.call_args_list
            for call in calls:
                self.assertEqual(
                    call[1]['columns'], 
                    ("Étel", "Kcal", "g/ml"))
                self.assertEqual(call[1]['show'], "headings")

    def test_load_user_meals(self):
        """Felhasználó étkezéseinek betöltése tesztelése"""
        self.mock_app.breakfast_table = MagicMock()
        self.mock_app.lunch_table = MagicMock()
        self.mock_app.dinner_table = MagicMock()
        self.mock_app.other_table = MagicMock()
        
        self.mock_app.user_id = 1
        test_date = "2025-01-01"
        
        test_meals = [("breakfast_table", "Tojásrántotta", 300, 200),
                      ("lunch_table", "Csirkemell", 500, 300),
                      ("dinner_table", "Tonhalsaláta", 400, 250),
                      ("other_table", "Gyümölcs", 100, 150)]
        self.mock_app.db_cursor.fetchall.return_value = test_meals
        
        self.diet_manager.load_user_meals(test_date)
        
        expected_query = "SELECT table_name, food_name, calories, amount FROM users_meals WHERE user_id = ? AND date = ?"
        self.mock_app.db_cursor.execute.assert_called_with(
            expected_query, 
            (self.mock_app.user_id, test_date))
        
        self.mock_app.breakfast_table.delete.assert_called()
        self.mock_app.lunch_table.delete.assert_called()
        self.mock_app.dinner_table.delete.assert_called()
        self.mock_app.other_table.delete.assert_called()
        
        self.mock_app.breakfast_table.insert.assert_called_with("", "end", values=("Tojásrántotta", "300 kcal", 200))
        self.mock_app.lunch_table.insert.assert_called_with("", "end", values=("Csirkemell", "500 kcal", 300))
        self.mock_app.dinner_table.insert.assert_called_with("", "end", values=("Tonhalsaláta", "400 kcal", 250))
        self.mock_app.other_table.insert.assert_called_with("", "end", values=("Gyümölcs", "100 kcal", 150))

    def test_update_meter(self):
        """Kalória mérő frissítésének tesztelése"""
        self.mock_app.meter = MagicMock()
        self.mock_app.date_entry = MagicMock()
        self.mock_app.date_entry.entry = MagicMock()
        self.mock_app.date_entry.entry.get.return_value = "2025-01-01"
        self.mock_app.user_id = 1
        self.mock_app.tdee = 2000

        #1. Eset: Alacsony kalória bevitel (<75%)
        test_meals_low = [(1, 350, "2025-01-01")]
        self.mock_app.db_cursor.fetchall.return_value = test_meals_low
        
        self.diet_manager.update_meter()
        
        total_calories = 350
        self.mock_app.meter.configure.assert_any_call(amountused=total_calories)
        self.mock_app.meter.configure.assert_any_call(bootstyle="primary")

        #2. Eset: Közepes kalória bevitel (75-100%)
        test_meals_medium = [(1, 1500, "2025-01-01")]
        self.mock_app.db_cursor.fetchall.return_value = test_meals_medium
        
        self.diet_manager.update_meter()
        
        self.mock_app.meter.configure.assert_any_call(amountused=1500)
        self.mock_app.meter.configure.assert_any_call(bootstyle="warning")

        #3. Eset: Magas kalória bevitel (>100%)
        test_meals_high = [(1, 2200, "2025-01-01")]  #Egy étkezés 2200 kalóriával
        self.mock_app.db_cursor.fetchall.return_value = test_meals_high
        
        self.diet_manager.update_meter()
        
        self.mock_app.meter.configure.assert_any_call(amountused=2200)
        self.mock_app.meter.configure.assert_any_call(bootstyle="danger")

    def test_add_food(self):
        """Étel hozzáadásának tesztelése"""
        mock_table = MagicMock()
        self.mock_app.user_id = 1
        self.mock_app.date_entry = MagicMock()
        self.mock_app.date_entry.entry = MagicMock()
        self.mock_app.date_entry.entry.get.return_value = "2025-01-01"
        self.mock_app.breakfast_table = mock_table

        with patch('ttkbootstrap.Toplevel') as mock_toplevel, \
            patch('ttkbootstrap.Label') as mock_label, \
            patch('ttkbootstrap.Entry') as mock_entry, \
            patch('ttkbootstrap.Button') as mock_button, \
            patch('ttkbootstrap.Combobox') as mock_combobox, \
            patch('ttkbootstrap.Spinbox') as mock_spinbox:

            popup_window = MagicMock()
            mock_toplevel.return_value = popup_window
            
            test_tables = ["Reggeli", "Ebéd", "Vacsora", "Egyéb"]
            self.mock_app.db_cursor.fetchall.return_value = [(table,) for table in test_tables]

            self.diet_manager.add_food(mock_table)

            mock_toplevel.assert_called_once()
            popup_window.title.assert_called_with("Étel hozzáadása")
            
            self.assertGreater(mock_label.call_count, 0)
            self.assertGreater(mock_combobox.call_count, 0)
            self.assertGreater(mock_entry.call_count, 0)
            self.assertGreater(mock_button.call_count, 0)
            self.assertGreater(mock_spinbox.call_count, 0)

            self.mock_app.db_cursor.execute.assert_called_with("SELECT name FROM sqlite_master WHERE type='table';")

    def test_load_food_options(self):
        """Étel opciók betöltésének tesztelése"""
        mock_event = MagicMock()
        mock_meal_type_var = MagicMock()
        
        mock_food_input = MagicMock()
        mock_custom_food_entry = MagicMock()
        mock_amount_label = MagicMock()

        self.diet_manager.food_input = mock_food_input
        self.diet_manager.custom_food_entry = mock_custom_food_entry
        self.diet_manager.amount_label = mock_amount_label

        #1. Eset: Egyéni étel kiválasztása
        mock_meal_type_var.get.return_value = "Egyéni"
        
        self.diet_manager.load_food_options(mock_event, mock_meal_type_var)
        
        mock_food_input.grid_remove.assert_called_once()
        mock_custom_food_entry.grid.assert_called_once()
        mock_amount_label.configure.assert_called_with(text="Kalória (kcal)")

        mock_food_input.reset_mock()
        mock_custom_food_entry.reset_mock()
        mock_amount_label.reset_mock()

        #2. Eset: Előre definiált ital kiválasztása
        mock_meal_type_var.get.return_value = "Italok"
        test_drinks = [("Víz", 0), ("Üdítő", 40)]
        self.mock_app.db_cursor.fetchall.return_value = test_drinks
        
        self.diet_manager.load_food_options(mock_event, mock_meal_type_var)
        
        mock_custom_food_entry.grid_remove.assert_called_once()
        mock_food_input.grid.assert_called_once()
        mock_amount_label.configure.assert_called_with(text="Mennyiség (g/ml)")
        mock_food_input.__setitem__.assert_called_with(
            'values', 
            ["Víz (0 kcal/100ml)", "Üdítő (40 kcal/100ml)"])

        mock_food_input.reset_mock()
        mock_custom_food_entry.reset_mock()
        mock_amount_label.reset_mock()

        #3. Eset: Előre definiált étel kiválasztása
        mock_meal_type_var.get.return_value = "Húsok"
        test_foods = [("Csirkemell", 165), ("Marha hús", 250)]
        self.mock_app.db_cursor.fetchall.return_value = test_foods
        
        self.diet_manager.load_food_options(mock_event, mock_meal_type_var)
        
        mock_custom_food_entry.grid_remove.assert_called_once()
        mock_food_input.grid.assert_called_once()
        mock_amount_label.configure.assert_called_with(text="Mennyiség (g/ml)")
        mock_food_input.__setitem__.assert_called_with(
            'values', 
            ["Csirkemell (165 kcal/100g)", "Marha hús (250 kcal/100g)"])
        
        self.mock_app.db_cursor.execute.assert_any_call('SELECT Név, Kalória FROM "Italok";')
        self.mock_app.db_cursor.execute.assert_any_call('SELECT Név, Kalória FROM "Húsok";')

if __name__ == '__main__':
    unittest.main()

"""  python -m unittest app/tesztek/test_diet_manager.py
     coverage run -m unittest app/tesztek/test_diet_manager.py
     coverage report
"""
