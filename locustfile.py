import os
from locust import HttpUser, task, between
from dotenv import load_dotenv

load_dotenv()


class SalixNigra(HttpUser):
    wait_time = between(1, 5)

    @task
    def home(self):
        self.client.get("")
        self.client.get("trading/")

    @task(2)
    def dashboard(self):
        self.client.get("dashboard/")
        self.client.get("dashboard/detailed-summary")
        self.client.get("dashboard/deposit")
        self.client.get("dashboard/withdraw")

    def on_start(self):
        self.client.post("user/login/",
                         json={"email": os.environ.get("environ"), "password": os.environ.get("password")})

    def on_stop(self):
        self.client.get("user/logout")
