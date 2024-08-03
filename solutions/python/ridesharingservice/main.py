# driver.py
from enum import Enum

class DriverStatus(Enum):
    AVAILABLE = 1
    BUSY = 2

class Driver:
    def __init__(self, id, name, contact, license_plate, location, status):
        self.id = id
        self.name = name
        self.contact = contact
        self.license_plate = license_plate
        self.location = location
        self.status = status

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_contact(self, contact):
        self.contact = contact

    def set_license_plate(self, license_plate):
        self.license_plate = license_plate

    def set_location(self, location):
        self.location = location

    def set_status(self, status):
        self.status = status

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_contact(self):
        return self.contact

    def get_license_plate(self):
        return self.license_plate

    def get_location(self):
        return self.location

    def get_status(self):
        return self.status

# location.py
class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

# passenger.py
class Passenger:
    def __init__(self, id, name, contact, location):
        self.id = id
        self.name = name
        self.contact = contact
        self.location = location

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_contact(self):
        return self.contact

    def get_location(self):
        return self.location

# payment.py
from enum import Enum

class PaymentStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3

class Payment:
    def __init__(self, id, ride, amount, status):
        self.id = id
        self.ride = ride
        self.amount = amount
        self.status = status

# ride.py
from enum import Enum

class RideStatus(Enum):
    REQUESTED = 1
    ACCEPTED = 2
    IN_PROGRESS = 3
    COMPLETED = 4
    CANCELLED = 5

class Ride:
    def __init__(self, id, passenger, driver, source, destination, status, fare):
        self.id = id
        self.passenger = passenger
        self.driver = driver
        self.source = source
        self.destination = destination
        self.status = status
        self.fare = fare

    def set_driver(self, driver):
        self.driver = driver

    def set_status(self, status):
        self.status = status

    def set_fare(self, fare):
        self.fare = fare

    def get_id(self):
        return self.id

    def get_passenger(self):
        return self.passenger

    def get_driver(self):
        return self.driver

    def get_source(self):
        return self.source

    def get_destination(self):
        return self.destination

    def get_status(self):
        return self.status

    def get_fare(self):
        return self.fare

# ride_service.py
from concurrent.futures import ThreadPoolExecutor
from ride import Ride, RideStatus
from driver import DriverStatus
import random
import math
import time

class RideService:
    _instance = None
    _lock = ThreadPoolExecutor(max_workers=1)

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.passengers = {}
        self.drivers = {}
        self.rides = {}
        self.requested_rides = []

    def add_passenger(self, passenger):
        self.passengers[passenger.get_id()] = passenger

    def add_driver(self, driver):
        self.drivers[driver.get_id()] = driver

    def request_ride(self, passenger, source, destination):
        ride_id = self._generate_ride_id()
        ride = Ride(ride_id, passenger, None, source, destination, RideStatus.REQUESTED, 0.0)
        self.requested_rides.append(ride)
        self._notify_drivers(ride)

    def accept_ride(self, driver, ride):
        if ride.get_status() == RideStatus.REQUESTED:
            ride.set_driver(driver)
            ride.set_status(RideStatus.ACCEPTED)
            driver.set_status(DriverStatus.BUSY)
            self._notify_passenger(ride)

    def start_ride(self, ride):
        if ride.get_status() == RideStatus.ACCEPTED:
            ride.set_status(RideStatus.IN_PROGRESS)
            self._notify_passenger(ride)

    def complete_ride(self, ride):
        if ride.get_status() == RideStatus.IN_PROGRESS:
            ride.set_status(RideStatus.COMPLETED)
            ride.get_driver().set_status(DriverStatus.AVAILABLE)
            fare = self._calculate_fare(ride)
            ride.set_fare(fare)
            self._process_payment(ride, fare)
            self._notify_passenger(ride)
            self._notify_driver(ride)

    def cancel_ride(self, ride):
        if ride.get_status() in [RideStatus.REQUESTED, RideStatus.ACCEPTED]:
            ride.set_status(RideStatus.CANCELLED)
            if ride.get_driver():
                ride.get_driver().set_status(DriverStatus.AVAILABLE)
            self._notify_passenger(ride)
            self._notify_driver(ride)

    def _notify_drivers(self, ride):
        for driver in self.drivers.values():
            if driver.get_status() == DriverStatus.AVAILABLE:
                distance = self._calculate_distance(driver.get_location(), ride.get_source())
                if distance <= 5.0:  # Notify drivers within 5 km radius
                    # Send notification to the driver
                    print(f"Notifying driver: {driver.get_name()} about ride request: {ride.get_id()}")

    def _notify_passenger(self, ride):
        passenger = ride.get_passenger()
        message = ""
        if ride.get_status() == RideStatus.ACCEPTED:
            message = f"Your ride has been accepted by driver: {ride.get_driver().get_name()}"
        elif ride.get_status() == RideStatus.IN_PROGRESS:
            message = "Your ride is in progress"
        elif ride.get_status() == RideStatus.COMPLETED:
            message = f"Your ride has been completed. Fare: ${ride.get_fare():.2f}"
        elif ride.get_status() == RideStatus.CANCELLED:
            message = "Your ride has been cancelled"
        # Send notification to the passenger
        print(f"Notifying passenger: {passenger.get_name()} - {message}")

    def _notify_driver(self, ride):
        driver = ride.get_driver()
        if driver:
            message = ""
            if ride.get_status() == RideStatus.COMPLETED:
                message = f"Ride completed. Fare: ${ride.get_fare():.2f}"
            elif ride.get_status() == RideStatus.CANCELLED:
                message = "Ride cancelled by passenger"
            # Send notification to the driver
            print(f"Notifying driver: {driver.get_name()} - {message}")

    def _calculate_fare(self, ride):
        base_fare = 2.0
        per_km_fare = 1.5
        per_minute_fare = 0.25

        distance = self._calculate_distance(ride.get_source(), ride.get_destination())
        duration = self._calculate_duration(ride.get_source(), ride.get_destination())

        fare = base_fare + (distance * per_km_fare) + (duration * per_minute_fare)
        return round(fare, 2)

    def _calculate_distance(self, source, destination):
        # Calculate the distance between two locations using a distance formula (e.g., Haversine formula)
        # For simplicity, let's assume a random distance between 1 and 20 km
        return random.uniform(1, 20)

    def _calculate_duration(self, source, destination):
        # Calculate the estimated duration between two locations based on distance and average speed
        # For simplicity, let's assume an average speed of 30 km/h
        distance = self._calculate_distance(source, destination)
        return (distance / 30) * 60  # Convert hours to minutes

    def _process_payment(self, ride, amount):
        # Process the payment for the ride
        pass

    def _generate_ride_id(self):
        return int(time.time())

    def get_rides(self):
        return self.rides

    def get_requested_rides(self):
        return self.requested_rides

# ride_sharing_service_demo.py
from ride_service import RideService
from passenger import Passenger
from location import Location
from driver import Driver, DriverStatus

class RideSharingServiceDemo:
    def run():
        ride_service = RideService()

        # Create passengers
        passenger1 = Passenger(1, "John Doe", "1234567890", Location(37.7749, -122.4194))
        passenger2 = Passenger(2, "Jane Smith", "9876543210", Location(37.7860, -122.4070))
        ride_service.add_passenger(passenger1)
        ride_service.add_passenger(passenger2)

        # Create drivers
        driver1 = Driver(1, "Alice Johnson", "4567890123", "ABC123", Location(37.7749, -122.4194), DriverStatus.AVAILABLE)
        driver2 = Driver(2, "Bob Williams", "7890123456", "XYZ789", Location(37.7860, -122.4070), DriverStatus.AVAILABLE)
        ride_service.add_driver(driver1)
        ride_service.add_driver(driver2)

        # Passenger 1 requests a ride
        ride_service.request_ride(passenger1, passenger1.get_location(), Location(37.7887, -122.4098))

        # Driver 1 accepts the ride
        ride = ride_service.get_requested_rides().pop(0)
        ride_service.accept_ride(driver1, ride)

        # Start the ride
        ride_service.start_ride(ride)

        # Complete the ride
        ride_service.complete_ride(ride)

        # Passenger 2 requests a ride
        ride_service.request_ride(passenger2, passenger2.get_location(), Location(37.7749, -122.4194))

        # Driver 2 accepts the ride
        ride2 = ride_service.get_requested_rides().pop(0)
        ride_service.accept_ride(driver2, ride2)

        # Passenger 2 cancels the ride
        ride_service.cancel_ride(ride2)

if __name__ == "__main__":
    RideSharingServiceDemo.run()

