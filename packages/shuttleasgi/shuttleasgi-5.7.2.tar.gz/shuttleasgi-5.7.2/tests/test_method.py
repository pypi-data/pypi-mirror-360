import pytest
from shuttleasgi import Application, Response, post

# Create a simple app with a POST endpoint
app = Application()

@post("/test")
async def handle_post(request):
    data = await request.json()  # Assuming JSON body
    return Response(200, body=f"Received: {data.get('message', 'No message')}".encode())

# Test cases
def test_post_endpoint():
    # Simulate a POST request (simplified; adjust based on shuttleasgi's API)
    response = app.handle_request({"method": "POST", "path": "/test", "body": b'{"message": "hello"}'})
    assert response.status == 200
    assert b"Received: hello" in response.body

def test_get_on_post_endpoint():
    # Simulate a GET request on the same endpoint
    response = app.handle_request({"method": "GET", "path": "/test"})
    assert response.status == 404  # Expect 404 since GET isn't defined