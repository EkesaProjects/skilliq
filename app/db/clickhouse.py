from clickhouse_driver import Client
from app.core.config import settings
import clickhouse_connect

# client = Client(
#     host=settings.DB_HOST,
#     user=settings.DB_USER,
#     password=settings.DB_PASSWORD,
#     database=settings.DB_NAME,
#     port=9000,  # default TCP port
# )

def get_id(col_name, table_name):
        result = execute_command(f"SELECT coalesce(MAX({col_name}), 0)+1 FROM {table_name}")
        # id = result.result_rows[0][0]
        return result

client = clickhouse_connect.get_client(host=settings.DB_HOST, username=settings.DB_USER, password=settings.DB_PASSWORD, database=settings.DB_NAME)
def get_table_columns(table: str) -> list[str]:
    """Fetch column names from ClickHouse system.columns table."""
    query = f"""
        SELECT name
        FROM system.columns
        WHERE table = '{table}' AND database = '{settings.DB_NAME}'
        ORDER BY position
    """
    # print(table, type(table), query)
    # result = execute_command(query)
    result = client.command(query)
    # return [row[0] for row in result]
    return result.split()


def execute_command(query: str, params: dict = None):
    return client.command(query)
    # return client.query(query).result_rows
    # return client.execute(query, params)

def execute_query(query: str, params: dict = None):
    return client.query(query).result_rows
    # return client.execute(query, params)

def insert_data(table: str, data: list[dict]):
    try:
        if not data:
            return

        print("this data i am getting from insert dao|||||||||||||||||",data)
        columns = get_table_columns(table)
        # # values = [
        # #     [row.get(col, None) for col in columns]
        # #     for row in data
        # # ]
        # # print(';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;',columns)
        # # values = [tuple(row.get(col) for col in columns) for row in data]
        # # values = [data.get(col, None) for col in columns]
        # # print(data.values())
        # # for col in columns:
        # #     print(data.get(col, None))

        # columns =  ", ".join(columns)
        # # values = ", ".join(["%s"] * len(data))
        # # print(values)
        # # flat_values = [val for row in values for val in row]

        # query = f"INSERT INTO {table} ({columns}) VALUES"
        # print("this is your sql qury===========================", query, data)
        # client.execute(query, data)
        data = [[item.get(col, None) for col in columns] for item in data]
        # data = list(data.values())


        client.insert(table, data ,columns)
        
    except Exception as e:
        print("Error occured ", e)

def insert_skill_list_data(table: str, data: list[dict]):
    try:
        if not data:
            return
        print("this data i am getting from insert dao|||||||||||||||||",data)
        columns = get_table_columns(table)
        expanded_data = []
        current_skill_id = get_id('skill_id', 'skills')

        for row in data:
            skills = row.get('skill', [])
            for skill in skills:
                print(get_id('skill_id', 'skills'))
                entry = {
                    'skill': skill['skill'],
                    'category': skill['category'],
                    'candidate_id': row.get('candidate_id'),
                    'skill_id': current_skill_id
                }
                current_skill_id += 1 
                expanded_data.append(entry)

        # Reorder data per columns
        formatted_data = [[item.get(col, None) for col in columns] for item in expanded_data]

        print("Formatted data to be inserted:", formatted_data)
        print("Columns:", columns)

        client.insert(table, formatted_data, columns)
    except Exception as e:
        print("Error occured ", e)

def insert_education_list_data(table: str, data: list[dict]):
    try:
        if not data:
            return
        print("this data i am getting from insert dao|||||||||||||||||",data)
        columns = get_table_columns(table)
        expanded_data = []
        current_education_id = get_id('education_id', table)


        for row in data:
            candidate_id = row.get('candidate_id')
            degrees = row.get('degree', [])  # This is a list of degree dictionaries

            for degree_entry in degrees:
                entry = {
                    'education_id': current_education_id,
                    'candidate_id': candidate_id,
                    'degree': degree_entry.get('degree'),
                    'institution': degree_entry.get('institution'),
                    'start_date': degree_entry.get('start_date'),
                    'end_date': degree_entry.get('end_date'),
                    'cgpa': degree_entry.get('cgpa'),
                    'percentage': degree_entry.get('percentage')
                }
                current_education_id += 1
                expanded_data.append(entry)

        # Reorder data per columns
        formatted_data = [[item.get(col, None) for col in columns] for item in expanded_data]

        print("Formatted data to be inserted:", formatted_data)
        print("Columns:", columns)

        client.insert(table, formatted_data, columns)
    except Exception as e:
        print("Error occured ", e)

def insert_experience_list_data(table: str, data: list[dict]):
    try:
        if not data:
            return

        print("This is the data I am getting from insert DAO:", data)
        columns = get_table_columns(table)
        expanded_data = []

        current_experience_id = get_id('experience_id', table)

        for row in data:
            candidate_id = row.get('candidate_id')
            experiences = row.get('title', [])  # this is the correct key
            # expirence - description
            # candidate - professional_summary
            # candidate - file_path
            for exp_entry in experiences:
                entry = {
                    'experience_id': current_experience_id,
                    'candidate_id': candidate_id,
                    'title': exp_entry.get('title'),
                    'company': exp_entry.get('company'),
                    'description': exp_entry.get('description'),
                    'start_date': exp_entry.get('start_date'),
                    'end_date': exp_entry.get('end_date')
                }
                current_experience_id += 1
                expanded_data.append(entry)

        formatted_data = [[item.get(col, None) for col in columns] for item in expanded_data]

        print("Formatted data to be inserted:", formatted_data)
        print("Columns:", columns)

        client.insert(table, formatted_data, columns)

    except Exception as e:
        print("Error occurred:", e)

def insert_projects_list_data(table: str, data: list[dict]):
    try:
        if not data:
            return

        print("This is the data I am getting from insert DAO:", data)
        columns = get_table_columns(table)
        expanded_data = []

        current_project_id = get_id('project_id', table)

        for row in data:
            candidate_id = row.get('candidate_id')
            projects = row.get('title', [])  # assuming all project data is under 'title' key

            for project_entry in projects:
                entry = {
                    'project_id': current_project_id,
                    'candidate_id': candidate_id,
                    'title': project_entry.get('title'),
                    'description': project_entry.get('description'),
                    'github_link': project_entry.get('github_link'),
                    'start_date': project_entry.get('start_date'),
                    'end_date': project_entry.get('end_date')
                }
                current_project_id += 1
                expanded_data.append(entry)

        formatted_data = [[item.get(col, None) for col in columns] for item in expanded_data]

        print("Formatted data to be inserted:", formatted_data)
        print("Columns:", columns)

        client.insert(table, formatted_data, columns)

    except Exception as e:
        print("Error occurred:", e)