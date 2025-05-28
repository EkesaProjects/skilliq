import os
import fitz
from datetime import datetime, date
from app.db.clickhouse import execute_command
from fastapi import UploadFile
from docx import Document 
import shutil
# from app.core import settings


def extract_text_from_file(file_path):
    print("file is", file_path)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return ""

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    text = ""

    if ext == ".pdf":
        doc = fitz.open(file_path)
        for page_number in range(len(doc)):
            page = doc[page_number]
            text += page.get_text()
        doc.close()

    elif ext == ".docx":
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    else:
        print(f"Unsupported file type: {ext}")
        return ""

    return text

# def extract_text_from_file(file: UploadFile) -> str:
#     filename = file.filename.lower()
#     try:
#         if filename.endswith(".pdf"):
#             reader = PdfReader(file.file)
#             text = "".join([page.extract_text() or "" for page in reader.pages])
#             return text
#         elif filename.endswith(".docx"):
#             temp_path = f"temp_{file.filename}"
#             with open(temp_path, "wb") as temp_file:
#                 temp_file.write(file.file.read())
#             text = docx2txt.process(temp_path)
#             os.remove(temp_path)
#             return text
#         elif filename.endswith(".txt"):
#             return file.file.read().decode("utf-8", errors="ignore")
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file format")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def get_id(col_name, table_name):
    result = execute_command(f"SELECT coalesce(MAX({col_name}), 0)+1 FROM {table_name}")
    # id = result.result_rows[0][0]
    return result

def group_candidate_data(rows):
    if not rows:
        return None

    base = {
        "candidate_id": rows[0][0],
        "candidate_name": rows[0][1],
        "email_address": rows[0][2],
        "mobile_number": rows[0][3],
        "skills": set(),
        "education": set(),
        "experience": set(),
        "projects": set()
    }

    for row in rows:
        # print('rows in view gruoup function >>>>>>>>>>>>>>>>>>>>', row)
        # Indexes match SELECT columns
        skill_name = row[4]
        degree, institution, year = row[5], row[6], row[7]
        company, title, start, end = row[8], row[9], row[10], row[11]
        project_name, project_desc = row[12], row[13]

        if skill_name is not None:
            base["skills"].add(skill_name)

        if any([degree, institution, year]):
            base["education"].add((degree, institution, year))

        if any([company, title, start, end]):
            base["experience"].add((company, title, start, end))

        if any([project_name, project_desc]):
            base["projects"].add((project_name, project_desc))


    # Convert sets to lists
    base["skills"] = list(base["skills"])
    base["education"] = list(base["education"])
    base["experience"] = list(base["experience"])
    base["projects"] = list(base["projects"])

    return base



# def save_uploaded_file(upload_file):
#     # Ensure the base folder exists
#     if not os.path.exists(settings.UPLOAD_FOLDER):
#         os.makedirs(settings.UPLOAD_FOLDER)

#     # Create subfolder for today's date (e.g. 2025-05-28)
#     today_folder = os.path.join(settings.UPLOAD_FOLDER, date.today().isoformat())
#     if not os.path.exists(today_folder):
#         os.makedirs(today_folder)

#     # Unique filename to avoid collision
#     filename = f"{upload_file.filename}"
#     filepath = os.path.join(today_folder, filename)

#     # Save file to that location
#     with open(filepath, "wb") as buffer:
#         shutil.copyfileobj(upload_file.file, buffer)

#     return filepath