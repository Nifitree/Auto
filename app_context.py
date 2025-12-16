# core/app_context.py
# เป็นตัวกลางเก็บ app และ main_window ให้ทุก flow ใช้ร่วมกัน
from typing import Optional, Tuple
from pywinauto.application import Application


class AppContext:
    """เก็บสถานะของ Application และ Main Window
    - ให้ทุก flow ใช้ร่วมกัน ไม่ต้อง connect ซ้ำๆ
    """

    def __init__(self, window_title_regex: str, backend: str = "uia"):
        self.window_title_regex = window_title_regex
        self.backend = backend
        self.app: Optional[Application] = None
        self.main_window = None

    def connect(self, timeout: int = 10) -> Tuple[Application, object]:
        """เชื่อมต่อกับแอป ถ้ายังไม่เคยเชื่อมต่อ ก็ connect ใหม่
        ถ้าเคยแล้วจะใช้ instance เดิม
        """
        if self.app is None:
            print(f"[*] กำลังเชื่อมต่อ Application ด้วย title: {self.window_title_regex}")
            self.app = Application(backend=self.backend).connect(
                title_re=self.window_title_regex,
                timeout=timeout,
            )
            self.main_window = self.app.window(title_re=self.window_title_regex,)
            self.main_window.set_focus()
            print("[/] เชื่อมต่อ Application สำเร็จ")
        return self.app, self.main_window