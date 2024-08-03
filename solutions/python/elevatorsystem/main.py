# direction.py
from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2

# elevator.py
import time
from threading import Lock, Condition
from request import Request
from direction import Direction

class Elevator:
    def __init__(self, id: int, capacity: int):
        self.id = id
        self.capacity = capacity
        self.current_floor = 1
        self.current_direction = Direction.UP
        self.requests = []
        self.lock = Lock()
        self.condition = Condition(self.lock)

    def add_request(self, request: Request):
        with self.lock:
            if len(self.requests) < self.capacity:
                self.requests.append(request)
                print(f"Elevator {self.id} added request: {request.source_floor} to {request.destination_floor}")
                self.condition.notify_all()

    def get_next_request(self) -> Request:
        with self.lock:
            while not self.requests:
                self.condition.wait()
            return self.requests.pop(0)

    def process_requests(self):
        while True:
            with self.lock:
                while self.requests:
                    request = self.get_next_request()
                    self.process_request(request)
                self.condition.wait()

    def process_request(self, request: Request):
        start_floor = self.current_floor
        end_floor = request.destination_floor

        if start_floor < end_floor:
            self.current_direction = Direction.UP
            for i in range(start_floor, end_floor + 1):
                self.current_floor = i
                print(f"Elevator {self.id} reached floor {self.current_floor}")
                time.sleep(1)  # Simulating elevator movement
        elif start_floor > end_floor:
            self.current_direction = Direction.DOWN
            for i in range(start_floor, end_floor - 1, -1):
                self.current_floor = i
                print(f"Elevator {self.id} reached floor {self.current_floor}")
                time.sleep(1)  # Simulating elevator movement

    def run(self):
        self.process_requests()

# elevator_controller.py
from threading import Thread
from elevator import Elevator
from request import Request

class ElevatorController:
    def __init__(self, num_elevators: int, capacity: int):
        self.elevators = []
        for i in range(num_elevators):
            elevator = Elevator(i + 1, capacity)
            self.elevators.append(elevator)
            Thread(target=elevator.run).start()

    def request_elevator(self, source_floor: int, destination_floor: int):
        optimal_elevator = self.find_optimal_elevator(source_floor, destination_floor)
        optimal_elevator.add_request(Request(source_floor, destination_floor))

    def find_optimal_elevator(self, source_floor: int, destination_floor: int) -> Elevator:
        optimal_elevator = None
        min_distance = float('inf')

        for elevator in self.elevators:
            distance = abs(source_floor - elevator.current_floor)
            if distance < min_distance:
                min_distance = distance
                optimal_elevator = elevator

        return optimal_elevator

# elevator_system_demo.py
import time
from elevator_controller import ElevatorController

class ElevatorSystemDemo:
    @staticmethod
    def run():
        controller = ElevatorController(3, 5)
        controller.request_elevator(5, 10)
        controller.request_elevator(3, 7)
        controller.request_elevator(8, 2)
        controller.request_elevator(1, 9)

        # Keep the main thread running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Elevator system stopped.")        

if __name__ == "__main__":
    ElevatorSystemDemo.run()

# request.py
class Request:
    def __init__(self, source_floor, destination_floor):
        self.source_floor = source_floor
        self.destination_floor = destination_floor

