from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing


class EsportsBehavior(TaskSet):
    @task
    def index(self):
        response = self.client.get("/esports")
        if response.status_code != 200:
            print(f"Esports index failed: {response.status_code}")


class EsportsUser(HttpUser):
    tasks = [EsportsBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
