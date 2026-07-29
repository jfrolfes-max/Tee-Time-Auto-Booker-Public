# UT-Tee-Time-Booking-Public-

These scripts are designed to automate booking tee times for Utah State Park's golf courses.
I use it specifically for Fridays, but you can schedule booking runs ~11 days out from any desired day.

The email portion will email the player to request the player's preferred tee time and course for the Friday after next.
    (Update target date function if not booking on a Friday)

The booking portion will:

Parse the player's email response and store preferred tee time and course.
    (Player's email response must be fresher than two days old from time of booking run to prevent stale or duplicate bookings.)

Navigate time and date filters to parse all available UT State Park golf course tee times for 10 days out

Search for the closest 4-man tee time (within +/- 30 min from player's preferred time at preferred course) and select it

     If none exist +/- 30 min at the player's preferred course, 
     the script will book the nearest-to-preferred available 4-man tee time at one of the other courses

Navigate through the booking form and complete booking based on the booking info variables defined at the top of the script.

Batch the email script to run at 12:00 PM the Sunday 12 days before desired tee time for best results.

Batch the booking script to run some time between 6:50 PM and 11:59 PM on Monday 11 days before the desired tee time for best results.

