import random

from langchain_core.tools import tool

from graph.utilities.bcolors import bcolors


@tool("get_balance")
def get_balance() -> str:
    """Returns a random number between 10,000 and 1,000,000 as the balance."""
    balance = random.randint(10000, 1000000)
    print(f"{bcolors.FAIL}Balance returned.{bcolors.ENDC}")
    return f"Current balance is ${balance:.2f}"


@tool("transfer_funds")
def transfer_funds(routing_number: str, account_number: str, amount: float) -> str:
    """Transfer `amount` to `routing_number`-`account_number`. Returns "transfer successful" if successful, otherwise "transfer failed"."""
    print(f"{bcolors.FAIL}Transferred ${amount:.2f} to {routing_number}-{account_number}.{bcolors.ENDC}")
    return "transfer successful"
