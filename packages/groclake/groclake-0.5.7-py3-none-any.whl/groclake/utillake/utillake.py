
from flask import Flask, request, jsonify, Response
from ..config import BASE_URL, AGENT_BASE_URL
import os
from dotenv import load_dotenv
load_dotenv()
from groclake.modellake import Modellake
from groclake.memorylake import Memorylake
import requests
import uuid
import traceback
from typing import List, Dict, Callable, Union
from groclake.toollake.db import MysqlDB
from groclake.toollake.apm import NewRelic
from groclake.toollake.db import Elastic
from groclake.toollake.cloudstorage import AWSS3
from groclake.toollake.db import ESVector
from groclake.toollake.comm import Slack
from groclake.toollake.db import MongoVector
from groclake.toollake.db import MongoDB
from groclake.toollake.devops import GCP
from groclake.toollake.db import Neo4jDB
from groclake.toollake.db import SnowflakeDB
from groclake.toollake.itops import ServiceNow
from groclake.toollake.db import Redis
from groclake.toollake.grocmock import Grocmock
from groclake.toollake.code import GitHub
from groclake.toollake.comm import AWSSes
from cryptography.fernet import Fernet
from groclake.config import GrocConfig

from queue import Queue, Empty
import json
import time
from datetime import datetime, date
session_url = os.getenv("session_url", "https://api-uat-cartesian.groclake.ai/agache/agent/1169cc54-ef61-4f67-9813-91cc93bf0da5/query")

class GrocAgent:

    def __init__(self, app, agent_name, initial_intent=None, intent_description=None, intent_handler=None, adaptor_config=None):
        """
        Initializes the GrocAgent with a name and optionally registers an initial intent.

        Args:
            agent_name (str): The name of the agent.
            initial_intent (str, optional): The initial intent to register.
            intent_description (str, optional): Description of the initial intent.
        """
        self._intent = []
        self._intent_handlers = {}
        self._app = app
        self.uname = agent_name
        self.log_level = 'NO_LOG'
        self.debug_mode = False
        self.mysql_connection = None
        self.attp_api_token = None

        # Initialize Fernet key
        self.fernet = Fernet(GrocConfig.SEC_CONFIG['resource_encr_key'].encode('utf-8'))

        if adaptor_config is not None and adaptor_config.get('log_level'):
            self.log_level = adaptor_config['log_level']
        
        if adaptor_config is not None and adaptor_config.get('debug_mode'):
            self.debug_mode = adaptor_config['debug_mode']

        self.attp_api_token = adaptor_config['attp_api_token'] if adaptor_config['attp_api_token'] else None

        #get resource agent base url, uname and uuid from adaptor_config
        self.resource_agent_apc_id = adaptor_config.get('resource_agent_apc_id') if adaptor_config.get('resource_agent_apc_id') else None
        self.resource_agent_base_url = adaptor_config.get('resource_agent_base_url') if adaptor_config.get('resource_agent_base_url') else None
        self.resource_agent_uname = adaptor_config.get('resource_agent_uname') if adaptor_config.get('resource_agent_uname') else None
        self.resource_agent_uuid = adaptor_config.get('resource_agent_uuid') if adaptor_config.get('resource_agent_uuid') else None
        
        #get agent base url from adaptor_config if provided
        self.agent_base_url = adaptor_config.get('agent_base_url') if adaptor_config.get('agent_base_url') else self.resource_agent_base_url 

        # Fetch agent_uuid from adaptor_config if provided
        self.agent_uuid = adaptor_config.get('agent_uuid') if adaptor_config.get('agent_uuid') else self.uname
        
        # Set client_agent_uuid in adaptor_config if not already set
        if adaptor_config is not None and self.agent_uuid:
            adaptor_config['agent_uuid'] = self.agent_uuid

        # Set client_agent_uuid in adaptor_config if not already set
        if adaptor_config is not None and self.agent_base_url:
            adaptor_config['agent_base_url'] = self.agent_base_url

        # Set client_agent_uuid in adaptor_config if not already set
        if adaptor_config is not None and self.resource_agent_apc_id:
            adaptor_config['apc_id'] = self.resource_agent_apc_id

        if adaptor_config is not None and self.agent_uuid:
            adaptor_config['client_agent_uuid'] = self.agent_uuid

        if adaptor_config is not None and adaptor_config.get('uname'):
            self.uname = adaptor_config['uname']

        if adaptor_config is not None and self.agent_uuid:
            if not adaptor_config.get('uname'):
                adaptor_config['uname'] = agent_name

        self._intent = ["groclake_fetch_agent_memory"]  # List of registered intents
        self._intent_handlers = {
            "groclake_fetch_agent_memory": self.groclake_fetch_agent_memory
        }
        
        if initial_intent:
            self._intent_handlers[initial_intent] = intent_handler

        # Add the adaptor configuration handling
        _handler = self.intentOrchestrator

        # Setup adaptor for the agent (needed here for resource fetch which is an agent call)
        self.adaptor = AttpAdaptor(app, _handler, adaptor_config)

        if initial_intent and intent_description:
            self.registerIntent(initial_intent, intent_description)
        
        #fetch resources from resource manager if this is not a resource manager agent
        if not self.uname == self.resource_agent_uname:
            # --- Fetch all resources once ---
            resource_config = {"resource_type": "all", "resource_name": "", "resource_agent_uname": self.resource_agent_uname}
            
            try:
                if self.uname and self.resource_agent_uname:
                    entities = self.resource_fetch(self.uname, resource_config)
                    mysql_tool_config = None
                    openai_tool_config = None
                    elastic_tool_config = None
                    newrelic_tool_config = None
                    esvector_tool_config = None
                    awss3_tool_config = None
                    slack_tool_config = None
                    mongovector_tool_config = None
                    mongodb_tool_config = None
                    redis_tool_config = None
                    gcp_tool_config = None
                    neo4j_tool_config = None
                    snowflake_tool_config = None
                    grocmock_tool_config = None
                    servicenow_tool_config = None
                    github_tool_config = None
                    awsses_tool_config = None
                    provisioned_lakes = []
                    self.redis = None
                    self.mysql_connection = None
                    self.elastic = None
                    self.newrelic = None
                    self.esvector = None
                    self.awss3 = None
                    self.slack = None
                    self.mongovector = None
                    self.mongodb = None
                    self.gcp = None
                    self.neo4j = None
                    self.snowflake = None
                    self.awsses = None
                    for entity in entities:
                        if entity.get("resource_type") == "tool":
                            if entity.get("resource_name") == "MysqlDB" and not mysql_tool_config:
                                mysql_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "OpenAI" and not openai_tool_config:
                                openai_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "Elastic" and not elastic_tool_config:
                                elastic_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "New Relic" and not newrelic_tool_config:
                                newrelic_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "ESVector" and not esvector_tool_config:
                                esvector_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "AWSS3" and not awss3_tool_config:
                                awss3_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "Slack" and not slack_tool_config:
                                slack_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "MongoVector" and not mongovector_tool_config:
                                mongovector_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "MongoDB" and not mongodb_tool_config:
                                mongodb_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "Redis" and not redis_tool_config:
                                redis_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "GCP" and not gcp_tool_config:
                                gcp_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "Neo4jDB" and not neo4j_tool_config:
                                neo4j_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "SnowflakeDB" and not snowflake_tool_config:
                                snowflake_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "Grocmock" and not grocmock_tool_config:
                                grocmock_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "ServiceNow" and not servicenow_tool_config:
                                servicenow_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "GitHub" and not github_tool_config:
                                github_tool_config = entity.get("resource_config")
                            elif entity.get("resource_name") == "AWSSes" and not awsses_tool_config:
                                awsses_tool_config = entity.get("resource_config")
                        if entity.get("resource_type") == "lake":
                            lake_resource_entity = {
                                "index_name": entity['resource_id'],
                                "lake_config": entity['resource_config'].get('lake_config', {}),
                                "lake_id": entity['resource_id']
                            }
                            provisioned_lakes.append(lake_resource_entity)
            except Exception as e:
                print(f"Failed to initialize resources from resource manager: {e}")

            # Initialize tool configurations
            self.mysql_tool_config = mysql_tool_config
            self.openai_tool_config = openai_tool_config
            self.elastic_tool_config = elastic_tool_config
            self.newrelic_tool_config = newrelic_tool_config
            self.esvector_tool_config = esvector_tool_config
            self.awss3_tool_config = awss3_tool_config
            self.slack_tool_config = slack_tool_config
            self.mongovector_tool_config = mongovector_tool_config
            self.mongodb_tool_config = mongodb_tool_config
            self.redis_tool_config = redis_tool_config
            self.gcp_tool_config = gcp_tool_config
            self.neo4j_tool_config = neo4j_tool_config
            self.snowflake_tool_config = snowflake_tool_config
            self.grocmock_tool_config = grocmock_tool_config
            self.servicenow_tool_config = servicenow_tool_config
            self.github_tool_config = github_tool_config
            self.awsses_tool_config = awsses_tool_config
            if mysql_tool_config:
                self.mysql_connection = MysqlDB(mysql_tool_config)
                adaptor_config['mysql_connection'] = self.mysql_connection
            if elastic_tool_config:
                self.elastic = Elastic(elastic_tool_config)
            if newrelic_tool_config:
                self.newrelic = NewRelic(newrelic_tool_config)
            if openai_tool_config:
                self.modellake = Modellake(openai_tool_config)
            if esvector_tool_config:
                self.esvector = ESVector(esvector_tool_config)
            if awss3_tool_config:
                self.awss3 = AWSS3(awss3_tool_config)
            if slack_tool_config:
                self.slack = Slack(slack_tool_config)
            if mongovector_tool_config:
                self.mongovector = MongoVector(mongovector_tool_config)
            if mongodb_tool_config:
                self.mongodb = MongoDB(mongodb_tool_config)
            if redis_tool_config:
                self.redis = Redis(redis_tool_config)
                redis_config = { "database_type": "redis", "connection": self.redis }
                self.memorylake = Memorylake(redis_config)
                adaptor_config['redis_connection'] = self.redis
            if gcp_tool_config:
                self.gcp = GCP(gcp_tool_config)
            if neo4j_tool_config:
                self.neo4j = Neo4jDB(neo4j_tool_config)
            if snowflake_tool_config:
                self.snowflake = SnowflakeDB(snowflake_tool_config)
            if grocmock_tool_config:
                self.grocmock = Grocmock(grocmock_tool_config)
            if servicenow_tool_config:
                self.servicenow = ServiceNow(servicenow_tool_config)
            if github_tool_config:
                self.github = GitHub(github_tool_config)
            if awsses_tool_config:
                self.awsses = AWSSes(awsses_tool_config)
            if provisioned_lakes:
                self.provisioned_lakes = provisioned_lakes

        else:
            self.mysql_connection = adaptor_config['mysql_connection'] if adaptor_config['mysql_connection'] else None
            self.redis = adaptor_config['redis_connection'] if adaptor_config['redis_connection'] else None
            if self.redis:
                redis_config = { "database_type": "redis", "connection": self.redis }
                self.memorylake = Memorylake(redis_config)
                adaptor_config['redis_connection'] = self.redis

        #fetch agent info from resource manager 
        agent_info = self.get_agent_info(self.uname)
        self.agent_uuid = agent_info['agent_uuid']
        self.apc_id = agent_info['apc_id']
        self.agent_base_url = agent_info['agent_base_url']
        adaptor_config['agent_uuid'] = self.agent_uuid
        adaptor_config['agent_base_url'] = self.agent_base_url
        adaptor_config['resource_agent_base_url'] = self.resource_agent_base_url
        adaptor_config['resource_agent_uname'] = self.resource_agent_uname
        adaptor_config['resource_agent_uuid'] = self.resource_agent_uuid
        adaptor_config['apc_id'] = self.apc_id
        adaptor_config['uname'] = self.uname
        adaptor_config['log_level'] = self.log_level
        adaptor_config['debug_mode'] = self.debug_mode
        adaptor_config['client_agent_uuid'] = self.agent_uuid

        #Call update_adaptor_config to update the adaptor config post resource fetch
        self.adaptor.update_adaptor_config(adaptor_config)
        
        #Set log event stream queue
        self.adaptor.set_log_event_stream_queue()

        # Fetch and set intent configurations
        self.intent_configs = self.get_self_intent_configs()
        self.register_intents(self.intent_configs)


    def encrypt_value(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        return self.fernet.decrypt(encrypted_value.encode()).decode()
    
    def fetch_sose_bucket_id(self, event_time):
        """
        Fetches the sose_id for a given event_time.
        """
        # Example datetime
        dt = datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S")

        # Truncate to start of the hour
        sose_bucket_id = dt.replace(minute=0, second=0, microsecond=0)

        return sose_bucket_id.strftime("%Y-%m-%d-%H:%M:%S")
    
    def convert_datetime_to_serializable(self, obj):
        """
        Recursively convert datetime objects in a data structure to JSON-serializable format.
        """
        if isinstance(obj, dict):
            return {key: self.convert_datetime_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_datetime_to_serializable(item) for item in obj]
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        else:
            return obj

    def fetch_intent_lake(self, intent_name):
        """
        Fetches the lake_id for a given intent name.
        """
        for intent in self.intent_configs:
            if intent['intent_name'] == intent_name:
                return intent['lake_id']
        return None
    
    def get_agent_info(self, uname):
        """
        Fetches agent information from the database.
        """
        query = """
            SELECT  agent_uuid, apc_id, agent_url FROM groclake_agent_registry
            WHERE uname = %s
        """
        results = self.mysql_connection.read(query, (uname,), multiple=False)
        return {
            "agent_uuid": results['agent_uuid'],
            "apc_id": results['apc_id'],
            "agent_base_url": results['agent_url']
        }

    def get_self_intent_configs(self):
        """
        Fetches intent configurations for this agent (self.agent_uuid).
        The handler for each intent is expected to be a method named {intent_name}_handler.
        """
        try:
            query = """
                SELECT intent_name, intent_description, intent_handler_name, lake_id
                FROM groclake_intent_registry
                WHERE status = 'active'
                  AND agent_uuid = %s
            """
            results = self.mysql_connection.read(query, (self.agent_uuid,), multiple=True)
            intent_configs = []
            for row in results:
                intent_name = row['intent_name']
                description = row['intent_description'] or f"Handler for {intent_name}"
                lake_id = row['lake_id']
                handler = getattr(self, f"{row['intent_handler_name']}", None)
                if handler is None:
                    # Optionally, log or warn if the handler does not exist
                    print(f"Warning: No handler found for intent '{intent_name}' (expected method '{intent_name}_handler')")
                intent_configs.append({
                    'intent_name': intent_name,
                    'description': description,
                    'handler': handler,
                    'lake_id': lake_id
                })
            return intent_configs
        except Exception as e:
            print(f"Error fetching self intent configurations: {str(e)}")
            return []
    
    def run(self, host="0.0.0.0", port=5000, debug=True):
        """
        Proxy method to run the Flask app.
        """

        self._app.run(host=host, port=port, debug=debug)

    def intentDetect(self, query_text, intent, entities, metadata):
        """
        Detects the intent based on the given query text and metadata.

        Args:
            query_text (str): The input text to analyze.
            intent (str): The detected intent.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            str: The detected intent.
        """
        # Simulated logic to detect intent (expand as needed)
        return intent

    def intentOrchestrator(self, attphandler_payload):
        """
        Handles the detected intent and provides a response.

        Args:
            query_text (str): The input text to analyze.
            intent (str): The detected intent.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.
            client_agent_uuid (str): The unique identifier for the client.
            message_id (str): The unique message identifier.
            task_id (str): The unique task identifier.

        Returns:
            dict: Response in a structured format.
        """
        intent = attphandler_payload.get("intent")
        entities = attphandler_payload.get("entities", [])
        metadata = attphandler_payload.get("metadata", {})
        query_text = attphandler_payload.get("query_text")
        client_agent_uuid = attphandler_payload.get("client_agent_uuid")
        message_id= attphandler_payload.get("message_id")
        task_id = attphandler_payload.get("task_id")

        if intent in self._intent_handlers:
            response = self._intent_handlers.get(intent)(attphandler_payload)
            response.update({
                "client_agent_uuid": client_agent_uuid,
                "message_id":message_id,
                "task_id": task_id
            })
            return response
        else:
            # Default response if intent is not recognized
            return {
                    "entities": entities,
                    "intent": intent,
                    "metadata": metadata,
                    "client_agent_uuid": client_agent_uuid,
                    "message_id":message_id,
                    "task_id": task_id,
                    "query_text": query_text,
                    "response_text": f"Intent '{intent}' not recognized.",
                    "status": 400
            }

    def registerIntent(self, intent, intent_description):
        """
        Registers a new intent with its description.

        Args:
            intent (str): The name of the intent to register.
            intent_description (str): A description of the intent.

        Returns:
            str: Error message if registration fails, otherwise None.
        """
        if intent in [i[0] for i in self._intent]:
            return f"Error: Intent '{intent}' is already registered."

        self._intent.append([intent, intent_description])
        return None

    def registerHandler(self, intent_name, handler_function):
        """
        Dynamically registers a handler function for a specific intent.

        Args:
            intent_name (str): The name of the intent.
            handler_function (callable): The handler function.

        Returns:
            str: Success message or error message if the intent is already registered.
        """
        #if intent_name in self._intent_handlers:
        #    return f"Error: Intent '{intent_name}' is already registered."

        self._intent_handlers[intent_name] = handler_function
        return f"Handler for intent '{intent_name}' successfully registered."

    def getName(self):
        """
        Returns the name of the agent.

        Returns:
            str: The name of the agent.
        """
        return self.uname

    def getIntent(self):
        """
        Returns the list of registered intents.

        Returns:
            list: The list of registered intents.
        """
        return self._intent

    def rewrite_query(self, agent_config):

        if not agent_config:
            return {"error": "Missing required parameter agent_config is required."}
        query_text = agent_config.get("query_text")
        agent_last_conversation = agent_config.get("agent_last_conversation")
        agent_name = agent_config.get("agent_name")
        agent_role = agent_config.get("agent_role")
        agent_description = agent_config.get("agent_description")
        context_attributes = agent_config.get('context_attributes', {})

        try:
            system_prompt = f"""
                            You are an AI-powered assistant named {agent_name}, {agent_description}.
                            Your primary role is to {agent_role} while maintaining conversational memory, ensuring seamless multi-turn interactions, knowledge retrieval, and intelligent responses.

                          ### **Guidelines for Query Rewriting**
                            1. **Context Awareness**: Always consider recent interactions to ensure smooth conversation flow.
                            2. **Enhancing Follow-ups**: If the new query builds on past messages, refine it by adding missing context.
                            3. **Handling Context Attributes**: If relevant attributes exist (e.g., order_id, product_name), incorporate them when refining the query.
                            4. **Independent Queries**: If the user’s new input is unrelated to previous discussions, return it as-is.
                            5. **Handling Incomplete Inputs**:  
                               - If the input appears **incomplete**, infer the missing details using past context.  
                               - Example:  
                                 - Previous: `"Cancel my order"`  
                                 - Current: `"53159959"`  
                                 - **Rewritten Query:** `"Cancel my order with Order ID 53159959."`  
                            6. **Avoiding Duplicates**: If the new query is a **repetition of a previous question**, rephrase it instead of returning the same text.
                            7. **Special Case Handling**:  
                               - **Greetings & Small Talk**: Return greetings/appreciation messages exactly as they are.  
                               - **Standalone Numeric Inputs**: If the query is just a number, assume it relates to the last relevant conversation and construct a meaningful query.  
                            8. **Strict Output Format**:  
                               - Return only the **rewritten query** in plain text.  
                               - **Do not** include labels, explanations, or metadata (e.g., `"Enhanced query:"`).  
                               - Ensure the output remains **natural and human-like**. 
                            9. **Analyze Past Conversations**:  
                               - When enhancing a query, review both **past user queries and system responses** to ensure consistency.  
                               - Example:  
                                 - **Past User Query:** `"Where is my order?"`  
                                 - **System Response:** `"Your order will be delivered by tomorrow."`  
                                 - **New Input:** `"Cancel it"`  
                                 - **Enhanced Query:** `"Cancel my order that is scheduled for delivery tomorrow."`  """

            user_prompt = f"""
                            ### previous Context to current user query:
                            - Conversation History (Last Two Interactions):
                                {agent_last_conversation} 
                            - Context attributes:
                                 {context_attributes}
                            - current User Query:
                                "{query_text}"

                            ### Output:
                             **The output should be a natural, standalone query without any formatting or extra annotations.**
                               [Enhanced query]
                            """
            response_payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }

            response = self.modellake.chat_complete(payload=response_payload)
            if isinstance(response, tuple):
                return response
            return response.get('answer', f"give your introduction with {agent_name} and {agent_description}")
        except Exception as e:
            return query_text

    def validate_session(self, payload):
        # Extract required fields
        query_text = payload.get('query_text', '')
        intent = payload.get('intent', '')
        entities = payload.get('entities', [])
        metadata = payload.get('metadata', {})
        client_agent_uuid = payload.get('client_agent_uuid', '')

        customer_id = metadata.get('customer_id', '')
        session_token = metadata.get('session_token', '')
        session_agent_uuid = metadata.get('session_agent_uuid', '')

        if not all([customer_id, session_agent_uuid, session_token]):
            metadata['valid_session'] = 0  # Ensure metadata always has valid_session
            return {
                "query_text": query_text,
                "response_text": "Missing required fields",
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }

        validation_payload = {
            "header": {
                "apc_id": "apc-9876",
                "client_agent_uuid": client_agent_uuid,
                "content-type": "application/json",
                "message": "request",
                "message_id": "msg-2025-01-13-001",
                "server_agent_uuid": "server_agent_manager_uuid",
                "task_id": "task-0001",
                "version": "1.0"
            },
            "body": {
                "query_text": "validate_session",
                "intent": "validate_session",
                "entities": [
                    {
                        "customer_id": customer_id,
                        "session_token": session_token,
                        "session_agent_uuid": session_agent_uuid
                    }
                ],
                "metadata": metadata
            }
        }

        endpoint = session_url

        try:
            response = requests.post(endpoint, json=validation_payload, timeout=5)
            response_data = response.json()
            # Check if response contains valid session info
            session_valid = any(entity.get('valid_session', 0) == 1 for entity in response_data.get('body', {}).get('entities', []))

            # Update metadata with session validation result
            metadata['valid_session'] = 1 if session_valid else 0

            return {
                "query_text": query_text,
                "response_text": "Session is valid" if session_valid else "Invalid session",
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }

        except Exception as e:
            metadata['valid_session'] = 0  # Ensure session is marked invalid on failure
            return {
                "query_text": query_text,
                "response_text": f"Error while connecting to validation service - {e}" ,
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }

    def validate_session_prod(self, payload):
        # Extract required fields
        query_text = payload.get('query_text', '')
        intent = payload.get('intent', '')
        entities = payload.get('entities', [])
        metadata = payload.get('metadata', {})
        client_agent_uuid = payload.get('client_agent_uuid', '')

        customer_id = metadata.get('customer_id', '')
        session_token = metadata.get('session_token', '')
        session_agent_uuid = metadata.get('session_agent_uuid', '')

        if not all([customer_id, session_agent_uuid, session_token]):
            metadata['valid_session'] = 0  # Ensure metadata always has valid_session
            return {
                "query_text": query_text,
                "response_text": "Missing required fields",
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }

        validation_payload = {
            "header": {
                "apc_id": "apc-9876",
                "client_agent_uuid": client_agent_uuid,
                "content-type": "application/json",
                "message": "request",
                "message_id": "msg-2025-01-13-001",
                "server_agent_uuid": "server_agent_manager_uuid",
                "task_id": "task-0001",
                "version": "1.0"
            },
            "body": {
                "query_text": "validate_session",
                "intent": "validate_session",
                "entities": [
                    {
                        "customer_id": customer_id,
                        "session_token": session_token,
                        "session_agent_uuid": session_agent_uuid
                    }
                ],
                "metadata": metadata
            }
        }

        endpoint = session_url

        try:
            response = requests.post(endpoint, json=validation_payload, timeout=5)
            response_data = response.json()
            # Check if response contains valid session info
            session_valid = any(entity.get('valid_session', 0) == 1 for entity in response_data.get('body', {}).get('entities', []))

            # Update metadata with session validation result
            metadata['valid_session'] = 1 if session_valid else 0

            return {
                "query_text": query_text,
                "response_text": "Session is valid" if session_valid else "Invalid session",
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }

        except requests.RequestException:
            metadata['valid_session'] = 0  # Ensure session is marked invalid on failure
            return {
                "query_text": query_text,
                "response_text": "Error while connecting to validation service",
                "intent": intent,
                "entities": entities,
                "metadata": metadata
            }


    def agentsmith_log(self, payload):
        # Extract required fields
        query_text_to_log = payload.get('query_text', '')
        response_text_to_log = payload.get('response_text', '')
        client_agent_uuid = payload.get('client_agent_uuid', '')
        server_agent_uuid = payload.get('server_agent_uuid', '')

        if not all([query_text_to_log, response_text_to_log, client_agent_uuid, server_agent_uuid]):
            return {
                "response_text": "Missing required fields",
            }

        validation_payload = {
            "body": {
                "query_text": "log this message",
                "intent": "log",
                "entities": [
                    {
                        "client_agent_uuid": client_agent_uuid,
                        "query_text": query_text_to_log,
                        "response_text": response_text_to_log,
                        "server_agent_uuid": server_agent_uuid
                    }
                ],
                "metadata": {
                    "additional_info": "Agent log message request",
                    "nums_offset": "nums_offset",
                    "nums_offset_item": "nums_offset_item"
                }
            },
            "header": {
                "apc_id": "apc-9876",
                "client_agent_uuid": "client_agent_uuid",
                "content-type": "application/json",
                "message": "request",
                "message_id": "msg-2025-01-13-001",
                "server_agent_uuid": "server_agent_uuid",
                "task_id": "task-0001",
                "version": "1.0"
            }
        }

        endpoint = "https://api-uat-cartesian.groclake.ai/agache/agent/e4b77981-4f7e-4d33-9e92-d84cbe0c05cb/query"

        try:
            response = requests.post(endpoint, json=validation_payload, timeout=5)
            response_data = response.json()

            response_text = response_data.get("body", {}).get("response_text", "No response_text in response")
            return {"response_text": response_text}

        except requests.RequestException:
            return {"response_text": "Error while connecting to validation service"}
        

    def groclake_fetch_agent_memory(self, memory_payload):
        """
        Fetch agent memory based on the provided payload.

        Args:
            memory_payload (dict): The payload containing memory retrieval parameters.

        Returns:
            Retrieved memory based on the payload filters.
        """

        try:
            # Extract required parameters from payload
            entities = memory_payload.get("entities", {})
            user_uuid = entities.get("user_uuid")
            memory_context = {
                "context_entity_id": entities.get("context_entity_id", "*"),
                "context_id": entities.get("context_id", "*"),
                "memory_type": entities.get("memory_type", "*"),
            }
            memory_type = entities.get("type", "short_memory")  # Default to short_memory
            n = entities.get("n", None)  # Number of messages to fetch

            # Validate required parameters
            if not user_uuid:
                return {
                    "query_text": memory_payload.get("query_text", ""),
                    "response_text": "Missing required parameter: user_uuid",
                    "intent": "fetch_agent_memory",
                    "entities": [],
                    "metadata": {},
                    "status": 400  # Bad Request
                }

            # Fetch memory using read_memory function
            response = self.memorylake.read_memory(user_uuid, memory_context, memory_type, n)

            # Extract only entities and metadata from the response
            entities_list = []
            metadata = {}

            if isinstance(response, list):
                for item in response:
                    if "entities" in item:
                        entities_list.extend(item["entities"])  # Collect all entities
                    if "metadata" in item:
                        metadata.update(item["metadata"])  # Merge metadata if available

            return {
                "query_text": memory_payload.get("query_text", ""),
                "response_text": "Memory fetched successfully",
                "intent": "fetch_agent_memory",
                "entities": entities_list,  # Return extracted entities
                "metadata": metadata,  # Return extracted metadata (if available)
                "status": 200
            }

        except Exception as e:
            return {
                "query_text": memory_payload.get("query_text", ""),
                "response_text": f"Error while fetching memory: {str(e)}",
                "intent": "fetch_agent_memory",
                "entities": [],
                "metadata": {},
                "status": 500  # Internal Server Error
            }

        
    def register_intents(self, intent_configs: List[Dict[str, Union[str, Callable]]]) -> None:
        """
        Register multiple intents with validation and error handling.
        
        Args:
            intent_configs: List of dictionaries containing intent configurations
                Each dict should have: intent_name, description, and handler
        
        Raises:
            ValueError: If intent configuration is invalid
        """
        for config in intent_configs:
            try:
                # Extract and validate required fields
                intent_name = config.get('intent_name')
                description = config.get('description')
                handler = config.get('handler')
                
                # Validate field types
                if not isinstance(intent_name, str):
                    raise ValueError(f"Intent name must be a string: {intent_name}")
                
                if not isinstance(description, str):
                    raise ValueError(f"Description must be a string: {description}")
                
                if not callable(handler):
                    raise ValueError(f"Handler must be callable: {handler}")
                
                # Check for duplicate intents
                #if hasattr(self, 'registered_intents') and intent_name in self.registered_intents:
                #    raise ValueError(f"Duplicate intent name: {intent_name}")
                
                # Register the intent and its handler
                self.registerIntent(intent_name, description)
                self.registerHandler(intent_name, handler)
                
                # Track registered intents
                if not hasattr(self, 'registered_intents'):
                    self.registered_intents = set()
                self.registered_intents.add(intent_name)
                
            except Exception as e:
                raise ValueError(f"Error registering intent configuration: {config}. Error: {str(e)}")

    def resource_fetch(self, uname, resource_config):
        """
        Fetch provisioned resources for the given agent_uuid using the Resource Manager agent.
        """
        payload = {
            "intent": "groclake_resource_request",
            "query_text": "Fetch my provisioned resources",
            "entities": [
                {
                    "uname": uname,
                    "resource_type": resource_config['resource_type'],
                    "resource_name": resource_config['resource_name']
                }
            ],
            "metadata": {}
        }
        response = self.adaptor.callAgent(resource_config['resource_agent_uname'], payload)
        entities = response.get("entities", [])
        #decrypt resource_config
        for entity in entities:
            if entity.get('resource_config'):
                entity['resource_config'] = self.decrypt_value(entity['resource_config'])
                if isinstance(entity['resource_config'], str):
                    entity['resource_config'] = json.loads(entity['resource_config'])
                #print(f"resource_config_decrypted: {entity['resource_config']}")
        return entities

    def get_error_trace(self):
        error_trace = ""
        if self.debug_mode:
            error_trace = traceback.format_exc() 
        return error_trace
    
    def log_event_stream(self, message, user_id=1):
        try:
            if self.debug_mode:
                if not user_id:
                    user_id = "1"
                if self.redis:
                    # Ensure message is properly formatted as JSON
                    event_data = {
                        "agent": self.uname,
                        "message": str(message)  # Ensure it's a string
                    }
                    # Serialize to JSON string before publishing
                    json_message = json.dumps(event_data)
                    self.redis.publish(f"sse_events:{user_id}", json_message)
        except Exception as e:
            print(f"Error in log_event_stream: {str(e)}")



class AttpAdaptor:
    def __init__(self, app, callback, adaptor_config):
        self.app = app
        self.callback = callback
        self.apc_id = adaptor_config.get('apc_id')
        self.client_agent_uuid = adaptor_config.get('client_agent_uuid')
        self.log_level = 'NO_LOG'
        self.debug_mode = False
        self.mysql_connection = None
        self.uname = adaptor_config.get('uname')
        self.agent_uuid = adaptor_config.get('agent_uuid')
        self.agent_base_url = adaptor_config.get('agent_base_url') if adaptor_config.get('agent_base_url') else None
        self.redis = None
        self.attp_api_token = adaptor_config.get('attp_api_token', None)

        if adaptor_config.get('mysql_connection'):
            self.mysql_connection = adaptor_config.get('mysql_connection')
        if adaptor_config.get('debug_mode'):
            self.debug_mode = adaptor_config.get('debug_mode')
        if adaptor_config.get('log_level'):
            self.log_level = adaptor_config.get('log_level')
        
        if adaptor_config.get('redis_connection'):
            self.redis = adaptor_config.get('redis_connection')

        self.app.add_url_rule('/query', 'query_handler', self.query_handler, methods=['POST'])
        self.app.add_url_rule('/readme', 'readme_handler', self.readme_handler, methods=['POST'])
        self.app.add_url_rule('/pinger', 'pinger_handler', self.pinger_handler, methods=['POST'])

    def update_adaptor_config(self, adaptor_config):
        """
        Updates the adaptor configuration.
        """
        if adaptor_config.get('mysql_connection'):
            self.mysql_connection = adaptor_config.get('mysql_connection')
        if adaptor_config.get('debug_mode'):
            self.debug_mode = adaptor_config.get('debug_mode')
        if adaptor_config.get('log_level'):
            self.log_level = adaptor_config.get('log_level')
        if adaptor_config.get('redis_connection'):
            self.redis = adaptor_config.get('redis_connection')
        if adaptor_config.get('resource_agent_base_url'):
            self.resource_agent_base_url = adaptor_config.get('resource_agent_base_url')
        if adaptor_config.get('resource_agent_uname'):
            self.resource_agent_uname = adaptor_config.get('resource_agent_uname')
        if adaptor_config.get('resource_agent_uuid'):
            self.resource_agent_uuid = adaptor_config.get('resource_agent_uuid')
        if adaptor_config.get('agent_base_url'):
            self.agent_base_url = adaptor_config.get('agent_base_url')
        if adaptor_config.get('agent_uuid'):
            self.agent_uuid = adaptor_config.get('agent_uuid')
        if adaptor_config.get('apc_id'):
            self.apc_id = adaptor_config.get('apc_id')
        if adaptor_config.get('client_agent_uuid'):
            self.client_agent_uuid = adaptor_config.get('client_agent_uuid')


    def set_log_event_stream_queue(self):
         #add event stream queue
        if self.debug_mode:
            self.app.add_url_rule('/log_event_stream', 'log_event_stream_handler', self.log_event_stream_handler, methods=['GET'])
            self.log_event_stream_queue = Queue(maxsize=100)
            if self.redis:
                user_id = "1"
                self.redis.subscribe(f"sse_events:{user_id}", self.log_event_stream_subscribe_handler)

    def extract_header(self, request_data):
        """
        Extracts the header from the request data.
        """
        header = request_data.get('header', {})
        return {
            'client_agent_uuid': header.get('client_agent_uuid'),
            'server_agent_uuid': header.get('server_agent_uuid'),
            'message_id': header.get('message_id'),
            'task_id': header.get('task_id'),
            'apc_id': header.get('apc_id'),
            'auth_token': header.get('auth_token') if header.get('auth_token') else "",
        }

    def extract_body(self, request_data):
        """
        Extracts the body from the request data.
        """
        body = request_data.get('body', {})
        return {
            'query_text': body.get('query_text'),
            'intent': body.get('intent'),
            'entities': body.get('entities'),
            'metadata': body.get('metadata'),
        }

    def create_header(self, auth_token, apc_id, server_agent_uuid, client_agent_uuid, message_id, task_id):
        """
        Creates the header part of the response payload.
        """
        return {
            "version": "1.0",
            "message": "response",
            "content-type": "application/json",
            "auth_token": auth_token,
            "apc_id": apc_id,
            "server_agent_uuid": server_agent_uuid,
            "client_agent_uuid": client_agent_uuid,
            "message_id": message_id,
            "task_id": task_id,
        }

    def create_body(self, response):
        """
        Creates the body part of the response payload.
        """
        return {
            "query_text": response.get("query_text", ""),
            "response_text": response.get("response_text", "Search completed successfully."),
            "intent": response.get("intent", ""),
            "entities": response.get("entities", []),
            "metadata": response.get("metadata", {}),
        }

    def get_readme_content(self, readme_payload):
        """
        Reads the content of a README file if it exists and constructs a response.
        """
        query_text = readme_payload.get("query_text", "")
        intent = readme_payload.get("intent", "")
        entities = readme_payload.get("entities", [])
        metadata = readme_payload.get("metadata", {})

        readme_file_path = os.path.join(os.getcwd(), '.readme')

        if os.path.exists(readme_file_path):
            with open(readme_file_path, 'r') as file:
                readme_content = file.read()
        else:
            readme_content = "README file not found."

        return {
            "query_text": query_text,
            "response_text": readme_content,
            "intent": intent,
            "entities": entities,
            "metadata": metadata,
        }


    def sendQuery(self, server_uuid, payload, task_id=None, base_url=None):
        """
        Send a query to a server agent.
        
        Args:
            server_uuid (str): UUID of the server agent
            payload (dict): The payload to send
            task_id (str, optional): Task ID for the request. If None, generates a UUID
            base_url (str, optional): Base URL for the request. If None, uses localhost
            
        Returns:
            dict: Response from the server or error message
        """
        try:
            # Set default base_url if not provided
            if self.agent_base_url:
                base_url = self.agent_base_url
            elif base_url is None:
                base_url = "http://localhost"
            
            # Remove trailing slash if present
            base_url = base_url.rstrip('/')
            
            # Construct the full URL
            url = f"{base_url}/agache/agent/{server_uuid}/query"
            
            # Generate task_id if not provided
            if task_id is None:
                task_id = str(uuid.uuid4())
            
            # Generate message_id
            message_id = str(uuid.uuid4())

            headers = {
                "content-type": "application/json"
            }

            body_payload = {
                "header": {
                    "version": "1.0",
                    "message": "Request",
                    "Content-Type": "application/json",
                    "apc_id": self.apc_id,
                    "server_agent_uuid": server_uuid,
                    "client_agent_uuid": self.client_agent_uuid,
                    "message_id": message_id,
                    "task_id": task_id
                },
                "body": {
                    "query_text": payload.get("query_text", ""),
                    "intent": payload.get("intent"),
                    "entities": payload.get("entities", []),
                    "metadata": payload.get("metadata", {})
                }
            }

            # Send the HTTP POST request
            response = requests.post(url, json=body_payload, headers=headers)
            response.raise_for_status()

            # Return the response from the server
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error in sendQuery: {str(e)}")
            return {
                "error": "Failed to send query",
                "details": str(e),
                "url": url  # Include the attempted URL in error response
            }

    def query_handler(self):
        try:
            request_data = request.get_json()
            if self.debug_mode:
                print(f"Received request data: {request_data}")
            
            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                body.get('query_text'),
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                print(f"Missing required fields in payload: {body.get('query_text')}, {header.get('client_agent_uuid')}, {header.get('server_agent_uuid')}")
                return jsonify({"error": "Missing required fields in payload"}), 400
            message_id= header.get('message_id')
            client_agent_uuid = header.get('client_agent_uuid')
            task_id = header.get('task_id')
            
            query_text = body.get('query_text')
            intent = body.get('intent')
            metadata = body.get('metadata')

            #check session_token in metadata
            session_token = metadata.get("session_token")
            customer_id = metadata.get("customer_id", None)
            user_id = metadata.get("user_id", customer_id)

            session_validation = True

            attp_api_token = metadata.get("attp_api_token", None)
            #attp_api_token_decrypted = self.decrypt_value(attp_api_token)
            attp_api_token_decrypted = attp_api_token

            if attp_api_token_decrypted is not None and attp_api_token_decrypted == self.attp_api_token:
                session_validation = False
                #reset attp_api_token
                metadata["attp_api_token"] = None

            #print(f"Intent: {intent}, session_token: {session_token}, user_id: {user_id}")
            if intent in ['groclake_session_create', 'groclake_resource_request', 'groclake_session_validate']:
                #print(f"Skipping session validation for intent: {intent}")
                session_validation = False

            if session_validation:
                if session_token:
                    #print(f"Session token provided: {session_token}")
                    #check if session_token is valid
                    #create a new session for the user by calling the groclake_session_manager using callAgent
                    session_entity = {
                        "session_token": session_token,
                        "user_id": user_id
                    }

                    session_payload = {
                        "query_text": query_text,
                        "intent": 'groclake_session_validate',
                        "entities": [session_entity],
                        "metadata": metadata
                    }

                    session_agent_response = self.callAgent("groclake_session_manager", session_payload, task_id)
                    metadata = session_agent_response.get('metadata', {})
                    response_text_agentcall = session_agent_response.get('response_text', '')
                
                    if not self.is_valid_response(metadata):
                        print(f"Invalid session token: {response_text_agentcall}")
                        return jsonify(f"Invalid session token: {response_text_agentcall}"), 400
                
                    session_response_entity = session_agent_response.get('entities', [])[0]
                    session_valid = session_response_entity.get('valid', False)
                    if not session_valid:
                        #print(f"Invalid session token: {response_text_agentcall}")
                        return jsonify(f"Invalid session token: {response_text_agentcall}"), 400
                else:
                    #print(f"No session token provided")
                    return jsonify(f"No session token provided"), 400

            if not metadata.get("task_context"):
                task_context = {
                    "task_id": task_id,
                    "query_text": query_text,
                    "intent": intent,
                    "uname": self.uname,
                    "agent_uuid": self.agent_uuid
                }
                metadata["task_context"] = task_context

            # Check if required header fields are present
            if not all([message_id, client_agent_uuid, task_id]):
                #print(f"Missing required fields in header for msgid,clientagentuuid,task_id fields: {message_id}, {client_agent_uuid}, {task_id}")
                return jsonify({"error": "Missing required fields in header for msgid,clientagentuuid,task_id fields"}), 400

            # Prepare payload for callback
            attphandler_payload = {
                "query_text": body.get('query_text'),
                "intent": body.get('intent'),
                "entities": body.get('entities'),
                "metadata": body.get('metadata'),
                "message_id": message_id,
                "client_agent_uuid": client_agent_uuid,
                "task_id": task_id
            }

            # Call the callback function
            try:
                response = self.callback(attphandler_payload)
                metadata = response.get("metadata", {})
            except Exception as e:
                return jsonify({"error": "Internal Server Error"}), 500

            intent_handler_status = metadata.get("intent_handler_status", "")
            agent_trace = {
                "agent_uuid": self.agent_uuid,
                "uname": self.uname,
                "query_text": query_text,
                "response_text": response.get("response_text", ""),
                "intent_handler_status": intent_handler_status,
                "intent": intent
            }

            if metadata.get("task_context"):
                if not metadata.get("task_context").get("agent_trace"):
                    metadata["task_context"]["agent_trace"] = [agent_trace]
                else:
                    metadata["task_context"]["agent_trace"].append(agent_trace)
            else:
                metadata["task_context"] = {"agent_trace": [agent_trace]}

            # Create header and body
            response_header = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            response_body = self.create_body(response)

            # log both request and response only if the intent handler status is success
            if intent_handler_status:
                if self.log_level == 'LOG_REQUEST_RESPONSE' and intent_handler_status == "success":
                    self.logIntentPayload(body.get("intent"), 'request', body)
                    self.logIntentPayload(body.get("intent"), 'response', response_body)

            # Create the response payload
            response_payload = {
                "header": response_header,
                "body": response_body
            }

            #self.find_none_keys(response_payload)

            return jsonify(response_payload), 200

        except Exception as e:
            return jsonify({"error": "Internal Server Error"}), 500

    def find_none_keys(self,obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                current_path = f"{path}['{k}']" if k is not None else f"{path}[None]"
                if k is None:
                    print(f"❌ Found None key at path: {path}")
                self.find_none_keys(v, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self.find_none_keys(item, f"{path}[{i}]")

    def readme_handler(self):
        try:
            request_data = request.get_json()

            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                body.get('query_text'),
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                return jsonify({"error": "Missing required fields in payload"}), 400

            readme_payload = {
                "query_text": body.get('query_text'),
                "intent": body.get('intent'),
                "entities": body.get('entities'),
                "metadata": body.get('metadata')
            }

            response = self.get_readme_content(readme_payload)

            # Create header and body
            header_part = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            body_part = self.create_body(response)

            # Create the response payload
            response_payload = {
                "header": header_part,
                "body": body_part
            }

            return jsonify(response_payload), 200

        except Exception as e:
            print(f"Error in readme_handler: {str(e)}")  # For debugging
            return jsonify({"error": "Internal Server Error"}), 500

    def pinger_handler(self):
        try:
            # Get JSON data from the request
            request_data = request.get_json()

            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                return jsonify({"error": "Missing required fields in payload"}), 400

            # Set the response text to "yes"
            response_text = "yes"

            # Create header and body for response
            header_part = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            body_part = self.create_body({
                "intent": body.get('intent', ''),
                "query_text": body.get('query_text', ''),
                "entities": body.get('entities', []),
                "metadata": body.get('metadata', {}),
                "response_text": response_text
            })

            # Create the response payload
            response_payload = {
                "header": header_part,
                "body": body_part
            }

            return jsonify(response_payload), 200

        except Exception as e:
            # Log the error and return a generic message
            print(f"Error in pinger_handler: {str(e)}")
            return jsonify({"error": "Internal Server Error"}), 500

    def callAgent(self, server_uuid, payload, task_id=None, base_url=None):
        """
        Send a query to a server agent and return only the body payload from the response.
        
        Args:
            server_uuid (str): UUID of the server agent
            payload (dict): The payload to send
            task_id (str, optional): Task ID for the request. If None, generates a UUID
            base_url (str, optional): Base URL for the request. If None, uses localhost
            
        Returns:
            dict: Body payload from the server response or empty dict on error
        """
        try:
            # Set default base_url if not provided
            if base_url is not None:
                base_url = base_url
            elif self.agent_base_url:
                base_url = self.agent_base_url
            elif base_url is None:
                base_url = "http://localhost"
            
            # Remove trailing slash if present
            base_url = base_url.rstrip('/')
            
            # Construct the full URL
            url = f"{base_url}/agache/agent/{server_uuid}/query"
            
            # Generate task_id if not provided
            if task_id is None or task_id == "":
                task_id = str(uuid.uuid4())
            
            # Generate message_id
            message_id = str(uuid.uuid4())

            headers = {
                "content-type": "application/json"
            }

            metadata = payload.get("metadata", {})
            metadata['attp_api_token'] = self.attp_api_token

            request_body_payload = {
                    "query_text": payload.get("query_text", ""),
                    "intent": payload.get("intent"),
                    "entities": payload.get("entities", []),
                    "metadata": metadata
            }

            request_header_payload = {
                    "version": "1.0",
                    "message": "Request",
                    "Content-Type": "application/json",
                    "apc_id": self.apc_id,
                    "server_agent_uname": server_uuid,
                    "server_agent_uuid": server_uuid,
                    "client_agent_uname": self.uname,
                    "client_agent_uuid": self.agent_uuid,
                    "message_id": message_id,
                    "task_id": task_id
            }

            request_full_payload = {
                "header": request_header_payload,
                "body": request_body_payload
            }          
            
            response = requests.post(url, json=request_full_payload, headers=headers)
            response.raise_for_status()

            # Return only the body part of the response
            return response.json().get("body", {})

        except requests.exceptions.RequestException as e:
            print(f"Error in callAgent: {str(e)}")
            return {
                "query_text": payload.get("query_text", ""),
                "response_text": f"Failed to send query: {str(e)}",
                "intent": payload.get("intent"),
                "entities": [],
                "metadata": {}
            }
        
    def is_valid_response(self, metadata):
        if metadata.get("intent_handler_status") == "success":
            return True
        else:
            return False
    
    def logIntentPayload(self, intent_name, type, payload):
        """
        Log request or response payload for an intent in the groclake_intent_registry table.
        Overwrites the existing schema with the new payload.
        
        Args:
            intent_name (str): Name of the intent
            type (str): Either 'request' or 'response'
            payload (dict): The payload to log
        """
        try:
            # Determine which schema field to update based on type
            schema_field = 'intent_handler_request_schema' if type == 'request' else 'intent_handler_response_schema'
            
            # Update the schema in database
            update_query = """
                UPDATE groclake_intent_registry
                SET {schema_field} = %s,
                    updated_at = NOW()
                WHERE intent_name = %s
            """.format(schema_field=schema_field)
            
            payload_size = len(json.dumps(payload))

            #do not save large payloads
            if payload_size < 10000:
                if self.mysql_connection:
                    self.mysql_connection.write(update_query, [json.dumps(payload), intent_name])
            
        except Exception as e:
            print(f"Error logging intent payload: {str(e)}")

    def log_event_stream_generator(self, queue):
        while True:
            try:
                msg = queue.get(timeout=10)
                
                # Handle both string and bytes
                if isinstance(msg, bytes):
                    msg = msg.decode('utf-8')
                
                # Ensure the message is valid JSON
                try:
                    # Try to parse as JSON to validate
                    json.loads(msg)
                    yield f"data: {msg}\n\n"
                except json.JSONDecodeError:
                    # If not valid JSON, wrap it
                    safe_msg = json.dumps({"message": str(msg)})
                    yield f"data: {safe_msg}\n\n"
                    
            except Empty:
                yield "data: {\"type\": \"keepalive\"}\n\n"
            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                yield f"data: {error_msg}\n\n"
            
            time.sleep(0.5)

    def log_event_stream_subscribe_handler(self, message):
        try:
            # Handle Redis message format
            if hasattr(message, 'data'):
                data = message.data
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                self.log_event_stream_queue.put(data)
            else:
                # Direct message
                if isinstance(message, bytes):
                    message = message.decode('utf-8')
                self.log_event_stream_queue.put(message)
        except Exception as e:
            print(f"Error in subscribe handler: {str(e)}")

    def log_event_stream_handler(self):
        try:
            response = Response(
                self.log_event_stream_generator(self.log_event_stream_queue), 
                mimetype='text/event-stream'
            )
            
            # Essential SSE headers
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Connection'] = 'keep-alive'
            response.headers['X-Accel-Buffering'] = 'no'  # Disable nginx buffering
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as e:
            print(f"Error in log_event_stream_handler: {str(e)}")
            return jsonify({"error": "Internal Server Error"}), 500


class Utillake:
    def __init__(self):
        self.groc_api_key = self.get_groc_api_key()

    @staticmethod
    def get_groc_api_key():
        groc_api_key = os.getenv('GROCLAKE_API_KEY')
        if not groc_api_key:
            raise ValueError("GROCLAKE_API_KEY is not set in the environment variables.")
        groc_account_id = os.getenv('GROCLAKE_ACCOUNT_ID')
        if not groc_account_id:
            raise ValueError("GROCLAKE_ACCOUNT_ID is not set in the environment variables.")
        return groc_api_key

    @staticmethod
    def _get_groc_api_headers():
        return {'GROCLAKE-API-KEY': os.getenv('GROCLAKE_API_KEY')}

    @staticmethod
    def _add_groc_account_id(payload):
        return payload.update({'groc_account_id': os.getenv('GROCLAKE_ACCOUNT_ID')})

    def call_api(self, endpoint, payload,lake_obj=None):
        headers = self._get_groc_api_headers()
        url = f"{BASE_URL}{endpoint}"
        if lake_obj:
            lake_ids = ['cataloglake_id', 'vectorlake_id', 'datalake_id', 'modellake_id']

            for lake_id in lake_ids:
                if hasattr(lake_obj, lake_id) and getattr(lake_obj, lake_id):
                    payload[lake_id] = getattr(lake_obj, lake_id)

        self._add_groc_account_id(payload)
        if not endpoint:
            raise ValueError("Invalid API call.")
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}

    def call_api_agent(self, endpoint, payload, lake_obj=None):
        headers = self._get_groc_api_headers()
        url = f"{AGENT_BASE_URL}{endpoint}"
        if lake_obj:
            lake_ids = ['cataloglake_id', 'vectorlake_id', 'datalake_id', 'modellake_id']

            for lake_id in lake_ids:
                if hasattr(lake_obj, lake_id) and getattr(lake_obj, lake_id):
                    payload[lake_id] = getattr(lake_obj, lake_id)

        #self._add_groc_account_id(payload)
        if not endpoint:
            raise ValueError("Invalid API call.")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}


    def call_knowledgelake_payload(self, payload, lake_obj=None):
        headers = self._get_groc_api_headers()
        if lake_obj:
            lake_ids = ['cataloglake_id', 'vectorlake_id', 'datalake_id', 'modellake_id', 'knowledgelake_id']
            for lake_id in lake_ids:
                if hasattr(lake_obj, lake_id) and getattr(lake_obj, lake_id):
                    payload[lake_id] = getattr(lake_obj, lake_id)

        self._add_groc_account_id(payload)
        return payload

    def get_api_response(self, endpoint):
        headers = self._get_groc_api_headers()
        url = f"{BASE_URL}{endpoint}"
        if not endpoint:
            raise ValueError("Invalid API call.")
        try:
            response = requests.get(url, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}
