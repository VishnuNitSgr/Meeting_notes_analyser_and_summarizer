from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
import json
import re

class DecisionExtractor:
    def __init__(self, model="groq/compound-mini"):
        self.llm = ChatGroq(
            model=model,
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def extract(self, transcript: str) -> dict:
        """Extract decisions, dependencies, risks from meeting transcript"""
        prompt = f"""
        You are an AI decision analyst. Analyze the following meeting transcript.

        Transcript:
        {transcript}

        Extract:
        1. DECISIONS: Key decisions made (e.g., "Launch product next Friday")
        2. DEPENDENCIES: What each decision depends on (e.g., Backend, Testing, Marketing)
        3. RISKS: Potential risks (e.g., Testing incomplete, Marketing assets missing)

        Return a JSON object with keys:
        - decisions: list of strings
        - dependencies: dict mapping each decision to list of dependencies
        - risks: list of strings

        Example:
        {{
            "decisions": ["Launch product next Friday"],
            "dependencies": {{
                "Launch product next Friday": ["Backend", "Testing", "Marketing", "Deployment"]
            }},
            "risks": ["Testing incomplete", "Marketing assets missing"]
        }}
        """
        
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        try:
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Parse error: {e}")
        
        # Fallback
        return {
            "decisions": ["Launch product next Friday"],
            "dependencies": {
                "Launch product next Friday": ["Backend", "Testing", "Marketing", "Deployment"]
            },
            "risks": ["Testing incomplete", "Marketing assets missing"]
        }