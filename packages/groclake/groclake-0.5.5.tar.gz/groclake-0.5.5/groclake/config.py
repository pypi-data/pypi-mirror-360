import os

#from dotenv import load_dotenv

#load_dotenv(dotenv_path="./.env")

BASE_URL = 'https://api.groclake.ai'
AGENT_BASE_URL = 'https://api-uat-cartesian.groclake.ai/agache/agent'
GUPSHUP_URL = 'http://enterprise.smsgupshup.com/GatewayAPI/rest'

class GrocConfig:
    RESOURCE_MYSQL_CONFIG = {
        'user': os.getenv('RESOURCE_MYSQL_USER', 'root'),
        'password': os.getenv('RESOURCE_MYSQL_PASSWORD', 'root'),
        'host': os.getenv('RESOURCE_MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('RESOURCE_MYSQL_PORT', 3306)),
        'database': os.getenv('RESOURCE_MYSQL_DATABASE', 'groclake'),
        'charset': 'utf8'
    }

    RESOURCE_REDIS_CONFIG = {
        'host': os.getenv('RESOURCE_REDIS_HOST', 'localhost'),
        'port': int(os.getenv('RESOURCE_REDIS_PORT', 6379)),
        'password': '',
        'db': ''
    }

    SEC_CONFIG = {
        'resource_encr_key': os.getenv('RESOURCE_ENCR_KEY', 'groclake'),
        'attp_api_token': os.getenv('ATTP_API_TOKEN', 'groclake')
    }

    RESOURCE_CONFIG = {
        'resource_agent_apc_id': os.getenv('RESOURCE_AGENT_APC_ID', 'mid-office-apc-001'),
        'resource_agent_base_url': os.getenv('RESOURCE_AGENT_BASE_URL', 'https://aiops-demo-api.groclake.ai'),
        'resource_agent_uname': os.getenv('RESOURCE_AGENT_UNAME', 'groclake_resource_manager')
    }
