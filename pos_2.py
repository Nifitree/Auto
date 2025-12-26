from pos_core import *
from ui_helper import select_combobox_item

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running POS Service 2 (30221)...")
    app = None
    try:
        if not pos_services_main(): exit()
        app, main_window = connect_main_window()

        # 1. เลือกรายการ (30221)
        SERVICE_TITLE = S_CFG['PRAISANI_2_TITLE']
        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        
        main_window.child_window(title=SERVICE_TITLE, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 2. กรอกข้อมูล (ดึงจาก Config P1 มาใช้เลย เพราะเหมือนกัน)
        print("[*] Filling Data Form (Using P1 Config)...")

        # 2.1 เลขที่สมาชิก
        # ใช้ P1_AUTOID_MEMBER และ P1_MEMBER_ID
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_MEMBER']).type_keys(S_CFG['P1_MEMBER_ID'])
        time.sleep(0.5)

        # 2.2 ประเภทเงิน (Dropdown)
        # ใช้ P1_AUTOID_MONEY_TYPE และ P1_MONEY_TYPE
        # **ข้อควรระวัง**: ถ้า Service 2 ต้องเลือก Dropdown คนละค่ากับ Service 1 (เช่น อันนึงเลือก "เติมเงิน" อีกอันเลือก "สมัครสมาชิก")
        # คุณอาจต้องสร้างตัวแปรแยกเฉพาะบรรทัดนี้ครับ แต่ถ้าเลือกเหมือนกันก็ใช้ P1 ได้เลย
        select_combobox_item(
            main_window, 
            combo_auto_id=S_CFG['P1_AUTOID_MONEY_TYPE'], 
            item_title=S_CFG['P1_MONEY_TYPE'], 
            sleep=WAIT_TIME
        )
        time.sleep(0.5)

        # 2.3 ชื่อ-สกุล
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_NAME']).type_keys(S_CFG['P1_NAME'])
        time.sleep(0.5)

        # 2.4 เลขที่บัตรประชาชน
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_IDCARD']).type_keys(S_CFG['P1_ID_CARD'])
        time.sleep(0.5)

        # 2.5 หมายเหตุ
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_NOTE']).type_keys(S_CFG['P1_NOTE'])
        time.sleep(0.5)

        # 2.6 จำนวนเงิน
        main_window.child_window(auto_id=S_CFG['P1_AUTOID_AMOUNT']).type_keys(S_CFG['P1_AMOUNT'])
        time.sleep(0.5)

        # 2.7 จำนวนเงินที่ต้องชำระ (Amount)
        amt_total = main_window.child_window(auto_id=S_CFG['P1_AUTOID_TOTAL'])
        if amt_total.exists(timeout=1):
             amt_total.type_keys(S_CFG['P1_AMOUNT'])

        time.sleep(WAIT_TIME)

        # 3. Flow ต่อไปจนจบ
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print(f"[*] Receive Payment ({RECEIVE_PAYMENT_TITLE})")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE, control_type="Text").click_input()
        
        # --- Fast Cash ---
        print("[*] Waiting for Payment Screen (3s)...")
        time.sleep(3)
        main_window.set_focus()

        fast_cash_btn = main_window.child_window(auto_id="EnableFastCash")
        if fast_cash_btn.exists(timeout=2):
            fast_cash_btn.click_input()
        else:
            main_window.type_keys(T_CFG['PAYMENT_FAST'])
        
        time.sleep(WAIT_TIME)
        # -----------------

        print("[*] Next (3)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
        print("[V] Service 2 Success!")

    except Exception as e:
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "POS Service 2",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] Evidence Saved")
        print(f"[X] FAILED: {e}")