from locust import HttpUser, task, between
import json
import random


class WebsiteUser(HttpUser):
    wait_time = between(1, 2)  # Simulates a wait time between 1 to 5 seconds between tasks

    @task
    def update_balance(self):
        user_id = random.randint(1, 5)
        # Randomly select a city for the update_balance task
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        city = random.choice(cities)

        self.client.post("/update_balance", json={"userId": user_id, "city": city})
