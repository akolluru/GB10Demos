import requests
import logging
import json
import time

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Changed from INFO to WARNING
logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        """Initialize the Ollama client."""
        self.base_url = "http://localhost:11434/api/generate"
        self.timeout = 120  # Increased timeout for LLM inference (2 minutes)
        self.max_retries = 3
        self.logger = logging.getLogger(__name__)
        
    def generate_response(self, model: str, prompt: str, max_tokens: int = 200) -> str:
        """Generate a response from the Ollama model."""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Generating response from {model} model...")
                self.logger.info(f"Prompt length: {len(prompt)} characters")
                
                # Check if Ollama server is running
                try:
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    response.raise_for_status()
                    available_models = response.json().get("models", [])
                    self.logger.info(f"Available models: {[m['name'] for m in available_models]}")
                    
                    if not any(m['name'] == model for m in available_models):
                        self.logger.error(f"Model {model} not found in available models")
                        raise ValueError(f"Model {model} not found. Please ensure it's pulled using 'ollama pull {model}'")
                except requests.exceptions.ConnectionError:
                    self.logger.error("Could not connect to Ollama server. Is it running?")
                    raise RuntimeError("Ollama server is not running. Please start it using 'ollama serve'")
                
                # Make the generation request
                self.logger.info(f"Sending request to Ollama with model {model}...")
                response = requests.post(
                    self.base_url,
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40,
                            "num_ctx": 4096,  # Increased context window for longer reports
                            "num_predict": max_tokens,
                            "repeat_penalty": 1.1,
                            "repeat_last_n": 64,
                            "seed": 42
                        }
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                self.logger.info("Successfully generated response")
                return result["response"]
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    logger.debug(f"Request timed out (attempt {attempt + 1}/{self.max_retries}), retrying...")
                else:
                    logger.warning(f"Request timed out after {self.max_retries} attempts")
                    raise RuntimeError("Request timed out after multiple attempts")
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Failed to connect to Ollama server: {str(e)}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Ollama server error: {error_msg}")
                logger.error(f"Error type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise RuntimeError(f"Ollama server error: {error_msg}")
            
            # Wait before retrying
            time.sleep(1)
            
    def list_models(self):
        """List available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/tags")
            response.raise_for_status()
            return response.json()["models"]
        except Exception as e:
            self.logger.error(f"Error listing Ollama models: {str(e)}")
            raise
            
    def check_model_availability(self, model_name):
        """Check if a specific model is available."""
        try:
            models = self.list_models()
            return any(model["name"] == model_name for model in models)
        except Exception as e:
            self.logger.error(f"Error checking model availability: {str(e)}")
            return False 