import random
import time
import mysql.connector

MyDb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='elite_db'
)

MyCursor = MyDb.cursor()
# MyCursor.execute('CREATE DATABASE elite_db')

# to show databases
# MyCursor.execute('SHOW DATABASES')
# for db in MyCursor:
#     print(db)

# creating table
# MyCursor.execute('CREATE TABLE  users (name VARCHAR(255), dob INT(10), address VARCHAR(255), bvn INT(10), gender VARCHAR(6), account_no INT(10)), balance.')
# for tb in MyCursor:
#     print(tb)

# MyCursor.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS balance FLOAT')
# MyDb.commit()

# MyCursor.execute('ALTER TABLE users MODIFY COLUMN account_no VARCHAR(15)')
# MyDb.commit()


class User:
    def __init__(self, name, dob, address, bvn, gender):
        self.name = name
        self.dob = dob
        self.address = address
        self.bvn = bvn
        self.gender = gender
        self.account_number = self.generate_account_number()
        self.balance = 0

    # saving to database
    def save_to_database(self):
        # Insert the user details into the 'users' table
        sql = "INSERT INTO users (name, dob, address, bvn, gender, account_no, balance) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (self.name, self.dob, self.address, self.bvn, self.gender, self.account_number, self.balance)

        try:
            MyCursor.execute(sql, values)
            MyDb.commit()
            print("User details saved to the database successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def generate_account_number(self):
        return str(random.randint(1000000000, 9999999999))

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.update_balance_in_database()  # Update balance in the database
            return f"Deposited {amount} successfully. New balance: {self.balance}"
        else:
            return "Invalid deposit amount."
        
    # Update the 'balance' column in the 'users' table for the current user
    def update_balance_in_database(self):
        sql = "UPDATE users SET balance = %s WHERE account_no = %s"
        values = (self.balance, self.account_number)

        try:
            MyCursor.execute(sql, values)
            MyDb.commit()  # Commit the transaction
            print("Balance updated in the database successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def withdraw(self, amount):
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            self.update_balance_in_database()  # Update balance in the database
            return f"Withdrew {amount} successfully. New balance: {self.balance}"
        elif amount <= 0:
            return "Invalid withdrawal amount."
        else:
            return "Insufficient funds."

    def check_balance(self):
        return f"Account balance for {self.name}: {self.balance}"

    def transfer(self, recipient, amount):
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            recipient.balance += amount
            self.update_balance_in_database()  # Update sender's balance in the database
            recipient.update_balance_in_database()  # Update recipient's balance in the database
            return f"Transferred {amount} to {recipient.name}. Your new balance: {self.balance}"
        elif amount <= 0:
            return "Invalid transfer amount."
        else:
            return "Insufficient funds."


class Bank:
    def __init__(self):
        self.users = {}
        self.load_users_from_database()
        
    def load_users_from_database(self):
        # Retrieve user data from the 'users' table in the database
        MyCursor.execute('SELECT * FROM users')
        rows = MyCursor.fetchall()
        
        for row in rows:
            name, dob, address, bvn, gender, account_number, balance = row
            user = User(name, dob, address, bvn, gender)
            user.account_number = account_number
            user.balance = balance
            self.users[account_number] = user
            
    def commit_changes(self):
        # Update user data in the 'users' table in the database
        for account_number, user in self.users.items():
            sql = "UPDATE users SET name=%s, dob=%s, address=%s, bvn=%s, gender=%s, balance=%s WHERE account_no=%s"
            values = (user.name, user.dob, user.address, user.bvn, user.gender, user.balance, account_number)

            try:
                MyCursor.execute(sql, values)
            except mysql.connector.Error as err:
                print(f"Error updating user {account_number}: {err}")

    def save_user_to_database(self, user):
        # Insert a new user into the 'users' table in the database
        sql = "INSERT INTO users (name, dob, address, bvn, gender, account_no, balance) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (user.name, user.dob, user.address, user.bvn, user.gender, user.account_number, user.balance)

        try:
            MyCursor.execute(sql, values)
            self.users[user.account_number] = user
        except mysql.connector.Error as err:
            print(f"Error inserting user {user.account_number} into the database: {err}")
        
        
    
    def login(self, account_number):
        return self.users.get(account_number, None)

    def create_account(self, name, dob, address, bvn, gender):
        user = User(name, dob, address, bvn, gender)
        self.users[user.account_number] = user
        user.save_to_database()  # Save user to the database
        MyDb.commit()  # Commit the transaction
        return user


def main():
    bank = Bank()

    print('''\nWelcome to Richard Banking System!
    Bank for Rich Kids people...\n
    ''')

    while True:
        ans = input("""Welcome Back:
    (1) Log in
    (2) Sign up?
    
    Enter 1 or 2: """)

        if ans == '1':
            # Log in
            account_number = input("Enter your account number: ")
            user = bank.login(account_number)

            if user:
                print(f"Welcome back, {user.name}!".center(70,'_'))
                time.sleep(1)
                
                while True:
                    print('''
                        1. Deposit
                        2. Withdraw
                        3. Check Balance
                        4. Transfer
                        5. Logout
                        ''')
                    choice = input("Enter your choice (1-5): ")

                    if choice == '1':
                        amount = float(input("Enter the deposit amount: "))
                        time.sleep(2)
                        print(user.deposit(amount))

                    elif choice == '2':
                        amount = float(input("Enter the withdrawal amount: "))
                        time.sleep(2)
                        print(user.withdraw(amount))

                    elif choice == '3':
                        print('Working on it...')
                        time.sleep(2)
                        print(user.check_balance())

                    elif choice == '4':
                        recipient_account_number = input("Enter the recipient's account number: ")
                        recipient = bank.login(recipient_account_number)
                        if recipient:
                            amount = float(input("Enter the transfer amount: "))
                            time.sleep(2)
                            print(user.transfer(recipient, amount))
                        else:
                            time.sleep(2)
                            print("Recipient not found. Please check the account number.")

                    elif choice == '5':
                        print("Logged out.")
                        break

                    else:
                        print("Invalid choice. Please enter a number between 1 and 5.")

            else:
                print("\nInvalid account number. Please try again.\n")

        elif ans == '2':
            name = input("Enter your name: ").strip().title()
            dob = input("Enter your date of birth (YYYY-MM-DD): ").strip()
            address = input("Enter your address: ").strip()
            bvn = input("Enter your Bank Verification Number: ").strip()
            gender = input("Enter your Gender: ").strip()

            print('Confirming your details...')
            time.sleep(2)
            print("Confirmed!!")
            time.sleep(2)

            # Create an account
            user = bank.create_account(name, dob, address, bvn, gender)
            print(f"Account created successfully for {user.name} with account number {user.account_number}")

            while True:
                time.sleep(2)
                print('''
                    1. Deposit
                    2. Withdraw
                    3. Check Balance
                    4. Transfer
                    5. Logout
                    ''')
                choice = input("Enter your choice (1-5): ")

                if choice == '1':
                    amount = float(input("Enter the deposit amount: "))
                    time.sleep(2)
                    print(user.deposit(amount))

                elif choice == '2':
                    time.sleep(2)
                    print("Cannot withdraw from a new account. Deposit some money first.")

                elif choice == '3':
                    time.sleep(2)
                    print(user.check_balance())

                elif choice == '4':
                    time.sleep(2)
                    print("Cannot transfer from a new account. Deposit some money first.")

                elif choice == '5':
                    print("Logged out.")
                    break

                else:
                    print("\nInvalid choice. Please enter a number between 1 and 5.\n")

        else:
            print("\nInvalid choice. Please enter 1 or 2.\n")


if __name__ == "__main__":
    main()


Bank.commit_changes()
MyDb.commit()
MyCursor.close()
MyDb.close()