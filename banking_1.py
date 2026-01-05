import time
from banking_core import *
# ค่าคงที่สำหรับ Flow นี้
BARCODE_VALUE = "|0107535000176014033752004685193000"
PAYMENT_AMOUNT = "100.00"   # หมายเหตุ: ผมใส่ค่าสมมติไว้ คุณสามารถแก้เป็นยอดจริงที่ต้องการเทสได้ครับ

def run_banking_1_custom():
    step_name = "banking_services1 (Custom Flow)"
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name}")

        # 1. เข้าเมนูหลัก Banking (Agency -> BaS -> Read ID -> Fill Info)
        if not banking_services_main():
            return

        app, window = connect_main_window()

        # 2. เลือกรายการ 30156
        service_title = S_CFG["BANKING_1_TITLE"]
        print(f"[*] Selecting Service: {service_title}")
        window.child_window(
            title=service_title, 
            auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], 
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        # 3. กรอก Barcode (BARCODE_INPUT_ID1)
        barcode_id = S_CFG["BARCODE_INPUT_ID1"]
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

        # 5. กรอกจำนวนเงิน (AutoID = "Amount")
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
        # หมายเหตุ: ใช้ title="รับเงิน" ตามที่คุณระบุ
        print("[*] Clicking 'Receive Money'...")
        window.child_window(title="รับเงิน", control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 9. กดจ่ายเงิน Payment (Fast Cash)
        # หมายเหตุ: ใช้ title="Payment (Fast Cash)" หรือถ้ามี AutoID เฉพาะสามารถแก้ตรงนี้ได้
        print("[*] Clicking 'Payment (Fast Cash)'...")
        # ลองหาปุ่มที่มีคำว่า Payment (Fast Cash) หรือ Fast Cash
        # หากปุ่มชื่อ "Payment (Fast Cash)" เป๊ะๆ ให้ใช้บรรทัดล่างนี้:
        window.child_window(title="Payment (Fast Cash)", control_type="Text").click_input()
        
        # กรณีถ้าปุ่มเป็นชื่ออื่น เช่น "Fast Cash" เฉยๆ ให้แก้ title ครับ
        time.sleep(WAIT_TIME)

        print(f"[V] SUCCESS: {step_name} Completed")

    except Exception as e:
        print(f"[X] FAILED: {step_name} error: {e}")

if __name__ == "__main__":
    run_banking_1_custom()