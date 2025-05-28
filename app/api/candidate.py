import os
import json
import uuid
from typing import List
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.dao.candidate_dao import CandidateDAO
from app.core.config import settings
from app.utils.helpers import extract_text_from_file
from app.services.gemini_service import parse_resume
from fastapi import FastAPI, File, UploadFile
from app.db.clickhouse import get_table_columns
from datetime import date

UPLOAD_FOLDER = settings.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

TABLES = ['candidate', 'skills', 'education', 'experience', 'projects']

# @router.get('/')
# def Home():
#     candidate_dao = CandidateDAO()
#     results = candidate_dao.get_all_candidate()
#     serializable_results = [
#         {
#             'id': str(record[0]),
#             'name': record[1],
#             'email': record[2],
#             'phone': record[3]
#         }
#         for record in results
#     ]

#     # return jsonify(serializable_results)
#     return render_template('candidate.html', records=results)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    dao = CandidateDAO()
    columns = []
    for table in TABLES:
        columns.append(get_table_columns(table))
    results = dao.get_all_candidate()
    print("results are===============", results)
    return templates.TemplateResponse("candidate.html", {"request": request, "records": results, 'columns': columns, 'tables': TABLES})


@router.get('/upload_resumes', response_class=HTMLResponse)
async def upload_resumes(request: Request):
    return templates.TemplateResponse('upload_resumes.html',{"request": request})

@router.post('/upload_bulk')
async def upload_bulk(request: Request, files: List[UploadFile] = File(...)):
    # print(request)
    if not len(files):
        return "No file part", 400
 
    today_folder = os.path.join(settings.UPLOAD_FOLDER, date.today().isoformat())
    if not os.path.exists(today_folder):
        os.makedirs(today_folder)
        
    for file in files:
        print(file.filename)
        if file.filename: 
            filepath = os.path.join(today_folder, file.filename)

            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)

            extracted_resume_text = extract_text_from_file(filepath)
            json_payload = parse_resume(extracted_resume_text)

            candidate_data = json.loads(json_payload)
            # print("+++++++++++++++++++++++++++", candidate_data)

            candidate_dao = CandidateDAO()
            candidate_id = candidate_dao.get_id('candidate_id', 'candidate')
            # print("this is cnadidatre id ______________________",candidate_id)
            candidate_dao.insert_candidate_data(candidate_id, candidate_data)
            candidate_dao.insert_skills(candidate_id, candidate_data.get('skills', []))
            candidate_dao.insert_education(candidate_id, candidate_data.get('education', []))
            candidate_dao.insert_experience(candidate_id, candidate_data.get('experience', []))
            candidate_dao.insert_projects(candidate_id, candidate_data.get('projects', []))

    print("All data inserted successfully.")
    # return render_template('upload_resumes.html', uploaded=True)
    return f"{len(files)} file(s) uploaded successfully!"
    # return f"file(s) uploaded successfully!"

@router.get("/candidate/{candidate_id}", response_class=HTMLResponse)
def candidate_detail(request: Request, candidate_id: int):
    print("-------------------------------------------------------------", candidate_id)
    # return {"candidate_id": candidate_id}
    candidate_dao = CandidateDAO()
    candidate = candidate_dao.get_candidate_details(candidate_id)
    print(candidate)
    return templates.TemplateResponse("candidate_detail.html", {"request": request, "candidate": candidate})
