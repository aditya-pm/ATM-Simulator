import os
from atmsim import AtmSim, Fore
import logging

database_password = input("Enter database password: ")
atm = AtmSim(database_password)

print(Fore.fstring("ATM Simulator", "BOLD", "YELLOW", "UNDERLINE"))
print()

while True:
    print("━" * 8, Fore.fstring("LOGIN", "BLUE", "UNDERLINE"), "━" * 8)
    username = input("Enter username: ")

    if atm.check_user(username):
        password = ""

        while password != atm.get_pin(username):
            password = input("Enter PIN: ")
            
            if password == atm.get_pin(username):

                logging.info(f" New User login - '{username}'")
                os.system("cls")
                username_formatted = Fore.fstring(
                    username.title(), "CYAN", "BOLD", "UNDERLINE")
                print(Fore.fstring(
                    f"\nSuccessfully logged in as {username_formatted}!", "GREEN"))
                atm.logged_user = username

                while True:
                    print()
                    choice = input(
                        "Actions (Enter number corresponding to action):\n"
                        "1. Withdraw\n2. Deposit\n3. Change PIN\n"
                        "4. Check balance\n5. Check Denominations\n"
                        "0. Logout \n: "
                    )

                    if choice == "1":
                        os.system("cls")
                        try:
                            amount_withdraw = float(input("Enter amount to withdraw: "))
                            print()
                            print(atm.withdraw(username, amount_withdraw))
                        except ValueError:
                            print(Fore.fstring(
                                "Enter a NUMBER to withdraw", "BOLD"))

                    elif choice == "2":
                        os.system("cls")
                        try:
                            amount_deposit = float(
                                input("Enter amount to deposit: "))
                            print("\n" + atm.deposit(username, amount_deposit))
                            print()
                        except ValueError:
                            print(Fore.fstring(
                                "Enter a NUMBER to deposit", "BOLD"))

                    elif choice == "3":
                        os.system("cls")
                        new_password = input("Enter new PIN: ")
                        password = new_password
                        print("\n" + atm.change_pin(username, new_password))

                    elif choice == "4":
                        os.system("cls")
                        print("\n" + Fore.fstring(
                            f"Current Balance - ₹{atm.get_balance(username)}",
                            "BOLD", "UNDERLINE"))

                    elif choice == "5":
                        os.system("cls")
                        print(Fore.fstring(
                            "\nDenominations available currently in the ATM:", 
                            "BOLD", "UNDERLINE"))
                        print(Fore.fstring("₹500", "GREEN") +
                              f" --> {atm.check_denomination(atm.fivehundreds)}")
                        print(Fore.fstring("₹200", "ORANGE") +
                              f" --> {atm.check_denomination(atm.twohundreds)}")
                        print(Fore.fstring("₹100", "MAGENTA") +
                              f" --> {atm.check_denomination(atm.hundreds)}")

                    elif choice == "0":
                        logging.info(f" User logged out - '{username}'")
                        os.system("cls")
                        break

                    else:
                        os.system("cls")
                        print(Fore.fstring(
                            "\nNot a valid action. Choose between 1, 2, 3, 4, 5 and 0", 
                            "YELLOW"))

            elif password == "0":
                os.system("cls")
                break

            else:
                print(Fore.fstring(
                    "Incorrect PIN. Try again. Press 0 to go back to login.", "RED"))

    else:
        print(Fore.fstring(f"Invalid username. Try again.", "RED"))
