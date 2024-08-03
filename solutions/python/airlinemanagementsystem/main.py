# aircraft.py
class Aircraft:
    def __init__(self, tail_number, model, total_seats):
        self.tail_number = tail_number
        self.model = model
        self.total_seats = total_seats

# airline_management_system.py
from flight import Flight
from aircraft import Aircraft
from flight_search import FlightSearch
from booking_manager import BookingManager
from payment_processor import PaymentProcessor

class AirlineManagementSystem:
    def __init__(self):
        self.flights = []
        self.aircrafts = []
        self.flight_search = FlightSearch(self.flights)
        self.booking_manager = BookingManager()
        self.payment_processor = PaymentProcessor()

    def add_flight(self, flight):
        self.flights.append(flight)

    def add_aircraft(self, aircraft):
        self.aircrafts.append(aircraft)

    def search_flights(self, source, destination, date):
        return self.flight_search.search_flights(source, destination, date)

    def book_flight(self, flight, passenger, seat, price):
        return self.booking_manager.create_booking(flight, passenger, seat, price)

    def cancel_booking(self, booking_number):
        self.booking_manager.cancel_booking(booking_number)

    def process_payment(self, payment):
        self.payment_processor.process_payment(payment)

# airline_management_system_demo.py
from datetime import datetime, timedelta
from typing import List
from airline_management_system import AirlineManagementSystem
from passenger import Passenger
from flight import Flight
from aircraft import Aircraft
from seat import Seat, SeatType

class AirlineManagementSystemDemo:
    @staticmethod
    def run():
        airline_management_system = AirlineManagementSystem()

        # Create users
        passenger1 = Passenger("U001", "John Doe", "john@example.com", "1234567890")

        # Create flights
        departure_time1 = datetime.now() + timedelta(days=1)
        arrival_time1 = departure_time1 + timedelta(hours=2)
        flight1 = Flight("F001", "New York", "London", departure_time1, arrival_time1)

        departure_time2 = datetime.now() + timedelta(days=3)
        arrival_time2 = departure_time2 + timedelta(hours=5)
        flight2 = Flight("F002", "Paris", "Tokyo", departure_time2, arrival_time2)

        airline_management_system.add_flight(flight1)
        airline_management_system.add_flight(flight2)

        # Create aircrafts
        aircraft1 = Aircraft("A001", "Boeing 747", 300)
        aircraft2 = Aircraft("A002", "Airbus A380", 500)
        airline_management_system.add_aircraft(aircraft1)
        airline_management_system.add_aircraft(aircraft2)

        # Search flights
        search_date = datetime.now().date() + timedelta(days=1)
        search_results: List[Flight] = airline_management_system.search_flights("New York", "London", search_date)
        print("Search Results:")
        for flight in search_results:
            print(f"Flight: {flight.flight_number} - {flight.source} to {flight.destination}")

        seat = Seat("25A", SeatType.ECONOMY)

        # Book a flight
        booking = airline_management_system.book_flight(flight1, passenger1, seat, 100)
        if booking:
            print(f"Booking successful. Booking ID: {booking.booking_number}")
        else:
            print("Booking failed.")

        # Cancel a booking
        airline_management_system.cancel_booking(booking.booking_number)
        print("Booking cancelled.")

if __name__ == "__main__":
    AirlineManagementSystemDemo.run()

# booking.py
from enum import Enum

class BookingStatus(Enum):
    CONFIRMED = 1
    CANCELLED = 2
    PENDING = 3
    EXPIRED = 4

class Booking:
    def __init__(self, booking_number, flight, passenger, seat, price):
        self.booking_number = booking_number
        self.flight = flight
        self.passenger = passenger
        self.seat = seat
        self.price = price
        self.status = BookingStatus.CONFIRMED

    def cancel(self):
        self.status = BookingStatus.CANCELLED

# booking_manager.py
import datetime
from booking import Booking
from threading import Lock

class BookingManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.bookings = {}
        self.booking_counter = 0

    def create_booking(self, flight, passenger, seat, price):
        booking_number = self._generate_booking_number()
        booking = Booking(booking_number, flight, passenger, seat, price)
        with self._lock:
            self.bookings[booking_number] = booking
        return booking

    def cancel_booking(self, booking_number):
        with self._lock:
            booking = self.bookings.get(booking_number)
            if booking:
                booking.cancel()

    def _generate_booking_number(self):
        self.booking_counter += 1
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return f"BKG{timestamp}{self.booking_counter:06d}"

# flight.py
from datetime import datetime

class Flight:
    def __init__(self, flight_number, source, destination, departure_time, arrival_time):
        self.flight_number = flight_number
        self.source = source
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.available_seats = []

    def get_source(self):
        return self.source

    def get_destination(self):
        return self.destination

    def get_departure_time(self):
        return self.departure_time

# flight_search.py
from datetime import date

class FlightSearch:
    def __init__(self, flights):
        self.flights = flights

    def search_flights(self, source, destination, date):
        return [flight for flight in self.flights
                if flight.get_source().lower() == source.lower()
                and flight.get_destination().lower() == destination.lower()
                and flight.get_departure_time().date() == date]

# passenger.py
class Passenger:
    def __init__(self, passenger_id, name, email, phone):
        self.id = passenger_id
        self.name = name
        self.email = email
        self.phone = phone

# payment.py
from enum import Enum

class PaymentStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    REFUNDED = 4

class Payment:
    def __init__(self, payment_id, payment_method, amount):
        self.payment_id = payment_id
        self.payment_method = payment_method
        self.amount = amount
        self.status = PaymentStatus.PENDING

    def process_payment(self):
        # Process payment logic
        self.status = PaymentStatus.COMPLETED

# payment_processor.py
from threading import Lock

class PaymentProcessor:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def process_payment(self, payment):
        # Process payment using the selected payment method
        payment.process_payment()

# seat.py
from enum import Enum

class SeatStatus(Enum):
    AVAILABLE = 1
    RESERVED = 2
    OCCUPIED = 3

class SeatType(Enum):
    ECONOMY = 1
    PREMIUM_ECONOMY = 2
    BUSINESS = 3
    FIRST_CLASS = 4

class Seat:
    def __init__(self, seat_number, seat_type):
        self.seat_number = seat_number
        self.type = seat_type
        self.status = SeatStatus.AVAILABLE

    def reserve(self):
        self.status = SeatStatus.RESERVED

    def release(self):
        self.status = SeatStatus.AVAILABLE

