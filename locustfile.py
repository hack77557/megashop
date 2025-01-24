from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/shop")
        self.client.get("/cart")

# In the HOST URL, in the locust UI do not write /shop
