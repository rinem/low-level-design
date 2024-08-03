# connection.py
from datetime import datetime

class Connection:
    def __init__(self, user, connection_date: datetime):
        self._user = user
        self._connection_date = connection_date

    @property
    def user(self):
        return self._user

    @property
    def connection_date(self) -> datetime:
        return self._connection_date


# education.py
class Education:
    def __init__(self, school: str, degree: str, field_of_study: str, start_date: str, end_date: str):
        self.school = school
        self.degree = degree
        self.field_of_study = field_of_study
        self.start_date = start_date
        self.end_date = end_date


# experience.py
class Experience:
    def __init__(self, title: str, company: str, start_date: str, end_date: str, description: str):
        self.title = title
        self.company = company
        self.start_date = start_date
        self.end_date = end_date
        self.description = description


# job_posting.py
from datetime import datetime
from typing import List

class JobPosting:
    def __init__(self, job_id: str, title: str, description: str, requirements: List[str], location: str, post_date: datetime):
        self._id = job_id
        self._title = title
        self._description = description
        self._requirements = requirements
        self._location = location
        self._post_date = post_date

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def requirements(self) -> List[str]:
        return self._requirements

    @property
    def location(self) -> str:
        return self._location

    @property
    def post_date(self) -> datetime:
        return self._post_date


# linkedin_demo.py
from datetime import datetime
from linkedin_service import LinkedInService
from user import User
from profile import Profile
from job_posting import JobPosting

class LinkedInDemo:
    @staticmethod
    def run():
        linkedin_service = LinkedInService()

        # User registration
        user1 = User("1", "John Doe", "john@example.com", "password", Profile(), [], [], [])
        user2 = User("2", "Jane Smith", "jane@example.com", "password", Profile(), [], [], [])
        linkedin_service.register_user(user1)
        linkedin_service.register_user(user2)

        # User login
        logged_in_user = linkedin_service.login_user("john@example.com", "password")
        if logged_in_user:
            print(f"User logged in: {logged_in_user.name}")
        else:
            print("Invalid email or password.")

        # Update user profile
        profile = Profile()
        profile.set_headline("Software Engineer")
        profile.set_summary("Passionate about coding and problem-solving.")
        logged_in_user.set_profile(profile)
        linkedin_service.update_user_profile(logged_in_user)

        # Send connection request
        linkedin_service.send_connection_request(user1, user2)

        # Accept connection request
        linkedin_service.accept_connection_request(user2, user1)

        # Post a job listing
        job_posting = JobPosting("1", "Software Developer", "We are hiring!", ["Java", "Python"], "San Francisco", datetime.now())
        linkedin_service.post_job_listing(job_posting)

        # Search for users
        search_results = linkedin_service.search_users("John")
        print("Search Results:")
        for user in search_results:
            print(f"Name: {user.name}")
            print(f"Headline: {user.profile.headline}")
            print()

        # Search for job postings
        job_posting_results = linkedin_service.search_job_postings("Software")
        print("Job Posting Results:")
        for posting in job_posting_results:
            print(f"Title: {posting.title}")
            print(f"Description: {posting.description}")
            print()

        # Send a message
        linkedin_service.send_message(user1, user2, "Hi Jane, hope you're doing well!")

        # Get notifications
        notifications = linkedin_service.get_notifications(user2.id)
        print("Notifications:")
        for notification in notifications:
            print(f"Type: {notification.type}")
            print(f"Content: {notification.content}")
            print()

if __name__ == "__main__":
    LinkedInDemo.run()


# linkedin_service.py
from datetime import datetime
from typing import List, Dict, Optional
from threading import Lock
import uuid
from user import User
from job_posting import JobPosting
from connection import Connection
from notification import Notification, NotificationType
from message import Message

class LinkedInService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.users: Dict[str, User] = {}
                cls._instance.job_postings: Dict[str, JobPosting] = {}
                cls._instance.notifications: Dict[str, List[Notification]] = {}
        return cls._instance

    def register_user(self, user: User):
        self.users[user.id] = user

    def login_user(self, email: str, password: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email and user.password == password:
                return user
        return None

    def update_user_profile(self, user: User):
        self.users[user.id] = user

    def send_connection_request(self, sender: User, receiver: User):
        connection = Connection(sender, datetime.now())
        receiver.connections.append(connection)
        notification = Notification(self._generate_notification_id(), receiver,
                                    NotificationType.CONNECTION_REQUEST,
                                    f"New connection request from {sender.name}",
                                    datetime.now())
        self._add_notification(receiver.id, notification)

    def accept_connection_request(self, user: User, connection_user: User):
        for connection in user.connections:
            if connection.user == connection_user:
                user.connections.append(Connection(connection_user, datetime.now()))
                break

    def search_users(self, keyword: str) -> List[User]:
        return [user for user in self.users.values() if keyword.lower() in user.name.lower()]

    def post_job_listing(self, job_posting: JobPosting):
        self.job_postings[job_posting.id] = job_posting
        for user in self.users.values():
            notification = Notification(self._generate_notification_id(), user,
                                        NotificationType.JOB_POSTING,
                                        f"New job posting: {job_posting.title}",
                                        datetime.now())
            self._add_notification(user.id, notification)

    def search_job_postings(self, keyword: str) -> List[JobPosting]:
        return [job for job in self.job_postings.values()
                if keyword.lower() in job.title.lower() or keyword.lower() in job.description.lower()]

    def send_message(self, sender: User, receiver: User, content: str):
        message = Message(self._generate_message_id(), sender, receiver, content, datetime.now())
        receiver.inbox.append(message)
        sender.sent_messages.append(message)
        notification = Notification(self._generate_notification_id(), receiver,
                                    NotificationType.MESSAGE,
                                    f"New message from {sender.name}",
                                    datetime.now())
        self._add_notification(receiver.id, notification)

    def _add_notification(self, user_id: str, notification: Notification):
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        self.notifications[user_id].append(notification)

    def get_notifications(self, user_id: str) -> List[Notification]:
        return self.notifications.get(user_id, [])

    def _generate_notification_id(self) -> str:
        return str(uuid.uuid4())

    def _generate_message_id(self) -> str:
        return str(uuid.uuid4())

# message.py
from datetime import datetime

class Message:
    def __init__(self, message_id: str, sender, receiver, content: str, timestamp: datetime):
        self._id = message_id
        self._sender = sender
        self._receiver = receiver
        self._content = content
        self._timestamp = timestamp

    @property
    def id(self) -> str:
        return self._id

    @property
    def sender(self):
        return self._sender

    @property
    def receiver(self):
        return self._receiver

    @property
    def content(self) -> str:
        return self._content

    @property
    def timestamp(self) -> datetime:
        return self._timestamp


# notification.py
from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    CONNECTION_REQUEST = "CONNECTION_REQUEST"
    MESSAGE = "MESSAGE"
    JOB_POSTING = "JOB_POSTING"

class Notification:
    def __init__(self, notification_id: str, user, type: NotificationType, content: str, timestamp: datetime):
        self._id = notification_id
        self._user = user
        self._type = type
        self._content = content
        self._timestamp = timestamp

    @property
    def id(self) -> str:
        return self._id

    @property
    def user(self):
        return self._user

    @property
    def type(self) -> NotificationType:
        return self._type

    @property
    def content(self) -> str:
        return self._content

    @property
    def timestamp(self) -> datetime:
        return self._timestamp


# notification_type.py
from enum import Enum

class NotificationType(Enum):
    CONNECTION_REQUEST = "CONNECTION_REQUEST"
    MESSAGE = "MESSAGE"
    JOB_POSTING = "JOB_POSTING"

# profile.py
from typing import List
from experience import Experience
from education import Education
from skill import Skill

class Profile:
    def __init__(self):
        self.profile_picture: str = ""
        self.headline: str = ""
        self.summary: str = ""
        self.experiences: List[Experience] = []
        self.educations: List[Education] = []
        self.skills: List[Skill] = []

    def set_summary(self, summary: str):
        self.summary = summary

    def set_headline(self, headline: str):
        self.headline = headline

    def add_experience(self, experience: Experience):
        self.experiences.append(experience)

    def add_education(self, education: Education):
        self.educations.append(education)

    def add_skill(self, skill: Skill):
        self.skills.append(skill)

# skill.py
class Skill:
    def __init__(self, name: str):
        self.name = name


# user.py
from typing import List
from profile import Profile
from connection import Connection
from message import Message

class User:
    def __init__(self, id: str, name: str, email: str, password: str, profile: Profile, connections: List[Connection], inbox: List[Message], sent_messages: List[Message]):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.profile = profile
        self.connections = connections
        self.inbox = inbox
        self.sent_messages = sent_messages

    def set_profile(self, profile: Profile):
        self.profile = profile

