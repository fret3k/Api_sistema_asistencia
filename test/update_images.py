
import re
import os

ts_file_path = r"c:\Users\fret\Documents\proyect\app_recon_main\AppSismtAsistenF\src\utils\reportImages.ts"
base64_file_path = r"c:\Users\fret\Documents\proyect\app_recon_main\Api_sistema_asistencia\base64_output.txt"

try:
    if not os.path.exists(base64_file_path):
        print(f"Error: Base64 file not found at {base64_file_path}")
        exit(1)
        
    with open(base64_file_path, 'r', encoding='utf-8') as f:
        new_logo_data = f.read().strip()
        
    if not os.path.exists(ts_file_path):
        print(f"Error: TS file not found at {ts_file_path}")
        exit(1)

    with open(ts_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match LOGO_BICENTENARIO: '...'
    # Assumes single quotes as seen in previous view_file
    pattern = r"(LOGO_BICENTENARIO:\s*)'[^']*'"
    
    # Check if pattern exists first
    if not re.search(pattern, content):
        print("Error: Could not find LOGO_BICENTENARIO key pattern in file.")
        # Fallback debug: print first 500 chars
        print(content[:500])
        exit(1)

    replacement = f"\\1'{new_logo_data}'"
    new_content = re.sub(pattern, replacement, content)

    with open(ts_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("Successfully updated LOGO_BICENTENARIO in reportImages.ts")

except Exception as e:
    print(f"An error occurred: {e}")
