from banking_core import run_service, S_CFG

if __name__ == "__main__":
    run_service("Banking_10", S_CFG["BANKING_10_TITLE"], use_search=True)