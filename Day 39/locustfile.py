from locust import HttpUser, between, task


class FastAPIUser(HttpUser):
    host = "http://localhost:8000"

    wait_time = between(0.1, 0.5)

    @task
    def predict(self):
        payload = {
            "Age": 30,
            "Gender": "Male",
            "Product_Category": "Electronics",
            "Quantity": 2,
            "Price_per_Unit": 500,
        }

        self.client.post("/predict", json=payload)
