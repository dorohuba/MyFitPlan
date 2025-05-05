import ttkbootstrap as ttk
from app.app import MyFitPlan

window = ttk.Window(themename="myfitplan_theme")
app = MyFitPlan(window)
window.mainloop()