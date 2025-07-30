import anthropic
from openai import OpenAI
import google.generativeai as genai
import os
from groq import Groq
import base64
from io import BytesIO
import tiktoken

class Modellake:
    def __init__(self, model_config):
        self.model_provider = model_config.get("model_provider", "openai")
        self.model_name = model_config.get("model_name", "gpt-3.5-turbo")
        self.api_key = model_config.get("api_key", None)

        if self.model_provider == "openai":
            self.client = OpenAI(api_key=self.api_key)
        elif self.model_provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=self.api_key)
        elif self.model_provider == "google":
            self.client = genai.GenerativeModel(self.model_name)
        elif self.model_provider == "groq":
            self.client = Groq(api_key=self.api_key)
        elif self.model_provider == "deepseek":
            self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key)

    def openAI_model(self, messages, token_size=None, model_name=None):
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=model_name,
                max_tokens=token_size,
                temperature=0.5,
            )
            usage = chat_completion.usage

            return {
                "answer": chat_completion.choices[0].message.content.strip(),
                "input_tokens": usage.prompt_tokens if usage else None,
                "output_tokens": usage.completion_tokens if usage else None,
                "total_tokens": usage.total_tokens if usage else None
            }

        except Exception as e:
            return {"error": str(e)}

    def gemini_model(self, messages, token_size=None, model_name=None):
        try:
            GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
            if not GOOGLE_API_KEY:
                return {"error": "API key is missing. Please set GOOGLE_API_KEY as an environment variable."}

            genai.configure(api_key=GOOGLE_API_KEY)
            model_name = model_name or 'gemini-1.5-flash'
            model = genai.GenerativeModel(model_name)
            user_input = "\n".join([msg["content"] for msg in messages if msg["role"] == "user"])
            system_input = "\n".join([msg["content"] for msg in messages if msg["role"] == "system"])
            final_message = f"System message:{system_input} User message:{user_input}"
            response = model.generate_content(final_message, generation_config={"max_output_tokens": token_size})
            token_usage = response.usage_metadata
            return {
                "answer": response.text.strip(),
                "input_tokens": token_usage.prompt_token_count if token_usage else None,
                "output_tokens": token_usage.candidates_token_count if token_usage else None,
                "total_tokens": (
                            token_usage.prompt_token_count + token_usage.candidates_token_count) if token_usage else None
            }

        except Exception as e:
            return str(e)

    def deepseek_model(self, messages, token_size=None, model_name=None):
        try:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                return {"error": "API key is missing. Please set DEEPSEEK_API_KEY as an environment variable."}

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            model_name = model_name
            completion = client.chat.completions.create(
                extra_headers={
                },
                extra_body={},
                model=model_name,
                max_tokens=token_size,
                messages=messages
            )

            response = completion.choices[0].message.content
            if hasattr(completion, "usage"):
                token_usage = completion.usage
                input_tokens = getattr(token_usage, "prompt_tokens", 0)
                output_tokens = getattr(token_usage, "completion_tokens", 0)
                total_tokens = getattr(token_usage, "total_tokens", input_tokens + output_tokens)
            else:
                input_tokens = output_tokens = total_tokens = None

            return {

                "answer": response,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }

        except Exception as e:
            return str(e)

    def llama_model(self, messages, token_size=None, model_name=None):
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return {"error": "API key is missing. Please set GROQ_API_KEY as an environment variable."}

            client = Groq(api_key=api_key)

            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=1,
                max_tokens=token_size,
                top_p=1,
                stream=False
            )

            response_text = completion.choices[0].message.content.strip()
            input_tokens = getattr(completion.usage, "prompt_tokens", 0)
            output_tokens = getattr(completion.usage, "completion_tokens", 0)
            total_tokens = getattr(completion.usage, "total_tokens", input_tokens + output_tokens)

            return {
                "answer": response_text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
        except Exception as e:
            return str(e)

    def claude_model(self, messages, token_size=None, model_name=None):
        try:
            api_key = os.getenv("ANTROPHIC_API_KEY")
            if not api_key:
                return {"error": "API key is missing. Please set ANTROPHIC_API_KEY as an environment variable."}

            client = anthropic.Anthropic(api_key=api_key)

            msg_list = [msg for msg in messages if msg.get("role") == "user"]

            response = client.messages.create(
                model=model_name,
                max_tokens=token_size,
                messages=msg_list
            )

            model_response = response.content[0].text

            input_tokens = getattr(response.usage, "input_tokens", 0)
            output_tokens = getattr(response.usage, "output_tokens", 0)
            total_tokens = input_tokens + output_tokens

            return {
                "answer": model_response.strip(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
        except Exception as e:
            return str(e)

    def chat_complete(self, payload):
        model_name = payload.get("model_name", "gpt-3.5-turbo").strip().lower()
        messages = payload.get("messages", [])
        token_size = payload.get("max_tokens", 150)

        self.valid_models = {
            "openai": {"gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"},
            "gemini": {"gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-1.5-pro-latest"},
            "deepseek": {"deepseek/deepseek-r1:free", "deepseek/deepseek-r1:8b", "deepseek/deepseek-r1:7b",
                         "deepseek/deepseek-r1:67b"},
            "llama": {"llama3-70b-8192", "llama3-8b", "llama3-70b"},
            "claude": {"claude-3-5-sonnet-20241022", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"},
        }

        try:
            if "gpt" in model_name:
                return self.openAI_model(messages, token_size, model_name)
            elif "gemini" in model_name:
                return self.gemini_model(messages, token_size, model_name)
            elif "deepseek" in model_name:
                return self.deepseek_model(messages, token_size, model_name)
            elif "llama" in model_name:
                return self.llama_model(messages, token_size, model_name)
            elif "claude" in model_name:
                return self.claude_model(messages, token_size, model_name)
        except Exception as e:
            return {"error": str(e)}
    
    def get_embedding(self, payload):
        """
        Generate embeddings for the given text.
        
        :param text: Text to generate embeddings for
        :return: List of floats representing the embedding vector
        """
        model_provider = payload.get("model_provider", "openai")
        if model_provider == "openai":
            return self._openai_embedding(payload)
        else:
            raise NotImplementedError(f"Provider '{self.provider}' is not supported yet.")

    def _openai_embedding(self, payload):
        """
        Generate embeddings using OpenAI's API.
        
        :param text: Text to generate embeddings for
        :return: List of floats representing the embedding vector
        """
        text = payload.get("chunks", "")
        model_name = payload.get("model_name", "text-embedding-3-small")
        try:
            # Handle both new and old OpenAI client versions
            if hasattr(self.client, 'embeddings'):
                # New version
                response = self.client.embeddings.create(
                    model=model_name,
                    input=text
                )
                embedding = response.data[0].embedding
            else:
                # Old version
                response = self.client.Embedding.create(
                    model=model_name,
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

    def get_batch_embeddings(self, payload):
        """
        Generate embeddings for multiple texts in one API call.
        
        :param texts: List of texts to generate embeddings for
        :return: List of embedding vectors
        """
        model_provider = payload.get("model_provider", "openai")
        model_name = payload.get("model_name", "text-embedding-3-small")
        vector_dimension = payload.get("vector_dimension", 1536)
        texts = payload.get("chunks", "")

        model_provider = model_provider.lower()

        if model_provider == "openai":
            try:
                # Handle both new and old OpenAI client versions
                if hasattr(self.client, 'embeddings'):
                    # New version
                    response = self.client.embeddings.create(
                        model=model_name,
                        input=texts
                    )
                    embeddings = [data.embedding for data in response.data]
                else:
                    # Old version
                    response = self.client.Embedding.create(
                        model=model_name,
                        input=texts
                    )
                    embeddings = [data['embedding'] for data in response['data']]

                # Validate dimensions
                for i, emb in enumerate(embeddings):
                    if len(emb) != vector_dimension:
                        raise ValueError(
                            f"Generated embedding dimension ({len(emb)}) for text {i} "
                            f"does not match configured dimension ({vector_dimension})"
                        )

                return embeddings

            except Exception as e:
                raise RuntimeError(f"Error generating batch embeddings with OpenAI: {str(e)}")
        else:
            raise NotImplementedError(f"Batch embeddings not implemented for provider '{model_provider}'")
        
    def file_audio_transcription(self, payload):
        model_name = payload.get("model_name", "gpt-4o-transcribe")
        audio_file = payload.get("audio_file", "")
        response_format = payload.get("response_format", "text")

        audio_file = open(audio_file, "rb")

        transcription = self.client.audio.transcriptions.create(
            model=model_name, 
            file=audio_file, 
            response_format=response_format
        )

        return transcription
    
    def base64_audio_transcription(self, payload):
        model_name = payload.get("model_name", "gpt-4o-transcribe")
        audio_base64 = payload.get("audio_base64", "")
        audio_bytes = base64.b64decode(audio_base64)
        audio_file = BytesIO(audio_bytes)
        file_type = payload.get("file_type", "mp3")
        response_format = payload.get("response_format", "text")
        audio_file.name = f"audio.{file_type}" 

        if file_type not in ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]:
            raise ValueError(f"Unsupported audio format: {file_type}")

        transcription = self.client.audio.transcriptions.create(
            model=model_name, 
            file=audio_file, 
            response_format=response_format
        )

        return transcription
    
    def bytes_audio_transcription(self, payload):
        model_name = payload.get("model_name", "gpt-4o-transcribe")
        audio_bytes = payload.get("audio_bytes", "")
        file_type = payload.get("file_type", "mp3")
        response_format = payload.get("response_format", "text")
        audio_file = BytesIO(audio_bytes)
        audio_file.name = f"audio.{file_type}" 

        if file_type not in ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]:
            raise ValueError(f"Unsupported audio format: {file_type}")

        transcription = self.client.audio.transcriptions.create(
            model=model_name, 
            file=audio_file, 
            response_format=response_format
        )

        return transcription
    
    def base64_image_summarize(self, payload):
        base64_image = payload.get("base64_image", "")
        model_name = payload.get("model_name", "gpt-4o")
        file_type = payload.get("file_type", "png")
        data_url = f"data:image/{file_type};base64,{base64_image}"  # Adjust MIME if needed

        if file_type == "jpg":
            file_type = "jpeg"
        elif file_type not in ["png", "jpeg", "gif", "webp"]:
            raise ValueError(f"Unsupported image type for OpenAI: {file_type}")

        # Optionally validate base64
        try:
            base64.b64decode(base64_image)
        except Exception:
            raise ValueError("Invalid Base64-encoded image data")

        response = self.client.chat.completions.create(
            model=model_name,  # or "gpt-4-turbo" with vision support
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Summarize the content of this image."},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ]
        )

        return response.choices[0].message.content
    
    def base64_image_metadata(self, payload):
        base64_image = payload.get("base64_image", "")
        model_name = payload.get("model_name", "gpt-4o")
        file_type = payload.get("file_type", "png")
        prompt_metadata = payload.get("prompt_metadata", "")
        data_url = f"data:image/{file_type};base64,{base64_image}"  # Adjust MIME if needed

        if file_type == "jpg":
            file_type = "jpeg"
        elif file_type not in ["png", "jpeg", "gif", "webp"]:
            raise ValueError(f"Unsupported image type for OpenAI: {file_type}")

        # Optionally validate base64
        try:
            base64.b64decode(base64_image)
        except Exception:
            raise ValueError("Invalid Base64-encoded image data")

        response = self.client.chat.completions.create(
            model=model_name,  # or "gpt-4-turbo" with vision support
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_metadata},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ]
        )

        return response.choices[0].message.content
    
    def clean_llm_output(self, llm_output: str) -> str:
        llm_output = llm_output.strip()

        # Remove Markdown-style code block wrapper like ```json or ```python
        if llm_output.startswith("```json"):
            llm_output = llm_output[len("```json"):].strip()
        elif llm_output.startswith("```python"):
            llm_output = llm_output[len("```python"):].strip()
        elif llm_output.startswith("```"):
            llm_output = llm_output[len("```"):].strip()

        if llm_output.endswith("```"):
            llm_output = llm_output[:-3].strip()

        return llm_output

    def calculate_model_cost(self, payload):

        MODEL_PRICING = {
            # GPT-4 series
            "gpt-4o": {"input": 0.005, "output": 0.015},            # per 1K tokens
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-32k": {"input": 0.06, "output": 0.12},

            # GPT-3.5 series
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
            "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},

            # GPT-4 Turbo (latest versions via `gpt-4-turbo` alias)
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},

            # Text Embedding models (input only)
            "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
            "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
            "text-embedding-ada-002": {"input": 0.0001, "output": 0.0},

            # InstructGPT (deprecated but still used)
            "text-davinci-003": {"input": 0.02, "output": 0.02},
            "text-curie-001": {"input": 0.002, "output": 0.002},
            "text-babbage-001": {"input": 0.0005, "output": 0.0005},
            "text-ada-001": {"input": 0.0004, "output": 0.0004},

            # Code models
            "code-davinci-002": {"input": 0.10, "output": 0.10},
            "code-cushman-001": {"input": 0.02, "output": 0.02},
        }


        model_name = payload.get("model_name", "gpt-4o")
        input_tokens = payload.get("input_tokens", 0)
        output_tokens = payload.get("output_tokens", 0)
        total_tokens = input_tokens + output_tokens
        
        if model_name in MODEL_PRICING:
            input_cost = MODEL_PRICING[model_name]["input"] * (input_tokens / 1000)
            output_cost = MODEL_PRICING[model_name]["output"] * (output_tokens / 1000)
            total_cost = input_cost + output_cost
        else:
            raise ValueError(f"Unsupported model: {model_name}")

        return {
            "model_name": model_name,
            "input_tokens": input_tokens if input_tokens else 0,
            "output_tokens": output_tokens if output_tokens else 0,
            "total_cost": total_cost if total_cost else 0,
            "input_cost": input_cost if input_cost else 0,
            "output_cost": output_cost if output_cost else 0,
            "total_tokens": total_tokens if total_tokens else 0
        }

    def estimate_model_tokens(self, text, model="gpt-4o"):
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))




