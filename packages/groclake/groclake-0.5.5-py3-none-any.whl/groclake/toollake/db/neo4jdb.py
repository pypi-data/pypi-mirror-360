from neo4j import GraphDatabase
from typing import Dict, Any
from urllib.parse import urlparse

class Neo4jDB():
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize Neo4j connection with tool configuration.
        
        Expected tool_config format:
        {
            'host': 'neo4j://localhost:7687',
            'username': 'neo4j',
            'password': 'password'
        }
        """
        self.tool_config = tool_config
        self.uri = self.tool_config['host']
        self.user = self.tool_config['username']
        self.pwd = self.tool_config['password']
        self.connect()

    def connect(self):
        self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.pwd))
        self.database = self.tool_config.get("database", "neo4j")  # default to "neo4j"
        
    def close(self):
        self._driver.close()

    def format_properties(self,prefix, props):
        """Build Cypher properties string and parameters."""
        prop_str = ", ".join([f"{k}: ${prefix}_{k}" for k in props])
        param_dict = {f"{prefix}_{k}": v for k, v in props.items()}
        return f"{{{prop_str}}}", param_dict
    
    def convert_nodes_to_json(self, nodes):
        results = []
        for record in nodes:
            node = record["n"]  # Extract the Node object from the Record
            node_data = dict(node)
            node_data["type"] = list(node.labels)[0]  # Get label like 'Class', 'Method', etc.
            results.append(node_data)
        return results

    
    def create_node(self, payload):
        """Create or merge a node using all properties, and return meaningful properties."""
        label = payload.get("label")
        properties = payload.get("properties")

        if not label or not properties:
            raise ValueError({"error": "label and at least one property must be provided to create a Node"})

        # Build dynamic MERGE clause using all properties
        merge_props_str = ", ".join([f"{key}: ${key}" for key in properties.keys()])
        
        query = (
            f"MERGE (n:{label} {{ {merge_props_str} }}) "
            f"SET n += $props "
            f"RETURN n"
        )

        with self._driver.session() as session:
            result = session.run(query, **properties, props=properties).single()
            node = result["n"]
            return {
                "message": f"Node for {label} Merged",
                "Node": dict(node)
            }


     
    def update_node_properties(self, payload):
        """
        Updates properties of a node and returns a meaningful response.
        """
        label = payload['label']
        identity_props = payload['identity_props']
        update_props = payload['update_props']

        match_query = f"""
        MATCH (n:{label} {{{', '.join([f'{k}: ${k}' for k in identity_props])}}})
        RETURN n
        """
        update_query = f"""
        MATCH (n:{label} {{{', '.join([f'{k}: ${k}' for k in identity_props])}}})
        SET {', '.join([f'n.{k} = ${k}' for k in update_props])}
        RETURN n
        """

        with self._driver.session() as session:
            match_result = session.run(match_query, **identity_props)
            if not match_result.peek():
                return {"status": "error", "message": "Node not found", "identity": identity_props}

            result = session.run(update_query, **identity_props, **update_props)
            updated_node = result.single()['n']
            return {
                "status": "success",
                "message": "Node properties updated",
                "updated_fields": list(update_props.keys()),
                "node": dict(updated_node)
            }
 
    
    def add_property_to_node(self, payload):
        """
        Adds or updates a single property on a matched node and returns a response.
        """
        label = payload['label']
        identity_props = payload['identity_props']
        prop_key = payload['prop_key']
        prop_value = payload['prop_value']

        match_query = f"""
        MATCH (n:{label} {{{', '.join([f'{k}: ${k}' for k in identity_props])}}})
        RETURN n
        """
        update_query = f"""
        MATCH (n:{label} {{{', '.join([f'{k}: ${k}' for k in identity_props])}}})
        SET n.{prop_key} = $prop_value
        RETURN n
        """

        with self._driver.session() as session:
            match_result = session.run(match_query, **identity_props)
            if not match_result.peek():
                return {"status": "error", "message": "Node not found", "identity": identity_props}

            result = session.run(update_query, **identity_props, prop_value=prop_value)
            updated_node = result.single()['n']
            return {
                "status": "success",
                "message": f"Property '{prop_key}' set successfully",
                "updated_property": {prop_key: prop_value},
                "node": dict(updated_node)
            }
    
    
    def create_relationship(self, payload):
        """
        Create a relationship between two nodes with the given label and properties.

        Expected payload:
        {
            "node1": "Person", // label
            "node2": "Person", // label
            "relation": "Friends_with",
            "prop1": { "name": "Alice", "age": 53 },
            "prop2": { "name": "John", "age": 35 }
        }
        """
        label1 = payload["node1"]
        label2 = payload["node2"]
        rel_type = payload["relation"]
        props1 = payload["prop1"]
        props2 = payload["prop2"]
        if not props1 or not props2:
            raise ValueError("Both 'prop1' and 'prop2' must contain at least one property to create a relation.")

        props1_str, params1 = self.format_properties("p1", props1)
        props2_str, params2 = self.format_properties("p2", props2)

        query = (
            f"MERGE (a:{label1} {props1_str}) "
            f"MERGE (b:{label2} {props2_str}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            f"RETURN r"
        )

        params = {**params1, **params2}

        with self._driver.session() as session:
            session.run(query, params).single()
            return {"message": f"Relationship `{rel_type}` created between `{label1}` and `{label2}`"}

    
    def get_nodes(self, payload=None):
        """
        Retrieve all nodes, or nodes with a specific label and properties from a payload.
        
        Args:
            payload (dict): Dictionary with optional 'label' (str) and 'properties' (dict) keys.
            
        Returns:
            list: Matching nodes.
        """
        payload = payload or {}
        label = payload.get("label", "")
        properties = payload.get("properties", {})

        props_string = ""
        if properties:
            props_list = [f"{key}: ${key}" for key in properties]
            props_string = "{" + ", ".join(props_list) + "}"

        if label:
            query = f"MATCH (n:{label} {props_string}) RETURN n"
        else:
            query = f"MATCH (n {props_string}) RETURN n"

        with self._driver.session() as session:
            return self.convert_nodes_to_json(session.run(query, properties))
        
    def get_nodes_by_modified_time(self, payload=None):
        """
        Retrieve nodes with an optional label where 'last_modified' is on or after a given timestamp.
        
        Args:
            payload (dict): Should include:
                - 'label' (str): Optional node label.
                - 'modified_since' (str): ISO 8601 formatted timestamp (e.g. '2024-12-01T00:00:00').
                
        Returns:
            list: Matching nodes.
        """
        payload = payload or {}
        label = payload.get("label", "")
        modified_since = payload.get("modified_time")

        if not modified_since:
            raise ValueError("The 'modified_time' field is required in the payload.")

        label_str = f":{label}" if label else ""
        query = (
        f"MATCH (n{label_str}) "
        f"WHERE datetime(n.modified_time) >= datetime($modified_since) "
        f"RETURN n"
    )


        with self._driver.session() as session:
            result = session.run(query, {"modified_since": modified_since})
            return self.convert_nodes_to_json(result)
   
        
    def get_node_relations(self, payload=None):
        """
        Retrieve all nodes with a specific label and properties, along with their relationships.

        Args:
            payload (dict): Dictionary with optional 'label' (str) and 'properties' (dict) keys.

        Returns:
            list: List of dictionaries with start_node, relationship, and end_node in JSON format.
        """
        payload = payload or {}
        label = payload.get("label", "")
        properties = payload.get("properties", {})

        # Construct Cypher query based on provided parameters
        if label:
            # Start node has a label
            if properties:
                # Label with properties
                props_list = [f"{key}: ${key}" for key in properties]
                props_string = "{" + ", ".join(props_list) + "}"
                query = f"MATCH (a:{label} {props_string})-[r]->(b) RETURN a, r, b"
            else:
                # Label only, no properties
                query = f"MATCH (a:{label})-[r]->(b) RETURN a, r, b"
        else:
            # No label specified, just properties
            if properties:
                props_list = [f"{key}: ${key}" for key in properties]
                props_string = "{" + ", ".join(props_list) + "}"
                query = f"MATCH (a {props_string})-[r]->(b) RETURN a, r, b"
            else:
                # Require at least label or properties
                raise ValueError("Either 'label' or 'properties' must be provided")
        with self._driver.session() as session:
            result = session.run(query, properties)
            return [
                {
                    "start_node": {
                        "labels": list(record["a"].labels),
                        "properties": dict(record["a"])
                    },
                    "relationship": {
                        "type": record["r"].type,
                        "properties": dict(record["r"])
                    },
                    "end_node": {
                        "labels": list(record["b"].labels),
                        "properties": dict(record["b"])
                    }
                }
                for record in result
            ]


    def get_relationships(self, payload=None):
        """
        Retrieve relationships based on relationship type and optional properties.

        Args:
            payload (dict): Optional dictionary with 'rel_type' (str) and 'properties' (dict).

        Returns:
            list: Matching relationships.
        """
        payload = payload or {}
        rel_type = payload.get("rel_type", "")
        properties = payload.get("properties", {})

        props_string = ""
        if properties:
            props_list = [f"{key}: ${key}" for key in properties]
            props_string = "{" + ", ".join(props_list) + "}"

        # Build Cypher query based on presence of rel_type and properties
        if rel_type:
            query = f"MATCH ()-[r:{rel_type} {props_string}]->() RETURN r"
        else:
            query = f"MATCH ()-[r {props_string}]->() RETURN r"

        with self._driver.session() as session:
            return [record["r"] for record in session.run(query, properties)]

    def delete_node(self, payload):
        """
        Delete a node with the specified label and matching properties.
        
        Args:
            label (str): The label of the node to delete.
            properties (dict): Dictionary of properties to identify the node.
            
        Raises:
            ValueError: If label or properties are not provided.
        """
        label = payload.get("label","")
        properties = payload.get("properties",{})
        if not label or not properties:
            raise ValueError("Both label and at least one property are required to delete a node.")

        props_list = [f"{key}: ${key}" for key in properties]
        props_string = "{" + ", ".join(props_list) + "}"
        
        query = f"MATCH (n:{label} {props_string}) DETACH DELETE n"
        
        with self._driver.session() as session:
            session.run(query, properties)
            return session.run(query, properties)
        
    
    def delete_all_nodes(self, label):
        """
        Delete all nodes with the specified label and optional properties.
        
        Args:
            label (str): The label of the nodes to delete.
            properties (dict, optional): Properties to match for deletion.
        
        Raises:
            ValueError: If label is not provided.
        """
        if not label:
            raise ValueError("Label is required to delete nodes.")
        query = f"MATCH (n:{label}) DETACH DELETE n"
        print(f"Deleting {label}")
        with self._driver.session() as session:
            return session.run(query)



    def delete_relationship(self, payload):
        """
        Delete a relationship between two nodes using dynamic labels and properties.

        Payload format:
        {
            "label1": "Person",
            "prop1": { "name": "Alice" },
            "label2": "Person",
            "prop2": { "name": "Bob" },
            "rel_type": "FRIENDS_WITH"
        }
        """
        label1 = payload.get("label1")
        label2 = payload.get("label2")
        prop1 = payload.get("prop1", {})
        prop2 = payload.get("prop2", {})
        rel_type = payload.get("rel_type")

        if not (label1 and label2 and prop1 and prop2 and rel_type):
            raise ValueError("Payload must include label1, prop1, label2, prop2, and rel_type")

        # Convert prop1 and prop2 to Cypher match strings
        prop1_str = ", ".join([f"{k}: $prop1_{k}" for k in prop1])
        prop2_str = ", ".join([f"{k}: $prop2_{k}" for k in prop2])

        query = (
            f"MATCH (a:{label1} {{{prop1_str}}})"
            f"-[r:{rel_type}]->"
            f"(b:{label2} {{{prop2_str}}}) DELETE r"
        )

        # Merge parameters with prefixes to avoid collision
        parameters = {f"prop1_{k}": v for k, v in prop1.items()}
        parameters.update({f"prop2_{k}": v for k, v in prop2.items()})

        with self._driver.session() as session:
            return session.run(query, parameters)
        

    def delete_all_relationships(self, rel_type):
        """
        Delete all relationships of a specific type (label).

        Args:
            rel_type (str): The type of the relationship to delete.

        Raises:
            ValueError: If rel_type is not provided.
        """
        if not rel_type:
            raise ValueError("Relationship type (label) is required to delete relationships.")

        query = f"MATCH ()-[r:{rel_type}]->() DELETE r"
        print(f"Deleting all relations of '{rel_type}")
        with self._driver.session() as session:
            session.run(query)
      
    def node_exists(self, payload, match_keys=None):
        """
        Check if a node exists with the given label and properties.

        :param payload: dict with 'label' and full 'properties'
        :param match_keys: list of property keys to use for the MATCH query (e.g. ['instance_id'])
        """
        label = payload.get("label")
        properties = payload.get("properties", {})

        if not label or not properties:
            raise ValueError("Payload must contain 'label' and 'properties'.")

        # Use only match_keys to build the MATCH clause
        if not match_keys:
            # default to all keys (existing behavior, but risky for timestamps)
            match_keys = properties.keys()

        match_props = {k: properties[k] for k in match_keys if k in properties}
        prop_query = ", ".join(f"{k}: ${k}" for k in match_props)
        query = f"MATCH (n:{label} {{{prop_query}}}) RETURN n LIMIT 1"

        print(f"Executing Query: {query} with properties: {match_props}")

        with self._driver.session() as session:
            result = session.run(query, match_props).single()
            if result:
                print("Node exists.")
            else:
                print("No node found.")
            return result is not None

    def relationship_exists(self, payload, match_keys1=None, match_keys2=None):
        """
        Check if a relationship exists between two nodes using only selected property keys for matching.

        match_keys1 and match_keys2 allow controlling which keys to use for node1 and node2 matching.
        """
        label1 = payload.get("node1")
        label2 = payload.get("node2")
        rel_type = payload.get("relation")
        prop1 = payload.get("prop1", {})
        prop2 = payload.get("prop2", {})

        if not label1 or not label2 or not rel_type or not prop1 or not prop2:
            raise ValueError("Payload must contain 'node1', 'node2', 'relation', 'prop1', and 'prop2'.")

        if not match_keys1:
            match_keys1 = list(prop1.keys())
        if not match_keys2:
            match_keys2 = list(prop2.keys())

        prop1_filtered = {k: prop1[k] for k in match_keys1 if k in prop1}
        prop2_filtered = {k: prop2[k] for k in match_keys2 if k in prop2}

        prop1_query = ", ".join(f"{k}: $p1_{k}" for k in prop1_filtered)
        prop2_query = ", ".join(f"{k}: $p2_{k}" for k in prop2_filtered)

        query = (
            f"MATCH (a:{label1} {{{prop1_query}}})-[r:{rel_type}]->(b:{label2} {{{prop2_query}}}) "
            f"RETURN r LIMIT 1"
        )

        params = {f"p1_{k}": v for k, v in prop1_filtered.items()}
        params.update({f"p2_{k}": v for k, v in prop2_filtered.items()})

        print(f"Executing Relationship Query: {query} with params: {params}")

        with self._driver.session() as session:
            result = session.run(query, params).single()
            return result is not None

    def run_cypher_query(self, cypher_query, parameters=None):
        """
        Run a raw Cypher query and return results.

        Args:
            cypher_query (str): The Cypher query string.
            parameters (dict, optional): Parameters for the query.

        Returns:
            list: Query result.
        """
        parameters = parameters or {}
        with self._driver.session() as session:
            result = session.run(cypher_query, parameters)
            return [record.data() for record in result]
          
    def get_path_parts(self,file_url):
        if file_url.startswith("http"):
            parsed_url = urlparse(file_url)
            path_parts = parsed_url.path.split('/')[5:]  # user/repo/blob/branch/file/path...
        else:
            path_parts = file_url.split('/')
        return path_parts

    def upload_repo_data_to_neo4j(self, git_data):
        file_count = 1
        for item in git_data:
            file_url = item['file_url']
            file_name = file_url.split("/")[-1].split("?")[0]
            
            repo_name = item['repo']
            repo_url = item['repo_url']

            path_parts = self.get_path_parts(file_url)
            file_path = "/".join(path_parts[:-1])
            full_file_path = "/".join(path_parts)

            last_modified_time = item.get('last_modified_time')
            commit_message = item.get('commit_message')
            committer_name = item.get('committer_name')

            # Create Repository node
            repo_props = {
                "label": "Repository",
                "properties": {
                    "name": repo_name,
                    "url": repo_url
                }
            }
            self.create_node(repo_props)
            print(f"file {file_name} uploaded to Neo4j count: {file_count}")
            
            file_count+=1
            # Create Directory nodes
            current_dir_path = ""
            parent_label = "Repository"
            parent_props = {"name": repo_name}

            for part in path_parts[:-1]:
                current_dir_path = f"{current_dir_path}/{part}" if current_dir_path else part
                dir_props = {
                    "label": "Directory",
                    "properties": {
                        "name": part,
                        "full_path": current_dir_path
                    }
                }

                self.create_node(dir_props)
                self._driver.create_relationship({
                    "node1": parent_label,
                    "prop1": parent_props,
                    "relation": "HAS_DIRECTORY",
                    "node2": "Directory",
                    "prop2": {"name": part, "full_path": current_dir_path},
                    "rel_props": {"nested": True}
                })

                parent_label = "Directory"
                parent_props = {"name": part, "full_path": current_dir_path}

            # Create File node
            file_props = {
                "label": "File",
                "properties": {
                    "name": file_name,
                    "full_path": full_file_path,
                    "created_time": last_modified_time,
                    "modified_time": last_modified_time,
                    "commit_message": commit_message,
                    "committer": committer_name
                }
            }
            self.create_node(file_props)

            # File relationship
            if path_parts[:-1]:
                self.create_relationship({
                    "node1": parent_label,
                    "prop1": parent_props,
                    "relation": "HAS_FILE",
                    "node2": "File",
                    "prop2": {"name": file_name, "full_path": full_file_path},
                    "rel_props": {"defined_in_repo": repo_name}
                })
            else:
                self.create_relationship({
                    "node1": "Repository",
                    "prop1": {"name": repo_name},
                    "relation": "HAS_FILE",
                    "node2": "File",
                    "prop2": {"name": file_name, "full_path": full_file_path},
                    "rel_props": {"defined_in_repo": repo_name}
                })

            # Import nodes
            for imp in item['imports']:
                import_props = {
                    "label": "Import",
                    "properties": {
                        "name": imp
                    }
                }
                self.create_node(import_props)
                self.create_relationship({
                    "node1": "File",
                    "prop1": {"name": file_name, "full_path": full_file_path},
                    "relation": "IMPORTS",
                    "node2": "Import",
                    "prop2": {"name": imp},
                    "rel_props": {"from": file_name}
                })

            # Class and Method nodes
            for class_name, method_list in item['classes'].items():
                class_props = {
                    "label": "Class",
                    "properties": {
                        "name": class_name,
                        "file": file_name,
                        "full_path": full_file_path,
                        "created_time": last_modified_time,
                        "modified_time": last_modified_time,
                        "commit_message": commit_message,
                        "committer": committer_name
                    }
                }
                self.create_node(class_props)
                self.create_relationship({
                    "node1": "File",
                    "prop1": {"name": file_name, "full_path": full_file_path},
                    "relation": "HAS_CLASS",
                    "node2": "Class",
                    "prop2": {"name": class_name, "file": file_name, "full_path": full_file_path},
                    "rel_props": {"defined_in": file_name}
                })

                for method_name in method_list:
                    method_props = {
                        "label": "Method",
                        "properties": {
                            "name": method_name,
                            "class": class_name,
                            "file": file_name,
                            "full_path": full_file_path,
                            "created_time": last_modified_time,
                            "modified_time": last_modified_time,
                            "commit_message": commit_message,
                            "committer": committer_name
                        }
                    }
                    self.create_node(method_props)
                    self.create_relationship({
                        "node1": "Class",
                        "prop1": {"name": class_name, "file": file_name, "full_path": full_file_path},
                        "relation": "HAS_METHOD",
                        "node2": "Method",
                        "prop2": {"name": method_name, "class": class_name, "file": file_name, "full_path": full_file_path},
                        "rel_props": {"method_of": class_name}
                    })

    def get_graph_data_all(self):

        query = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 100
        """

        with self._driver.session() as session:
            result = session.run(query)

            nodes = {}
            edges = []

            for record in result:
                n = record["n"]
                m = record["m"]
                r = record["r"]

                for node in (n, m):
                    nid = node.id
                    if nid not in nodes:
                        nodes[nid] = {
                            "id": nid,
                            "label": next(iter(node.labels), "Unknown"),
                            **node._properties
                        }

                edges.append({
                    "from": n.id,
                    "to": m.id,
                    "label": r.type
                })

            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }


    