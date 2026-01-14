from utility_core import *
import time

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Utility Service 1 (50002) [Normal Selection + Barcode + DueDate]...")

    app = None
    WAIT_TIME = 2

    try:
        if not utility_services_main(): exit()
        app, main_window = connect_main_window()

        SERVICE_TITLE = S_CFG['UTILITY_1_TITLE']         # 50002
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']   # SubTextTextBlock

        # 1. เลือกรายการ
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANS_TYPE, control_type="Text").click_input()
        time.sleep(2) 

        # 2. พิมพ์บาร์โค้ด
        BARCODE_ID = S_CFG['BARCODE_INPUT_ID1']      
        BARCODE_VAL = S_CFG.get('TEST_BARCODE_VALUE1', "|0994000165463002017829830427897172608660700000079154") 
        
        main_window.child_window(auto_id=BARCODE_ID).type_keys(BARCODE_VAL)
        print(f"[*] Typed Barcode: {BARCODE_VAL}")
        time.sleep(1)

        # 3. กดถัดไป (ครั้งที่ 1)
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        # ---------------------------------------------------------
        # [FIXED DUPLICATE ID] กรอกวันครบกำหนดชำระ
        # แก้ปัญหาเจอ ID ซ้ำ 2 ตัว โดยการระบุ found_index=0
        # ---------------------------------------------------------
        due_date_id = S_CFG.get('DUE_DATE_ID', 'REFNO7') 
        due_date_val = S_CFG.get('DUE_DATE_VALUE', '02/02/2026')

        print(f"[*] Force setting Due Date: {due_date_val} at ID: {due_date_id}")
        
        # ใช้ found_index=0 เพื่อบอกว่า "เอาตัวแรกที่เจอ" (แก้ Error: There are 2 elements...)
        # ถ้าตัวแรกพิมพ์ไม่ได้ ให้ลองเปลี่ยนเป็น found_index=1
        try:
            due_date_field = main_window.child_window(auto_id=due_date_id, found_index=0)
            
            # ใช้ท่าไม้ตาย set_text (ไม่ต้องคลิก ไม่ต้องลบค่าเก่า)
            # ถ้าวิธีนี้ผ่าน ค่าจะเปลี่ยนทันที
            due_date_field.set_text(due_date_val)
            print("[/] Used set_text() successfully on index 0.")

        except Exception as e_set_text:
            print(f"[!] set_text failed ({e_set_text}), trying Focus & Type method...")
            
            try:
                # ถ้า set_text ไม่ได้ ลองวิธีบ้านๆ: คลิก -> ลบ -> พิมพ์
                # ต้องระบุ found_index=0 เหมือนเดิม
                due_date_field = main_window.child_window(auto_id=due_date_id, found_index=0)
                
                due_date_field.set_focus()
                due_date_field.click_input()
                time.sleep(0.5)
                
                # ลบค่าเก่า: กด Backspace 15 ครั้ง (ชัวร์กว่า Ctrl+A)
                due_date_field.type_keys("{BACKSPACE 15}")
                time.sleep(0.5)
                
                # พิมพ์ค่าใหม่
                due_date_field.type_keys(due_date_val)
                print("[/] Typed value manually.")
                
            except Exception as e_manual:
                 print(f"[X] Failed to input date: {e_manual}")

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

        # 8. กดเสร็จสิ้น (ถ้ามี)
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