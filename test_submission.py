import requests

def test_submission():
    url = "http://127.0.0.1:5000/api/submit_complaint"
    data = {
        "citizen_name": "",
        "citizen_email": "",
        "citizen_phone": "",
        "citizen_address": "",
        "latitude": "20.5937",
        "longitude": "78.9629",
        "category": "Water_Supply",
        "description": "emergency case fire on a building",
        "citizen_language": "en"
    }
    
    files = {'media_upload': ('dummy.txt', open('dummy.txt', 'rb'))}
    try:
        response = requests.post(url, data=data, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_submission()
