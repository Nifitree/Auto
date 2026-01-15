from utility_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Utility Service 6 (50982) [Normal Selection + Barcode]...")

    app = None
    WAIT_TIME = 2

    try:
        # 1. รัน Main Flow
        if not utility_services_main(): exit()
        app, main_window = connect_main_window()

        # --- ส่วน Logic ---

        SERVICE_TITLE = S_CFG['UTILITY_6_TITLE']         # 50982
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']   

        # 1. เลือกรายการ
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) 

        # 2. พิมพ์บาร์โค้ด
        # ใช้ ID6 ตาม Config
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID6']      # Barcode_50982
        BARCODE_VAL = S_CFG.get('TEST_BARCODE_VALUE6', "125366068001612530572036125375210966000006484") 
        
        main_window.child_window(auto_id=BARCODE_ID).type_keys(BARCODE_VAL)
        print(f"[*] Typed Barcode: {BARCODE_VAL}")
        time.sleep(1)

        # 3. กดถัดไป (ครั้งที่ 1)
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # ---------------------------------------------------------
        # [FIXED DUPLICATE ID] กรอกวันครบกำหนดชำระ
        # ---------------------------------------------------------
        due_date_id = S_CFG.get('DUE_DATE_ID2', 'REFNO6') 
        due_date_val = S_CFG.get('DUE_DATE_VALUE', '02/02/2026')

        print(f"[*] Force setting Due Date: {due_date_val} at ID: {due_date_id}")
        
        try:
            # ใช้ found_index=0 แก้ปัญหา ID ซ้ำ
            due_date_field = main_window.child_window(auto_id=due_date_id, found_index=0)
            due_date_field.set_text(due_date_val)
            print("[/] Used set_text() successfully.")

        except Exception as e:
            print(f"[!] set_text failed ({e}), trying manual type...")
            try:
                due_date_field = main_window.child_window(auto_id=due_date_id, found_index=0)
                due_date_field.set_focus()
                due_date_field.click_input()
                time.sleep(0.5)
                due_date_field.type_keys("{BACKSPACE 15}")
                time.sleep(0.5)
                due_date_field.type_keys(due_date_val)
            except Exception as e2:
                 print(f"[X] Failed to input date: {e2}")

        time.sleep(1)
        
        # กดปุ่ม PART_Button (อ่านจาก Config)
        part_btn_id = S_CFG.get('PART_BUTTON_ID', 'PART_Button') # อ่านจาก config
        print(f"[*] Clicking '{part_btn_id}'...")
        
        try:
            # ใช้ found_index=0 เพื่อความชัวร์ (เหมือน REFNO7)
            main_window.child_window(auto_id=part_btn_id, found_index=0).click_input()
        except:
            # ถ้าไม่เจอ ลองหาแบบปกติ
            main_window.child_window(auto_id=part_btn_id).click_input()
        
        time.sleep(1)

        # 4. กดถัดไป (ครั้งที่ 2)
        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 5. กดถัดไป (ครั้งที่ 3)
        print("[*] Next (3)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 6. กดรับเงิน
        receive_btn_title = S_CFG.get('BTN_RECEIVE_MONEY_TITLE', 'รับเงิน')
        print(f"[*] Click Receive Money ({receive_btn_title})")
        main_window.child_window(title=receive_btn_title).click_input()
        time.sleep(WAIT_TIME)

        # 7. จ่ายด้วยวิธี Fast Cash
        fast_cash_id = S_CFG.get('BTN_FAST_CASH_ID', 'EnableFastCash')
        print(f"[*] Click Fast Cash ({fast_cash_id})")
        main_window.child_window(auto_id=fast_cash_id).click_input()
        time.sleep(WAIT_TIME)

        # 8. กดเสร็จสิ้น
        try:
            finish_btn = main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"])
            if finish_btn.exists(timeout=2):
                finish_btn.click_input()
                print(f"[*] Clicked {B_CFG['FINISH_BUTTON_TITLE']}")
        except:
            print("[*] Finish button not found or process completed.")

    except Exception as e:
        target_app = app if (app is not None) else (ctx.app if 'ctx' in globals() else None)
        
        if target_app:
            try:
                save_evidence_context(target_app, {
                    "test_name": "Utility Service 1",
                    "step_name": "Execution Failed",
                    "error_message": str(e)
                })
                print("[/] บันทึกภาพ Error เรียบร้อย")
            except: pass
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")