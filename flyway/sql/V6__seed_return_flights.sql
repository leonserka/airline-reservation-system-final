INSERT INTO flights_flight
    (flight_number, departure_country, departure_city, departure_timezone, arrival_country, arrival_city, arrival_timezone, date, departure_time, arrival_time, price, total_seats, available_seats, flight_type)
VALUES
    -- Day 1: Zagreb <-> Berlin
    ('CR101', 'Croatia',   'Zagreb',    'Europe/Zagreb', 'Germany',  'Berlin',    'Europe/Berlin',    '2026-02-22', '08:00', '09:45', 89.99,  120, 120, 'INT'),
    ('CR102', 'Germany',   'Berlin',    'Europe/Berlin', 'Croatia',  'Zagreb',    'Europe/Zagreb',    '2026-02-22', '18:00', '19:45', 89.99,  120, 120, 'INT'),

    -- Day 2: Vienna <-> Rome
    ('CR201', 'Austria',   'Vienna',    'Europe/Vienna', 'Italy',    'Rome',      'Europe/Rome',      '2026-02-23', '07:30', '09:15', 109.99, 160, 160, 'INT'),
    ('CR202', 'Italy',     'Rome',      'Europe/Rome',   'Austria',  'Vienna',    'Europe/Vienna',    '2026-02-23', '17:30', '19:15', 109.99, 160, 160, 'INT'),

    -- Day 3: London <-> Paris
    ('CR301', 'United Kingdom', 'London', 'Europe/London', 'France', 'Paris',     'Europe/Paris',     '2026-02-24', '09:00', '10:30', 129.99, 180, 180, 'INT'),
    ('CR302', 'France',    'Paris',     'Europe/Paris',  'United Kingdom', 'London', 'Europe/London', '2026-02-24', '19:00', '20:30', 129.99, 180, 180, 'INT'),

    -- Day 4: Belgrade <-> Istanbul
    ('CR401', 'Serbia',    'Belgrade',  'Europe/Belgrade', 'Turkey', 'Istanbul',  'Europe/Istanbul',  '2026-02-25', '06:30', '09:00', 79.99,  140, 140, 'INT'),
    ('CR402', 'Turkey',    'Istanbul',  'Europe/Istanbul', 'Serbia', 'Belgrade',  'Europe/Belgrade',  '2026-02-25', '16:30', '19:00', 79.99,  140, 140, 'INT'),

    -- Day 5: Amsterdam <-> Barcelona
    ('CR501', 'Netherlands','Amsterdam', 'Europe/Amsterdam','Spain',  'Barcelona', 'Europe/Madrid',    '2026-02-26', '10:00', '12:30', 119.99, 160, 160, 'INT'),
    ('CR502', 'Spain',     'Barcelona', 'Europe/Madrid',  'Netherlands','Amsterdam','Europe/Amsterdam','2026-02-26', '20:00', '22:30', 119.99, 160, 160, 'INT');
