import os
import random
import string
from datetime import datetime, date
import json
import pytz
import uuid
import logging

from groclake.datalake import Datalake
from dotenv import load_dotenv



load_dotenv()

class Config:
    # ES Configuration
    ES_CONFIG = {
        "host": os.getenv("ES_HOST"),
        "port": int(os.getenv("ES_PORT")),
        "api_key": os.getenv("ES_API_KEY"),
        "schema": os.getenv("ES_SCHEMA")
    }

    MYSQL_CONFIG = {
        'user': os.getenv('MYSQL_USER'),
        'passwd': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT')),
        'db': os.getenv('MYSQL_DB'),
        'charset': 'utf8'
    }

class DatalakeConnection(Datalake):
    def __init__(self):
        super().__init__()

        ES_CONFIG = Config.ES_CONFIG
        ES_CONFIG['connection_type'] = 'es'

        MYSQL_CONFIG = Config.MYSQL_CONFIG
        MYSQL_CONFIG['connection_type'] = 'sql'

        self.plotch_pipeline = self.create_pipeline(name="groclake_pipeline")
        self.plotch_pipeline.add_connection(name="es_connection", config=ES_CONFIG)
        self.plotch_pipeline.add_connection(name="sql_connection", config=MYSQL_CONFIG)

        self.execute_all()

        self.connections = {
            "es_connection": self.get_connection("es_connection"),
            "sql_connection": self.get_connection("sql_connection")
        }

    def get_connection(self, connection_name):
        """
        Returns a connection by name from the pipeline.
        """
        return self.plotch_pipeline.get_connection_by_name(connection_name)

datalake_connection = DatalakeConnection()
es_connection = datalake_connection.connections["es_connection"]
mysql_connection = datalake_connection.connections["sql_connection"]

class Agentlake:
    def __init__(self, index_uuid=None):
        if not index_uuid:
            raise ValueError(
                'Missing required index_uuid. Ensure you pass a valid index UUID when initializing the class.')
        self.index_uuid = index_uuid

    def generate_unique_id(self, length=16):
        characters = string.ascii_lowercase + string.digits
        unique_id = ''.join(random.choices(characters, k=length))
        return unique_id

    def get_current_datetime(self) -> str:
        return datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

    def get_existing_index_uuid(self, index_uuid, entity_type):
        condition_clause = "entity_id = %s AND entity_type= %s"
        query = f"SELECT * FROM groclake_entity_master WHERE {condition_clause}"
        params = (index_uuid, entity_type)
        result = mysql_connection.read(query, params, multiple=False)
        return result

    def save_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return mysql_connection.write(query, tuple(db_params.values()))
        else:
            return mysql_connection.write(query, tuple(db_params.values()))

    def get_agent_by_uuid(self, agent_uuid):
        query = '''SELECT * FROM groclake_agentlake_agents WHERE agent_uuid = %s '''
        response = mysql_connection.read(query, (agent_uuid,))
        return response

    def get_agent_by_uname(self, uname):
        query = '''SELECT * FROM groclake_agentlake_agents WHERE uname = %s '''
        response = mysql_connection.read(query, (uname,))
        return response

    def get_apc_data(self, apc_name):
        query = '''SELECT * FROM groclake_agentlake_apc WHERE apc_name = %s '''
        response = mysql_connection.read(query, (apc_name,))
        return response

    def get_by_apc_id(self, apc_id):
        query = '''SELECT * FROM groclake_agentlake_apc WHERE apc_id = %s '''
        response = mysql_connection.read(query, (apc_id,))
        return response

    def get_apc_mapping(self, agent_uuid, apc_id):
        query = '''SELECT * FROM groclake_agentlake_agent_apc_mapping WHERE agent_uuid = %s  AND apc_id = %s '''
        response = mysql_connection.read(query, (agent_uuid, apc_id))
        return response

    def convert_to_datetime(self, date_str):
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            raise ValueError(f"Error parsing date string: {e}")

    def generate_uuid(self):
        unique_id = uuid.uuid4()
        return unique_id

    def update_request_log(self, groc_account_id, event_type=None, lake_id=None, input_token=None, output_token=None):
        request_id = self.generate_uuid()
        db_params = {
            "request_id": str(request_id),
            "request_api": '',  # No endpoint path needed
            "request_event_type": event_type,
            "account_id": groc_account_id or '',
            "created_at": self.get_current_datetime(),
            "lake_id": lake_id or '',
            "input_token_length": input_token or '',
            "output_token_length": output_token or '',
        }
        self.save_data_in_db(db_params, 'groclake_api_request_log')
        return str(request_id)

    def register_agent(self, params):
        self.update_request_log(params.get("groc_account_id"), event_type="agentlake")
        category = params.get('agent_category')
        # if not self.is_valid_category(category):
        #     return {"message": f"Invalid category. Allowed categories are: {', '.join(self.is_valid_category(None, is_not_true=True))}"}
        agent_uuid = params.get('agent_uuid') or str(uuid.uuid4())
        params['agent_uuid'] = agent_uuid
        existing_agent = self.get_agent_by_uuid(agent_uuid)
        if existing_agent:
            return {"message": f"Agent with this UUID {agent_uuid} already exists and has been made active."}
        uname = params.get('uname')
        if uname:
            existing_agent = self.get_agent_by_uname(uname)
            if existing_agent:
                return {"message": f"Agent with username {uname} already exists."}
        datetime_fields = ['valid_from', 'valid_until', 'created', 'updated']
        for field in datetime_fields:
            if field in params and params.get(field):
                params[field] = self.convert_to_datetime(params.get(field))
        agent_data = {
            'agent_uuid': params.get('agent_uuid') or None,
            'agent_name': params.get('agent_name') or None,
            'agent_logo_url': params.get('agent_logo_url') or None,
            'agent_description': params.get('agent_description') or None,
            'agent_code': params.get('agent_code') or None,
            'status': params.get('status') or None,
            'agent_url': params.get('agent_url') or None,
            'country': params.get('country') or None,
            'valid_from': params.get('valid_from') or None,
            'valid_until': params.get('valid_until') or None,
            'agent_category': params.get('agent_category') or None,
            'signing_public_key': params.get('signing_public_key') or None,
            'encr_public_key': params.get('encr_public_key') or None,
            'created': params.get('created') or None,
            'updated': params.get('updated') or None,
            'organization': params.get('organization') or None,
            'agent_rating': params.get('agent_rating') or None,
            'uname': params.get('uname') or None
        }
        result = self.save_data_in_db(agent_data, 'groclake_agentlake_agents')
        if result:
            self.push_to_cataloglake(params.get('agent_uuid'), params.get('agent_category'),
                                     params.get('agent_description'),
                                     params.get('organization'), params.get('agent_name'),
                                     params.get('country'), params.get('agent_logo_url'))
        return {"message": "Agent registered successfully!", "agent_uuid": agent_uuid}

    def is_valid_category(self, category, is_not_true=False):
        """Check if the category is valid or return all valid categories."""
        VALID_CATEGORIES = {
            "ERP Agents", "Coding Agents", "Customer Service Agents", "Marketing Agents",
            "Web Scraping Agents", "Shopping Agents", "Translation Agents",
            "Recruitment Agents", "Video Agents", "Image Agents", "Social Agents", "AI Voice Agents", "Analytics", "AIOps"
        }
        if is_not_true:
            return list(VALID_CATEGORIES)
        return category in VALID_CATEGORIES

    def push_to_cataloglake(self, agent_uuid, agent_category, agent_description, organization, agent_name, country, agent_logo_url):
        product_object = {
            "groc_account_id": '',
            "client_item_id": agent_uuid,
            "cataloglake_id": '',
            "product_id": '',
            "groc_category": agent_category,
            "groc_category_id": '',
            "product_type": '',
            "name": agent_name,
            "description": agent_description,
            "short_description": agent_description,
            "category": agent_category,
            "variant_group_id": '',
            "variant": '',
            "group_id": '',
            "location_id": '',
            "inventory_qty": 0,
            "inventory_min_qty": 0,
            "inventory_max_qty": 0,
            "is_in_stock": 0,
            "mrp": 0.0,
            "sale_price": 0.0,
            "discount_start_date": None,
            "discount_end_date": None,
            "discounted_price": 0.0,
            "image1": agent_logo_url,
            "image2": '',
            "image3": '',
            "image4": '',
            "pattern": '',
            "material": '',
            "occasion": '',
            "season": '',
            "trend": '',
            "features": '',
            "material_finish": '',
            "size_chart": '',
            "fulfillment_mode": '',
            "available_on_cod": 0,
            "cancellable": 0,
            "rateable": 0,
            "return_pickup": 0,
            "return_window": None,
            "returnable": 0,
            "time_to_ship": None,
            "common_or_generic_name_of_commodity": '',
            "imported_product_country_of_origin": country,
            "manufacturer_name": organization,
            "measure_of_commodity_in_pkg": '',
            "month_year_of_manufacture": None,
            "nutritional_info": '',
            "additives_info": '',
            "brand_owner_fssai_license_no": '',
            "other_fssai_license_no": '',
            "importer_fssai_license_no": '',
            "is_veg": 0,
            "ondc_domain": '',
            "gender": '',
            "colour": '',
            "size": '',
            "brand": '',
            "fabric": '',
            "strap_material": '',
            "water_resistant": 0,
            "display": '',
            "glass_material": '',
            "colour_name": '',
            "sport_type": '',
            "base_metal": '',
            "plating": '',
            "care_instructions": '',
            "wash_type": '',
            "fit": '',
            "collar": '',
            "neck": '',
            "hemline": '',
            "sleeve_length": '',
            "battery_life": '',
            "bluetooth": '',
            "model": '',
            "model_year": None,
            "os_type": '',
            "weight": 0.0,
            "length": 0.0,
            "breadth": 0.0,
            "height": 0.0,
            "refurbished": 0,
            "skin_type": '',
            "ingredient": '',
            "formulation": '',
            "veg_nonveg_flag": '',
            "upc_code": None,
            "ram": None,
            "ram_unit": None,
            "storage": None,
            "storage_unit": None,
            "storage_type": None,
            "screen_size": None,
            "cpu": None,
            "os_version": None,
            "form_factor": None,
            "expiry_date": None,
            "best_before": None,
            "marketed_by": None,
            "net_weight": 0.0,
            "number_of_items": 0,
            "item_quantity": 0,
            "flavour": None,
            "country_of_origin": '',
            "number_of_pieces": 0,
            "allergen_information": None,
            "package_information": None,
            "package_weight": 0.0,
            "item_form": None,
            "sodium_mg": 0.0,
            "total_fat_gm": 0.0,
            "total_fat_saturated_gm": 0.0,
            "total_fat_trans_gm": 0.0,
            "energy_kcal": 0.0,
            "protein_gm": 0.0,
            "carbohydrates_gm": 0.0,
            "scent": None,
            "consumer_care_phone": None,
            "consumer_care_email": None,
            "manufacturing_date": None,
            "batch_number": None,
            "product_description": None,
            "product_benefits": None,
            "product_highlights": None,
            "item_volume": 0.0,
            "net_volume": 0.0,
            "product_disclaimer": None,
            "product_instructions": None,
            "more_image_links": '',
            "scan_type": None,
            "GTIN": None,
            "CSIN": None,
            "fssai_number": None,
            "marketing_fssai_number": None,
            "manufacturer_fssai_number": None,
            "request_id": "",
            "created_at": self.get_current_datetime(),
            "updated_at": self.get_current_datetime(),
            "cache_enabled": 0,
            "cdn_image1": '',
            "cdn_image2": '',
            "cdn_image3": '',
            "cdn_image4": '',
            "provider_id": '',
            "provider": '',
            "gl_score": 0
        }
        self.save_data_in_db(product_object, 'groclake_cataloglake_catalog_products')

    def category_list_fetch(self):
        categories = self.is_valid_category(None, is_not_true=True)
        if categories is None or not categories:
            raise Exception("Failed to fetch categories due to an internal error.")
        return {"categories": categories}

    def agent_fetch(self, params):
        self.update_request_log(params.get("groc_account_id"), event_type="agentlake")
        agent_uuid = params.get('agent_uuid')
        response = self.get_agent_by_uuid(agent_uuid)
        if not response:
            return {"message": "No agents found for the given UUID"}
        uname = params.get('uname')
        response_uname = self.get_agent_by_uname(uname)
        if not response_uname:
            return {"message": "No agents found for the given UUID"}
        agents = self.convert_datetime_to_str(response)
        agents.pop('id')
        agents.pop('agent_rating')
        return {"message": "Agent details fetched successfully", "Agent Details": agents}

    def convert_datetime_to_str(self, agent_data):
        datetime_fields = ['created', 'updated', 'valid_from', 'valid_until']
        for field in datetime_fields:
            if field in agent_data and isinstance(agent_data[field], (datetime, date)):
                agent_data[field] = agent_data[field].strftime('%Y-%m-%d %H:%M:%S')
        return agent_data

    def apc_create(self, params):
        self.update_request_log(params.get("groc_account_id"), event_type="agentlake")
        ALLOWED_CATEGORIES = ["private", "public"]
        required_fields = ['apc_name', 'apc_category']
        for field in required_fields:
            if field not in params or not params.get(field):
                return {"message": f"Required field '{field}' is missing."}

        if params.get('apc_category').lower() not in ALLOWED_CATEGORIES:
            return {"message": f"Invalid category. Allowed categories are: {', '.join(ALLOWED_CATEGORIES)}"}

        apc_name = self.get_apc_data(params.get('apc_name'))
        if apc_name:
            return {"message": "APC with this name already exists"}

        apc_id = str(uuid.uuid4())
        apc_data = {
            "apc_id": apc_id,
            'apc_name': params.get('apc_name') or '',
            'apc_description': params.get('apc_description') or '',
            'status': params.get('status', 'inactive') or '',
            'apc_tags': params.get('apc_tags') or '',
            'gateway_agent_uuid': params.get('gateway_agent_uuid') or '',
            'agentwall_id': params.get('agentwall_id') or '',
            'apc_category': params.get('apc_category') or '',
            'signing_public_key': params.get('signing_public_key') or '',
            'encr_public_key': params.get('encr_public_key') or '',
            'created_at': self.get_current_datetime(),
            'updated_at': self.get_current_datetime()
        }
        self.save_data_in_db(apc_data, 'groclake_agentlake_apc')
        return {"apc_id": apc_id, "message": "APC created successfully!"}

    def apc_agent_assign(self, params):
        self.update_request_log(params.get("groc_account_id"), event_type="agentlake")
        apc_id = params.get("apc_id")
        agent_uuid = params.get('agent_uuid')
        required_fields = ['agent_uuid', 'apc_id', 'agent_type']
        for field in required_fields:
            if field not in params or not params.get(field):
                return {"message": f"Required field '{field}' is missing."}
        ALLOWED_AGENT_TYPES = ["gateway", "ordinary"]
        if params.get('agent_type').lower() not in ALLOWED_AGENT_TYPES:
            return {"message": f"Invalid category. Allowed categories are: {ALLOWED_AGENT_TYPES}."}
        apc_data = self.get_by_apc_id(apc_id)
        if not apc_data:
            return {"message": "APC not found."}
        apc_mapping = self.get_apc_mapping(agent_uuid, apc_id)
        if apc_mapping:
            return {"message": "APC already assigned to this agent."}
        db_params = {
            'agent_uuid': agent_uuid or '',
            'apc_id': apc_id or '',
            'agent_type': params.get('agent_type') or '',
            'created_at': self.get_current_datetime(),
            'updated_at': self.get_current_datetime()
        }
        self.save_data_in_db(db_params, 'groclake_agentlake_agent_apc_mapping')
        return {"agent_uuid": agent_uuid, "apc_id": apc_id, "message": "Agent assigned to apc."}