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
- ⏰ APScheduler — background task scheduler (24h flight reminders)

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
| **2026-03-14** | v1.3 | Added **online check-in system** — passengers verify identity (name, surname, ID number) before check-in, with timestamp recording and check-in confirmation email; PDF boarding pass download is locked until check-in is complete. Boarding pass PDF upgraded with **QR code** (ticket ID encoded) and gate closing time (departure − 30 min). Added **round-trip booking support** — session now tracks return flight and redirects Step 3 between outbound and return seat selection. Refactored all business logic into a **service layer** (`booking_service`, `ticket_service`, `flight_service`, `email_service`, `pdf_service`, `seatmap_service`, `booking_session`). Added **departure/arrival timezone fields** on the Flight model with timezone-aware datetime properties. Email confirmation now includes the **receipt PDF as attachment** and uses styled HTML email template. Implemented solution to the race condition problem — locking rows in the database (select_for_update) during simultaneous reservations of the same seat in `booking_service.py` |
| **2026-03-29** | v1.4 | Added **hamburger/mega menu** (slide-in panel, login-only content for unauthenticated users). Replaced `/flights/` search with home-style widget (pre-filled from URL params). Added **forgot password** link on login. Split **My Bookings into Active/Past** — check-in blocked on past flights. Fixed **wrong prices** on confirmation, About Ticket and boarding pass PDF (seat upgrade + extras now included). Fixed **email sending** (Gmail App Password). Auto-generate flight number and auto-fill timezone/city dropdowns on Create Flight. Added **Free seat selection** row to seat class comparison. Extracted all inline CSS/JS to static files; split `base.css` into `base.css`, `components.css`, `nav.css`. Removed unused static files and dead CSS. |
| **2026-04-02** | v1.5 | Added **User Profile page** — edit name, email, date of birth, phone number, country; change password with email notification. Added **Resend receipt email** button on About Ticket page. Fixed **receipt PDF** — seat number was showing N/A, return flight missing from payment table. Redesigned **city/airport search dropdown** (Ryanair-style: 5-column country grid, airport panel, active pill highlights). Flight list now shows **departure and arrival local times** (timezone-aware). Added **Admin Panel** — KPI cards, Chart.js bookings/revenue dual-axis chart (last 14 days), flight occupancy table with search filters (route, flight number, date), all-reservations list with status filter. Added **Admin Flight Detail page** — per-flight KPIs, occupancy bar, full passenger list. Password change email notification added to forgot-password flow as well. Extracted all remaining inline CSS/JS to external files (`profile.css`, `admin.css`, `admin_panel.js`); fixed Chart.js not rendering after extraction. |
| **2026-04-24** | v1.6 | Added **check-in 24h window enforcement** — online check-in is blocked if more than 24 hours or less than 2 hours remain before departure; About Ticket page dynamically shows "Check-In Not Open Yet", "Check-In Now", or "Check-In Closed" based on current time. Added **24-hour flight reminder emails** — APScheduler background job runs every 5 minutes, detects flights departing in ~24 hours and sends styled HTML reminder email to all booked passengers; `notification_sent` flag on Flight prevents duplicate sends (Flyway migration V10). Added **Admin cancel flight** — admin can cancel any flight from the Flight Detail page; all booked tickets are automatically refunded and each passenger receives a cancellation email stating the refund is available within 24 hours. Added **email pre-fill on booking Step 1** — first passenger's email field is automatically populated from the logged-in user's account email. |

---

## 🗓️ Development Plan

### Phase 3 — 26.04 → 03.05
- **Refund Receipt** — sending refund receipt to email / cancelation email
- **Currencies** — multi-currency support + on email picked currency 
- **Design** — edit hamburger menu with more content, home page edits
- **Responsive design for phones** — CSS improvements for mobile

---

Made by **Leon Šerka**