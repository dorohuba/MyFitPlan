import unittest
from unittest.mock import MagicMock, patch
from app.app import MyFitPlan

class TestMyFitPlan(unittest.TestCase):
    
    def setUp(self):
        """Teszt környezet előkészítése"""
        self.root = MagicMock()
        with patch('app.app.UserManager'), \
             patch('app.app.DietManager'), \
             patch('app.app.TrainingManager'), \
             patch('app.app.sqlite3'):
            self.app = MyFitPlan(self.root)

    def test_clear_screen(self):
        """Képernyő tisztítás tesztelése"""
        mock_widget = MagicMock()
        self.root.winfo_children.return_value = [mock_widget]
        
        self.app.clear_screen()
        
        mock_widget.destroy.assert_called_once()

    def test_back(self):
        """Visszalépő funkció tesztelése"""
        mock_function = MagicMock()
        self.app.screen_stack.append(mock_function)
        
        self.app.back()
        
        mock_function.assert_called_once()
        self.assertEqual(len(self.app.screen_stack), 0)

    def test_load_navigation_bar(self):
        """Navigációs sáv tesztelése"""
        with patch('ttkbootstrap.Canvas') as mock_canvas, \
             patch('ttkbootstrap.Frame') as mock_frame, \
             patch('ttkbootstrap.Button') as mock_button, \
             patch('ttkbootstrap.PhotoImage') as mock_photo:
            
            mock_canvas_instance = MagicMock()
            mock_canvas.return_value = mock_canvas_instance
            mock_frame_instance = MagicMock()
            mock_frame.return_value = mock_frame_instance
            
            mock_canvas_instance.__str__ = lambda x: "mock_canvas"
            
            mock_photo_instance = MagicMock()
            mock_photo_instance.subsample.return_value = mock_photo_instance
            mock_photo.return_value = mock_photo_instance
            
            self.app.load_navigation_bar()
            
            mock_canvas.assert_called_once()
            mock_frame.assert_called()
            self.assertEqual(mock_button.call_count, 10)

    def test_create_database(self):
        """Adatbázis létrehozás tesztelése"""
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        
        self.app.db_cursor = mock_cursor
        self.app.db_connection = mock_connection
        
        self.app.create_database()
        
        expected_tables = ['CREATE TABLE IF NOT EXISTS users',
                           'CREATE TABLE IF NOT EXISTS users_meals',
                           'CREATE TABLE IF NOT EXISTS training_days',
                           'CREATE TABLE IF NOT EXISTS exercises',]
        
        calls = mock_cursor.execute.call_args_list
        for expected_table in expected_tables:
            found = False
            for call in calls:
                if expected_table in call[0][0]:
                    found = True
                    break
            self.assertTrue(found, f"Hiányzó tábla létrehozás: {expected_table}")
        
        mock_connection.commit.assert_called_once()

    def test_custom_messagebox(self):
        """Egyedi üzenetablak tesztelése"""
        with patch('ttkbootstrap.Toplevel') as mock_toplevel, \
             patch('ttkbootstrap.Label') as mock_label, \
             patch('ttkbootstrap.Button') as mock_button:
            
            mock_popup = MagicMock()
            mock_toplevel.return_value = mock_popup
            
            test_title = "Test Title"
            test_message = "Test Message"
            
            self.app.custom_messagebox(test_title, test_message)
            
            mock_toplevel.assert_called_once()
            mock_popup.title.assert_called_with(test_title)
            mock_label.assert_called_once()
            mock_button.assert_called_once()
            
            self.app.custom_messagebox(test_title, test_message, login=True)
            self.app.custom_messagebox(test_title, test_message, diet=True)
            self.app.custom_messagebox(test_title, test_message, profile=True)

if __name__ == '__main__':
    unittest.main()

"""  python -m unittest app/tesztek/test_app.py
     coverage run -m unittest app/tesztek/test_app.py
     coverage report
"""