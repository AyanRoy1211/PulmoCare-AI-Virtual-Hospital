from shared.llm_client import chat, vision
import os
import json
from dotenv import load_dotenv

load_dotenv()

INTERACTION_PROMPT = """
You are a clinical pharmacologist. Analyze the following list of medications for 
potential drug-drug interactions.

MEDICATIONS:
{drug_list}

For each interaction found, classify it as:
- 🔴 SEVERE — Contraindicated, potentially life-threatening
- 🟡 MODERATE — Monitor closely, may need dose adjustment  
- 🟢 MILD — Minor interaction, generally safe

Return your response in this format:

## DRUG INTERACTION ANALYSIS

### [Severity Emoji] Drug A + Drug B
**Interaction:** (what happens mechanistically)
**Clinical Risk:** (what this means for the patient)
**Recommendation:** (what should be done)

---

If no significant interactions are found, state that clearly.
Always end with: 'This analysis must be verified by a licensed pharmacist or physician.'
"""

def check_drug_interactions(medications: list):

    if len(medications) < 2:
        yield "At least 2 medications required for interaction analysis."
        return
    
    drug_list = "\n".join([f"- {drug}" for drug in medications])
    prompt = INTERACTION_PROMPT.format(drug_list=drug_list)
    
    try:
        for chunk in chat(prompt):
            yield chunk
            
    except Exception as e:
        yield f"An error occurred: {str(e)}"