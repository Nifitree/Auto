from utility_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Utility Service 1 (50002) [Search + Barcode]...")

    app = None
    WAIT_TIME = 2

    try:
        # 1. เรียกใช้ Main Flow เพื่อเข้าหน้า Agency -> BaS -> กรอกข้อมูลผู้ส่ง
        if not utility_services_main(): exit()
        
        # เชื่อมต่อหน้าต่างหลังจาก Main Flow เสร็จ
        app, main_window = connect_main_window()

        # --- เริ่มขั้นตอน Logic (เลียนแบบ pos_5) ---

        # ดึงตัวแปรจาก Config [UTILITY_SERVICES]
        SERVICE_TITLE = S_CFG['UTILITY_1_TITLE']             
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']   

        # STEP 1: ค้นหาและเลือกรายการ
        print(f"[*] Searching: {SERVICE_TITLE}")
        
        # 1.1 พิมพ์รหัสค้นหา
        main_window.child_window(auto_id=SEARCH_ID).type_keys(SERVICE_TITLE)
        time.sleep(2) # รอระบบกรอง

        # 1.2 คลิกเลือกรายการ
        print(f"[*] Selecting: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) # รอโหลดหน้า

        # STEP 2: พิมพ์บาร์โค้ด
        # ใช้ ID1 ตามที่คุณระบุใน Config
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID1']
        BARCODE_VAL = S_CFG.get('TEST_BARCODE_VALUE', "9999999999") 
        
        main_window.child_window(auto_id=BARCODE_ID).type_keys(BARCODE_VAL)
        print(f"[*] Typed Barcode: {BARCODE_VAL}")
        time.sleep(1)

        # STEP 3: กดถัดไป
        print("[*] Next")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # STEP 4: กดตกลง
        print("[*] Clicked OK")
        # ใช้ค่าจาก Config หรือ Default เป็น "ตกลง"
        accept_title = B_CFG.get("ACCEPT_TITLE", "ตกลง") 
        main_window.child_window(title=accept_title, auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(1)

        # STEP 5: กดเสร็จสิ้น
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"]).click_input()
        print(f"[*] Clicked {B_CFG['FINISH_BUTTON_TITLE']}")

    except Exception as e:
        # ใช้ ctx จาก utility_core (หรือ app)
        target_app = app if (app is not None) else (ctx.app if 'ctx' in globals() else None)
        
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Utility Service 1",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")