import os
import json
import re
# from google import genai
from google import generativeai as genai
from app.core.config import settings
import logging

# def parse_resume(extracted_resume_text):
#     client_genai = genai.Client(api_key=settings.GEMINI_API_KEY)
#     response = client_genai.models.generate_content(
#         model="gemini-2.0-flash", 
#         contents=f"""
#                     You are an expert resume parser. Extract the following details from this resume text:
#                     - Full Name
#                     - Email
#                     - Phone Number
#                     - Skills (list) and categorise them as primary and secondary according to their projects and experiences
#                     - Education (list of objects degree, institution, start_date, end_date, cgpa, percentage)
#                     - Work Experience (list of objects with title, company, description, start_date, end_date or empty list if not present) 
#                     - Projects (list of objects with title, description, github_link, start_date, end_date)
#                     - Professional Summary: A clear, concise summary of the candidate's whole profile as per my resume extracted text . This should capture their professional  identity, key experience, skills, areas of expertise, and career goals. It will be used for matching against job descriptions later.

#                     **Important:**  
#                         • Do NOT include any bullet characters (e.g. “•”) in your JSON.  
#                         • Normalize any ligatures (e.g. “ﬁ” → “fi”).  
#                         • Return flat JSON arrays and strings only—no leading symbols or special punctuation.

#                     Return the output keys:  'candidate_name', 'email_address', 'mobile_number', 'phone_number', 'date_of_birth' ('%Y-%m-%d'), 'linkedin_link', 'github_link', 'total_experience', 'sector', 'current_designation', 'current_employer', 'notice_period_days', 'expected_ctc', 'current_ctc', 'current_address', 'current_locality', 'current_city', 'current_state', 'current_zip', 'permanent_address', 'permanent_locality', 'permanent_city', 'permanent_state' 
#                     'permanent_zip', 'professional_summary', 'skills', 'education', 'experience', 'projects'.

#                     Output should be in JSON format, wrapped only in ''' ''' (triple quotes) without additional explanation.

#                     Resume Text:
#                     {extracted_resume_text}

#                     ps: ignore
#                     """, 
#         config={"response_mime_type": "application/json"}
#     )

#     parsed_json_data = response.text
#     print(parsed_json_data)

#     return parsed_json_data
# Configure logging (optional)

logging.basicConfig(level=logging.INFO)

# Gemini config
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def preprocess_text(text: str) -> str:
    return (
        text.replace("ﬁ", "fi")
            .replace("ﬂ", "fl")
            .replace("•", "-")
            .replace("“", '"').replace("”", '"')
            .replace("‘", "'").replace("’", "'")
    )
def extract_json(text: str) -> str:
    """
    Extract JSON block from raw Gemini output.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else "{}"

def parse_resume(extracted_resume_text: str) -> dict:
    """
    Sends resume text to Gemini API and returns structured candidate data.
    Handles fallback, cleanup, and logging.
    """
    preprocessed_text = preprocess_text(extracted_resume_text)
    prompt = f"""
    You are an expert resume parser. Extract and return the following details in valid flat JSON format:

    - 'candidate_name'
    - 'email_address'
    - 'mobile_number'
    - 'phone_number'
    - 'date_of_birth' (format: 'YYYY-MM-DD')
    - 'linkedin_link'
    - 'github_link'
    - 'total_experience' (in float value)
    - 'sector': please identify the sector based on past experiences
    - 'current_designation'
    - 'current_employer'
    - 'notice_period_days'
    - 'expected_ctc'
    - 'current_ctc'
    - 'current_address'
    - 'current_locality'
    - 'current_city'
    - 'current_state'
    - 'current_zip'
    - 'permanent_address'
    - 'permanent_locality'
    - 'permanent_city'
    - 'permanent_state'
    - 'permanent_zip'
    - 'professional_summary': A clear, concise summary of the candidate's profile. This should capture their professional identity, key experience, core skills, areas of expertise, and career goals. It will be used for job matching in the future.
    - 'Skills' (list of objects: Skills and categorize them in primary or secondary)
    - 'experience' (list of objects: title, company, description, start_date, end_date)
    - 'projects' (list of objects: title, description, github_link, start_date, end_date)

    **Important Instructions**:
    - Do NOT include bullet characters (e.g. “•”).
    - Normalize ligatures (e.g. “ﬁ” → “fi”).
    - Only return valid, structured JSON — no commentary, prefix, or explanation.
    - Ensure all fields are flat and follow the naming format above.

    Resume Text:
    \"\"\"{preprocessed_text}\"\"\"
    """

    try:
        response = model.generate_content(prompt)
        content = extract_json(response.text)
        print(content)
        return json.loads(content)

    except json.JSONDecodeError as je:
        logging.warning("JSON Decode Error on main prompt. Trying fallback...")
        logging.debug(f"Raw Gemini Output: {response.text}")

        # Retry with simpler fallback prompt
        fallback_prompt = f"""
            Extract any available structured information from this resume into flat JSON:
            Name, email, phone, experience, education, skills — return whatever you find.
            \"\"\"{preprocessed_text}\"\"\"
        """
        try:
            fallback_response = model.generate_content(fallback_prompt)
            fallback_content = extract_json(fallback_response.text)
            return json.loads(fallback_content)
        except Exception as fallback_error:
            logging.error("Fallback also failed.")
            logging.debug(f"Fallback Output: {fallback_response.text}")
            return {}

    except Exception as e:
        logging.error("Gemini Parsing Error:", exc_info=e)
        return {}