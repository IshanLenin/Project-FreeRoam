Project FreeRoam: Campus Room Finder
Live Demo: https://freeroam.ishan-visionary.tech

1. Overview
Project FreeRoam is a full-stack web application designed to solve a common problem for university students: finding an empty classroom to study, relax, or work in between lectures. The application provides a real-time, mobile-friendly interface that displays a list of all currently available classrooms based on the university's official timetable.

This project demonstrates a complete end-to-end engineering lifecycle, from tackling a highly unstructured data source to building a robust backend API, a clean frontend, and deploying the entire system as a containerized application on a cloud server.

2. The Challenge: Parsing Unstructured Data
The most significant technical challenge of this project was data acquisition and processing. The only available data source was a 96-page, highly unstructured PDF document containing the timetable for the entire School of Computer Science.

The PDF lacked a consistent format, with data misaligned across rows and columns. My initial approach using text and coordinate-based parsing with regular expressions proved insufficient due to these inconsistencies.

The final, successful solution involved a more robust data engineering strategy:

Direct Table Extraction: I leveraged the pdfplumber library's powerful table detection capabilities to directly extract the grid-like structure from each page, bypassing the messy text layer.

Rule-Based Cleaning: I developed a Python script using the pandas library to programmatically clean the extracted data, creating rules to correctly identify and pair course codes with their corresponding room numbers for each time slot.

Database Creation: The final, clean data was then used to populate a lightweight SQLite database, which serves as the single source of truth for the application's backend.

3. System Architecture
The application is built on a modern, decoupled architecture:

Data Pipeline: A set of Python scripts (parse_timetable.py, database_setup.py) that handle the one-time task of parsing the source PDF and creating the timetable.db database.

Backend API: A robust backend built with FastAPI that serves the application's logic. It exposes a simple REST API endpoint (/api/free-rooms/now) that queries the SQLite database to find and return a list of currently unoccupied rooms.

Frontend Interface: A simple, lightweight, and mobile-friendly single-page application built with vanilla HTML, CSS, and JavaScript. It uses the fetch API to call the backend and dynamically displays the list of available rooms.

Deployment: The entire application is containerized using Docker and deployed on a DigitalOcean Linux server. An Nginx web server acts as a reverse proxy to handle incoming traffic and is secured with SSL/TLS certificates from Certbot.

4. Tech Stack
Category

Technology

Backend

Python, FastAPI

Frontend

HTML, CSS, JavaScript

Database

SQLite

Data Parsing

pdfplumber, pandas, Regular Expressions

Deployment

Docker, Nginx, DigitalOcean, Certbot (SSL)

Dev Tools

Git, GitHub, VS Code, Postman

5. Local Setup and Installation
To run this project on your local machine, follow these steps:

Prerequisites:

Python 3.9+

The socse_timetable.pdf file in the root directory.

1. Clone the Repository:

git clone https://github.com/IshanLenin/Project-FreeRoam.git
cd Project-FreeRoam

2. Install Dependencies:

pip install -r requirements.txt

3. Build the Database:
First, run the parsing script to create the timetable.csv file, and then run the database setup script to create timetable.db.

python parse_timetable.py
python database_setup.py

4. Run the API Server:

uvicorn main:app --reload

The application will be available at http://127.0.0.1:8000.
