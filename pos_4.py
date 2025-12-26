import configparser
from pywinauto.application import Application
# ... imports อื่นๆ ...

# 1. อ่านไฟล์ Config
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8') # ตรวจสอบชื่อไฟล์ .ini ของคุณให้ตรง

# ดึงค่าตัวแปรจาก Config
# ส่วน Barcode (Service)
barcode_input_id = config['PRAISANI_POS_SERVICES']['BARCODE_INPUT_ID']
test_barcode_value = config['PRAISANI_POS_SERVICES']['TEST_BARCODE_VALUE']

# ส่วนปุ่มกด (Main)
next_btn_title = config['PRAISANI_POS_MAIN']['NEXT_TITLE']
finish_btn_title = config['PRAISANI_POS_MAIN']['FINISH_BUTTON_TITLE']

try:
    # 1. พิมพ์บาร์โค้ด (ดึง ID และ Value จาก Config)
    window.child_window(auto_id=barcode_input_id).type_keys(test_barcode_value)
    print(f"พิมพ์บาร์โค้ด {test_barcode_value} เรียบร้อย")

    # 2. กดปุ่ม "ถัดไป" (ดึงชื่อปุ่มจาก Config)
    window.child_window(title=next_btn_title).click()
    print(f"กดปุ่ม {next_btn_title} เรียบร้อย")

    # 3. กดปุ่ม "ตกลง" 
    # (ใน Config ที่ให้มายังไม่มีตัวแปรปุ่ม 'ตกลง' ผมเลยใส่เป็น text ตรงๆ ไว้นะครับ)
    window.child_window(title="ตกลง").click()
    print("กดปุ่ม ตกลง เรียบร้อย")

    # 4. กดปุ่ม "เสร็จสิ้น" (ดึงชื่อปุ่มจาก Config)
    window.child_window(title=finish_btn_title).click()
    print(f"กดปุ่ม {finish_btn_title} เรียบร้อย")

except Exception as e:
    print(f"เกิดข้อผิดพลาดใน pos_4: {e}")