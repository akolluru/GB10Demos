import logging
import torch
from utils.vision_utils import VisionProcessor
from utils.ollama_utils import OllamaClient
import gc
import numpy as np
import cv2
import os
import base64
import requests
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ScoutAgent:
    def __init__(self):
        """Initialize the Scout Agent with YOLO and SAM models."""
        try:
            # Initialize vision processor with caching
            self.vision_processor = VisionProcessor()
            
            # Initialize Ollama client with caching
            self.ollama_client = OllamaClient()
            self.ollama_base_url = "http://localhost:11434/api/generate"
            
            # Pre-warm the models
            self._pre_warm_models()
            
        except Exception as e:
            logger.error(f"Error initializing Scout Agent: {str(e)}")
            raise

    def _pre_warm_models(self):
        """Pre-warm the models to reduce inference time."""
        try:
            # Create a small dummy image
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            dummy_path = "dummy.jpg"
            cv2.imwrite(dummy_path, dummy_image)
            
            # Run a quick inference
            self.vision_processor.process_image(dummy_path)
            
            # Clean up
            os.remove(dummy_path)
            
        except Exception as e:
            logger.warning(f"Pre-warming models failed: {str(e)}")

    def analyze_scene(self, image_path: str) -> Dict[str, Any]:
        """Analyze the scene using LLM vision capabilities."""
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create prompt for scene analysis
            prompt = """Analyze this emergency/disaster scene image and provide a detailed assessment. Focus on:

1. Scene Description:
   - Overall situation and environment
   - Visible hazards and dangers
   - Access points and obstacles
   - Weather and lighting conditions

2. Detected Elements:
   - People and their conditions
   - Vehicles and equipment
   - Structures and buildings
   - Natural features and terrain
   - Signs of damage or destruction

3. Emergency Response Needs:
   - Immediate rescue requirements
   - Access and evacuation challenges
   - Required equipment and resources
   - Safety concerns for responders

Format the response in a clear, structured way that can be used for emergency response planning."""

            # Generate response using LLM with image
            response = requests.post(
                self.ollama_base_url,
                json={
                    "model": "llava:latest",  # Using LLaVA for vision capabilities
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_ctx": 4096,
                        "num_predict": 500,
                        "repeat_penalty": 1.1,
                        "repeat_last_n": 64,
                        "seed": 42
                    }
                }
            )
            response.raise_for_status()
            analysis = response.json()["response"]

            # Create visualization using the original image
            img = cv2.imread(image_path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                img = None

            return {
                "analysis": analysis,
                "visualization": img,
                "terrain_data": {
                    "terrain_analysis": {
                        "people": [{"class": "person", "confidence": 1.0}],
                        "vehicles": [{"class": "vehicle", "confidence": 1.0}],
                        "structures": [{"class": "building", "confidence": 1.0}]
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error in scene analysis: {str(e)}")
            return {
                "analysis": "Error: Could not analyze scene",
                "visualization": None,
                "terrain_data": {
                    "terrain_analysis": {}
                }
            }

    def _format_analysis_prompt(self, terrain_analysis):
        """Format terrain analysis data into a concise prompt."""
        prompt = """You are an emergency response analyst. Analyze this disaster scene and provide a brief assessment focusing on rescue operations and emergency response.

Detected Elements:
"""
        
        # Add detected objects by category
        for category, items in terrain_analysis.items():
            if items:
                prompt += f"{category.title()}: "
                items_list = [f"{item['class']} ({item.get('confidence', 0):.2f})" for item in items]
                prompt += ", ".join(items_list) + "\n"
        
        prompt += """
Provide a brief emergency response assessment covering:

1. Critical Scene Elements:
   - Impact on rescue operations
   - Access points for emergency teams
   - Resource deployment considerations

2. Immediate Hazards:
   - Risks to rescue personnel
   - Threats to victims
   - Environmental dangers

3. Priority Actions:
   - First responder safety measures
   - Victim rescue procedures
   - Resource allocation needs
"""
        return prompt

    def _create_basic_analysis(self, terrain_analysis):
        """Create a basic analysis from terrain data when LLM fails."""
        analysis = "Emergency Response Scene Assessment:\n\n"
        
        # Add detected objects by category
        for category, items in terrain_analysis.items():
            if items:
                analysis += f"{category.title()}:\n"
                for item in items:
                    confidence = item.get('confidence', 0)
                    area = item.get('area_m2', 0)
                    analysis += f"- {item['class']} (Confidence: {confidence:.2f}, Area: {area:.2f}m²)\n"
        
        analysis += "\nEmergency Response Priorities:\n"
        analysis += "1. Secure the area and establish a safe perimeter for rescue operations\n"
        analysis += "2. Assess immediate threats to rescue personnel and victims\n"
        analysis += "3. Identify and clear access routes for emergency teams\n"
        analysis += "4. Deploy appropriate rescue resources based on scene assessment\n"
        
        return analysis

    def get_detailed_analysis(self, image_path):
        """Get a comprehensive analysis of the scene."""
        try:
            # Get basic scene analysis
            scene_analysis = self.analyze_scene(image_path)
            
            # Get additional image analysis
            image_analysis = self.vision_processor.process_image(image_path)
            
            # Combine analyses
            return {
                "scene_analysis": scene_analysis,
                "image_analysis": image_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in get_detailed_analysis: {str(e)}")
            raise 