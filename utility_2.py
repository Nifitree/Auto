from utility_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Utility Service 2 (50387) [Normal Selection + Barcode]...")

    app = None
    WAIT_TIME = 2

    try:
        # 1. รัน Main Flow (Agency -> BaS -> กรอกข้อมูลผู้ส่ง)
        if not utility_services_main(): exit()
        app, main_window = connect_main_window()

        # --- ส่วน Logic ---

        SERVICE_TITLE = S_CFG['UTILITY_2_TITLE']         # 50387
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']   

        # 1. เลือกรายการ
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) 

        # 2. พิมพ์บาร์โค้ด
        # ใช้ ID2 ตาม Config
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID2']      # Barcode_50387
        BARCODE_VAL = S_CFG.get('TEST_BARCODE_VALUE2', "|0107564000014007010795803392836551009202337036") 
        
        main_window.child_window(auto_id=BARCODE_ID).type_keys(BARCODE_VAL)
        print(f"[*] Typed Barcode: {BARCODE_VAL}")
        time.sleep(1)

        # 3. กดถัดไป
        print("[*] Next")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 4. กดถัดไป
        print("[*] Next")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # 5. กดถัดไป
        print("[*] Next")
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
            save_evidence_context(target_app, {
                "test_name": "Utility Service 2",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")