MEDICINE EXPIRY TRACKER
=======================

WHAT THIS PROJECT DOES
- Add a medicine name, quantity, expiry date and optional notes.
- Save records in medicines.json on your computer.
- Show whether a medicine is expired, expiring within 30 days, or safe by date.
- Delete a medicine record.

IMPORTANT
This is an educational tracking project. It does not verify medicine quality,
storage conditions, authenticity, or whether a medicine is suitable to take.
Always check the package and consult a pharmacist or healthcare professional.

HOW TO RUN ON WINDOWS
1. Install Python 3 from https://www.python.org/downloads/
   During installation, tick "Add Python to PATH".
2. Extract this ZIP file.
3. Open the extracted medicine_expiry_tracker folder.
4. Click the folder address bar, type cmd, and press Enter.
5. Run these commands one at a time:

   py -m venv venv
   venv\Scripts\activate
   py -m pip install -r requirements.txt
   py app.py

6. Open your browser and visit:
   http://127.0.0.1:5000

7. To stop the website, return to the Command Prompt and press Ctrl + C.

WHERE IS THE DATA SAVED?
The app creates medicines.json in the project folder when you add the first
record. Do not delete this file if you want to keep your saved entries.

PROJECT FILES
app.py                 Python Flask application
templates/index.html   Website page
static/style.css       Website design
requirements.txt       Python package list
README.txt             Setup instructions
