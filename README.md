
# Tee-Time-Auto-Booker-Public

This repository contains a small pair of automation scripts for booking Utah State Park golf tee times. The workflow is intentionally simple: one script sends a planning email to collect a preferred course and time, and the other script reads the reply and attempts to book a matching tee time.

## What the project does

- The email script sends a request for the golfer's preferred course and tee time for the Friday after next.
- The booking script checks for a recent reply, parses the preference, and attempts to find a matching tee time.
- If the preferred course is unavailable within the requested window, the script falls back to the closest available option at another course.

## Repository layout

- [README.md](README.md) — overview and usage notes
- [test_ut_tee_time_booking.py](test_ut_tee_time_booking.py) — booking automation flow
- [test_ut_tee_time_email.py](test_ut_tee_time_email.py) — email inquiry flow
- [docs/SETUP.md](docs/SETUP.md) — setup and scheduling guidance
- [.gitignore](.gitignore) — ignores generated screenshots, credentials, and Python cache files

## Setup

1. Install the required packages:
   - `pip install -r requirements.txt`
2. Fill in the required email, payment, and contact values at the top of the relevant Python script.
3. Review the timing logic and adjust the target date or email body if your booking window differs from the default Friday-after-next flow.

## Recommended timing

For the default workflow, the scripts are best run in this order:

1. Run the email script on Sunday around 12:00 PM MT, 12 days before the desired tee time.
2. Run the booking script between 6:50 PM MT and 11:59 PM MT on Monday, 11 days before the desired tee time.

## Notes

- The scripts are intentionally lightweight and depend on a few browser and email integrations.
- They were written for a specific workflow and may need minor adjustments if the website structure changes.
- Review the scripts carefully before using them for a real booking.

