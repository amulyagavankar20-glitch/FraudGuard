import sys
sys.path.append('src')
from fastapi.testclient import TestClient
from fraudguard.service.app import app

client = TestClient(app)
print('Health:', client.get('/health').json())
resp = client.get('/v1/comparison')
print('Comparison status:', resp.status_code)
if resp.status_code == 200:
    print('Metrics:', resp.json()['metrics'])
