# task.py
from enum import Enum
from datetime import datetime

class TaskStatus(Enum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3

class Task:
    def __init__(self, task_id, title, description, due_date, priority, assigned_user):
        self.id = task_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.assigned_user = assigned_user

    # Getters and setters
    def get_id(self):
        return self.id

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_priority(self):
        return self.priority

    def get_due_date(self):
        return self.due_date

    def get_status(self):
        return self.status

    def get_assigned_user(self):
        return self.assigned_user

    def set_title(self, title):
        self.title = title

    def set_description(self, description):
        self.description = description

    def set_due_date(self, due_date):
        self.due_date = due_date

    def set_priority(self, priority):
        self.priority = priority

    def set_status(self, status):
        self.status = status

# task_management_system_demo.py

from task_manager import TaskManager
from task import Task, TaskStatus
from user import User
from datetime import datetime

class TaskManagementSystemDemo:
    @staticmethod
    def run():
        task_manager = TaskManager.get_instance()

        # Create users
        user1 = User("1", "John Doe", "john@example.com")
        user2 = User("2", "Jane Smith", "jane@example.com")

        # Create tasks
        task1 = Task("1", "Task 1", "Description 1", datetime.now(), 1, user1)
        task2 = Task("2", "Task 2", "Description 2", datetime.now(), 2, user2)
        task3 = Task("3", "Task 3", "Description 3", datetime.now(), 1, user1)

        # Add tasks to the task manager
        task_manager.create_task(task1)
        task_manager.create_task(task2)
        task_manager.create_task(task3)

        # Update a task
        task2.set_description("Updated description")
        task_manager.update_task(task2)

        # Search tasks
        search_results = task_manager.search_tasks("Task")
        print("Search Results:")
        for task in search_results:
            print(task.get_title())

        # Filter tasks
        filtered_tasks = task_manager.filter_tasks(TaskStatus.PENDING, datetime(1970, 1, 1), datetime.now(), 1)
        print("Filtered Tasks:")
        for task in filtered_tasks:
            print(task.get_title())

        # Mark a task as completed
        task_manager.mark_task_as_completed("1")

        # Get task history for a user
        task_history = task_manager.get_task_history(user1)
        print("Task History for " + user1.get_name() + ":")
        for task in task_history:
            print(task.get_title())

        # Delete a task
        task_manager.delete_task("3")


if __name__ == "__main__":
    TaskManagementSystemDemo.run()

# task_manager.py
from datetime import datetime
from task import Task, TaskStatus
from user import User

class TaskManager:
    _instance = None

    def __init__(self):
        if TaskManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TaskManager._instance = self
            self.tasks = {}
            self.user_tasks = {}

    @staticmethod
    def get_instance():
        if TaskManager._instance is None:
            TaskManager()
        return TaskManager._instance

    def create_task(self, task):
        self.tasks[task.get_id()] = task
        self._assign_task_to_user(task.get_assigned_user(), task)

    def update_task(self, updated_task):
        existing_task = self.tasks.get(updated_task.get_id())
        if existing_task:
            existing_task.set_title(updated_task.get_title())
            existing_task.set_description(updated_task.get_description())
            existing_task.set_due_date(updated_task.get_due_date())
            existing_task.set_priority(updated_task.get_priority())
            existing_task.set_status(updated_task.get_status())
            previous_user = existing_task.get_assigned_user()
            new_user = updated_task.get_assigned_user()
            if previous_user != new_user:
                self._unassign_task_from_user(previous_user, existing_task)
                self._assign_task_to_user(new_user, existing_task)

    def delete_task(self, task_id):
        task = self.tasks.pop(task_id, None)
        if task:
            self._unassign_task_from_user(task.get_assigned_user(), task)

    def search_tasks(self, keyword):
        matching_tasks = []
        for task in self.tasks.values():
            if keyword in task.get_title() or keyword in task.get_description():
                matching_tasks.append(task)
        return matching_tasks

    def filter_tasks(self, status, start_date, end_date, priority):
        filtered_tasks = []
        for task in self.tasks.values():
            if (
                task.get_status() == status
                and start_date <= task.get_due_date() <= end_date
                and task.get_priority() == priority
            ):
                filtered_tasks.append(task)
        return filtered_tasks

    def mark_task_as_completed(self, task_id):
        task = self.tasks.get(task_id)
        if task:
            task.set_status(TaskStatus.COMPLETED)

    def get_task_history(self, user):
        return self.user_tasks.get(user.get_id(), [])

    def _assign_task_to_user(self, user, task):
        self.user_tasks.setdefault(user.get_id(), []).append(task)

    def _unassign_task_from_user(self, user, task):
        tasks = self.user_tasks.get(user.get_id())
        if tasks:
            tasks.remove(task)

# user.py
class User:
    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email

    # Getters and setters
    def get_id(self):
        return self.id

    def get_email(self):
        return self.email

    def get_name(self):
        return self.name

