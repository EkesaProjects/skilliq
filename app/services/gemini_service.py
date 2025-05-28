import os
from google import genai
from app.core.config import settings

def parse_resume(extracted_resume_text):
    client_genai = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client_genai.models.generate_content(
        model="gemini-2.0-flash", 
        contents=f"""
                    You are an expert resume parser. Extract the following details from this resume text:
                    - Full Name
                    - Email
                    - Phone Number
                    - Skills (list)
                    - Education (list of objects degree, institution, start_date, end_date, cgpa, percentage)
                    - Work Experience (list of objects with title, company, description, start_date, end_date or empty list if not present) 
                    - Projects (list of objects with title, description, github_link, start_date, end_date)

                    **Important:**  
                        • Do NOT include any bullet characters (e.g. “•”) in your JSON.  
                        • Normalize any ligatures (e.g. “ﬁ” → “fi”).  
                        • Return flat JSON arrays and strings only—no leading symbols or special punctuation.

                    Return the output keys:  'candidate_name', 'email_address', 'mobile_number', 'phone_number', 'date_of_birth' ('%Y-%m-%d'), 'linkedin_link', 'github_link', 'total_experience', 'sector', 'current_designation', 'current_employer', 'notice_period_days', 'expected_ctc', 'current_ctc', 'current_address', 'current_locality', 'current_city', 'current_state', 'current_zip', 'permanent_address', 'permanent_locality', 'permanent_city', 'permanent_state', 'permanent_zip', 'skills', 'education', 'experience', 'projects'.
                    in just ''' '''
                    Resume Text:
                    {extracted_resume_text}

                    ps: ignore
                    """, 
        config={"response_mime_type": "application/json"}
    )

    parsed_json_data = response.text
    print(parsed_json_data)

    return parsed_json_data