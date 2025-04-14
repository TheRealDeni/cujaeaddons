from gevent import monkey
monkey.patch_all()
import requests
from locust import HttpUser,between,task
class SurveyUser(HttpUser):
    wait_time = between(1, 5)
    base_url = "http://localhost:8070"
    database = "odootesis"
    login = "admin"
    password = "admin"

    def on_start(self):
        self.client.post(f"{self.base_url}/web/session/authenticate", json={
            "jsonrpc": "2.0",
            "params": {
                "db": self.database,
                "login": self.login,
                "password": self.password,
            }
        })

    @task(5)
    def create_survey_question(self):
        response = self.client.post(f"{self.base_url}/api/survey_question", json={
            "title": "Sample Question",
            "description": "This is a sample question for testing."
        })
        print(response.json())

    @task(5)
    def search_survey_question_by_title(self):
        question_title = "Sample Question"
        response = self.client.get(f"{self.base_url}/api/survey_question", params={"title": question_title})
        print(response.json())

    @task(5)
    def modify_survey_question(self):
        question_id = 1  # Asume que ya tienes el ID de la pregunta que quieres modificar
        response = self.client.put(f"{self.base_url}/api/survey_question/{question_id}", json={
            "description": "Updated description for Sample Question"
        })
        print(response.json())

    @task(5)
    def create_survey(self):
        response = self.client.post(f"{self.base_url}/api/survey", json={
            "title": "Sample Survey",
            "exam": True
        })
        print(response.json())

    @task(5)
    def search_survey_by_title(self):
        survey_title = "Sample Survey"
        response = self.client.get(f"{self.base_url}/api/survey", params={"title": survey_title})
        print(response.json())

    @task(5)
    def modify_survey(self):
        survey_id = 1  # Asume que ya tienes el ID de la encuesta que quieres modificar
        response = self.client.put(f"{self.base_url}/api/survey/{survey_id}", json={
            "exam": False
        })
        print(response.json())

    @task(5)
    def create_slide(self):
        response = self.client.post(f"{self.base_url}/api/slide", json={
            "name": "Sample Slide"
        })
        print(response.json())

    @task(5)
    def search_slide_by_name(self):
        slide_name = "Sample Slide"
        response = self.client.get(f"{self.base_url}/api/slide", params={"name": slide_name})
        print(response.json())

    @task(5)
    def modify_slide(self):
        slide_id = 1  # Asume que ya tienes el ID de la diapositiva que quieres modificar
        response = self.client.put(f"{self.base_url}/api/slide/{slide_id}", json={
            "name": "Updated Sample Slide"
        })
        print(response.json())

    @task(5)
    def create_survey_based_on_slide(self):
        slide_id = 1  # Asume que ya tienes el ID de la diapositiva
        slide_response = self.client.get(f"{self.base_url}/api/slide/{slide_id}")
        slide_data = slide_response.json()

        if slide_data.get('exam'):
            response = self.client.post(f"{self.base_url}/api/survey", json={
                "title": "Exam Survey",
                "exam": True
            })
        else:
            response = self.client.post(f"{self.base_url}/api/survey", json={
                "title": "Regular Survey",
                "exam": False
            })
        print(response.json())
