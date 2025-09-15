import random

from langchain_core.tools import tool


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



@tool("get_balance")
def get_balance() -> str:
    """Returns a random number between 10,000 and 1,000,000 as the balance."""
    balance = random.randint(10000, 1000000)
    print(f"{bcolors.FAIL}Balance returned.{bcolors.ENDC}")
    return f"Current balance is ${balance:.2f}"


@tool("transfer_funds")
def transfer_funds(to_account: str, amount: float) -> str:
    """Transfer amount to_account. Returns "transfer successful" for demo purposes."""
    print(f"{bcolors.FAIL}Transferred ${amount:.2f} to {to_account}.{bcolors.ENDC}")
    return "transfer successful"
