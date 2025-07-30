import os
from typing import Dict, Any, List
from openai import OpenAI

class Embeddings:
    def __init__(self, embeddings_config: Dict[str, Any]):
        """
        Initialize the Embeddings class with configuration.
        
        :param embeddings_config: Dictionary containing:
            - api_key: API key for the embedding provider
            - embedding_provider: Name of the embedding provider (e.g., "openai")
            - embedding_model: Model to use for embeddings (e.g., "text-embedding-ada-002")
            - vector_dimension: Dimension of the output vectors
        """
        self.api_key = embeddings_config.get('api_key') or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided either in config or as environment variable")

        self.provider = embeddings_config.get('embedding_provider', 'openai').lower()
        self.model = embeddings_config.get('embedding_model', 'text-embedding-ada-002')
        self.vector_dimension = embeddings_config.get('vector_dimension', 1536)  # OpenAI ada-002 default

        # Initialize OpenAI client with basic configuration
        if self.provider == 'openai':
            try:
                # First try with just api_key (newer versions)
                self.client = OpenAI(api_key=self.api_key)
            except TypeError:
                try:
                    # Fallback for older versions
                    import openai
                    openai.api_key = self.api_key
                    self.client = openai
                except Exception as e:
                    raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}")

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate the embedding configuration."""
        valid_providers = ['openai']  # Add more providers as they're implemented
        if self.provider not in valid_providers:
            raise ValueError(f"Unsupported embedding provider. Must be one of: {valid_providers}")

        # Provider-specific validation
        if self.provider == 'openai':
            valid_models = ['text-embedding-ada-002']
            if self.model not in valid_models:
                raise ValueError(f"Unsupported OpenAI model. Must be one of: {valid_models}")

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text.
        
        :param text: Text to generate embeddings for
        :return: List of floats representing the embedding vector
        """
        if self.provider == "openai":
            return self._openai_embedding(text)
        else:
            raise NotImplementedError(f"Provider '{self.provider}' is not supported yet.")

    def _openai_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings using OpenAI's API.
        
        :param text: Text to generate embeddings for
        :return: List of floats representing the embedding vector
        """
        try:
            # Handle both new and old OpenAI client versions
            if hasattr(self.client, 'embeddings'):
                # New version
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                embedding = response.data[0].embedding
            else:
                # Old version
                response = self.client.Embedding.create(
                    model=self.model,
                    input=text
                )
                embedding = response['data'][0]['embedding']

            # Validate embedding dimension
            if len(embedding) != self.vector_dimension:
                raise ValueError(
                    f"Generated embedding dimension ({len(embedding)}) "
                    f"does not match configured dimension ({self.vector_dimension})"
                )

            return embedding

        except Exception as e:
            raise RuntimeError(f"Error generating embeddings with OpenAI: {str(e)}")

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in one API call.
        
        :param texts: List of texts to generate embeddings for
        :return: List of embedding vectors
        """
        if self.provider == "openai":
            try:
                # Handle both new and old OpenAI client versions
                if hasattr(self.client, 'embeddings'):
                    # New version
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=texts
                    )
                    embeddings = [data.embedding for data in response.data]
                else:
                    # Old version
                    response = self.client.Embedding.create(
                        model=self.model,
                        input=texts
                    )
                    embeddings = [data['embedding'] for data in response['data']]

                # Validate dimensions
                for i, emb in enumerate(embeddings):
                    if len(emb) != self.vector_dimension:
                        raise ValueError(
                            f"Generated embedding dimension ({len(emb)}) for text {i} "
                            f"does not match configured dimension ({self.vector_dimension})"
                        )

                return embeddings

            except Exception as e:
                raise RuntimeError(f"Error generating batch embeddings with OpenAI: {str(e)}")
        else:
            raise NotImplementedError(f"Batch embeddings not implemented for provider '{self.provider}'")

# Example usage:
# config = {
#     "api_key": "sk-...",
#     "embedding_provider": "openai",
#     "embedding_model": "text-embedding-ada-002",
#     "vector_dimension": 1536
# }
# embeddings = Embeddings(embeddings_config=config)
# 
# # Single text embedding
# vector = embeddings.get_embedding("This is a test sentence.")
#
# # Batch embeddings
# vectors = embeddings.get_batch_embeddings(["First text", "Second text", "Third text"])
