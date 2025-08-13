import pdfplumber
import pandas as pd
import re

pdf_path = 'socse_timetable.pdf'

# Regex to find any course or room code

code_pattern = re.compile(r'\b((?!PUNIV)[A-Z]{2,}\d+)\b')# Known course prefixes to help differentiate
COURSE_PREFIXES = ('CSE', 'MAT', 'APT', 'FIN', 'IST', 'CSD', 'CSN', 'COM', 'CAI', 'CCS', 'CBD', 'CDV', 'CBC', 'CIT')

final_schedule = []

print("Attempting to parse tables directly from PDF...")

try:
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Use pdfplumber's built-in table extraction
            tables = page.extract_tables()
            if not tables:
                continue

            for table in tables:
                # The first row of a valid table should contain the time slots
                time_slots = table[0]
                
                # Process the rest of the rows in the table
                for row in table[1:]:
                    # The first column is usually the day
                    day = row[0]
                    if day and day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                        # Iterate through the cells for that day's row
                        for i, cell_content in enumerate(row[1:], 1):
                            if cell_content and i < len(time_slots):
                                # Clean up the cell content by replacing newlines
                                clean_cell = cell_content.replace('\n', ' ')
                                codes_in_cell = code_pattern.findall(clean_cell)
                                
                                courses_in_cell = [code for code in codes_in_cell if code.startswith(COURSE_PREFIXES)]
                                rooms_in_cell = [code for code in codes_in_cell if not code.startswith(COURSE_PREFIXES)]
                                
                                # If we find a course and a room in the same cell, pair them
                                if courses_in_cell and rooms_in_cell:
                                    final_schedule.append({
                                        'day': day,
                                        'time': time_slots[i],
                                        'course_code': courses_in_cell[0],
                                        'room_code': rooms_in_cell[0]
                                    })

except Exception as e:
    print(f"An error occurred: {e}")

if final_schedule:
    print("\nParsing complete. Saving results to CSV...")
    df = pd.DataFrame(final_schedule)
    df.drop_duplicates(inplace=True)
    
    # Clean up the time column from extra characters
    df['time'] = df['time'].str.replace('\n', ' ').str.strip()
    
    df.to_csv('timetable.csv', index=False)
    print("Successfully saved structured data to 'timetable.csv'")
    print("\nHere's a sample of the data:")
    print(df.head())
else:
    print("No schedule data was extracted. The document's table structure might be too irregular for automated parsing.")