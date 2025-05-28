import os
from dotenv import load_dotenv
from clickhouse_driver import Client

# load_dotenv()

# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# CLICKHOUSE_HOST = os.getenv('DB_HOST')
# CLICKHOUSE_USER = os.getenv('DB_USER')
# CLICKHOUSE_PASSWORD = os.getenv('DB_PASSWORD')
# CLICKHOUSE_DATABASE = os.getenv('DB_NAME')

# # MySQL Database Configuration

# # app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:root@localhost:3306/e_commerce_project?charset=utf8'
# # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db_client = Client(host=CLICKHOUSE_HOST, user=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD, database=CLICKHOUSE_DATABASE)
