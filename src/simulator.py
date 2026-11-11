from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import os
import json
import re

class ScenarioSimulator:
    def __init__(self, model="groq/compound-mini"):
        self.llm = ChatGroq(
            model=model,
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def simulate(self, decision: str, dependencies: list, risks: list, change: str) -> dict:
        """Simulate a what-if scenario"""
        prompt = f"""
        You are a future impact simulator. Given a decision and its dependencies, simulate what happens if a specific change occurs.

        Decision: {decision}
        Dependencies: {dependencies}
        Risks: {risks}
        Change: {change}

        Simulate the downstream impact step by step.

        Return JSON with:
        - scenario: description of the scenario
        - chain: list of events in order (e.g., ["Backend delayed", "Testing delayed", "Deployment delayed"])
        - risk_level: "LOW", "MEDIUM", or "HIGH"
        - recommendation: what to do about it
        - mitigation: how to reduce impact

        Example:
        {{
            "scenario": "Backend delayed by 2 days",
            "chain": ["Backend delayed 2 days", "Testing delayed", "Deployment delayed", "Launch risk HIGH"],
            "risk_level": "HIGH",
            "recommendation": "Prioritize backend team, allocate additional resources",
            "mitigation": "Consider soft launch with limited features"
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
            "scenario": change,
            "chain": [f"{change}", "Testing delayed", "Deployment delayed", "Launch risk HIGH"],
            "risk_level": "HIGH",
            "recommendation": "Allocate additional resources",
            "mitigation": "Consider soft launch"
        }