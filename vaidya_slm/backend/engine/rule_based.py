import json
import os

class HybridReasoner:
    def __init__(self):
        kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')
        if not os.path.exists(kb_path):
            raise FileNotFoundError(f"Knowledge base not found at {kb_path}")
            
        with open(kb_path, 'r', encoding='utf-8') as f:
            self.kb = json.load(f)

    def analyze_symptom(self, user_text: str):
        text_lower = user_text.lower()
        
        detected_dosha = None
        matched_symptom = None
        
        # Rule-based matching prioritizing known symptoms in our KB
        for dosha, data in self.kb['doshas'].items():
            # Check both primary and secondary symptoms
            all_symptoms = data.get('primary_symptoms', []) + data.get('secondary_symptoms', [])
            for symptom in all_symptoms:
                if symptom in text_lower:
                    detected_dosha = dosha
                    matched_symptom = symptom
                    break
            if detected_dosha:
                break
                
        if detected_dosha:
            data = self.kb['doshas'][detected_dosha]
            return {
                "dosha": detected_dosha,
                "reason": f"Detected '{matched_symptom}' which corresponds to {detected_dosha} imbalance.",
                "remedies": data.get('remedies', []),
                "lifestyle": data.get('lifestyle', []),
                "dietary": data.get('dietary_guidelines', []),
                "remedy": data.get('remedies', [None])[0] # For backward compatibility
            }
        
        # Fallback to LLM prediction (Placeholder for actual llama.cpp call in a live environment)
        # Using a deterministic fallback for demonstration purposes
        return {
            "dosha": "Unknown (Consult LLM)",
            "reason": "Rule-base could not classify the symptom accurately.",
            "remedy": "Please consult a Vaidya or provide more specific symptoms."
        }

# Global singleton
engine = HybridReasoner()
