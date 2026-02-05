
import base64
import sys

image_path = r"C:/Users/fret/.gemini/antigravity/brain/5638eadc-7a41-4b19-b70c-020926102cd4/uploaded_image_1_1768408788121.png"

try:
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        with open("base64_output.txt", "w") as out_file:
            out_file.write(f"data:image/png;base64,{encoded_string}")
        print("Success")
except Exception as e:
    print(f"Error: {e}")
