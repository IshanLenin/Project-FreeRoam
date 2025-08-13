import sqlite3
from fastapi import FastAPI
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="Project FreeRoam API",
    description="An API to find empty classrooms based on a schedule."
)

DB_PATH = 'timetable.db'
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_free_rooms_at(day: str, time: str):
    """
    Core logic to find free rooms for a specific day and time.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    occupied_rooms_query = """
        SELECT DISTINCT room_name
        FROM schedules
        WHERE day = ? AND ? BETWEEN start_time AND end_time;
    """
    all_rooms_query = "SELECT DISTINCT room_name FROM schedules;"

    occupied_rooms = [row[0] for row in cursor.execute(occupied_rooms_query, (day, time))]
    all_rooms = [row[0] for row in cursor.execute(all_rooms_query)]
    
    conn.close()

    free_rooms = [room for room in all_rooms if room not in occupied_rooms]
    return free_rooms

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/api/free-rooms/now")
def free_rooms_now():
    """
    API endpoint to get a list of currently free rooms.
    """
    now = datetime.now()
    current_day = now.strftime('%A')
    current_time = now.strftime('%H:%M')
    free_rooms = get_free_rooms_at(day=current_day, time=current_time)
    return {"free_rooms": free_rooms, "checked_at": f"{current_day} {current_time}"}

@app.get("/api/free-rooms/check")
def free_rooms_at_time(day: str, time: str):
    """
    API endpoint to get free rooms for a custom day and time.
    Example: /api/free-rooms/check?day=Tuesday&time=11:00
    """
    free_rooms = get_free_rooms_at(day=day, time=time)
    return {"free_rooms": free_rooms, "checked_at": f"{day} {time}"}