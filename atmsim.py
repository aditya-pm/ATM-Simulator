import mysql.connector as sqltor
from mysql.connector import errorcode
import os
import time
import logging

logging.basicConfig(
    filename="atm.log",
    level=logging.INFO,
    format='%(asctime)s : %(levelname)s : %(message)s',
)

class Logger:

    @staticmethod
    def log(func):
        def wrapper(instance, *args, **kwargs):
            result = func(instance, *args, **kwargs)
            logging.info(f" User '{instance.logged_user}' requested action `{func.__name__}`")
            return result
        return wrapper


class Fore:
    RESET = '\033[0m'
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[35m'
    ORANGE = '\033[38;5;214m'
    CYAN = '\033[96;5m'

    @classmethod
    def fstring(cls, string, *colour):
        """Creates a generator containing all the formats specified
        (ANSI codes) and joins it with a string and resets."""
        return "".join(getattr(cls, attr.upper()) for attr in colour) + string + Fore.RESET


class AtmSim:

    PIN_LENGTH = 4

    def __init__(self, database_password, database_name = "atmsim"):
        """ Initialise the ATM simulation. """

        self.password = database_password
        self.database = database_name
        self.user_table = "atmdetails"
        self.denomination_table = "denominations"
        self.host = "localhost"
        self.user = "root"
        self.username = "username"
        self.user_pin = "pin"
        self.balance = "balance"
        self.fivehundreds = "fivehundreds"
        self.twohundreds = "twohundreds"
        self.hundreds = "hundreds"
        self.logged_user = None
        os.system("cls")

        try:
            self.__setup_connection()
            self.__setup_database()
            self.__setup_tables()
            self.__insert_test_data()

        except sqltor.Error as error:
            print(Fore.fstring(f"MySQL ERROR: {error}", "RED"))
            if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("The password is likely incorrect.")
                logging.critical("Program terminated! - Incorrect database password")
                time.sleep(5)
                exit()
            if error.errno == errorcode.ER_DB_CREATE_EXISTS:
                logging.warning("Proceeding with the existing database")
                print("Proceeding with the existing database...")
            
        # main connection and cursor creation.
        self.__setup_connection(self.database)
        time.sleep(5)
        os.system("cls")

    def check_user(self, username: str) -> bool:
        """ Returns True if the username exists in the table; otherwise, returns False. """
        self.cursor.execute(
            f"SELECT * FROM {self.user_table} "
            f"WHERE {self.username} = %s;", (username,)
        )
        return False if self.cursor.fetchall() == [] else True

    def check_denomination(self, bills: str) -> int:
        """ Returns the number of notes of the given bill. bills can be one of these:
        fivehundreds, twohundreds, hundreds. """
        self.cursor.execute(f"SELECT {bills} FROM {self.denomination_table};")
        return self.cursor.fetchall()[0][0]

    def get_pin(self, username: str) -> str:
        """ Returns the user's PIN from the username. """
        self.cursor.execute(
            f"SELECT {self.user_pin} "
            f"FROM {self.user_table} "
            f"WHERE {self.username} = %s", (username,)
        )
        return self.cursor.fetchall()[0][0]

    @Logger.log
    def get_balance(self, username: str) -> float:
        """ Returns the user's balance from the username in the form of 
        a list containing a tuple, which is indexed to get balance. """
        self.cursor.execute(
            f"SELECT {self.balance} "
            f"FROM {self.user_table} "
            f"WHERE {self.username} = %s", (username,)
        )
        return self.cursor.fetchall()[0][0]

    def denominations_updater(
            self, amount, mode_of_transaction, deposit_denominations: list = None
        ):
        """
        withdraw does not need deposit_denominations list, hence to prevent
        required param error, we define it so it can be used along with both
        deposit and withdrawal. (Can be defined as anything, incl None).
        """

        available_500s = self.check_denomination(self.fivehundreds)
        available_200s = self.check_denomination(self.twohundreds)
        available_100s = self.check_denomination(self.hundreds)

        if mode_of_transaction == "w":

            needed_500s = amount // 500
            remaining_amount_500 = amount % 500
            if needed_500s > available_500s:
                needed_500s = available_500s
                remaining_amount_500 = amount - (needed_500s * 500)

            needed_200s = remaining_amount_500 // 200
            remaining_amount_200 = remaining_amount_500 % 200
            if needed_200s > available_200s:
                needed_200s = available_200s
                remaining_amount_200 = remaining_amount_500 - (needed_200s * 200)

            needed_100s = remaining_amount_200 // 100
            remaining_amount_100 = remaining_amount_200 % 100
            if needed_100s > available_100s:
                needed_100s = available_100s
                remaining_amount_100 = remaining_amount_200 - (needed_100s * 100)

            if remaining_amount_100 > 0:
                return "failed"

            self.cursor.execute(
                f"UPDATE {self.denomination_table} "
                f"SET {self.fivehundreds} = {self.fivehundreds} - {needed_500s}, "
                f"{self.twohundreds} = {self.twohundreds} - {needed_200s}, "
                f"{self.hundreds} = {self.hundreds} - {needed_100s}"
            )
            self.mycon.commit()
            return int(needed_500s), int(needed_200s), int(needed_100s)

        if mode_of_transaction == "d":

            if len(deposit_denominations) != 3:
                return "invalid no. of inputs"
            
            try:
                deposit_denominations = [int(x) for x in deposit_denominations]
            except:
                return "invalid input type"

            fivehundreds = deposit_denominations[0]
            twohundreds = deposit_denominations[1]
            hundreds = deposit_denominations[2]

            if 500 * fivehundreds + 200 * twohundreds + 100 * hundreds == amount:
                self.cursor.execute(
                    f"UPDATE {self.denomination_table} "
                    f"SET {self.fivehundreds} = {self.fivehundreds} + {fivehundreds}, "
                    f"{self.twohundreds} = {self.twohundreds} + {twohundreds}, "
                    f"{self.hundreds} = {self.hundreds} + {hundreds}"
                )
                self.mycon.commit()
                return "success"

    @Logger.log
    def withdraw(self, username: str, amount: float):
        """ withdraws money and updates denominations. """

        if amount < 0:
            return Fore.fstring(
                "You can't withdraw in terms of a negative.", "RED"
            )
        
        elif amount % 100 != 0:
            return Fore.fstring(
                "Withdrawal Failed! You can only withdraw in"
                "denominations of ₹100.", "RED"
            )

        balance = float(self.get_balance(username))
        if amount > balance:
            return Fore.fstring(
                "You can't withdraw more than your bank balance.",
                "RED", "BOLD"
            )
        
        else: 
            result = self.denominations_updater(amount, "w")
            if result == "failed":
                return (
                    "Transaction Failed!\nThere isn't enough "
                    "cash in the ATM currently to complete that transaction."
                    "\nTRY again later or withdraw a smaller amount."
                )
            
            else:
                remaining_amt = balance - amount
                self.cursor.execute(
                    f"UPDATE {self.user_table} "
                    f"SET {self.balance} = %s "
                    f"WHERE {self.username} = %s", (remaining_amt, username,)
                )
                self.mycon.commit()

                return (
                    Fore.fstring(f"Amount Withdrawn: ₹{amount}\n", "BLUE", "BOLD") +
                    Fore.fstring(f"Current Balance: ₹{remaining_amt}\n", "UNDERLINE", "BOLD") +
                    Fore.fstring(f"{result[0]} x ₹500", "GREEN") +
                    Fore.fstring(f"\t{result[1]} x ₹200", "ORANGE") +
                    Fore.fstring(f"\t{result[2]} x ₹100", "MAGENTA")
                )

    @Logger.log
    def deposit(self, username: str, amount: float) -> str:
        """ deposits money and updates denominations. """

        if amount % 100 != 0:
            return Fore.fstring(
                "Can only deposit amount in denominations of ₹100.", "RED"
            )
        
        if amount < 0:
            return Fore.fstring(
                "You can't deposit in terms of negatives.", "RED"
            )

        denominations_list = input("Enter denominations: <500> <200> <100>: ").split(" ")
        result = self.denominations_updater(amount, "d", denominations_list)

        if result == "success":
            balance = float(self.get_balance(username))
            new_amount = amount + balance
            self.cursor.execute(
                f"UPDATE {self.user_table} "
                f"SET {self.balance} = %s "
                f"WHERE {self.username} = %s", (new_amount, username,)
            )
            self.mycon.commit()

            return (
                Fore.fstring(f"Amount Desposited: ₹{amount}\n", "BLUE", "BOLD") +
                Fore.fstring(f"Current Balance: ₹{new_amount}", "UNDERLINE")
            )

        elif result == "invalid input type":
            return Fore.fstring(
                "Deposit Failed!\nEnter denominations in the format: "
                "<no. of 500 notes> <no. of 200 notes> <no. of 100 notes>",
                "RED"
            )

        elif result == "invalid no. of inputs":
            return Fore.fstring(
                "Deposit Failed\nEnter ALL 3 denominations "
                "(0 is valid, if applicable).", "RED"
            )
        
        else:
            return Fore.fstring(
                "Deposit Failed! The deposit amount and denominations "
                "specified do not match.", "RED"
            )

    @Logger.log
    def change_pin(self, username: str, new_password: str):
        """ change PIN of a user. """

        if new_password.isdigit() and len(new_password) == self.PIN_LENGTH:
            if new_password != self.get_pin(username):
                self.cursor.execute(
                    f"UPDATE {self.user_table} "
                    f"SET {self.user_pin} = %s "
                    f"WHERE {self.username} = %s", (new_password, username)
                )
                self.mycon.commit()
                return Fore.fstring("PIN has been changed.", "GREEN", "BOLD")
            
            else:
                return Fore.fstring(
                    "You can't set the new PIN to your current PIN.",
                    "BOLD", "RED"
                )
            
        else:
            return Fore.fstring(f"Your PIN must be {self.PIN_LENGTH} digits.", "BOLD", "RED")

    def __setup_connection(self, database=None):
        """ setting up the database connection. """

        if database is None:
            self.mycon = sqltor.connect(
                host=self.host, user=self.user, password=self.password
            )
        else:
            self.mycon = sqltor.connect(
                database=database, host=self.host, user=self.user, 
                password=self.password
            )

        self.cursor = self.mycon.cursor()
  
    def __setup_database(self):
        """ creating the database. """

        self.cursor.execute(f"CREATE DATABASE {self.database};")
        print(Fore.fstring(
            "Database creation successful!\nDatabases:", "GREEN")
        )
        self.cursor.execute("SHOW DATABASES;")
        print([x[0] for x in self.cursor.fetchall()])
        print("Not reached")
        self.__setup_connection(self.database)
 
    def __setup_tables(self):
        """ creating the tables. """

        self.cursor.execute(
            f"CREATE TABLE {self.user_table} ({self.username} varchar(30),"
            f" {self.user_pin} varchar(30), {self.balance} int);"
        )
        self.cursor.execute(
            f"CREATE TABLE {self.denomination_table} ({self.fivehundreds} int,"
            f" {self.twohundreds} int, {self.hundreds} int);"
        )
        print(Fore.fstring("Tables creation successful!", "GREEN"))
        self.cursor.execute("SHOW TABLES;")
        print([x[0] for x in self.cursor.fetchall()])

    def __insert_test_data(self):
        """ inserting test data into the tables. """

        self.cursor.execute(
            f'INSERT INTO {self.user_table} ' 
                'VALUES ("abhiram", "1234", 12300);'
        )
        self.cursor.execute(
            f'INSERT INTO {self.user_table} '
                'VALUES ("aditya", "1234", 9000);'
        )
        self.cursor.execute(
            f'INSERT INTO {self.user_table} '
                'VALUES ("darshan", "1234", 10000);'
        )
        self.cursor.execute(
            f'INSERT INTO {self.user_table} '
            ' values ("ojas", "1234", 5000);'
        )
        self.mycon.commit()
        print(Fore.fstring(
            f"Data creation successful! {self.user_table}", "GREEN"))
        self.cursor.execute(f"SELECT * FROM {self.user_table}")
        print([x for x in self.cursor.fetchall()])
        self.cursor.execute(
            f'INSERT INTO {self.denomination_table} ' 
                'values (250, 300, 350);'
        )
        self.mycon.commit()
        print(Fore.fstring(
            f"Data creation successful! {self.denomination_table}", "GREEN"))
        self.cursor.execute(f"SELECT * FROM {self.denomination_table}")
        print([x for x in self.cursor.fetchall()])
