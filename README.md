# ✈️ Airline Reservation System (Django)

The **Airline Reservation System** is a full-stack web application built with the Django framework and PostgreSQL(via Docker and Flyway migrations).It allows users to search, book, and cancel flight tickets, while administrators can manage flights and monitor all reservations through the Django Admin Panel.

---

## 🚀 Main Features

### 👤 Users
- User registration and login  
- Search for available flights by origin, destination, and date  
- Multi-step booking process:
  1. Enter personal information  
  2. Choose seat class (**Basic**, **Regular**, **Plus**)  
  3. Select a seat on the airplane map (supports multiple passengers)
  4. (Optional) Add extras: Extra Luggage (10/20/23 kg) & Equipment (Sports/Music/Baby)
  5. Payment & ticket issuing
- View all purchased tickets (**Check Booked Flights**) — shows tickets bought by the logged-in user (even for other passengers)
- View ticket details (**About Ticket**) — includes extras and PDF ticket with Code128 barcode  
- Cancel a ticket (**Cancel Ticket**) – available only for **PLUS** class  
- When a ticket is canceled, the seat automatically becomes available again  

### 🧑‍💼 Administrator
- Add, edit, and delete flights through the **Django Admin Panel**  
- View all booked tickets and their payment status
- Automatically sync database schema via Flyway migrations 

---

## 🗄️ Models

### ✈️ Flight
Contains flight details:
- Flight number  
- Departure and arrival cities 
- Date and time of departure  
- Flight price 
- Seat availability
- Flight type (Domestic / International) 

### 🎫 Ticket
Contains ticket and passenger details:
- Passenger info (name, surname, ID number, email, phone, country)  
- Linked flight (**ForeignKey → Flight**)  
- Seat class and seat number  
- Payment method  
- **Payment Status:** Paid / Refunded  
- **Ticket Status:** Booked / Canceled
- **Purchased By:** `auth.user` (who paid for the booking) 

---

## 📦 Technologies Used
- 🐍 Python (Django Framework)
- 🐘 PostgreSQL — primary database
- 🚀 Flyway — version-controlled database migrations
- 🐳 Docker & Docker Compose — containerized environment
- 💻 HTML, CSS, JavaScript
- 🎨 Bootstrap — frontend styling

---

## 🗄️ Database Technology

This project uses **PostgreSQL** as the primary database engine, managed through Flyway migrations for schema version control.
All database tables and structures are defined in SQL migration files stored under:
```bash
flyway/sql/
```
When the containers start, Flyway automatically applies any new migrations to keep the database schema up to date.


**Default configuration (docker-compose.yml):**
- Database: airline_db
- User: airline_user
- Password: airline_pass
- Port: 5432

This setup ensures consistent database state across all environments — development, testing, and production.


---

## 📅 Recent Updates

| Date | Version | Highlights |
|------|----------|-------------|
| **2026-02-03** | v1.0 | Initial MVP: Dockerized Django application with PostgreSQL and Flyway, user authentication (login/register), flight search and multi-step booking workflow (Step 1–5). |
| **2026-02-21** | v1.1 | Implemented ticket cancellation workflow (PLUS class restriction), automatic seat release, payment status transition (Paid → Refunded), PDF ticket generation with Code128 barcode, SMTP password reset setup, secure environment variable handling, Ngrok Docker integration, Flyway schema update (country fields), seat selection refactor, template & UX improvements. |
| **2026-02-28** | v1.2 | Extracted all inline styles and scripts into dedicated CSS/JS static files (per page: `base.css`, `book_step5.css`, `flight_step3.css`, `home_carousel.css`, `home_search.css`, `receipt_pdf.css`, `search.css`, `ticket_pdf.css`). Added interactive home page with promotional image carousel (auto-advance + prev/next controls) and a dynamic flight search widget (AJAX-powered country/city dropdowns, Flatpickr date picker with available-dates-only filtering, one-way/round-trip toggle). Added PayPal SDK integration on booking Step 5 — real payment flow with order capture, loading overlay, seat-conflict detection, and error handling. |
| **2026-03-14** | v1.3 | Added **online check-in system** — passengers verify identity (name, surname, ID number) before check-in, with timestamp recording and check-in confirmation email; PDF boarding pass download is locked until check-in is complete. Boarding pass PDF upgraded with **QR code** (ticket ID encoded) and gate closing time (departure − 30 min). Added **round-trip booking support** — session now tracks return flight and redirects Step 3 between outbound and return seat selection. Refactored all business logic into a **service layer** (`booking_service`, `ticket_service`, `flight_service`, `email_service`, `pdf_service`, `seatmap_service`, `booking_session`). Added **departure/arrival timezone fields** on the Flight model with timezone-aware datetime properties. Email confirmation now includes the **receipt PDF as attachment** and uses styled HTML email template. |

---

## 🔜 Next Steps / TODO

- **Reset Password** — complete the full password reset flow (email link → form → confirmation)
- **Currencies** — add multi-currency support (display prices in user's preferred currency)