-- V8: User profile table for extra passenger info
CREATE TABLE flights_userprofile (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    date_of_birth DATE,
    phone_number  VARCHAR(20) DEFAULT '',
    country       VARCHAR(50) DEFAULT ''
);
