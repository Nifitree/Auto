from pywinauto.application import Application
import time
from module.scroll_utils import force_scroll_down


def _ensure_spec(window):
    """Return a WindowSpecification for the given window-like object.

    Many pywinauto wrapper objects (UIAWrapper) don't provide
    child_window. Convert them to a WindowSpecification using the
    parent Application so the rest of the code can call
    child_window(...) reliably.
    """
    # If it already supports child_window, return as-is
    if hasattr(window, "child_window"):
        return window

    # Try to construct a WindowSpecification from wrapper's app and handle
    try:
        app = getattr(window, "app", None)
        handle = getattr(window, "handle", None)
        if app is not None and handle is not None:
            return app.window(handle=handle)
    except Exception:
        pass

    # Fallback: return original object (will raise if unsupported)
    return window


def connect_app(window_title):
    print("[*] Connecting to window...")
    app = Application(backend="uia").connect(title_re=window_title, timeout=10)
    win = app.window(title_re=window_title)
    win.set_focus()
    print("[/] Connected OK")
    return win

# ปุ่มตัวแทนรับชำระเงิน
def open_agency(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_AGENCY_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มตัวแทนรับชำระเงินสำเร็จ")

# ปุ่มแสกนบาร์โค้ดของหน่วยงาน
def open_SAB(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_SAB_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มแสกนบาร์โค้ดของหน่วยงานสำเร็จ")

# ปุ่มบริการทั้งหมด
def open_AS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_AS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการทั้งหมดสำเร็จ")

# ปุ่มบริการธนาคาร
def open_BaS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_BaS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการธนาคารสำเร็จ")

# ปุ่มบริการการจอง
def open_BoS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_BoS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการการจองสำเร็จ")

# ปุ่มบริการชำระเงิน DPost
def open_DPS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_DPS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการชำระเงิน DPostสำเร็จ")

# ปุ่มบริการชำระค่าสินค้า
def open_GPS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_GPS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการชำระค่าสินค้าสำเร็จ")

# ปุ่มบริการประกันภัย
def open_IS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_IS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการประกันภัยสำเร็จ")

# ปุ่มบริการสินเชื่อ
def open_LS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_LS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการสินเชื่อสำเร็จ")

# ปุ่มบริการกองทุนรวม
def open_MFS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_MFS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการกองทุนรวมสำเร็จ")

# ปุ่มบริการไปรษณีย์
def open_PoS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_PoS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการไปรษณีย์สำเร็จ")

# ปุ่มบริการชำระเงิน
def open_PaS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_PaS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มบริการชำระเงินสำเร็จ")

# ปุ่มชำระบิลมหาวิยาลัย
def open_UnS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_UnS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มชำระบิลมหาวิยาลัยสำเร็จ")

# ปุ่มสาธารณูปโภค
def open_UtS(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_UtS_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มสาธารณูปโภคสำเร็จ")

# ปุ่มตรวจสอบเบอร์ Wallet@Post
def open_CW(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_CW_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มตรวจสอบเบอร์ Wallet@Postสำเร็จ")

# ปุ่มการยืนยันตัวตน
def open_eKYC(win, AB, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=AB['HOTKEY_eKYC_TITLE'],
        auto_id=AB['HOTKEY_AUTO_ID'],
        control_type=AB['HOTKEY_CONTROL_TYPE']
    ).click_input()

    time.sleep(delay)
    print("[/] กดปุ่มการยืนยันตัวตนสำเร็จ")


def fill_phone_number(win, PH, delay, config):
    print("[*] ค้นหาเบอร์โทร...")

    try:
        spec = _ensure_spec(win)

        phone_custom = spec.child_window(
            auto_id="PhoneNumber_UserControlBase",
            control_type="Custom"
        )

        phone_custom.wait("ready", timeout=5)
    except:
        print("[!] ไม่พบ ต้อง scroll ลง")
        force_scroll_down(win, config)
        spec = _ensure_spec(win)
        phone_custom = spec.child_window(
            auto_id="PhoneNumber_UserControlBase",
            control_type="Custom"
        )

        phone_custom.wait("ready", timeout=5)

    phone_edit = phone_custom.child_window(
        auto_id="PhoneNumber",
        control_type="Edit"
    )

    phone_edit.wait("ready", timeout=5)

    phone_edit.click_input()
    time.sleep(0.2)
    phone_edit.type_keys("^a{BACKSPACE}")
    time.sleep(0.2)
    phone_edit.type_keys(PH['PHONE_NUM'], with_spaces=True)

    print("[/] กรอกเบอร์โทรเสร็จ")


def click_read_id(win, ID, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=ID['ID_TITLE'],
        auto_id=ID['ID_AUTO_ID'],
        control_type=ID['ID_CONTROL_TYPE']
    ).click_input()
    time.sleep(delay)

    print("[/] อ่านบัตรสำเร็จ")


def click_next(win, NX, delay):
    spec = _ensure_spec(win)

    spec.child_window(
        title=NX['NEXT_TITLE'],
        auto_id=NX['NEXT_AUTO_ID'],
        control_type=NX['NEXT_CONTROL_TYPE']
    ).click_input()
    time.sleep(delay)

    print("[/] กดปุ่มถัดไปสำเร็จ")