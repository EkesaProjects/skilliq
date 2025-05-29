# from base import db_client
from app.db.clickhouse import execute_query, execute_command, insert_data, insert_skill_list_data, insert_education_list_data, insert_experience_list_data, insert_projects_list_data
from datetime import datetime, date
from app.db.clickhouse import get_table_columns
from app.utils.helpers import calculate_age, group_candidate_data

TABLES = ['candidate', 'skills', 'education', 'experience', 'projects']

class CandidateDAO():
    def get_id(self, col_name, table_name):
        result = execute_command(f"SELECT coalesce(MAX({col_name}), 0)+1 FROM {table_name}")
        # id = result.result_rows[0][0]
        return result
    
    def get_all_candidate(self):
        # query = 'SELECT * from candidate'
        results = execute_query("SELECT candidate_id, candidate_name, email_address, mobile_number FROM candidate")
        return results
    from clickhouse_connect import get_client

    def get_candidate_details(self, candidate_id: int):
        
        view_queries = {

            'candidate_query' : (f"""
                select  
                c.candidate_name,
                c.email_address,
                c.mobile_number,
                c.current_designation,
                c.current_employer,
                c.notice_period_days,
                c.expected_ctc,
                c.current_city,
                c.professional_summary,
                ROUND(CAST(c.total_experience AS DECIMAL(16,1)), 1) AS total_experience,
                c.sector
                from candidate c
                where c.candidate_id = {candidate_id}
                order by c.candidate_id
            """),

            'skills_query' : ( f"""
            select  
                s.skill,
                s.category
                from skills s
                where s.candidate_id = {candidate_id}
                order by s.category
             """),
                
            'education_query' : (f"""
                select  
            e.degree,
            e.institution,
            e.start_date,
            e.end_date
            from education e
            where e.candidate_id = {candidate_id}

            """),
            'experience_query' : (f"""
                select 
            ex.company,
            ex.title,
            ex.description,
            ex.start_date,
            ex.end_date
            from experience ex
            where ex.candidate_id = {candidate_id}
            """),
            'projects_query' : (f"""
                select 
                p.title,
                p.description,
                p.github_link,
                p.start_date,
                p.end_date
                from projects p
                where candidate_id = {candidate_id}
                """)
        }

        result = []
        for table_qry in view_queries.values():
            result.append(execute_query(table_qry))
        print('query fetched result are |||||||||||||||||||||dsfgggggggggggggggggg', result)
        # for table in TABLES:
        #     result.append(execute_query(f'{table}_query'))
        # print('result from join query &&&&&&&&&&&&&&&&&&&&', result)

        # return group_candidate_data(result)
        return result

    def insert_candidate_data(self, candidate_id, candidate, filepath):
        print('Inserting candidate')
        # sql = "INSERT INTO candidate (id, name, email, phone) VALUES"

        now = datetime.now()

        dob_str = candidate.get('date_of_birth')
        if dob_str:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            age = calculate_age(dob)
        else:
            dob = None
            age = None

        base_data = {
            'candidate_id': candidate_id,
            'age': age,
            'parent_id': 0,
            'date_of_birth': dob,
            'created_date': now,
            'created_by': 1,
            'updated_date': now,
            'updated_by': 1,
            'file_path': filepath
        }
        columns = get_table_columns('candidate')
        print("qqqqqqqqqqqqqqqqqqqqqq", candidate, type(columns))
        candidate_basic_data = {}
        for col in columns:
            # print(col)
            if col in candidate:
                candidate_basic_data.update({col: candidate[col]}) 

        candidate_data = {**candidate_basic_data, **base_data}
        print(candidate_data)

        # for row in candidate_data:
        # for key in ['created_date', 'updated_date']:
        #     if isinstance(candidate_data.get(key), datetime):
        #         candidate_data[key] = candidate_data[key].strftime('%Y-%m-%d %H:%M:%S')
        # print("&97777777777)_0000000000000000000000000",candidate_data)
        # db_client.execute(sql, data)

        insert_data('candidate', [candidate_data])


        # print(candidate)
    
    def insert_skills(self, candidate_id, skills):
        print('Inserting skills')
        # skills = skills or []
        # sql = "INSERT INTO skills (candidate_id, skill) VALUES"
        # data = [(candidate_id, skill) for skill in skills if skill]
        # if data:
        #     db_client.execute(sql, data)
        print(skills)

        columns = get_table_columns('skills')
        print(columns)


        candidate_skills_data = {}
        for col in columns:
            # print(col)
            if col not in ['candidate_id', 'skill_id']:
                candidate_skills_data[col] = skills
        
        candidate_skills_data['skill'] = skills

        candidate_skills_data['candidate_id'] = candidate_id


        candidate_skills_data['skill_id'] = self.get_id('skill_id', 'skills')

        for skill in skills:
            if skill:
                pass
        # print(candidate_skills_data)
        insert_skill_list_data('skills', [candidate_skills_data])
        
    def insert_education(self, candidate_id, education_list):
        print('Inserting education')
        columns = get_table_columns('education')

        candidate_education_data = {}
        for col in columns:
            # print(col)
            if col not in ['candidate_id', 'education_id']:
                candidate_education_data[col] = education_list
        
        # candidate_education_data['skill'] = skills

        candidate_education_data['candidate_id'] = candidate_id


        candidate_education_data['education_id'] = self.get_id('education_id', 'education')

        insert_education_list_data('education', [candidate_education_data])
    
    
    def insert_experience(self, candidate_id, experience_list):
        print('Inserting experience')
        columns = get_table_columns('experience')
        
        candidate_experience_data = {}
        for col in columns:
            # print(col)
            if col not in ['candidate_id', 'experience_id']:
                candidate_experience_data[col] = experience_list
        
        # candidate_education_data['skill'] = skills

        candidate_experience_data['candidate_id'] = candidate_id


        candidate_experience_data['experience_id'] = self.get_id('experience_id', 'experience')

        insert_experience_list_data('experience', [candidate_experience_data])

    def insert_projects(self, candidate_id, project_list):
        print('Inserting projects')
        columns = get_table_columns('projects')
        
        candidate_project_data = {}
        for col in columns:
            # print(col)
            if col not in ['candidate_id', 'project_id']:
                candidate_project_data[col] = project_list
        
        # candidate_education_data['skill'] = skills

        candidate_project_data['candidate_id'] = candidate_id


        candidate_project_data['project_id'] = self.get_id('project_id', 'projects')

        insert_projects_list_data('projects', [candidate_project_data])