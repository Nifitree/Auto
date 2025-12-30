from pos_core import *

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 4 (51119)...")
    app = None
    try:
        # 1. เชื่อมต่อระบบ
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # ----------------------------------------------------
        # เริ่มการทำงาน Service 4
        # ----------------------------------------------------

        # ขั้นตอนที่ 0: กดเลือกเมนู 51119 ก่อน (เพื่อเข้าหน้า Barcode)
        service_name = config['PRAISANI_POS_SERVICES']['PRAISANI_4_TITLE'] # ค่า 51119
        main_window.child_window(title=service_name).click_input()
        print(f"[*] เลือกเมนู {service_name} เรียบร้อย")

        # ขั้นตอนที่ 1: พิมพ์บาร์โค้ดลงในช่อง AutoID: Barcode_51119
        barcode_id = config['PRAISANI_POS_SERVICES']['BARCODE_INPUT_ID']
        barcode_val = config['PRAISANI_POS_SERVICES']['TEST_BARCODE_VALUE']
        
        main_window.child_window(auto_id=barcode_id).type_keys(barcode_val)
        print(f"[*] พิมพ์บาร์โค้ด {barcode_val} เรียบร้อย")

        # ขั้นตอนที่ 2: กดปุ่ม "ถัดไป"
        next_btn = config['PRAISANI_POS_MAIN']['NEXT_TITLE']
        main_window.child_window(title=next_btn).click()
        print(f"[*] กดปุ่ม {next_btn} เรียบร้อย")

        # ขั้นตอนที่ 3: กดปุ่ม "ตกลง"
        main_window.child_window(title="ตกลง").click()
        print("[*] กดปุ่ม ตกลง เรียบร้อย")

        # ขั้นตอนที่ 4: กดปุ่ม "เสร็จสิ้น"
        finish_btn = config['PRAISANI_POS_MAIN']['FINISH_BUTTON_TITLE']
        main_window.child_window(title=finish_btn).click()
        print(f"[*] กดปุ่ม {finish_btn} เรียบร้อย")

    except Exception as e:
        print(f"\n[!] เกิดข้อผิดพลาด: {e}")