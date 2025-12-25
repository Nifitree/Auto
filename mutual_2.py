from mutual_core import *

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Mutual Service 2...")
    try:
        if not mutual_main(): exit()
        app, main_window = connect_main_window()
        
        # 1. Select Item
        run_mutual_transaction(main_window, S_CFG['MUTUAL_2_TITLE'])
        
        # 2. Fill 4 Fields
        print("[*] Filling 4 fields...")
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID).type_keys(MEMBER_ID_VALUE)
        main_window.child_window(auto_id=ACCOUNT_NUM_AUTO_ID).type_keys(ACCOUNT_NUM_VALUE)
        main_window.child_window(auto_id=ACCOUNT_NAME_AUTO_ID).type_keys(ACCOUNT_NAME_VALUE)
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID).type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)

        # 3. Flow
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)
        
        print("[*] Receive Payment")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE).click_input()
        
        # --- [จุดแก้ไข: เพิ่มความชัวร์ในการจ่ายเงิน] ---
        print("[*] Waiting for Payment Screen...")
        time.sleep(3)  # รอให้หน้าจอ Payment โหลดเสร็จ 100%
        
        print("[*] Focusing Window...")
        main_window.set_focus() # บังคับให้ Active ที่หน้าจอนี้
        
        print(f"[*] Payment Action: Pressing {T_CFG['PAYMENT_FAST']}")
        # ใช้วิธีจ่ายเงินด่วน (กด F)
        main_window.type_keys(T_CFG['PAYMENT_FAST']) 
        
        time.sleep(WAIT_TIME)
        # -------------------------------------------

        print("[*] Next (3)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        finish_transaction(main_window)
        print("[V] Service 2 Success!")

    except Exception as e:
        print(f"[X] FAILED: {e}")