# Setup and scheduling guide

## Requirements

- Python 3.10+
- A Gmail account with app-password support enabled if using Gmail
- The packages listed in requirements.txt

## Installation

```bash
pip install -r requirements.txt
```

## Configuration checklist

1. Open the booking script and fill in the sender, recipient, and payment fields.
2. Open the email script and fill in the sender and recipient email values.
3. Confirm the target booking date logic if you are not using the default Friday-after-next workflow.
4. Review the browser automation flow before running it against a live site.

## Suggested schedule

- Email script: Sunday around 12:00 PM MT, 12 days before the target tee time
- Booking script: Monday between 6:50 PM MT and 11:59 PM MT, 11 days before the target tee time

## Safety notes

- Keep authentication values private and avoid committing them to version control.
- Run the scripts carefully and review the output before making any real booking.
