
import time
import json

class Memorylake():
    def __init__(self, memory_config):
        
        if memory_config.get("database_type") == "redis":
            self.database_type = "redis"
        
        if memory_config.get("connection") and memory_config.get("database_type") == "redis":
            self.redis_client = memory_config.get("connection")
        else:
            raise ValueError("Connection is not available.")

        # Initialize Redis connection
        self.connections = {
            "redis_connection": self.redis_client,
        }

    def get_connection(self, connection_name):
        """
        Returns a connection by name from the pipeline.
        """
        return self.redis_client

    @staticmethod
    def validate_memory_type(memory_type):
        """Ensure memory_type is either '0' or '1'."""
        if memory_type not in ['0', '1']:
            raise ValueError("Invalid memory_type. It must be '0' or '1'.")

    @staticmethod
    def generate_key(user_uuid, context_entity_id, context_id, memory_type, memory_id):
        """Generates a unique key by concatenating user_uuid, context_entity_id, context_id, memory_type, and memory_id."""
        Memorylake.validate_memory_type(memory_type)
        return f"{user_uuid}:{context_id}:{context_entity_id}:{memory_type}:{memory_id}"

    def short_memory_create(self, user_uuid, memory_context, memory):
        """Creates a key-value pair in Redis only if the key does not already exist."""
        memory_type = str(memory_context.get('memory_type', '1'))
        self.validate_memory_type(memory_type)

        # Generate the key
        key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            memory_type,
            memory_context['memory_id']
        )

        value = {
            "query_text": memory['query_text'],
            "response_text": memory['response_text'],
            "memory_metadata": [
                {
                    "time": memory['time'],
                    "memory_id": memory_context['memory_id'],
                    "context_id": memory_context['context_id'],
                }
            ],
            "intent": memory.get("intent", ""),
            "entities": memory.get("entities", []),
            "metadata": memory.get("metadata", []),
        }

        ttl = memory.get('cache_ttl', 3600)

        # Check if the key already exists in Redis
        if self.redis_client.exists(key):
            raise ValueError(f"Key '{key}' already exists. Cannot create a new value for the same key.")

        # Store the new key-value pair in Redis
        self.redis_client.set(key, str(value), ex=ttl)

        # Add the key to a sorted set with the current timestamp as the score
        sorted_set_key = f"{user_uuid}:{memory_context['context_id']}:{memory_context['context_entity_id']}:{memory_type}:messages"
        self.redis_client.zadd(sorted_set_key, {key: time.time()})

        return f"Key '{key}' created with value '{value}' and TTL {ttl}s."

    def short_memory_read(self, user_uuid, memory_context, n=None):
        """
        Reads a value from Redis or performs wildcard searches based on input parameters.
        If `n` is provided, fetches the latest `n` messages for the given context.
        If `n` is None, performs a wildcard search based on the provided memory_context.
        Supports fetching all `context_entity_id` values when not provided.
        """

        if n is not None:
            # Fetch the latest `n` messages
            context_id = memory_context.get('context_id', '*')
            context_entity_id = memory_context.get('context_entity_id', '*')
            memory_type = memory_context.get('memory_type', '*')

            # Generate the pattern for sorted set keys
            sorted_set_pattern = f"{user_uuid}:{context_id}:{context_entity_id}:{memory_type}:messages"

            # Find all matching sorted set keys
            cursor = 0
            sorted_set_keys = []
            while True:
                cursor, keys = self.redis_client.scan(cursor=cursor, match=sorted_set_pattern)
                sorted_set_keys.extend(keys)
                if cursor == 0:
                    break

            # Collect all keys and their timestamps from the sorted sets
            all_keys_with_scores = []
            for sorted_set_key in sorted_set_keys:
                keys_with_scores = self.redis_client.zrevrange(sorted_set_key, 0, -1, withscores=True)
                all_keys_with_scores.extend(keys_with_scores)

            # Sort all keys globally by timestamp (score) in descending order
            all_keys_with_scores.sort(key=lambda x: x[1], reverse=True)

            # Get the latest `n` keys
            latest_keys = [key_score[0] for key_score in all_keys_with_scores[:n]]

            # Fetch the corresponding values for the latest keys
            results = {}
            for key in latest_keys:
                value = self.redis_client.get(key)
                if value:
                    results[key.decode('utf-8')] = eval(value)

            return results if results else f"No messages found for the given context."

        else:
            context_id = memory_context.get('context_id', '*')
            context_entity_id = memory_context.get('context_entity_id', "*")
            memory_type = str(memory_context.get('memory_type', "*"))
            memory_id = memory_context.get('memory_id', "*")

            if memory_type != "*":
                self.validate_memory_type(memory_type)

            pattern = f"{user_uuid}:{context_id}:{context_entity_id}:{memory_type}:{memory_id}"

            cursor = 0
            matching_keys = []
            while True:
                cursor, keys = self.redis_client.scan(cursor=cursor, match=pattern)
                matching_keys.extend(keys)
                if cursor == 0:
                    break

            results = {}
            for key in matching_keys:
                key_type = self.redis_client.type(key).decode('utf-8')
                if key_type != 'string':
                    continue
                try:
                    value = self.redis_client.get(key)
                    if value:
                        results[key.decode('utf-8')] = eval(value)
                except self.redis_client.exceptions.ResponseError as e:
                    print(f"Error reading key {key.decode('utf-8')}: {e}")

            return results if results else f"No matching keys found for pattern '{pattern}'."


    def short_memory_update_quality(self, user_uuid, memory_context, new_memory_type):
        new_memory_type = str(new_memory_type)
        self.validate_memory_type(new_memory_type)

        old_memory_type = str(memory_context.get('memory_type', '1'))
        self.validate_memory_type(old_memory_type)

        old_key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            old_memory_type,
            memory_context['memory_id']
        )

        new_key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            new_memory_type,
            memory_context['memory_id']
        )

        old_value = self.redis_client.get(old_key)
        if not old_value:
            return f"Memory '{old_key}' not found."

        memory_data = eval(old_value)
        ttl = memory_data.get('cache_ttl', 3600)
        self.redis_client.set(new_key, str(memory_data), ttl)

        self.redis_client.delete(old_key)

        return f"Memory quality updated to '{new_memory_type}' and key migrated from '{old_key}' to '{new_key}'."

    def short_memory_update_value(self, user_uuid, memory_context, memory):
        """Updates specific fields of a key-value pair in Redis."""

        memory_type = str(memory_context.get('memory_type', '1'))
        self.validate_memory_type(memory_type)

        key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            memory_type,
            memory_context['memory_id']
        )

        current_value = self.redis_client.get(key)
        if not current_value:
            return f"Key '{key}' not found. Unable to update."

        current_memory = eval(current_value)

        updated_memory = {
            "query_text": memory.get("query_text", current_memory.get("query_text")),
            "response_text": memory.get("response_text", current_memory.get("response_text")),
            "memory_metadata": memory.get("memory_metadata", current_memory.get("memory_metadata")),
            "intent": memory.get("intent", current_memory.get("intent")),
            "entities": memory.get("entities", current_memory.get("entities")),
            "metadata": memory.get("metadata", current_memory.get("metadata")),
        }

        ttl = memory.get('cache_ttl', 3600)
        self.redis_client.set(key, str(updated_memory), ttl)

        return f"Key '{key}' updated successfully with value '{updated_memory}' and TTL {ttl}s."

    def write_memory(self, user_uuid, memory_context, memory, type="short_memory",max_conversations=5):
        """Creates a memory in Redis based on the type (episodic or short memory)."""

        memory_type_str = str(memory_context.get('memory_type', '1'))
        self.validate_memory_type(memory_type_str)

        key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            memory_type_str,
            memory_context['memory_id']
        )

        value = {
            "query_text": memory['query_text'],
            "response_text": memory['response_text'],
            "memory_metadata": [
                {
                    "time": memory['time'],
                    "memory_id": memory_context['memory_id'],
                    "context_id": memory_context['context_id'],
                }
            ],
            "intent": memory.get("intent", ""),
            "entities": memory.get("entities", []),
            "metadata": memory.get("metadata", {}),
        }

        ttl = memory.get('cache_ttl', 3600)

        if type == "episodic_memory":
            # Existing episodic memory logic (key-value storage)
            if self.redis_client.exists(key):
                raise ValueError(f"Key '{key}' already exists. Cannot create a new value for the same key.")

            self.redis_client.set(key, json.dumps(value), ex=ttl)

            sorted_set_key = f"{user_uuid}:{memory_context['context_id']}:{memory_context['context_entity_id']}:{memory_type_str}:messages"
            self.redis_client.zadd(sorted_set_key, {key: time.time()})

            return f"Episodic Memory: Key '{key}' created with value '{value}' and TTL {ttl}s."

        elif type == "short_memory":
            # New short memory logic (bucket-style list)
            bucket_key = f"{user_uuid}:{memory_context['context_id']}:{memory_context['context_entity_id']}:{memory_type_str}:conversation"

            # Convert value to JSON string for Redis list storage
            self.redis_client.rpush(bucket_key, json.dumps(value))

            # Keep only the latest 'max_conversations' entries
            self.redis_client.ltrim(bucket_key, -max_conversations, -1)

            # Set TTL for short-term memory bucket
            self.redis_client.expire(bucket_key, ttl)

            return f"Short Memory: Added conversation entry to '{bucket_key}' created with value '{value}'  with TTL {ttl}s."

        else:
            raise ValueError(f"Invalid memory type: {type}. Supported: 'episodic_memory', 'short_memory'")


    def read_memory(self, user_uuid, memory_context, type="short_memory", n=None):
        """
        Reads memory based on type:
        - If `type="episode"`, performs wildcard search as usual.
        - If `type="short"`, fetches only the last message by default.
        - If `n` is negative, fetches the last `|n|` messages (up to 5 max).
        """

        memory_type = str(memory_context.get('memory_type', "*"))
        context_id = memory_context.get('context_id', '*')
        context_entity_id = memory_context.get('context_entity_id', '*')
        if type == "short_memory":
            # Default to last 1 conversation if `n` is not provided
            if n is None:
                n = 1
            elif n < 0:
                n = min(abs(n), 5)  # Ensure n does not exceed 5

            bucket_key = f"{user_uuid}:{context_id}:{context_entity_id}:{memory_type}:conversation"
            latest_conversations = self.redis_client.lrange(bucket_key, -n, -1)

            results = [json.loads(conv.decode('utf-8')) for conv in
                       latest_conversations] if latest_conversations else "No recent conversations found."
            return results

        elif type == "episodic_memory":  # episodic memory behavior
            sorted_set_key = f"{user_uuid}:{context_id}:{context_entity_id}:{memory_type}:messages"
            matching_keys = self.redis_client.zrevrange(sorted_set_key, 0, -1)

            if not matching_keys:
                return f"No matching keys found for pattern '{sorted_set_key}'."

            results = {}
            for key in matching_keys:
                key = key.decode('utf-8')
                value = self.redis_client.get(key)
                if value:
                    results[key] = json.loads(value)

            return results if results else f"No matching memories found under '{sorted_set_key}'."

