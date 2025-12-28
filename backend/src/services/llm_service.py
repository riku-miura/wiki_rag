import json
import logging
import requests
from typing import Generator, Optional, Dict, List
from ..models.query import Query

class LLMService:
    def __init__(self, ollama_base_url: str = "http://localhost:11434", model: str = "llama3.2:3b-instruct"):
        self.base_url = ollama_base_url
        self.model = model
        self.logger = logging.getLogger(__name__)

    def _generate_prompt(self, query: str, context: str) -> str:
        """
        Generates a prompt for the LLM using the RAG context and user query.
        """
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful assistant that answers questions based strictly on the provided Wikipedia context.
If the answer is not in the context, say "I cannot answer this based on the provided context."
Do not use outside knowledge.

Context:
{context}

<|eot_id|><|start_header_id|>user<|end_header_id|>

{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

    def check_health(self) -> bool:
        """Checks if Ollama is reachable."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except requests.RequestException:
            return False

    def stream_response(self, query: str, context: str) -> Generator[str, None, None]:
        """
        Streams the LLM response for a given query and context.
        Yields chunks of generated text.
        """
        prompt = self._generate_prompt(query, context)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.7,
                # "num_ctx": 4096 # Adjust based on context size if needed
            }
        }

        try:
            with requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True
            ) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        self.logger.error(f"Failed to decode JSON chunk: {line}")
                        continue

        except requests.RequestException as e:
            self.logger.error(f"Error calling Ollama: {str(e)}")
            yield f"Error: Could not generate response from LLM. {str(e)}"

    def generate_response(self, query: str, context: str) -> Optional[str]:
        """
        Non-streaming version of response generation.
        """
        response_text = ""
        for chunk in self.stream_response(query, context):
            response_text += chunk
        return response_text
