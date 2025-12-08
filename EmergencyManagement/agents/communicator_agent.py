import requests
import torch
from typing import Dict, Any
import logging
from utils.text_utils import TextProcessor
from utils.ollama_utils import OllamaClient

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def print_gpu_utilization():
    """Print current GPU utilization."""
    if torch.cuda.is_available():
        logger.debug(f"GPU Memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
        logger.debug(f"GPU Memory cached: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

class CommunicatorAgent:
    def __init__(self):
        """Initialize the Communicator Agent with language model."""
        try:
            self.ollama_client = OllamaClient()
        except Exception as e:
            logger.error(f"Error initializing Communicator Agent: {str(e)}")
            raise

    def generate_report(self, scout_results, plan_results):
        """Generate a comprehensive report based on scout and plan results."""
        try:
            logger.info("Starting report generation...")
            
            # Validate inputs
            if not scout_results or not plan_results:
                logger.error("Missing required input data")
                return {
                    "report": "Error: Missing required analysis data"
                }
            
            # Format report prompt
            logger.info("Formatting report prompt...")
            report_prompt = self._format_report_prompt(scout_results, plan_results)
            logger.info(f"Report prompt length: {len(report_prompt)} characters")
            
            # Generate response
            logger.info("Generating report using Mixtral...")
            response = self.ollama_client.generate_response(
                model="mixtral:latest",
                prompt=report_prompt,
                max_tokens=2000  # Increased significantly for comprehensive reports
            )
            
            logger.info("Report generated successfully")
            return {
                "report": response
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return a basic report if LLM fails
            return {
                "report": self._create_basic_report(scout_results, plan_results)
            }

    def _format_report_prompt(self, scout_results, plan_results):
        """Format scout and plan results into a comprehensive report prompt."""
        prompt = """As an emergency response coordinator, create a detailed emergency response report based on this disaster scene analysis:

SCENE ANALYSIS:
"""
        
        # Add terrain analysis
        terrain_data = scout_results.get("terrain_data", {})
        terrain_analysis = terrain_data.get("terrain_analysis", {})
        
        for category, items in terrain_analysis.items():
            if items:
                prompt += f"\n{category.title()}:\n"
                for item in items:
                    confidence = item.get('confidence', 0)
                    area = item.get('area_m2', 0)
                    prompt += f"- {item['class']} (Confidence: {confidence:.2f})"
                    if area > 0:
                        prompt += f" - Area: {area:.2f} m²"
                    prompt += "\n"
        
        # Add plan details
        prompt += "\nRESPONSE PLAN:\n"
        prompt += plan_results.get("plan", "No plan available")
        
        prompt += """

Create a comprehensive emergency response report that includes:

1. Emergency Response Assessment:
   - Current situation and immediate threats
   - Access and evacuation challenges
   - Resource deployment needs
   - Safety concerns for responders and victims

2. Required Emergency Resources:
   - Specific rescue equipment needed (e.g., helicopters, boats, heavy machinery)
   - Medical response teams and supplies
   - Evacuation vehicles and routes
   - Communication and coordination systems

3. Immediate Response Actions:
   - Evacuation procedures and routes
   - Search and rescue operations
   - Medical triage and treatment
   - Scene security and hazard control

4. Team Deployment:
   - Rescue team assignments and locations
   - Medical response team positions
   - Security and perimeter control
   - Resource management coordination

Focus on:
- Specific rescue and evacuation methods needed
- Required emergency vehicles and equipment
- Clear team assignments and responsibilities
- Safety protocols for responders
- Communication and coordination procedures
"""
        return prompt

    def _create_basic_report(self, scout_results, plan_results):
        """Create a basic report when LLM generation fails."""
        report = "Emergency Response Report\n"
        report += "=====================\n\n"
        
        # Add scene analysis
        report += "Scene Analysis:\n"
        report += scout_results["analysis"] + "\n\n"
        
        # Add detected objects
        report += "Detected Objects:\n"
        for category, items in scout_results["terrain_data"]["terrain_analysis"].items():
            if items:
                report += f"\n{category.title()}:\n"
                for item in items:
                    confidence = item.get('confidence', 0)
                    area = item.get('area_m2', 0)
                    report += f"- {item['class']} (Confidence: {confidence:.2f}, Area: {area:.2f}m²)\n"
        
        # Add response plan
        report += "\nResponse Plan:\n"
        report += plan_results["plan"] + "\n\n"
        
        # Add basic recommendations
        report += "Emergency Response Priorities:\n"
        report += "1. Secure the area and establish safe perimeter\n"
        report += "2. Assess immediate threats to personnel and victims\n"
        report += "3. Deploy rescue teams with appropriate equipment\n"
        report += "4. Monitor situation and adjust response as needed\n"
        
        return report

    def generate_comprehensive_report(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive report from the plan data."""
        # Enhance the report using Mistral
        prompt = f"""
        As a disaster response communicator, create a clear and concise field report based on this data:
        
        Terrain Analysis:
        {plan_data.get('terrain_description', 'No terrain analysis available')}
        
        Response Plan:
        {plan_data.get('response_plan', 'No response plan available')}
        
        Safety Notes:
        {plan_data.get('safety_notes', 'No safety notes available')}
        
        Recommended Actions:
        {plan_data.get('recommended_actions', 'No recommended actions available')}
        
        Format the report to be clear and actionable for field responders.
        """
        
        # Get enhanced report from Mistral
        enhanced_report = self._get_llm_report(prompt)
        
        # Format the final report
        final_report = self.text_processor.format_report({
            "terrain_description": plan_data.get('terrain_description', ''),
            "response_plan": enhanced_report,
            "safety_notes": plan_data.get('safety_notes', ''),
            "recommended_actions": plan_data.get('recommended_actions', '')
        })
        
        return {
            "report": final_report,
            "audio_file": self._generate_audio(final_report)
        }

    def _generate_audio(self, report: str) -> str:
        """Generate audio version of the report."""
        output_file = "field_report.mp3"
        self.text_processor.text_to_speech(report, output_file)
        return output_file

    def _get_llm_report(self, prompt: str) -> str:
        """Get comprehensive report from Mixtral model via Ollama."""
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
                        "num_ctx": 4096,
                        "num_predict": 500,  # Increased for more detailed report
                        "repeat_penalty": 1.1,
                        "repeat_last_n": 64,
                        "seed": 42
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Error getting LLM report: {e}")
            return "Error: Could not generate emergency response report" 