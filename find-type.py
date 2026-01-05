from pywinauto.application import Application
WINDOW_TITLE = ".*Riposte POS Application.*"

app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
main_window = app.top_window()

# 2. คำสั่งนี้จะปริ้นท์ log โครงสร้างทั้งหมดออกมาดู
print("กำลังดึงข้อมูล UI...")
main_window.print_control_identifiers()
print("เสร็จสิ้นการดึงข้อมูล UI.")
