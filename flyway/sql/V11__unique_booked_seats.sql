CREATE UNIQUE INDEX IF NOT EXISTS uniq_booked_seat_per_flight
ON flights_ticket (flight_id, seat_number)
WHERE seat_number IS NOT NULL AND status = 'booked';
