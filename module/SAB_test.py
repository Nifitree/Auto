from module.config_loader import read_config
from module.ui_debug import dump_tree
from module.actions import (
    connect_app, open_agency, open_SAB,
    fill_phone_number, click_read_id, click_next
)

def test_SAB(config):
    print("="*50)
    print("[*] เริ่มทดสอบ SAB")

    WINDOW_TITLE = config['GLOBAL']['WINDOW_TITLE']
    DELAY = config.getfloat('GLOBAL', 'LOAD_TIME_SEC')

    AB = config['agency']
    ID = config['ID']
    PH = config['phone']
    NX = config['NEXT']

    try:
        # เชื่อมต่อ App
        win = connect_app(WINDOW_TITLE)

        # กดเมนู
        open_agency(win, AB, DELAY)
        open_SAB(win, AB, DELAY)

        # Debug ก่อนค้นหา
        dump_tree(win)

        # กรอกเบอร์โทร
        fill_phone_number(win, PH, DELAY, config)

        # อ่านบัตร
        click_read_id(win, ID, DELAY)

        # ถัดไป
        click_next(win, NX, DELAY)

        print("[V] จบหน้า SAB รอ Barcode")

    except Exception as e:
        print(f"[X] ERROR: {e}")


# =============================================
#               MAIN ENTRY POINT
# =============================================
if __name__ == "__main__":
    config = read_config()

    if not config.sections():
        print("[X] โหลด config.ini ไม่สำเร็จ")
    else:
        test_SAB(config)
