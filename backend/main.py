from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib
import json
import queue


app = FastAPI()



@app.get("/kiosk")
def kiosk():
    return FileResponse("static/index.html")


WEBHOOK_SECRET = b"my-super-secret"

print_queue = queue.Queue()

attendees = {
    "A001": {
        "name": "Zuri",
        "status": "NOT_CHECKED_IN",
        "job_id": None
    },
    "A002": {
        "name": "Daniel",
        "status": "NOT_CHECKED_IN",
        "job_id": None
    },
    "A003": {
        "name": "Tzolis",
        "status": "NOT_CHECKED_IN",
        "job_id": None
    }
}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Solstice Check-In API is running"
    }


@app.get("/attendee/{attendee_id}")
def get_attendee(attendee_id: str):
    attendee = attendees.get(attendee_id)

    if attendee is None:
        return {
            "status": "error",
            "message": "Attendee not found"
        }

    return {
        "attendee_id": attendee_id,
        "name": attendee["name"],
        "status": attendee["status"],
        "job_id": attendee["job_id"]
    }


@app.post("/check-in/{attendee_id}")
def check_in(attendee_id: str):
    attendee = attendees.get(attendee_id)

    if attendee is None:
        return {
            "status": "error",
            "message": "Attendee not found"
        }

    if attendee["status"] != "NOT_CHECKED_IN":
        return {
            "status": "rejected",
            "message": "Attendee already has a check-in request",
            "attendee_id": attendee_id,
            "current_status": attendee["status"]
        }

    job_id = "JOB-" + attendee_id

    attendee["status"] = "PENDING"
    attendee["job_id"] = job_id

    print_queue.put({
        "job_id": job_id,
        "attendee_id": attendee_id
    })

    return {
        "status": "pending",
        "message": "Print request added to vendor queue",
        "attendee_id": attendee_id,
        "job_id": job_id
    }


@app.get("/print-queue/next")
def get_next_print_job():
    if print_queue.empty():
        return {
            "status": "empty",
            "message": "No print jobs waiting"
        }

    job = print_queue.get()

    return {
        "status": "job_available",
        "job": job
    }


@app.post("/webhook/print-complete")
async def print_complete(request: Request):
    body = await request.body()

    received_signature = request.headers.get("X-Signature")

    expected_signature = hmac.new(
        WEBHOOK_SECRET,
        body,
        hashlib.sha256
    ).hexdigest()

    print("Received:", received_signature)
    print("Expected:", expected_signature)

    if not received_signature:
        return {
            "status": "rejected",
            "message": "Missing signature"
        }

    if not hmac.compare_digest(
            received_signature,
            expected_signature
    ):
        return {
            "status": "rejected",
            "message": "Invalid signature"
        }

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {
            "status": "rejected",
            "message": "Invalid JSON"
        }

    attendee_id = data.get("attendee_id")
    job_id = data.get("job_id")

    attendee = attendees.get(attendee_id)

    if attendee is None:
        return {
            "status": "error",
            "message": "Attendee not found"
        }

    if attendee["status"] != "PENDING":
        return {
            "status": "rejected",
            "message": "Attendee does not have a pending print job",
            "attendee_id": attendee_id,
            "current_status": attendee["status"]
        }

    if attendee["job_id"] != job_id:
        return {
            "status": "rejected",
            "message": "Job ID does not match attendee",
            "attendee_id": attendee_id,
            "expected_job_id": attendee["job_id"],
            "received_job_id": job_id
        }

    attendee["status"] = "CHECKED_IN"

    return {
        "status": "success",
        "message": "Print completed and attendee checked in",
        "attendee_id": attendee_id,
        "job_id": job_id
    }