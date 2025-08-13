import pdfplumber
import pandas as pd
import re

pdf_path = 'socse_timetable.pdf'

# Regex to find any course or room code
code_pattern = re.compile(r'\b([A-Z]{2,}\d+)\b')

# Known course prefixes
COURSE_PREFIXES = ('CSE', 'MAT', 'APT', 'FIN', 'IST', 'CSD', 'CSN', 'COM', 'CAI', 'CCS', 'CBD', 'CDV', 'CBC', 'CIT')

final_schedule = []

print("Attempting to parse tables directly from PDF...")

try:
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Use pdfplumber's table extraction
            tables = page.extract_tables()
            if not tables:
                continue

            for table in tables:
                # The first row often contains the time slots
                time_slots = table[0]
                
                # Process the rest of the rows
                for row in table[1:]:
                    # The first column is usually the day
                    day = row[0]
                    if day and day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                        # Iterate through the cells for that day's row
                        for i, cell in enumerate(row[1:], 1):
                            if cell and i < len(time_slots):
                                # Find all codes within a single cell
                                codes = code_pattern.findall(cell.replace('\n', ' '))
                                
                                courses_in_cell = []
                                rooms_in_cell = []

                                # Classify codes found in the cell
                                for code in codes:
                                    if code.startswith(COURSE_PREFIXES):
                                        courses_in_cell.append(code)
                                    else:
                                        # Assume anything else is a room if it fits the general pattern
                                        rooms_in_cell.append(code)
                                
                                # If we have at least one course and one room, create an entry
                                if courses_in_cell and rooms_in_cell:
                                    # This assumes the first course pairs with the first room in a cell
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
    df.to_csv('timetable.csv', index=False)
    print("Successfully saved structured data to 'timetable.csv'")
    print("\nHere's a sample of the data:")
    print(df.head())
else:
    print("No schedule data was extracted. The table format may be too complex for automatic extraction.")