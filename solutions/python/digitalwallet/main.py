# account.py
from decimal import Decimal
from exception import InsufficientFundsException

class Account:
    def __init__(self, id, user, account_number, currency):
        self.id = id
        self.user = user
        self.account_number = account_number
        self.currency = currency
        self.balance = Decimal('0.00')
        self.transactions = []

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
        else:
            raise InsufficientFundsException("Insufficient funds in the account.")

    def add_transaction(self, transaction):
        self.transactions.append(transaction)


# bank_account.py
from payment_method import PaymentMethod

class BankAccount(PaymentMethod):
    def __init__(self, id, user, account_number, routing_number):
        super().__init__(id, user)
        self.account_number = account_number
        self.routing_number = routing_number

    def process_payment(self, amount, currency):
        # Process bank account payment
        return True

# credit_card.py
from payment_method import PaymentMethod

class CreditCard(PaymentMethod):
    def __init__(self, id, user, card_number, expiration_date, cvv):
        super().__init__(id, user)
        self.card_number = card_number
        self.expiration_date = expiration_date
        self.cvv = cvv

    def process_payment(self, amount, currency):
        # Process credit card payment
        return True


# currency.py
from enum import Enum

class Currency(Enum):
    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    JPY = 'JPY'


# currency_converter.py
from decimal import Decimal
from currency import Currency

class CurrencyConverter:
    exchange_rates = {
        Currency.USD: Decimal('1.00'),
        Currency.EUR: Decimal('0.85'),
        Currency.GBP: Decimal('0.72'),
        Currency.JPY: Decimal('110.00')
    }

    @staticmethod
    def convert(amount, source_currency, target_currency):
        source_rate = CurrencyConverter.exchange_rates[source_currency]
        target_rate = CurrencyConverter.exchange_rates[target_currency]
        return amount * source_rate / target_rate


# digital_wallet.py
import uuid
from user import User
from account import Account
from payment_method import PaymentMethod
from currency import Currency
from currency_converter import CurrencyConverter
from transaction import Transaction

class DigitalWallet:
    _instance = None

    def __init__(self):
        self.users = {}
        self.accounts = {}
        self.payment_methods = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_user(self, user):
        self.users[user.id] = user

    def get_user(self, user_id):
        return self.users.get(user_id)

    def create_account(self, account):
        self.accounts[account.id] = account
        account.user.add_account(account)

    def get_account(self, account_id):
        return self.accounts.get(account_id)

    def add_payment_method(self, payment_method):
        self.payment_methods[payment_method.id] = payment_method

    def get_payment_method(self, payment_method_id):
        return self.payment_methods.get(payment_method_id)

    def transfer_funds(self, source_account, destination_account, amount, currency):
        if source_account.currency != currency:
            amount = CurrencyConverter.convert(amount, currency, source_account.currency)
        source_account.withdraw(amount)

        if destination_account.currency != currency:
            amount = CurrencyConverter.convert(amount, currency, destination_account.currency)
        destination_account.deposit(amount)

        transaction_id = self._generate_transaction_id()
        transaction = Transaction(transaction_id, source_account, destination_account, amount, currency)
        source_account.add_transaction(transaction)
        destination_account.add_transaction(transaction)

    def get_transaction_history(self, account):
        return account.transactions

    def _generate_transaction_id(self):
        return "TXN" + str(uuid.uuid4()).replace('-', '').upper()[:8]


# digital_wallet_demo.py
from decimal import Decimal
from user import User
from account import Account
from currency import Currency
from digital_wallet import DigitalWallet
from credit_card import CreditCard
from bank_account import BankAccount

class DigitalWalletDemo:
    @staticmethod
    def run():
        digital_wallet = DigitalWallet.get_instance()

        # Create users
        user1 = User("U001", "John Doe", "john@example.com", "password123")
        user2 = User("U002", "Jane Smith", "jane@example.com", "password456")
        digital_wallet.create_user(user1)
        digital_wallet.create_user(user2)

        # Create accounts
        account1 = Account("A001", user1, "1234567890", Currency.USD)
        account2 = Account("A002", user2, "9876543210", Currency.EUR)
        digital_wallet.create_account(account1)
        digital_wallet.create_account(account2)

        # Add payment methods
        credit_card = CreditCard("PM001", user1, "1234567890123456", "12/25", "123")
        bank_account = BankAccount("PM002", user2, "9876543210", "987654321")
        digital_wallet.add_payment_method(credit_card)
        digital_wallet.add_payment_method(bank_account)

        # Deposit funds
        account1.deposit(Decimal("1000.00"))
        account2.deposit(Decimal("500.00"))

        # Transfer funds
        digital_wallet.transfer_funds(account1, account2, Decimal("100.00"), Currency.USD)

        # Get transaction history
        transaction_history1 = digital_wallet.get_transaction_history(account1)
        transaction_history2 = digital_wallet.get_transaction_history(account2)

        # Print transaction history
        print("Transaction History for Account 1:")
        for transaction in transaction_history1:
            print(f"Transaction ID: {transaction.id}")
            print(f"Amount: {transaction.amount} {transaction.currency}")
            print(f"Timestamp: {transaction.timestamp}")
            print()

        print("Transaction History for Account 2:")
        for transaction in transaction_history2:
            print(f"Transaction ID: {transaction.id}")
            print(f"Amount: {transaction.amount} {transaction.currency}")
            print(f"Timestamp: {transaction.timestamp}")
            print()

if __name__ == "__main__":
    DigitalWalletDemo.run()

# exception.py
class InsufficientFundsException(Exception):
    pass

# payment_method.py
class PaymentMethod:
    def __init__(self, id, user):
        self.id = id
        self.user = user

    def process_payment(self, amount, currency):
        raise NotImplementedError

# transaction.py
from datetime import datetime

class Transaction:
    def __init__(self, id, source_account, destination_account, amount, currency):
        self.id = id
        self.source_account = source_account
        self.destination_account = destination_account
        self.amount = amount
        self.currency = currency
        self.timestamp = datetime.now()


# user.py
class User:
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def remove_account(self, account):
        self.accounts.remove(account)

