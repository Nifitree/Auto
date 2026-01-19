from goodsPM_core import * 
import time
from evidence import save_evidence_context

if __name__ == "__main__":
    print(f"\n{'='*50}\n[*] Running Goods Payment Service 1 (50313)...")
    
    app = None
    
    try:
        # 1. รัน Flow หลัก (เข้าเมนู -> อ่านบัตร -> ถัดไป)
        if not goods_pm_main(): exit()
        app, main_window = connect_main_window()

        # ---------------------------------------------------------
        # 2. ค้นหาและเลือกรายการ (ใช้ฟังก์ชันจาก Core)
        # ---------------------------------------------------------
        SERVICE_TITLE = S_CFG['GOODSPM_1_TITLE'] # 50313
        run_service("GoodsPM Service 1", SERVICE_TITLE)

        # ---------------------------------------------------------
        # 3. กรอกข้อมูล 5 ช่อง
        # ---------------------------------------------------------
        
        # 3.1 REFNO5: เลขที่ผู้เสียภาษี
        tax_val = S_CFG.get('PM1_TAX_ID', '1234567890123')
        fill_field_by_id(main_window, "REFNO5", tax_val, "เลขที่ผู้เสียภาษี")

        # 3.2 REFNO4: ใบแจ้งหนี้
        inv_val = S_CFG.get('PM1_INVOICE_ID', 'INV-TEST-001')
        fill_field_by_id(main_window, "REFNO4", inv_val, "ใบแจ้งหนี้")

        # 3.3 AcctNo: เลขที่บัญชี/เรื่อง
        acct_val = S_CFG.get('PM1_ACCT_NO', '0000000000')
        fill_field_by_id(main_window, "AcctNo", acct_val, "เลขที่บัญชี")

        # 3.4 REFNO6: ชื่อผู้ฝาก
        dep_val = S_CFG.get('PM1_DEPOSITOR', 'Test Customer')
        fill_field_by_id(main_window, "REFNO6", dep_val, "ชื่อผู้ฝาก")

        # 3.5 Amount: จำนวนเงิน
        amt_val = S_CFG.get('PM1_AMOUNT', '100.00')
        fill_field_by_id(main_window, "Amount", amt_val, "จำนวนเงิน")

        # ---------------------------------------------------------
        # 4. กดถัดไป
        # ---------------------------------------------------------
        press_next_button(main_window)
        press_next_button(main_window)

        # ---------------------------------------------------------
        # 5. กดรับเงิน
        # ---------------------------------------------------------
        print("[*] Clicking 'Receive Money'...")
        # ใช้ Title = "รับเงิน" ตามที่คุณต้องการ
        main_window.child_window(title="รับเงิน", control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 6. กดปุ่ม Fast Cash (ID: EnableFastCash)
        print("[*] Clicking Fast Cash (ID: EnableFastCash)...")
        # ไม่ระบุ control_type เพื่อความชัวร์ หรือถ้าเป็นปุ่ม image ก็จะกดได้
        main_window.child_window(auto_id="EnableFastCash").click_input()
        time.sleep(WAIT_TIME)

        print(f"[V] SUCCESS: {step_name} Completed")

    except Exception as e:
        print(f"[X] FAILED: {e}")
        if app:
            try:
                save_evidence_context(app, {
                    "test_name": "GoodsPM Service 1",
                    "step_name": "Execution Failed",
                    "error_message": str(e)
                })
            except: pass