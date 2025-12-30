from pos_core import *
import configparser  # <--- 1. ต้อง import อันนี้เพิ่ม

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 4 (51119)...")
    
    # <--- 2. สร้างตัวแปร config และอ่านไฟล์ (สมมติชื่อไฟล์ config.ini)
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8') 
    # -----------------------------------------------------------

    app = None
    try:
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # ตอนนี้ตัวแปร config มีค่าแล้ว เรียกใช้ได้เลย
        
        # ชื่อเมนู 51119
        menu_title = config['PRAISANI_POS_SERVICES']['PRAISANI_4_TITLE']
        
        # ID ช่องบาร์โค้ด และ ค่าที่จะพิมพ์
        barcode_id = config['PRAISANI_POS_SERVICES']['BARCODE_INPUT_ID']
        barcode_val = config['PRAISANI_POS_SERVICES']['TEST_BARCODE_VALUE']
        
        # ชื่อปุ่ม
        next_btn = config['PRAISANI_POS_MAIN']['NEXT_TITLE']
        finish_btn = config['PRAISANI_POS_MAIN']['FINISH_BUTTON_TITLE']

        # --- เริ่มทำงาน (Flow) ---
        
        # STEP 1: กดเข้าเมนู 51119
        main_window.child_window(title=menu_title).click()
        print(f"[*] เข้าเมนู {menu_title} เรียบร้อย")

        # STEP 2: พิมพ์บาร์โค้ดลงไป
        main_window.child_window(auto_id=barcode_id).type_keys(barcode_val)
        print(f"[*] พิมพ์บาร์โค้ด {barcode_val} เรียบร้อย")

        # STEP 3: กดถัดไป
        main_window.child_window(title=next_btn).click()
        print(f"[*] กดปุ่ม {next_btn} เรียบร้อย")

        # STEP 4: กดตกลง
        main_window.child_window(title="ตกลง").click()
        print("[*] กดปุ่ม ตกลง เรียบร้อย")

        # STEP 5: กดเสร็จสิ้น
        main_window.child_window(title=finish_btn).click()
        print(f"[*] กดปุ่ม {finish_btn} เรียบร้อย")

    except Exception as e:
        print(f"\n[!] เกิดข้อผิดพลาด: {e}")