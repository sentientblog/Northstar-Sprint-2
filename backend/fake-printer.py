import requests
import hmac
import hashlib
import json

SECRET = b"my-super-secret"

url = "http://127.0.0.1:8000/webhook/print-complete"

jobs = [
    {
        "job_id": "JOB-A003",
        "attendee_id": "A003",
        "status": "completed"
    },
    {
        "job_id": "JOB-A001",
        "attendee_id": "A001",
        "status": "completed"
    },
    {
        "job_id": "JOB-A002",
        "attendee_id": "A002",
        "status": "completed"
    }
]

for job in jobs:
    body = json.dumps(job).encode()

    signature = hmac.new(
        SECRET,
        body,
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-Signature": signature,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        data=body,
        headers=headers
    )

    print("Sent:", job)
    print("Response:", response.text)
    print()