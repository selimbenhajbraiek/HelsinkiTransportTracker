# 🚦 Real-Time Transport Trends Dashboard

A full-stack application to analyze and visualize transport logs using FastAPI, PostgreSQL, and Chart.js.

This dashboard shows:
- 🚍 Vehicle activity per hour (to detect transport peaks).
- 🏙️ Station usage (to find the busiest hubs).
- 📊 Beautiful interactive charts in the browser.

---
#### 1. Clone the Repository

git clone [https://github.com/selimbenhajbraiek/HelsinkiTransportTracker.git]
cd HelsinkiTransportTracker

# Create PostgreSQL Database and Tables:
-- Table: stations
CREATE TABLE stations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

-- Table: vehicles
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    vehicle_type VARCHAR(50)
);

# Update the Database Connection
DATABASE_URL = "postgresql://selimbraiek:selimselim@localhost:5432/helsenki_db"

# two servers connection:
No need to update anything because already configurated.

# Run the Project:
uvicorn main:app --reload 
and the url must be: http://127.0.0.1:8000/

