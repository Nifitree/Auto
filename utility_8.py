from utility_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Utility Service 8 (52052) [Search + Electric Info]...")

    app = None
    WAIT_TIME = 2

    try:
        # 1. รัน Main Flow
        if not utility_services_main(): exit()
        app, main_window = connect_main_window()

        # --- ดึงค่าจาก Config ---
        SERVICE_TITLE = S_CFG['UTILITY_8_TITLE']         # 52052
        SEARCH_ID = S_CFG['SEARCH_EDIT_ID']
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']

        # ดึง AutoID
        ID_CUST = S_CFG['U8_ID_CUSTOMER']        
        ID_CONFIRM = S_CFG['U8_ID_CONFIRM']      
        ID_MOBILE = S_CFG['U8_ID_MOBILE']        
        VAL_CUST = S_CFG['U8_TEST_CUSTOMER_ID']  
        VAL_MOBILE = S_CFG['U8_TEST_MOBILE']     

        # --- เริ่มขั้นตอน Logic ---

        # 1. ค้นหาและเลือกรายการ
        print(f"[*] Searching: {SERVICE_TITLE}")
        main_window.child_window(auto_id=SEARCH_ID).type_keys(SERVICE_TITLE)
        time.sleep(2) 

        print(f"[*] Selecting: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) 

        # 2. กรอกข้อมูล 3 ช่อง (ใช้ตัวแปรจาก Config)
        
        # 2.1 หมายเลขผู้ใช้ไฟฟ้า
        print(f"[*] Typing Customer ID: {VAL_CUST}")
        main_window.child_window(auto_id=ID_CUST).type_keys(VAL_CUST)
        time.sleep(0.5)

        # 2.2 ยืนยันหมายเลขผู้ใช้ไฟฟ้า
        print(f"[*] Confirming Customer ID")
        main_window.child_window(auto_id=ID_CONFIRM).type_keys(VAL_CUST)
        time.sleep(0.5)

        # 2.3 เบอร์มือถือ
        print(f"[*] Typing Mobile: {VAL_MOBILE}")
        # ล้างค่าเก่าก่อน (เผื่อมี)
        main_window.child_window(auto_id=ID_MOBILE).type_keys("^a{BACKSPACE}") 
        main_window.child_window(auto_id=ID_MOBILE).type_keys(VAL_MOBILE)
        time.sleep(1)

        # 3. กดถัดไป
        print("[*] Next")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 4. กดตกลง
        print("[*] Clicked OK")
        accept_title = B_CFG.get("ACCEPT_TITLE", "ตกลง")
        main_window.child_window(title=accept_title, auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(1)

        # 5. กดเสร็จสิ้น
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"]).click_input()
        print(f"[*] Clicked {B_CFG['FINISH_BUTTON_TITLE']}")

    except Exception as e:
        target_app = app if (app is not None) else (ctx.app if 'ctx' in globals() else None)
        
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Utility Service 8",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")