# Solstice Events – Asynchronous Check-In System

## Overview

Solstice Events Co. required a check-in kiosk capable of handling badge printing through an asynchronous vendor integration.

The original synchronous printer workflow was changed during the sprint because the badge-printer vendor deprecated the synchronous API.

The final implementation uses:

- FastAPI for the backend API
- An in-memory message queue to simulate the vendor queue
- A fake printer service to consume print jobs
- A webhook to receive asynchronous print-completion events
- HMAC-SHA256 signatures for webhook verification
- Job IDs to associate print jobs with attendees
- A browser-based check-in interface

## Asynchronous Flow

The final system follows this sequence:

1. An attendee submits a check-in request.
2. The backend verifies that the attendee exists and has not already requested check-in.
3. A unique print job is created.
4. The attendee is immediately placed into `PENDING`.
5. The print job is placed onto the simulated vendor queue.
6. The simulated printer retrieves the job.
7. The printer sends a completion webhook to the backend.
8. The backend verifies the webhook signature.
9. The backend verifies that the job belongs to the attendee.
10. The attendee is changed to `CHECKED_IN`.
11. The frontend polls the attendee endpoint and reflects the updated status.

## Duplicate Protection

An attendee cannot create another print request while their status is `PENDING` or `CHECKED_IN`.

This prevents duplicate badge-print requests from repeated scans.

## Webhook Security

Webhook requests contain an `X-Signature` header.

The backend calculates an HMAC-SHA256 signature using the shared webhook secret and compares it against the received signature before processing the callback.

Invalid or missing signatures are rejected.

## Job Validation

Each print request receives a job ID in the form:

`JOB-A001`

The job ID is stored against the attendee while the print request is pending.

The webhook must provide both the attendee ID and matching job ID before the attendee can be marked as checked in.

## Out-of-Order Confirmations

Webhook processing identifies the attendee using the IDs contained in each callback rather than assuming that callbacks arrive in the same order as requests.

This allows print-completion events to be processed independently of request order.

The `out_of_order_test.py` script demonstrates callbacks arriving in a different order from the original check-in requests.

## Project Structure

- `main.py` – FastAPI backend and asynchronous workflow
- `frontend/index.html` – browser check-in interface
- `frontend/fake-printer.py` – simulated printer/vendor consumer
- `frontend/out_of_order_test.py` – out-of-order webhook simulation
- `docs/scope-delta-analysis.md` – analysis of the sprint pivot
- `docs/architecture.md` – final architecture
- `docs/testing-evidence.md` – functional testing and results

## Running the Backend

From the project directory:

```bash
python -m uvicorn main:app --reload
