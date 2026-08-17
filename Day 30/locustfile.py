from locust import HttpUser, task, between
class MLApiUser(HttpUser):
    wait_time = between(1, 3)
    @task
    def predict(self):
        payload = {
            "Age": 25,
            "Gender": "Female",
            "Product_Category": "Electronics",
            "Quantity": 2,
            "Price_per_Unit": 100.0
        }

        self.client.post(
            "/predict",
            json=payload,
            name="/predict"
        )