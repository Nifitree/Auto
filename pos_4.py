from pos_core import *
import configparser

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 4 (51119)...")
    
    # 1. โหลด Config
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    app = None
    try:
        # เชื่อมต่อ
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # --- ดึงค่าตัวแปร ---
        menu_title = config['PRAISANI_POS_SERVICES']['PRAISANI_4_TITLE'] # เมนู 51119
        barcode_id = config['PRAISANI_POS_SERVICES']['BARCODE_INPUT_ID']
        barcode_val = config['PRAISANI_POS_SERVICES']['TEST_BARCODE_VALUE']
        next_btn = config['PRAISANI_POS_MAIN']['NEXT_TITLE']
        finish_btn = config['PRAISANI_POS_MAIN']['FINISH_BUTTON_TITLE']

        # --- เริ่มทำงาน ---

        # 1. กดเข้าเมนู 51119 (ใส่คืนมาให้แล้วครับ)
        main_window.child_window(title=menu_title).click()
        print(f"[*] เข้าเมนู {menu_title} เรียบร้อย")

        # 2. พิมพ์บาร์โค้ด
        main_window.child_window(auto_id=barcode_id).type_keys(barcode_val)
        print(f"[*] พิมพ์บาร์โค้ด {barcode_val} เรียบร้อย")

        # 3. กดถัดไป
        main_window.child_window(title=next_btn).click()
        print(f"[*] กดปุ่ม {next_btn} เรียบร้อย")

        # 4. กดตกลง
        main_window.child_window(title="ตกลง").click()
        print("[*] กดปุ่ม ตกลง เรียบร้อย")

        # 5. กดเสร็จสิ้น
        main_window.child_window(title=finish_btn).click()
        print(f"[*] กดปุ่ม {finish_btn} เรียบร้อย")

    except Exception as e:
        print(f"\n[!] เกิดข้อผิดพลาด: {e}")
        # ส่วนแคปหน้าจอ (ใส่คืนมาให้แล้วครับ)
        if app and main_window:
            try:
                main_window.capture_as_image().save('error_pos_4.png')
                print("[!] บันทึกภาพหน้าจอ error_pos_4.png แล้ว")
            except:
                print("[!] ไม่สามารถบันทึกภาพหน้าจอได้")