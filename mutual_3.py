from mutual_core import *

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Mutual Service 3 (Combobox)...")
    app = None
    try:
        if not mutual_main(): exit()
        app, main_window = connect_main_window()
        
        # 1. เลือกรายการ (50413)
        run_mutual_transaction(main_window, S_CFG['MUTUAL_3_TITLE'])
        
        # 2. กรอกข้อมูล & เลือก Dropdown
        print("[*] Filling Data & Combobox...")
        
        # 2.1 กรอกเลขสมาชิก
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID).type_keys(MEMBER_ID_VALUE)
        time.sleep(0.5)
        
        # 2.2 เลือกประเภทเงินกู้ (Dropdown)
        select_combobox_item(main_window, LOAN_TYPE_COMBO_ID, LOAN_TYPE_SELECT, WAIT_TIME)
        time.sleep(WAIT_TIME)
        
        # 2.4 กรอกชื่อเจ้าของบัญชี
        main_window.child_window(auto_id=ACCOUNT_NUM_AUTO_ID).type_keys(ACCOUNT_NAME_VALUE)
        
        # 2.5 กรอกจำนวนเงิน
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID).type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)

        # 3. Flow: ถัดไป -> ถัดไป -> รับเงิน
        print("[*] Next (1)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        print("[*] Next (2)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)
        
        print("[*] Receive Payment")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE).click_input()
        
        # =========================================================
        # [STEP 7] PAYMENT SECTION
        # =========================================================
        print("[*] Waiting for Payment Screen (3s)...")
        time.sleep(3)           # รอหน้าจอโหลด
        main_window.set_focus() # ดึง Focus กลับมาที่หน้าจอ
        
        print(f"[*] Payment Action: Executing {T_CFG['PAYMENT_FAST']}...")
        
        # --- เลือกวิธีจ่ายเงิน (ลบ # หน้าวิธีที่จะใช้) ---
        # payment.pay_cash()                      # 1. เงินสด (ระบุจำนวน)
        main_window.type_keys(T_CFG['PAYMENT_FAST']) # 2. เงินสด (ด่วน F)
        # payment.pay_qr()                        # 3. QR PromptPay
        # payment.pay_credit()                    # 4. บัตรเครดิต
        # payment.pay_debit()                     # 5. บัตรเดบิต
        # payment.pay_check()                     # 6. เช็คธนาคาร
        # payment.pay_alipay()                    # 7. Alipay
        # payment.pay_wechat()                    # 8. WeChat Pay
        # payment.pay_thp()                       # 9. Wallet@Post
        # payment.pay_truemoney()                 # 10. TrueMoney Wallet
        # payment.pay_qr_credit()                 # 11. QR Credit
        
        time.sleep(WAIT_TIME)
        # =========================================================
        
        # 4. จบงาน: ถัดไป -> เสร็จสิ้น
        print("[*] Next (3)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"]).click_input()
        time.sleep(WAIT_TIME)

        finish_transaction(main_window)
        print("[V] Service 3 Success!")

    except Exception as e:
        # ระบบกู้ชีพ: พยายามหา App มาแคปภาพให้ได้
        target_app = app if (app is not None) else ctx.app
        
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Mutual Service 3",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
            print("[/] บันทึกภาพ Error เรียบร้อย")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (App Disconnected)")

        print(f"[X] FAILED: {e}")