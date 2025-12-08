import requests
import torch
from typing import Dict, Any, List
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def print_gpu_utilization():
    """Print current GPU utilization."""
    if torch.cuda.is_available():
        logger.debug(f"GPU Memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
        logger.debug(f"GPU Memory cached: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

class PlannerAgent:
    def __init__(self):
        # Force CUDA device
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available. Please check your GPU installation.")
        
        self.device = torch.device("cuda")
        self.ollama_base_url = "http://localhost:11434/api/generate"
        self.model_name = "phi:latest"  # Using phi:latest for faster planning
        
        # Clear GPU memory
        torch.cuda.empty_cache()
        print_gpu_utilization()

    def create_plan(self, scout_results):
        """Create a concise response plan based on scout analysis."""
        try:
            # Format plan prompt
            plan_prompt = self._format_plan_prompt(scout_results)
            
            # Generate response with reduced max_tokens
            response = self._get_llm_plan(plan_prompt)
            
            return {
                "plan": response
            }
            
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            return {
                "plan": "Basic Response Plan:\n1. Assess immediate hazards\n2. Secure the area\n3. Provide assistance to detected persons\n4. Monitor the situation"
            }

    def _format_plan_prompt(self, scout_results):
        """Format scout results into a concise plan prompt."""
        prompt = """As an emergency response coordinator, create a specific action plan based on this disaster scene analysis:

SCENE ANALYSIS:
"""
        
        # Add key findings
        terrain_data = scout_results.get("terrain_data", {})
        terrain_analysis = terrain_data.get("terrain_analysis", {})
        
        for category, items in terrain_analysis.items():
            if items:
                prompt += f"\n{category.title()}: "
                items_list = [f"{item['class']}" for item in items]
                prompt += ", ".join(items_list) + "\n"
        
        prompt += """
Create a detailed emergency response plan that includes:

1. Immediate Actions (Next 6-8 hours):
   - Specific rescue operations needed
   - Exact evacuation procedures
   - Precise hazard control measures
   - Resource deployment locations

2. Required Resources:
   - Specific equipment needed (e.g., "2 rescue helicopters", "3 medical teams")
   - Exact number of personnel required
   - Specific vehicles and access routes
   - Communication systems needed

3. Team Assignments:
   - Rescue Team: Specific tasks and locations
   - Medical Team: Triage points and treatment areas
   - Security Team: Perimeter control points
   - Resource Team: Supply distribution points
   - Communication Team: Command post locations

4. Priority Actions:
   - List specific tasks in order of priority
   - Include exact locations for each action
   - Specify timeframes for critical operations
   - Detail safety measures for each task

Format the response as a clear, actionable plan with specific numbers, locations, and timeframes. Focus on concrete actions rather than general guidelines."""

        return prompt

    def _format_terrain_analysis(self, terrain_analysis: Dict[str, List[Dict]]) -> str:
        """Format terrain analysis data into a detailed text description."""
        analysis_parts = []
        
        # Process each category
        for category, items in terrain_analysis.items():
            if items:
                analysis_parts.append(f"\n{category.title()}:")
                for item in items:
                    confidence = item.get('confidence', 0)
                    area = item.get('area_m2', 0)
                    class_name = item.get('class', 'Unknown')
                    
                    item_desc = f"- {class_name} (Confidence: {confidence:.2f})"
                    if area > 0:
                        item_desc += f" - Area: {area:.2f} m²"
                    analysis_parts.append(item_desc)
        
        return "\n".join(analysis_parts)

    def _get_llm_plan(self, prompt: str) -> str:
        """Get response plan from Gemma model via Ollama."""
        try:
            response = requests.post(
                self.ollama_base_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_ctx": 2048,
                        "num_predict": 500,  # Increased for more detailed plan
                        "repeat_penalty": 1.1,
                        "repeat_last_n": 64,
                        "seed": 42
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Error getting LLM plan: {e}")
            return "Error: Could not generate response plan"

    def _extract_safety_notes(self, plan: str) -> str:
        """Extract safety-related information from the plan."""
        prompt = f"""
        Extract only the safety-related information from this response plan:
        {plan}
        
        Focus on:
        - Hazards
        - Safety protocols
        - Risk assessments
        """
        
        try:
            response = requests.post(
                self.ollama_base_url,
                json={
                    "model": "phi",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error extracting safety notes: {e}")
            return "Error: Could not extract safety notes"

    def _extract_actions(self, plan: str) -> str:
        """Extract actionable items from the plan."""
        prompt = f"""
        Extract only the actionable items from this response plan:
        {plan}
        
        Format as a numbered list of specific actions to take.
        """
        
        try:
            response = requests.post(
                self.ollama_base_url,
                json={
                    "model": "phi",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error extracting actions: {e}")
            return "Error: Could not extract recommended actions" 