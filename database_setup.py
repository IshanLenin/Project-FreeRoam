import pandas as pd
import sqlite3

# Load the cleaned data from the CSV
df = pd.read_csv('timetable.csv')

# Drop duplicate entries and unnecessary columns
df.drop_duplicates(inplace=True)
df.dropna(subset=['room_code', 'time'], inplace=True) # Ensure room and time exist

# --- Robustly extract start and end times ---
def get_start_time(time_str):
    try:
        return time_str.split(' - ')[0]
    except:
        return None

def get_end_time(time_str):
    try:
        return time_str.split(' - ')[1]
    except:
        return None

df['start_time'] = df['time'].apply(get_start_time)
df['end_time'] = df['time'].apply(get_end_time)

# Drop any rows where time parsing failed
df.dropna(subset=['start_time', 'end_time'], inplace=True)

# Select and rename the final columns for our database table
final_df = df[['day', 'start_time', 'end_time', 'room_code']].copy()
final_df.rename(columns={'room_code': 'room_name'}, inplace=True)

# --- Create and Populate the SQLite Database ---
db_path = 'timetable.db'
conn = sqlite3.connect(db_path)
print(f"Database created at {db_path}")

# Write the DataFrame to a new SQL table named 'schedules'
final_df.to_sql('schedules', conn, if_exists='replace', index=False)
print("'schedules' table created and populated successfully.")

# --- Verify the data ---
print("\nFirst 5 entries in the 'schedules' table:")
cursor = conn.cursor()
for row in cursor.execute("SELECT * FROM schedules LIMIT 5"):
    print(row)

conn.close()
print("\nDatabase connection closed.")