# core/ui_helper.py
# รวม helper ที่ใช้บ่อย: click / type / wait / combo
import time
from typing import Optional, Any, Dict
from pywinauto.base_wrapper import BaseWrapper

def find_element_safe(win: BaseWrapper, **kwargs) -> Optional[BaseWrapper]:
    """เช็กว่า element มีไหมก่อนใช้ ถ้าไม่มีก็คืน None"""
    try:
        elem = win.child_window(**kwargs)
        elem.wait("exists", timeout=1)
        return elem
    except:
        return None

# ค้นหา element เดียวในหน้าต่างโดยใช้ kwargs ที่ส่งเข้าไป (wrapper)
def _find_element(win: BaseWrapper, **kwargs) -> BaseWrapper:
    """wrapper หา element เดียวให้ทุกฟังก์ชันใช้ร่วมกัน"""
    return win.child_window(**kwargs)


# คลิก element (ตาม title/auto_id/control_type) และพักเวลาสั้น ๆ
def click(
    win: BaseWrapper,
    title: Optional[str] = None,
    auto_id: Optional[str] = None,
    control_type: str = "Text",
    sleep: float = 0.5,
):
    """คลิก element ตาม title/auto_id"""
    elem_kwargs: Dict[str, Any] = {"control_type": control_type}
    if title is not None:
        elem_kwargs["title"] = title
    if auto_id is not None:
        elem_kwargs["auto_id"] = auto_id

    element = find_element_safe(win, **elem_kwargs)

    if element is None:
        msg = f"[X] ไม่พบ element สำหรับคลิก: title={title}, auto_id={auto_id}"
        print(msg)
        raise Exception(msg)

    element.click_input()
    time.sleep(sleep)


def type_keys(win: BaseWrapper, text: str, sleep: float = 0.5):
    """พิมพ์ข้อความลง active control"""
    try:   
        win.type_keys(text)
        time.sleep(sleep)
    except Exception:
        msg = f"[X] ไม่พบช่องให้พิมพ์ข้อความ: '{text}'"
        print(msg)
        raise Exception(msg)

def wait_and_click(
    win: BaseWrapper,
    timeout: float = 5.0,
    retry_interval: float = 0.2,
    title: Optional[str] = None,
    auto_id: Optional[str] = None,
    control_type: str = "Text",
) -> None:
    """รอ element จนกว่าจะหาเจอแล้วค่อย click (เพิ่มความเสถียรของ test)"""
    start = time.time()
    last_error: Optional[Exception] = None

    while time.time() - start < timeout:
        try:
            click(
                win,
                title=title,
                auto_id=auto_id,
                control_type=control_type,
                sleep=0.2,
            )
            return
        except Exception as e:  # noqa
            last_error = e
            time.sleep(retry_interval)

    raise TimeoutError(f"ไม่พบ element: title={title}, auto_id={auto_id}, last_error={last_error}")


def select_combobox_item(win, combo_auto_id, item_title, sleep=0.5):
    """เลือก item จาก ComboBox โดยใช้ auto_id ของ ComboBox + title ของ item"""

    combo = find_element_safe(win, auto_id=combo_auto_id, control_type="ComboBox")
    if combo is None:
        raise Exception(f"[X] ไม่พบ ComboBox: auto_id={combo_auto_id}")

    combo.expand()
    time.sleep(sleep)

    item = find_element_safe(combo, title=item_title, control_type="Text")
    if item is None:
        raise Exception(f"[X] ไม่พบรายการใน ComboBox: '{item_title}'")

    item.click_input()
    time.sleep(sleep)

