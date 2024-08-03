# account.py
from portfolio import Portfolio
from exceptions import InsufficientFundsException

class Account:
    def __init__(self, account_id, user, initial_balance):
        self.account_id = account_id
        self.user = user
        self.balance = initial_balance
        self.portfolio = Portfolio(self)

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
        else:
            raise InsufficientFundsException("Insufficient funds in the account.")

    def get_account_id(self):
        return self.account_id

    def get_user(self):
        return self.user

    def get_balance(self):
        return self.balance

    def get_portfolio(self):
        return self.portfolio

# buy_order.py
from order import Order, OrderStatus
from exceptions import InsufficientFundsException

class BuyOrder(Order):
    def __init__(self, order_id, account, stock, quantity, price):
        super().__init__(order_id, account, stock, quantity, price)

    def execute(self):
        total_cost = self.quantity * self.price
        if self.account.get_balance() >= total_cost:
            self.account.withdraw(total_cost)
            # Update portfolio and perform necessary actions
            self.status = OrderStatus.EXECUTED
        else:
            self.status = OrderStatus.REJECTED
            raise InsufficientFundsException("Insufficient funds to execute the buy order.")

# exceptions.py
class InsufficientFundsException(Exception):
    pass

class InsufficientStockException(Exception):
    pass

# order.py
from enum import Enum

class OrderStatus(Enum):
    PENDING = 0
    EXECUTED = 1
    REJECTED = 2

class Order:
    def __init__(self, order_id, account, stock, quantity, price):
        self.order_id = order_id
        self.account = account
        self.stock = stock
        self.quantity = quantity
        self.price = price
        self.status = OrderStatus.PENDING

    def execute(self):
        pass

# portfolio.py
from exceptions import InsufficientStockException

class Portfolio:
    def __init__(self, account):
        self.account = account
        self.holdings = {}

    def add_stock(self, stock, quantity):
        symbol = stock.get_symbol()
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity

    def remove_stock(self, stock, quantity):
        symbol = stock.get_symbol()
        if symbol in self.holdings:
            current_quantity = self.holdings[symbol]
            if current_quantity > quantity:
                self.holdings[symbol] = current_quantity - quantity
            elif current_quantity == quantity:
                del self.holdings[symbol]
            else:
                raise InsufficientStockException("Insufficient stock quantity in the portfolio.")
        else:
            raise InsufficientStockException("Stock not found in the portfolio.")

    def get_holdings(self):
        return self.holdings

# sell_order.py
from order import Order, OrderStatus

class SellOrder(Order):
    def __init__(self, order_id, account, stock, quantity, price):
        super().__init__(order_id, account, stock, quantity, price)

    def execute(self):
        # Check if the user has sufficient quantity of the stock to sell
        # Update portfolio and perform necessary actions
        total_proceeds = self.quantity * self.price
        self.account.deposit(total_proceeds)
        self.status = OrderStatus.EXECUTED

# stock.py
class Stock:
    def __init__(self, symbol, name, price):
        self.symbol = symbol
        self.name = name
        self.price = price

    def update_price(self, new_price):
        self.price = new_price

    def get_symbol(self):
        return self.symbol

    def get_name(self):
        return self.name

    def get_price(self):
        return self.price

# stock_broker.py
from queue import Queue
from threading import Lock
from account import Account
from exceptions import InsufficientFundsException, InsufficientStockException

class StockBroker:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.accounts = {}
                    cls._instance.stocks = {}
                    cls._instance.order_queue = Queue()
                    cls._instance.account_id_counter = 1
        return cls._instance

    def create_account(self, user, initial_balance):
        account_id = self._generate_account_id()
        account = Account(account_id, user, initial_balance)
        self.accounts[account_id] = account

    def get_account(self, account_id):
        return self.accounts.get(account_id)

    def add_stock(self, stock):
        self.stocks[stock.get_symbol()] = stock

    def get_stock(self, symbol):
        return self.stocks.get(symbol)

    def place_order(self, order):
        self.order_queue.put(order)
        self._process_orders()

    def _process_orders(self):
        while not self.order_queue.empty():
            order = self.order_queue.get()
            try:
                order.execute()
            except (InsufficientFundsException, InsufficientStockException) as e:
                # Handle exception and notify user
                print(f"Order failed: {str(e)}")

    def _generate_account_id(self):
        account_id = self.account_id_counter
        self.account_id_counter += 1
        return f"A{account_id:09d}"

# stock_brokerage_system_demo.py
from stock_broker import StockBroker
from user import User
from stock import Stock
from buy_order import BuyOrder
from sell_order import SellOrder

class StockBrokerageSystemDemo:
    def run():
        stock_broker = StockBroker()

        # Create user and account
        user = User("U001", "John Doe", "john@example.com")
        stock_broker.create_account(user, 10000.0)
        account = stock_broker.get_account("A000000001")

        # Add stocks to the stock broker
        stock1 = Stock("AAPL", "Apple Inc.", 150.0)
        stock2 = Stock("GOOGL", "Alphabet Inc.", 2000.0)
        stock_broker.add_stock(stock1)
        stock_broker.add_stock(stock2)

        # Place buy orders
        buy_order1 = BuyOrder("O001", account, stock1, 10, 150.0)
        buy_order2 = BuyOrder("O002", account, stock2, 5, 2000.0)
        stock_broker.place_order(buy_order1)
        stock_broker.place_order(buy_order2)

        # Place sell orders
        sell_order1 = SellOrder("O003", account, stock1, 5, 160.0)
        stock_broker.place_order(sell_order1)

        # Print account balance and portfolio
        print(f"Account Balance: ${account.get_balance()}")
        print(f"Portfolio: {account.get_portfolio().get_holdings()}")

if __name__ == "__main__":
    StockBrokerageSystemDemo.run()

# user.py
class User:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email

