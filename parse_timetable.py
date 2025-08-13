import pdfplumber
import re
import pandas as pd
from collections import defaultdict

pdf_path = 'socse_timetable.pdf'

# --- Patterns to find key information ---
day_pattern = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday)')
time_pattern = re.compile(r'(\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})')
code_pattern = re.compile(r'\b([A-Z]{3}\d{4}|[A-Za-z]{2,3}\d{2,3})\b')

# List to store all the final structured data
all_entries = []

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Processing {len(pdf.pages)} pages...")
        for page_num, page in enumerate(pdf.pages, 1):
            
            # Extract words with their positions
            words = page.extract_words(x_tolerance=1, y_tolerance=1)
            
            # --- Find the time slot boundaries from the page ---
            time_slots = []
            # Find all words that look like time ranges
            potential_times = time_pattern.findall(page.extract_text() or "")
            if potential_times:
                # Find the x-coordinate for each time slot header
                for time_str in sorted(list(set(potential_times))):
                    for word in words:
                        if time_str.startswith(word['text']):
                            time_slots.append({'text': time_str, 'x0': word['x0']})
                            break
            
            # Sort time slots by their horizontal position
            time_slots = sorted(time_slots, key=lambda x: x['x0'])

            # --- Extract the schedule grid ---
            current_day = None
            lines = defaultdict(list)
            for word in words:
                lines[int(word['top'])].append(word)

            for line_y in sorted(lines.keys()):
                line_words = sorted(lines[line_y], key=lambda w: w['x0'])
                line_text = ' '.join([w['text'] for w in line_words])

                day_match = day_pattern.match(line_text)
                if day_match:
                    current_day = day_match.group(1)
                
                if current_day and time_slots:
                    codes = code_pattern.findall(line_text)
                    if codes:
                        # For each code, find its x-position and map to a time slot
                        for code in codes:
                            for word in line_words:
                                if code == word['text']:
                                    code_x = word['x0']
                                    # Find the corresponding time slot
                                    assigned_time = "Unknown"
                                    for i, slot in enumerate(time_slots):
                                        # Check if the code's position is within this slot's boundary
                                        next_slot_x = time_slots[i+1]['x0'] if i + 1 < len(time_slots) else page.width
                                        if slot['x0'] <= code_x < next_slot_x:
                                            assigned_time = slot['text']
                                            break
                                    
                                    # Add the structured entry
                                    all_entries.append({
                                        'page': page_num,
                                        'day': current_day,
                                        'time': assigned_time,
                                        'code': code
                                    })
                                    break # Move to next code

except Exception as e:
    print(f"An error occurred: {e}")

# --- Save the results to a CSV file ---
if all_entries:
    print("\nParsing complete. Saving results to CSV...")
    df = pd.DataFrame(all_entries)
    
    # Simple heuristic to classify codes into 'course' or 'room'
    df['type'] = df['code'].apply(lambda x: 'course' if x.startswith(('CSE', 'MAT', 'APT')) else 'room')
    
    # Pivot the data to get course and room on the same line
    courses = df[df['type'] == 'course'].rename(columns={'code': 'course_code'})
    rooms = df[df['type'] == 'room'].rename(columns={'code': 'room_code'})
    
    # Merge based on page, day, and time
    final_df = pd.merge(courses, rooms, on=['page', 'day', 'time'], how='left')
    
    final_df[['day', 'time', 'course_code', 'room_code']].to_csv('timetable.csv', index=False)
    print("Successfully saved structured data to 'timetable.csv'")
    print("\nHere's a sample of the data:")
    print(final_df.head())
else:
    print("No entries were extracted.")