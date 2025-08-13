# Add these imports to the top
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Project FreeRoam API",
    description="An API to find empty classrooms based on a schedule."
)

# This line "mounts" the static directory, making files available
app.mount("/static", StaticFiles(directory="static"), name="static")

# Update your root endpoint to serve the index.html file
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# --- Database Path ---
DB_PATH = 'timetable.db'

def get_free_rooms():
    """
    Queries the database to find rooms that are free at the current time.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the current day and time
    now = datetime.now()
    current_day = now.strftime('%A')  # e.g., "Monday"
    current_time = now.strftime('%H:%M') # e.g., "14:30"
    
    # SQL query to find rooms that are currently occupied
    occupied_rooms_query = """
        SELECT DISTINCT room_name
        FROM schedules
        WHERE day = ? AND ? BETWEEN start_time AND end_time;
    """
    
    # SQL query to get a list of all unique rooms
    all_rooms_query = "SELECT DISTINCT room_name FROM schedules;"

    # Execute queries
    occupied_rooms = [row[0] for row in cursor.execute(occupied_rooms_query, (current_day, current_time))]
    all_rooms = [row[0] for row in cursor.execute(all_rooms_query)]
    
    conn.close()

    # Determine which rooms are free
    free_rooms = [room for room in all_rooms if room not in occupied_rooms]
    
    return free_rooms

@app.get("/")
def read_root():
    return {"message": "Welcome to the FreeRoam API!"}

@app.get("/api/free-rooms/now")
def free_rooms_now():
    """
    API endpoint to get a list of currently free rooms.
    """
    free_rooms = get_free_rooms()
    return {"free_rooms": free_rooms}