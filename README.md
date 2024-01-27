# ATM Simulator

## Overview
This is a simple school project, an ATM simulator implemented in Python, providing basic functionalities such as withdrawal, deposit, balance inquiry, and PIN change, etc.

## Features
- User authentication with PIN
- Withdrawal and deposit functionalities
- Balance inquiry
- PIN change option
- Logging user actions
- Keeps track of number of banknotes of each denomination, which is updated when you deposit or withdraw.

## Getting Started

### Prerequisites
- Python (version 3.11+, might be compatible with lower versions)
- MySQL database
- `mysql-connector-python`

### Installation
- Install Python from [python.org](https://www.python.org/).
- Install MySQL database.
- Install the required library using `pip install mysql-connector-python`.

### Running the Program
- Keep `main.py` and `atmsim.py` in the same directory, and run `main.py` using the command `python main.py` in your terminal.
- For a test run, use any of the 4 default added usernames, e.g. `aditya` (others are in `__insert_test_data` method in `atmsim.py`, edit the SQL query here to change the users added upon initial run of the program, if database does not already exist). PIN for all users by default is `1234`.

### Available Methods
- `withdraw`: Withdraw money from the user's account.
- `deposit`: Deposit money into the user's account.
- `balance`: Check the user's account balance.
- `change_pin`: Change the user's PIN.


## Contribution/Suggestions
Beginner programmer here, any suggestions (I am sure there are plenty) are welcome! Looking to improve, even in the smallest of ways.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License

Copyright (c) 2024 Aditya P Menon

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

