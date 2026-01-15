import time
from banking_core import *
from evidence import save_evidence_context

# ค่าคงที่สำหรับ Flow นี้
BARCODE_VALUE = "|01075370023380003100683648903010"
PAYMENT_AMOUNT = "100.00"

def run_banking_1_custom():
    step_name = "banking_services1 (Custom Flow)"
    app = None  # ประกาศตัวแปร app ไว้ก่อนเพื่อกัน error ใน except block
    
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name}")

        # 1. เข้าเมนูหลัก Banking (Agency -> BaS -> Read ID -> Fill Info)
        if not banking_services_main():
            return

        app, window = connect_main_window()

        # 2. ค้นหารายการ (Search)
        service_title = S_CFG["BANKING_8_TITLE"]
        search_id = S_CFG["SEARCH_EDIT_ID"]
        print(f"[*] Searching for Service: {service_title}")
        
        # หาช่อง Search และพิมพ์รหัส
        search_input = window.child_window(auto_id=search_id, control_type="Edit")
        search_input.click_input()
        search_input.type_keys("^a{BACKSPACE}")  # Clear ช่อง
        search_input.type_keys(service_title, with_spaces=True)
        search_input.type_keys("{ENTER}")
        time.sleep(1.5)
        
        # คลิกผลลัพธ์ที่ค้นหาได้
        target = window.child_window(title=service_title, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text")
        if target.exists(timeout=3):
            target.click_input()
        else:
            raise Exception(f"ไม่พบรายการ {service_title} ในผลการค้นหา")
        time.sleep(WAIT_TIME)

        # 3. กรอก Barcode (BARCODE_INPUT_ID8)
        barcode_id = S_CFG["BARCODE_INPUT_ID8"]
        print(f"[*] Typing Barcode at ID '{barcode_id}'...")
        barcode_input = window.child_window(auto_id=barcode_id, control_type="Edit")
        barcode_input.click_input()
        barcode_input.type_keys(BARCODE_VALUE)
        time.sleep(WAIT_TIME)

        # 4. กดปุ่มถัดไป (ครั้งที่ 1)
        print("[*] Clicking Next (1)...")
        window.child_window(
            title=B_CFG["NEXT_TITLE"], 
            auto_id=B_CFG["ID_AUTO_ID"], 
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        # 5. กรอกชื่อลูกค้า (AcctNo_UserControlBase)
        CUSTOMER_NAME = "นายทดสอบ ระบบ"  # ชื่อลูกค้าทดสอบ
        print(f"[*] Typing Customer Name '{CUSTOMER_NAME}'...")
        name_input = window.child_window(auto_id="REFN05", control_type="Edit")
        name_input.click_input()
        name_input.type_keys(CUSTOMER_NAME, with_spaces=True)
        time.sleep(WAIT_TIME)

        # 6. กรอกจำนวนเงิน (AutoID = "Amount")
        print(f"[*] Typing Amount '{PAYMENT_AMOUNT}'...")
        amount_input = window.child_window(auto_id="Amount", control_type="Edit")
        amount_input.click_input()
        amount_input.type_keys(PAYMENT_AMOUNT)
        time.sleep(WAIT_TIME)

        # 6. กดปุ่มถัดไป (ครั้งที่ 2)
        print("[*] Clicking Next (2)...")
        window.child_window(
            title=B_CFG["NEXT_TITLE"], 
            auto_id=B_CFG["ID_AUTO_ID"], 
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        # 7. กดปุ่มถัดไป (ครั้งที่ 3)
        print("[*] Clicking Next (3)...")
        window.child_window(
            title=B_CFG["NEXT_TITLE"], 
            auto_id=B_CFG["ID_AUTO_ID"], 
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        # 8. กดรับเงิน (Receive Money)
        print("[*] Clicking 'Receive Money'...")
        window.child_window(title="รับเงิน", control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 9. กดปุ่ม Fast Cash (ID: EnableFastCash)
        print("[*] Clicking Fast Cash (ID: EnableFastCash)...")
        # ไม่ระบุ control_type เพื่อความชัวร์ หรือถ้าเป็นปุ่ม image ก็จะกดได้
        window.child_window(auto_id="EnableFastCash").click_input()
        time.sleep(WAIT_TIME)

        print(f"[V] SUCCESS: {step_name} Completed")

    except Exception as e:
        # บันทึกหลักฐานเมื่อเกิด Error
        if app:
            save_evidence_context(app, {
                "test_name": "Banking Service 1 (Barcode Flow)",
                "step_name": step_name,
                "error_message": str(e)
            })
        print(f"[X] FAILED: {step_name} error: {e}")

if __name__ == "__main__":
    run_banking_1_custom()