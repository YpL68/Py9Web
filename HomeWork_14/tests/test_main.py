from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)
templates = Jinja2Templates(directory='templates')


def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.template.name == 'index.html'  # https://www.starlette.io/templates/
    assert "request" in response.context


# def test_healthchecker():
#     response = client.get('/api/healthchecker')
#     assert response.status_code == 200
#     assert response.json() == {'ALERT': 'Welcome to FastAPI! System ready!'}