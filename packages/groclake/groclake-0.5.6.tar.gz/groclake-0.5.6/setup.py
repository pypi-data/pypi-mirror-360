from setuptools import setup, find_packages

setup(
    name='groclake',  # Name of the package
    version='0.5.6',
    packages=find_packages(),
    namespace_packages=['groclake'],  # Declare the namespace
    install_requires=[
        'requests',  # For HTTP requests
        'mysql-connector-python',  # For MySQL connection
        'redis',  # For Redis connection
        'elasticsearch>=8.11.0,<9.0.0',  # For Elasticsearch connection
        'google-cloud-storage',  # For GCP Storage interaction
        'Pillow',  # For image processing (PIL)
        'boto3',  # For AWS S3 interaction
        'pymongo',  # For MongoDB connection
        'PyPDF2', # For PDF file reading
        'markdownify', # For Markdown conversion
        'python-docx', # For Word file reading
        'google-genai', # For Google Generative AI connection
        'openai', # For OpenAI connection
        'anthropic', # For Anthropic connection
        'google-generativeai', # For Google Generative AI connection
        'groq', # For Groq connection
        'pytz', # For timezone handling
        'python-dotenv', # For environment variables
        'notion-client', # For Notion connection
        'pypdf', # For PDF file reading
        'snowflake-connector-python', # For Snowflake connection
        'slack-sdk', # For Slack connection
        'jira', # For Jira connection
        'simple-salesforce', # For Salesforce connection
        'neo4j', # For Neo4j connection
        'python-magic', # For file type detection
        'python-pptx', # For PowerPoint file reading
        'python-docx', # For Word file reading
        'pymupdf', # For PDF file reading
        'reportlab', # For PDF file reading
        'xlrd',# For Excel file reading
        'tableauhyperapi',
        'pandas',
        'requests-toolbelt',
        'google-auth-oauthlib',
        'google-api-python-client',
        'google-auth',
        'google-cloud-compute',
        'google-cloud-redis',
        'google-cloud-storage',
        'google-api-python-client',
        'tiktoken',
        'hubspot-api-client',
        'scikit-learn',
        'xgboost',
        'matplotlib',
        'numpy',
        'scikit-learn',
        'schedule',
        'subprocess',
        'croniter',
        'datetime',
        'uuid',
        'time',
    ],
)
