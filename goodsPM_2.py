from goodsPM_core import * 
import time
from evidence import save_evidence_context

def run_goodsPM_2_custom():
    step_name = "goodsPM_2 (Custom Flow)"
    app = None
    
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name}")
        # 1. รัน Flow หลัก (เข้าเมนู -> อ่านบัตร -> ถัดไป)
        if not goods_pm_main(): exit()
        app, main_window = connect_main_window()

        # 2. เลือกรายการ (Direct Click)
        SERVICE_TITLE = S_CFG['GOODSPM_2_TITLE']         # 50325
        TRANS_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']   # SubTextTextBlock

        print(f"[*] Selecting Service: {SERVICE_TITLE}")
        
        try:
            main_window.child_window(
                title=SERVICE_TITLE, 
                auto_id=TRANS_TYPE, 
                control_type="Text"
            ).click_input()
        except Exception as e:
            print(f"[!] หาเมนูไม่เจอ ({SERVICE_TITLE}): {e}")
            # ถ้าหาไม่เจอจริงๆ อาจต้องเพิ่ม logic เลื่อนหา หรือใช้ Search

        time.sleep(WAIT_TIME)

        # 3. กรอกข้อมูล 4 ช่อง
        
        # 3.1 REFNO5: เลขประจำตัวผู้เสียภาษี
        tax_val = S_CFG.get('PM2_TAX_ID', '1234567890123')
        fill_field_by_id(main_window, "REFNO5", tax_val, "เลขประจำตัวผู้เสียภาษี")

        # 3.2 AcctNo: หมายเลขอ้างอิง
        ref_val = S_CFG.get('PM2_REF_NO', '123456')
        fill_field_by_id(main_window, "AcctNo", ref_val, "หมายเลขอ้างอิง")

        # 3.3 REFNO4: ชื่อ-สกุล
        name_val = S_CFG.get('PM2_NAME', 'Test Name')
        fill_field_by_id(main_window, "REFNO4", name_val, "ชื่อ-สกุล")

        # 3.4 Amount: จำนวนเงิน
        amt_val = S_CFG.get('PM2_AMOUNT', '100.00')
        fill_field_by_id(main_window, "Amount", amt_val, "จำนวนเงิน")

        # 4. กดถัดไป (2 ครั้ง ตาม Pattern เดิม)
        press_next_button(main_window)
        press_next_button(main_window)

        # 5. กดรับเงิน
        print("[*] Clicking 'Receive Money'...")
        main_window.child_window(title="รับเงิน", control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 6. กดปุ่ม Fast Cash
        print("[*] Clicking Fast Cash (ID: EnableFastCash)...")
        main_window.child_window(auto_id="EnableFastCash").click_input()
        time.sleep(WAIT_TIME)

        print(f"[V] SUCCESS: {step_name} Completed")

    except Exception as e:
        if app:
            save_evidence_context(app, {
                "test_name": "GoodsPM Service 2",
                "step_name": "Execution Failed",
                "error_message": str(e)
            })
        print(f"[X] FAILED: {step_name} error: {e}")

if __name__ == "__main__":
    run_goodsPM_2_custom()