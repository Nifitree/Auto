import time
from configparser import ConfigParser
from core.app_context import AppContext
from core.ui_helper import click, type_keys, run_step, select_combobox_item


class PaymentFlow:
    """Flow เกี่ยวกับการชำระเงินทุกรูปแบบ"""

    def __init__(self, config: ConfigParser, ctx: AppContext):
        self.config = config
        self.ctx = ctx
        self.PM = config["PAYMENT"]
        self.RS = config["RETAIL_SALES"]
        self.GL = config["GLOBAL"]
        self.SLEEP = config.getint("GLOBAL", "LOAD_TIME_SEC")

    def _abort_print(self, win):
        click(
            win,
            title=self.GL["ABORT_PRINT_TITLE"],
            auto_id=self.GL["ABORT_PRINT_AUTO_ID"],
            control_type="Button",
        )

    # ---------- 1) เงินสด ----------
    def pay_cash(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["CASH_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            type_keys(win, f"{self.PM['CASH_AMOUNT']}{{ENTER}}", sleep=self.SLEEP)
            try:
                click(
                win,
                title=self.RS["NEXT_TITLE"],
                auto_id=self.RS["NEXT_AUTO_ID"],
            )
            except Exception:
                print("[!] มีเงินทอนไม่เพียงพอ")
                raise Exception("INSUFFICIENT_CASH_CHANGE")    
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_cash", _inner)

    # ---------- 2) เงินพอดี (จ่ายเร็ว) ----------
    def pay_exact(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["PAYMENT_FAST"],
                auto_id=self.PM["HOTKEY_F_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_exact", _inner)

    # ---------- 3) QR พร้อมเพย์ ----------
    def pay_qr(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["QR_CODE_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            click(
                win,
                title=self.RS["NEXT_TITLE"],
                auto_id=self.RS["NEXT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_qr", _inner)

    # ---------- 4) เช็ค ----------
    def pay_cheque(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["CHECK_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)

            # กรอกข้อมูลเช็ค
            type_keys(win, f"{self.PM['NUMBER_P']}{{TAB}}", sleep=self.SLEEP)
            type_keys(win, f"{self.PM['NUMBER_C']}{{TAB}}", sleep=self.SLEEP)
            type_keys(win, f"{self.PM['DATE_C']}{{TAB}}", sleep=self.SLEEP)

            # เลือกธนาคารจาก ComboBox
            select_combobox_item(
                win,
                combo_auto_id=self.PM["BANK_COMBO_AUTO_ID"],
                item_title=self.PM["BANK_C"],
                sleep=self.SLEEP,
            )

            click(
                win,
                title=self.RS["NEXT_TITLE"],
                auto_id=self.RS["NEXT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_cheque", _inner)

    # ---------- 5) บัตรเครดิต ----------
    def pay_credit(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["CREDIT_CARD_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            type_keys(win, f"{self.PM['CREDIT_CARD_AMOUNT']}{{ENTER}}", sleep=self.SLEEP)
            click(
                win,
                title=self.RS["NEXT_TITLE"],
                auto_id=self.RS["NEXT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_credit", _inner)

    # ---------- 6) เดบิต ----------
    def pay_debit(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["DEBIT_CARD_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            click(
                win,
                title=self.RS["NEXT_TITLE"],
                auto_id=self.RS["NEXT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_debit", _inner)

    # ---------- 7) อาลีเพย์ ----------
    def pay_alipay(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["ALIPYAY_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_alipay", _inner)

    # ---------- 8) วีแชท ----------
    def pay_wechat(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["WECHAT_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_wechat", _inner)

    # ---------- 9) กระเป๋าตสตางค์@ไปรษณีย์ ----------
    def pay_thp_wallet(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["THP_PEYMENT_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_thp_wallet", _inner)

    # ---------- 10) QR เครดิต ----------
    def pay_qr_credit(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["QR_CREDIT_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_qr_credit", _inner)

    # ---------- 11) ทรูมันนี่ ----------
    def pay_truewallet(self):
        app, win = self.ctx.connect()

        def _inner():
            click(
                win,
                title=self.PM["TRUEMANEY_TITLE"],
                auto_id=self.PM["PAYMENT_AUTO_ID"],
            )
            time.sleep(self.SLEEP)
            self._abort_print(win)

        run_step(app, "payment_truewallet", _inner)