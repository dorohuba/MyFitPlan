import unittest
from unittest.mock import MagicMock, patch
from app.training_manager import TrainingManager

class TestTrainingManager(unittest.TestCase):

    def setUp(self):
        """Teszt környezet előkészítése"""
        self.mock_app = MagicMock()
        self.training_manager = TrainingManager(self.mock_app)

    def test_training_page(self):
        """Edzés oldal tesztelése"""
        with patch('ttkbootstrap.Frame') as mock_frame, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Treeview') as mock_treeview:

            self.mock_app.user_id = 1
            self.mock_app.root = MagicMock()

            def mock_execute(query, *args):
                if 'SELECT day_name' in query:
                    self.mock_app.db_cursor.fetchall.return_value = [("Hétfő",), ("Szerda",), ("Péntek",)]
                else:
                    self.mock_app.db_cursor.fetchall.return_value = []
                return self.mock_app.db_cursor

            self.mock_app.db_cursor.execute = MagicMock(side_effect=mock_execute)

            mock_table = MagicMock()
            mock_treeview.return_value = mock_table

            self.training_manager.training_page()

            self.mock_app.clear_screen.assert_called_once()
            self.mock_app.load_navigation_bar.assert_called_once()

            expected_query = """SELECT day_name FROM training_days WHERE user_id = ?"""
            self.mock_app.db_cursor.execute.assert_any_call(
                expected_query,
                (self.mock_app.user_id,)
            )

            self.assertGreater(mock_frame.call_count, 0)
            self.assertGreater(mock_button.call_count, 0)
            mock_treeview.assert_called_once()

            expected_button_count = 4
            self.assertEqual(len(self.training_manager.day_buttons), expected_button_count)

            mock_table = MagicMock()
            mock_table.get_children.return_value = []
            mock_table.heading = MagicMock()
            mock_table.column = MagicMock()
            mock_treeview.return_value = mock_table

            self.training_manager.training_page()

            expected_columns = ("Gyakorlat", "Sorozat", "Ismétlés", "Súly (kg)", "Kellékek", "Nehézség", "Leírás")
            expected_widths = {"Gyakorlat": 150, "Sorozat": 70, "Ismétlés": 70, 
                             "Súly (kg)": 70, "Kellékek": 150, "Nehézség": 100, "Leírás": 200}

            for col in expected_columns:
                mock_table.heading.assert_any_call(col, text=col, anchor="center")
                mock_table.column.assert_any_call(col, anchor="center", width=expected_widths[col])

    def test_select_training_day(self):
        """Edzésnap kiválasztásának tesztelése"""
        with patch('ttkbootstrap.Frame') as mock_frame, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Treeview') as mock_treeview:

            self.mock_app.user_id = 1
            self.mock_app.root = MagicMock()

            mock_button1 = MagicMock()
            mock_button2 = MagicMock()
            mock_button3 = MagicMock()
            mock_new_button = MagicMock()
            
            self.training_manager.day_buttons = [mock_button1, mock_button2, mock_button3, mock_new_button]
            mock_button1['text'] = "Hétfő"
            mock_button2['text'] = "Szerda"
            mock_button3['text'] = "Péntek"
            mock_new_button['text'] = "+ Új nap"

            mock_table = MagicMock()
            mock_table.get_children.return_value = []
            mock_treeview.return_value = mock_table
            self.training_manager.training_table = mock_table

            self.mock_app.db_cursor.fetchone = MagicMock(return_value=(1,))
            self.mock_app.db_cursor.fetchall = MagicMock(return_value=[
                ("Fekvőtámasz", 3, 12, 0, "Nincs", "Kezdő", "Alapgyakorlat")
            ])

            def mock_execute(query, params=None):
                normalized_query = ' '.join(query.split())
                if 'SELECT id FROM training_days WHERE user_id = ? AND day_name = ?' in normalized_query:
                    return self.mock_app.db_cursor
                elif 'SELECT exercise_name, sets, reps, weight, equipment, difficulty, description FROM exercises WHERE day_id = ?' in normalized_query:
                    return self.mock_app.db_cursor
                return self.mock_app.db_cursor

            self.mock_app.db_cursor.execute = MagicMock(side_effect=mock_execute)

            #1. Eset: "+ Új nap" kiválasztása
            self.training_manager.add_new_day = MagicMock()
            self.training_manager.select_training_day("+ Új nap")
            self.training_manager.add_new_day.assert_called_once()

            #2. Eset: Létező nap kiválasztása
            self.training_manager.select_training_day("Hétfő")

            for btn in self.training_manager.day_buttons:
                if btn['text'] == "Hétfő":
                    btn.configure.assert_called_with(style="selected.TButton")
                elif btn['text'] != "+ Új nap":
                    btn.configure.assert_called_with(style="words.TButton")

            self.assertEqual(self.training_manager.current_day, "Hétfő")

            calls = self.mock_app.db_cursor.execute.call_args_list
            expected_calls = [
                unittest.mock.call(
                    "SELECT id FROM training_days WHERE user_id = ? AND day_name = ?",
                    (self.mock_app.user_id, "Hétfő")
                ),
                unittest.mock.call(
                    "SELECT exercise_name, sets, reps, weight, equipment, difficulty, description FROM exercises WHERE day_id = ?",
                    (1,)
                )
            ]

            for expected_call in expected_calls:
                self.assertIn(expected_call, calls)

            mock_table.get_children.assert_called()
            mock_table.insert.assert_called_with("", "end", values=(
                "Fekvőtámasz", 3, 12, 0, "Nincs", "Kezdő", "Alapgyakorlat"
            ))


    def test_add_new_day(self):
        """Új edzésnap hozzáadásának tesztelése"""
        with patch('ttkbootstrap.Toplevel') as mock_toplevel, \
             patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Entry') as mock_entry, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Treeview') as mock_treeview:
            
            self.mock_app.user_id = 1
            self.mock_app.root = MagicMock()
            
            mock_table = MagicMock()
            mock_table.get_children.return_value = []
            mock_treeview.return_value = mock_table
            self.training_manager.training_table = mock_table

            #1. Eset: Túl sok nap
            self.training_manager.day_buttons = [MagicMock() for _ in range(7)]
            for btn in self.training_manager.day_buttons:
                btn['text'] = 'TestDay'
            
            self.training_manager.add_new_day()
            
            self.mock_app.custom_messagebox.assert_called_with(
                "Hiba", 
                "Maximum 7 napot lehet létrehozni!"
            )
            
            self.training_manager.day_buttons = [MagicMock() for _ in range(3)]
            self.mock_app.custom_messagebox.reset_mock()
            
            #2. Eset: Üres név megadása
            popup = MagicMock()
            mock_toplevel.return_value = popup
            popup.register = MagicMock()
            
            mock_entry_instance = MagicMock()
            mock_entry.return_value = mock_entry_instance
            mock_entry_instance.get.return_value = ""
            
            self.training_manager.add_new_day()
            
            save_button = None
            for call in mock_button.call_args_list:
                if call[1].get('text') == 'Mentés':
                    save_button = call[1]['command']
                    break
            
            self.assertIsNotNone(save_button)
            save_button()
            
            self.mock_app.custom_messagebox.assert_called_with(
                "Hiba",
                "Kérlek, add meg a nap nevét!"
            )
            
            self.mock_app.custom_messagebox.reset_mock()
            mock_toplevel.reset_mock()
            
            #3. Eset: Sikeres hozzáadás
            mock_entry_instance.get.return_value = "Kedd"
            self.mock_app.db_cursor.fetchone.return_value = None
            
            self.training_manager.add_new_day()
            
            save_button = None
            for call in mock_button.call_args_list:
                if call[1].get('text') == 'Mentés':
                    save_button = call[1]['command']
                    break
            
            self.assertIsNotNone(save_button)
            save_button()
            
            self.mock_app.db_cursor.execute.assert_any_call(
                """SELECT day_name FROM training_days WHERE user_id = ? AND day_name = ?""", (self.mock_app.user_id, "Kedd"))
            
            self.mock_app.db_cursor.execute.assert_any_call(
                """
                    INSERT INTO training_days (user_id, day_name)
                    VALUES (?, ?)
                """, (self.mock_app.user_id, "Kedd"))
            
            self.mock_app.db_connection.commit.assert_called()
            
            self.mock_app.custom_messagebox.reset_mock()
            
            #4. Eset: Létező nap hozzáadása
            self.mock_app.db_cursor.fetchone.return_value = ("Kedd",)
            save_button()
            
            self.mock_app.custom_messagebox.assert_called_with(
                "Hiba",
                "Már létezik ilyen nevű nap!"
            )

    def test_delete_current_day(self):
        """Edzésnap törlésének tesztelése"""
        with patch('ttkbootstrap.Toplevel') as mock_toplevel, \
             patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Frame') as mock_frame, \
             patch('ttkbootstrap.Treeview') as mock_treeview:

            self.mock_app.user_id = 1
            self.mock_app.root = MagicMock()
            
            self.mock_app.db_cursor.fetchone.return_value = (1,)
            self.mock_app.db_cursor.execute = MagicMock()

            mock_table = MagicMock()
            mock_table.get_children.return_value = []
            mock_treeview.return_value = mock_table
            self.training_manager.training_table = mock_table

            #1. Eset: Nincs kiválasztott nap
            for test_day in [None, "+ Új nap"]:
                self.training_manager.current_day = test_day
                self.training_manager.delete_current_day()
                self.mock_app.custom_messagebox.assert_called_with(
                    "Hiba", 
                    "Nincs kiválasztott nap!"
                )
                self.mock_app.custom_messagebox.reset_mock()

            #1. Eset: Sikeres törlés
            mock_day_button = MagicMock(spec=['destroy', '__getitem__', '__setitem__'])
            mock_day_button.__getitem__.return_value = "Hétfő"
            self.training_manager.day_buttons = [mock_day_button]
            self.training_manager.current_day = "Hétfő"

            popup = MagicMock()
            mock_toplevel.return_value = popup
            
            self.training_manager.delete_current_day()
            
            confirm_button = None
            for call in mock_button.call_args_list:
                if call[1].get('text') == 'Igen':
                    confirm_button = call[1]['command']
                    break
            
            self.assertIsNotNone(confirm_button)
            confirm_button()

            def normalize_query(query):
                return ' '.join(query.split())

            calls = self.mock_app.db_cursor.execute.call_args_list
            select_call_found = False
            delete_exercises_found = False
            delete_day_found = False

            expected_select = "SELECT id FROM training_days WHERE user_id = ? AND day_name = ?"
            expected_delete_exercises = "DELETE FROM exercises WHERE day_id = ?"
            expected_delete_day = "DELETE FROM training_days WHERE id = ?"

            for call in calls:
                query = normalize_query(call[0][0])
                if query == expected_select and call[0][1] == (self.mock_app.user_id, "Hétfő"):
                    select_call_found = True
                elif query == expected_delete_exercises and call[0][1] == (1,):
                    delete_exercises_found = True
                elif query == expected_delete_day and call[0][1] == (1,):
                    delete_day_found = True

            mock_day_button.destroy.assert_called_once()
            mock_table.get_children.assert_called()
            
            self.assertIsNone(self.training_manager.current_day)
            self.mock_app.custom_messagebox.assert_called_with(
                "Sikeres törlés",
                "A nap sikeresen törölve!"
            )

    def test_load_training_plan(self):
        """Edzésterv betöltésének tesztelése"""
        mock_table = MagicMock()
        items = ["item1", "item2"]
        mock_table.get_children.return_value = items
        self.training_manager.training_table = mock_table
        self.mock_app.user_id = 1

        test_exercises = [
            ("Fekvőtámasz", 3, 12, 20, "Nincs", "Kezdő", "Leírás 1"),
            ("Húzódzkodás", 4, 8, 0, "Húzódzkodó", "Haladó", "Leírás 2")
        ]

        def mock_execute(query, *args):
            if "SELECT id FROM training_days" in query:
                self.mock_app.db_cursor.fetchone.return_value = (1,)
            elif "SELECT exercise_name" in query:
                self.mock_app.db_cursor.fetchall.return_value = test_exercises
            return self.mock_app.db_cursor

        self.mock_app.db_cursor.execute = MagicMock(side_effect=mock_execute)

        self.training_manager.load_training_plan("Hétfő")

        mock_table.get_children.assert_called()
        for item in items:
            mock_table.delete.assert_any_call(item)

        def normalize_query(query):
            return ' '.join(query.split())

        calls = self.mock_app.db_cursor.execute.call_args_list
        select_day_found = False
        select_exercises_found = False

        expected_select_day = "SELECT id FROM training_days WHERE user_id = ? AND day_name = ?"
        expected_select_exercises = "SELECT exercise_name, sets, reps, weight, equipment, difficulty, description FROM exercises WHERE day_id = ?"

        for call in calls:
            query = normalize_query(call[0][0])
            if query == expected_select_day and call[0][1] == (self.mock_app.user_id, "Hétfő"):
                select_day_found = True
            elif query == expected_select_exercises and call[0][1] == (1,):
                select_exercises_found = True

        self.assertTrue(select_day_found, "SELECT training_days lekérdezés nem található")
        self.assertTrue(select_exercises_found, "SELECT exercises lekérdezés nem található")

        insert_calls = mock_table.insert.call_args_list
        self.assertEqual(len(insert_calls), len(test_exercises))

        for i, exercise in enumerate(test_exercises):
            self.assertEqual(
                insert_calls[i],
                unittest.mock.call("", "end", values=exercise)
            )

    def test_delete_exercise(self):
        """Kiválasztott gyakorlat törlésének tesztelése"""
        self.training_manager.training_table = MagicMock()
        self.mock_app.user_id = 1
        self.training_manager.current_day = "Hétfő"
        self.mock_app.db_cursor = MagicMock()

        #1. Eset: Nincs kiválasztott gyakorlat
        self.training_manager.training_table.selection.return_value = []
        self.training_manager.delete_exercise()
        self.mock_app.custom_messagebox.assert_called_with("Hiba", "Kérlek, válassz ki egy gyakorlatot a törléshez!")

        #2. Eset: Kiválasztott gyakorlat törlése
        selected_item = ["item1"]
        self.training_manager.training_table.selection.return_value = selected_item
        self.training_manager.training_table.item.return_value = {
            'values': ("Fekvőtámasz", 3, 12, 20)
        }
        self.mock_app.db_cursor.fetchone.return_value = (1,)

        def mock_execute(query, *args):
            normalized_query = ' '.join(query.split())
            expected_select = "SELECT id FROM training_days WHERE user_id = ? AND day_name = ?"
            expected_delete = "DELETE FROM exercises WHERE day_id = ? AND exercise_name = ? AND sets = ? AND reps = ? AND weight = ?"
            
            if normalized_query == expected_select or normalized_query == expected_delete:
                return self.mock_app.db_cursor
            return self.mock_app.db_cursor

        self.mock_app.db_cursor.execute = MagicMock(side_effect=mock_execute)

        self.training_manager.delete_exercise()

        normalized_select_query = "SELECT id FROM training_days WHERE user_id = ? AND day_name = ?"
        normalized_delete_query = "DELETE FROM exercises WHERE day_id = ? AND exercise_name = ? AND sets = ? AND reps = ? AND weight = ?"

        select_call_found = False
        delete_call_found = False

        for call in self.mock_app.db_cursor.execute.call_args_list:
            normalized_call_query = ' '.join(call[0][0].split())
            if normalized_call_query == normalized_select_query and call[0][1] == (self.mock_app.user_id, self.training_manager.current_day):
                select_call_found = True
            elif normalized_call_query == normalized_delete_query and call[0][1] == (1, "Fekvőtámasz", 3, 12, 20):
                delete_call_found = True

        self.assertTrue(select_call_found, "SELECT lekérdezés nem található a megfelelő paraméterekkel")
        self.assertTrue(delete_call_found, "DELETE lekérdezés nem található a megfelelő paraméterekkel")

        self.mock_app.db_connection.commit.assert_called_once()
        self.training_manager.training_table.delete.assert_called_with(selected_item[0])

    def test_add_exercise(self):
        """Új gyakorlat hozzáadásának tesztelése"""
        self.training_manager.training_table = MagicMock()
        self.mock_app.user_id = 1
        self.mock_app.root = MagicMock()

        #1. Eset: Nincs kiválasztott nap
        self.training_manager.current_day = None
        self.training_manager.add_exercise()
        self.mock_app.custom_messagebox.assert_called_with(
            "Hiba", 
            "Kérlek, először válassz vagy hozz létre egy napot!"
        )

        #2. Eset: Gyakorlat hozzáadása
        self.training_manager.current_day = "Hétfő"
        
        with patch('ttkbootstrap.Toplevel') as mock_toplevel, \
             patch('ttkbootstrap.Frame') as mock_frame, \
             patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Entry') as mock_entry, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.Combobox') as mock_combobox, \
             patch('ttkbootstrap.Spinbox') as mock_spinbox, \
             patch('ttkbootstrap.StringVar') as mock_stringvar:

            popup = MagicMock()
            popup.winfo_screenwidth.return_value = 1920
            popup.winfo_screenheight.return_value = 1080
            popup.winfo_width.return_value = 800
            popup.winfo_height.return_value = 500
            mock_toplevel.return_value = popup

            test_exercises = [
                ("Fekvőtámasz", "Nincs", "Kezdő"),
                ("Húzódzkodás", "Húzódzkodó", "Haladó")
            ]
            self.mock_app.db_cursor.fetchall.return_value = test_exercises

            mock_muscle_group_var = MagicMock()
            mock_exercise_var = MagicMock()
            mock_stringvar.side_effect = [mock_muscle_group_var, mock_exercise_var]

            expected_muscle_groups = ['bicepsz', 'comb', 'has', 'hát', 'kardió', 'mell', 
                                    'far', 'tricepsz', 'vádli', 'váll']

            self.training_manager.add_exercise()

            mock_toplevel.assert_called_once()
            popup.title.assert_called_with("Gyakorlat hozzáadása")

            combobox_calls = mock_combobox.call_args_list
            muscle_group_combobox_call = None
            for call in combobox_calls:
                if 'values' in call[1] and call[1]['values'] == expected_muscle_groups:
                    muscle_group_combobox_call = call
                    break
            
            self.assertIsNotNone(muscle_group_combobox_call, "Izomcsoport Combobox nem megfelelő értékekkel lett létrehozva")

if __name__ == '__main__':
    unittest.main()

"""  python -m unittest app/tesztek/test_training_manager.py
     coverage run -m unittest app/tesztek/test_training_manager.py
     coverage report
"""
