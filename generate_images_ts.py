import base64
import os

img1_path = r'C:/Users/fret/.gemini/antigravity/brain/03a5fbe0-fe1d-433c-b4cd-0f812ba31695/uploaded_image_1_1768364563100.png'
img2_path = r'C:/Users/fret/.gemini/antigravity/brain/03a5fbe0-fe1d-433c-b4cd-0f812ba31695/uploaded_image_2_1768364563100.png'
img3_path = r'C:/Users/fret/.gemini/antigravity/brain/03a5fbe0-fe1d-433c-b4cd-0f812ba31695/uploaded_image_3_1768364563100.png'

def get_b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

b64_1 = get_b64(img1_path)
b64_2 = get_b64(img2_path)
b64_3 = get_b64(img3_path)

ts_content = f"""export const REPORT_IMAGES = {{
    ESCUDO_PERU: '{b64_1}',
    LOGO_PJ: '{b64_2}',
    LOGO_BICENTENARIO: '{b64_3}'
}};
"""

output_path = r'c:\Users\fret\Documents\proyect\app_recon_main\AppSismtAsistenF\src\utils\reportImages.ts'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(ts_content)

print("File created successfully at " + output_path)
