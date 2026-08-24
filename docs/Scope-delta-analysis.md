# Scope Delta Analysis

## 1. Original Specification

The original Solstice Events check-in solution was designed around a synchronous printer integration. The kiosk would submit a check-in request to the printer service and receive an immediate response. A successful response would allow the attendee to be treated as checked in.

The original design also required duplicate-scan protection so that an attendee could not submit multiple check-in requests.

## 2. Mid-Sprint Pivot

During development, the printer vendor deprecated the synchronous printing API. The system therefore had to be redesigned around an asynchronous workflow with a message queue and webhook confirmation.

The new requirement was that a check-in could not immediately become `CHECKED_IN`. Instead, the attendee would enter a `PENDING` state while the print request was waiting for completion. The attendee would only become `CHECKED_IN` after a valid printer webhook was received.

## 3. What Changed

| Original                        | Pivoted implementation                      | Reason                                                        |
| ------------------------------- | ------------------------------------------- | ------------------------------------------------------------- |
| Synchronous printer request     | Asynchronous print queue                    | Vendor deprecated the synchronous API                         |
| Immediate check-in confirmation | `PENDING` → `CHECKED_IN`                    | Check-in must wait for actual print completion                |
| Direct printer response         | Webhook callback                            | Printer completion now happens asynchronously                 |
| Basic duplicate protection      | Duplicate protection plus job-ID validation | Confirmations may arrive separately from the original request |
| Printer integration             | Local fake-printer simulation               | A real vendor queue was unavailable during development        |
| Immediate frontend success      | Frontend polls attendee status              | UI must reflect the asynchronous state transition             |

## 4. New Work Required by the Pivot

The pivot required several components that were not part of the original synchronous flow:

* A simulated print queue.
* A unique print job ID for each check-in request.
* A queue endpoint for retrieving pending print jobs.
* A webhook endpoint for printer completion notifications.
* HMAC signature generation and verification.
* Validation of the attendee associated with a webhook.
* Validation that the webhook job ID matches the attendee's pending job.
* A `PENDING` attendee state.
* Frontend status monitoring so the UI updates after webhook confirmation.
* A fake printer to simulate the external vendor's asynchronous behaviour.

## 5. What Was Preserved

The pivot did not remove the core attendee check-in functionality.

The final implementation still:

* Validates attendee IDs.
* Retrieves attendee information.
* Rejects unknown attendees.
* Prevents duplicate check-in requests.
* Tracks attendee status.
* Provides a frontend check-in interface.
* Confirms successful check-in.

The primary change was the timing and mechanism of confirmation.

## 6. Cut or Deferred Work

Production-grade database persistence, a real external message broker, production printer integration, and production deployment were deferred.

The prototype uses in-memory attendee data and Python's queue implementation. These choices reduced implementation complexity while still demonstrating the required asynchronous architecture.

Additional frontend styling and non-essential UI functionality were also kept minimal so that the core pivot requirements could be completed within the available sprint time.

## 7. Trade-Offs

The main trade-off was prioritising architectural adaptation over production infrastructure and additional frontend polish.

A real message broker and persistent database would provide greater reliability and persistence, but implementing them during the sprint would have increased scope significantly.

The final prototype therefore focuses on demonstrating the required behaviour:

1. Check-in request creation.
2. Duplicate protection.
3. Print job creation.
4. Queue-based processing.
5. Asynchronous webhook confirmation.
6. Signature verification.
7. Job-ID validation.
8. Final transition to `CHECKED_IN`.

## 8. Result

The pivot was incorporated without removing the core check-in functionality. The final implementation demonstrates the required asynchronous printer workflow while preserving duplicate-scan protection and attendee validation.
