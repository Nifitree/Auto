from banking_core import run_service, S_CFG

if __name__ == "__main__":
    run_service("Banking_1", S_CFG["BANKING_1_TITLE"], use_main=True, double_next=True)