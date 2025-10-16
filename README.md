# Inventory Management App

A modern, full-stack Inventory Management System built with FastAPI, Streamlit, and PostgreSQL, containerized with Docker for seamless deployment.

Originally developed as part of a technical assessment, this project evolved into a showcase of clean backend design, database modeling, and user-friendly UI integration — demonstrating practical full-stack engineering skills.


## Highlights
- FastAPI Backend — RESTful API with SQLAlchemy ORM, robust CRUD operations, and data validation via Pydantic.
- Streamlit Frontend — intuitive dashboard for interacting with the database and visualizing parts, locations, and inventory levels.
- Duplicate Detection — intelligently identifies potential duplicate parts before insertion.
- Optimistic Locking — version control for inventory updates to prevent race conditions.
- Dockerized Architecture — runs the API, database, and UI in isolated containers for easy setup.


## Tech Stack
| Layer                | Technology              |
| -------------------- | ----------------------- |
| **Backend**          | FastAPI, SQLAlchemy     |
| **Frontend**         | Streamlit               |
| **Database**         | PostgreSQL              |
| **Containerization** | Docker & Docker Compose |
| **Migrations**       | Alembic                 |
| **Language**         | Python 3.11+            |


## Project Overview

The app helps small to medium teams track and manage inventory efficiently by organizing:

- Parts (with manufacturer, supplier, category, etc.)
- Storage Locations
- Inventory Quantities (by part and location)

It supports:

- Adding new parts while checking for duplicates
- Viewing all records in dynamic Streamlit tables
- Updating quantities safely with version tracking
- Modular API endpoints ready for integration with external systems


## Project Structure
inventory-management-app/
│
├── app/
│   ├── crud.py              # Database operations (CRUD logic)
│   ├── db.py                # DB connection setup
│   ├── main.py              # FastAPI backend entry point
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── streamlit_app.py     # Streamlit dashboard
│   └── __init__.py
│
├── alembic/                 # Alembic migrations
├── alembic.ini              # Alembic config
├── docker-compose.yml       # Multi-container setup (FastAPI, Streamlit, PostgreSQL)
├── Dockerfile               # Backend build file
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (excluded from Git)
└── README.md


## Getting Started
1. Docker Desktop (https://www.docker.com/products/docker-desktop/)

2. Clone the Repository
git clone https://github.com/YOUR_USERNAME/inventory-management-app.git
cd inventory-management-app

3. Configure Environment
Create a .env file
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/inventory

4. Run the App
docker compose up --build

5. Access the Interfaces
- Streamlit Dashboard: http://localhost:8501
- FastAPI Docs: http://localhost:8000/docs


## Future Improvements

- Role-based authentication (Admin vs Viewer)
- Search, filtering, and advanced reporting
- CSV / PDF export for inventory data
- Integration with barcode scanning
- Unit and integration testing
