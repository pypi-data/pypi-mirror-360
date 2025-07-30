from tableauhyperapi import HyperProcess, Connection, TableDefinition, SqlType, TableName, Telemetry, CreateMode
import pandas as pd
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os
from typing import Dict, Any


class Tableau:
    def __init__(self, tool_config: Dict[str, Any]):

        # Load configuration from environment variables
        self.server_url = tool_config.get('server_url')
        self.username = tool_config.get('username')
        self.password = tool_config.get('password')
        self.site_content_url = tool_config.get('site_content_url')
        self.site_id = tool_config.get('site_id')
        self.project_id = tool_config.get('project_id')
        self.api_version = tool_config.get('api_version', '3.6')

        # Initialize token
        self.token = None

        # Validate required environment variables
        self._validate_credentials()

        # Authenticate and get token
        self._authenticate()

    def _validate_credentials(self):
        """
        Validate that all required credentials are present
        """
        required_vars = [
            'server_url',
            'username',
            'password',
            'site_content_url',
            'site_id',
            'project_id'
        ]

        missing_vars = [var for var in required_vars if not getattr(self, var)]

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def _authenticate(self):
        """
        Authenticate with Tableau Server and get token
        """
        signin_url = f"{self.server_url}/api/{self.api_version}/auth/signin"

        xml_payload = f"""<tsRequest>
            <credentials name="{self.username}" password="{self.password}">
                <site contentUrl="{self.site_content_url}"/>
            </credentials>
        </tsRequest>"""

        headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/json'
        }

        try:


            response = requests.post(signin_url, data=xml_payload, headers=headers)

            # Print response details for debugging


            response.raise_for_status()

            # Parse the JSON response
            response_data = response.json()

            # Extract token from the response JSON
            if 'credentials' in response_data and 'token' in response_data['credentials']:
                self.token = response_data['credentials']['token']
                print("Successfully authenticated with Tableau Server")
            else:
                raise ValueError("Token not found in response data")

        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise
        except ValueError as e:
            print(f"Authentication failed: {str(e)}")
            raise



    def signout(self):
        """
        Sign out from Tableau Server
        """
        if not self.token:
            print("No active session to sign out from")
            return

        signout_url = f"{self.server_url}/api/{self.api_version}/auth/signout"
        headers = {'X-Tableau-Auth': self.token}

        try:
            response = requests.post(signout_url, headers=headers)
            response.raise_for_status()
            print("Successfully signed out from Tableau Server")
            self.token = None

        except requests.exceptions.RequestException as e:
            print(f"Sign out failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise

    def create_hyper_file(self, csv_path, output_path):

        # Read the CSV file
        df = pd.read_csv(csv_path)

        # Define the table structure based on CSV columns
        columns = []
        for col_name, dtype in df.dtypes.items():
            if dtype == 'int64':
                sql_type = SqlType.int()
            elif dtype == 'float64':
                sql_type = SqlType.double()
            else:
                sql_type = SqlType.text()
            columns.append(TableDefinition.Column(col_name, sql_type))

        table_definition = TableDefinition(
            table_name=TableName("Extract", "Data"),
            columns=columns
        )

        # Create the Hyper file
        with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(hyper.endpoint, output_path, CreateMode.CREATE_AND_REPLACE) as connection:
                # Create the schema and table
                connection.catalog.create_schema("Extract")
                connection.catalog.create_table(table_definition)

                # Insert the data row by row
                for _, row in df.iterrows():
                    values = []
                    for val in row:
                        if pd.isna(val):
                            values.append('NULL')
                        elif isinstance(val, str):
                            values.append(f"'{val}'")
                        else:
                            values.append(str(val))

                    insert_query = f"INSERT INTO {table_definition.table_name} VALUES ({', '.join(values)})"
                    connection.execute_command(insert_query)

                print(f"Successfully created Hyper file at {output_path} with {len(df)} records")

    def publish_datasource(self, filepath, datasource_name):
        """
        Publish datasource to Tableau Server
        """
        if not self.token:
            raise ValueError("Not authenticated. Token is missing.")

        publish_url = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/datasources"

        xml_payload = f"""<tsRequest>
            <datasource name="{datasource_name}">
                <project id="{self.project_id}"/>
            </datasource>
        </tsRequest>"""

        with open(filepath, 'rb') as f:
            multipart_data = MultipartEncoder(
                fields={
                    'request_payload': ('request.xml', xml_payload, 'text/xml'),
                    'tableau_datasource': (
                        os.path.basename(filepath),
                        f.read(),
                        'application/octet-stream'
                    )
                }
            )

            content_type = multipart_data.content_type.replace(
                'multipart/form-data',
                'multipart/mixed'
            )

            headers = {
                'X-Tableau-Auth': self.token,
                'Content-Type': content_type,
                'Accept': 'application/json'
            }

            try:
                response = requests.post(
                    publish_url,
                    data=multipart_data,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                print(f"Publishing failed: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response content: {e.response.text}")
                raise

    def fetch_datasource(self, datasource_id, output_file_path=None):

        if not self.token:
            raise ValueError("Not authenticated. Token is missing.")

        fetch_url = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/datasources/{datasource_id}/content"

        headers = {
            'X-Tableau-Auth': self.token,
            'Accept': 'application/json'
        }

        try:
            print(f"Fetching datasource content for ID: {datasource_id}")
            response = requests.get(fetch_url, headers=headers)
            response.raise_for_status()

            # If output file path is provided, save to disk
            if output_file_path:
                with open(output_file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Successfully downloaded datasource to: {output_file_path}")
                return output_file_path
            else:
                print(f"Successfully fetched datasource content ({len(response.content)} bytes)")
                return response.content

        except requests.exceptions.RequestException as e:
            print(f"Fetch datasource failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            raise

    def list_datasources(self):

        if not self.token:
            raise ValueError("Not authenticated. Token is missing.")

        list_url = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/datasources"

        headers = {
            'X-Tableau-Auth': self.token,
            'Accept': 'application/json'
        }

        try:
            response = requests.get(list_url, headers=headers)
            response.raise_for_status()

            datasources_data = response.json()
            print("Available datasources:")

            if 'datasources' in datasources_data and 'datasource' in datasources_data['datasources']:
                for ds in datasources_data['datasources']['datasource']:
                    print(f"  - Name: {ds.get('name', 'N/A')}, ID: {ds.get('id', 'N/A')}")

            return datasources_data

        except requests.exceptions.RequestException as e:
            print(f"List datasources failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise
