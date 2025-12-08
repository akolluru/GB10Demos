import pyttsx3
import json
from typing import Dict, Any

class TextProcessor:
    def __init__(self):
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume (0-1)

    def format_report(self, data: Dict[str, Any]) -> str:
        """Format the analysis data into a readable report."""
        report = f"""
DISASTER RESPONSE FIELD REPORT
=============================

TERRAIN ANALYSIS:
----------------
{data.get('terrain_description', 'No terrain analysis available')}

PLANNED RESPONSE:
----------------
{data.get('response_plan', 'No response plan available')}

SAFETY CONSIDERATIONS:
---------------------
{data.get('safety_notes', 'No safety notes available')}

RECOMMENDED ACTIONS:
-------------------
{data.get('recommended_actions', 'No recommended actions available')}
"""
        return report

    def text_to_speech(self, text: str, output_file: str = None):
        """Convert text to speech and optionally save to file."""
        if output_file:
            self.tts_engine.save_to_file(text, output_file)
            self.tts_engine.runAndWait()
        else:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    def save_report(self, report: str, filename: str):
        """Save the report to a JSON file."""
        data = {
            "report": report,
            "timestamp": "2024-05-27T11:00:00Z",  # This should be dynamic in production
            "version": "1.0"
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2) 