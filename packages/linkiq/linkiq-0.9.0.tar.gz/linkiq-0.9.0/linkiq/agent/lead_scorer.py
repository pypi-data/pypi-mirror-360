
import os
from linkiq.agent.llm_utils import LLMUtils
from rich import print

def score_lead(profile_traits: dict, target_persona: str, model_provider: str, model: str = None) -> dict:
    """
    Sends the LinkedIn profile traits and target persona to the LLM to get a lead score.

    Returns a dictionary with a score and explanation.
    """
    system_prompt = (
        "You are a B2B lead scoring assistant. Based on the profile traits and target persona, "
        "you'll assign a lead score from 0 to 100, where 100 is a perfect match. "
        "Keep the response short and clear."
    )

    user_prompt = (
        f"Here is the target persona:\n"
        f"{target_persona}\n\n"
        f"Here is the LinkedIn profile:\n"
        f"{profile_traits}\n\n"
        f"Based on this, assign a lead score from 0 to 100 and explain briefly why."
    )


    try:

        # Initialize LLMUtils and make the call
        llm_utils = LLMUtils()
        output = llm_utils.call_llm(
            prompt=user_prompt,
            model_provider=model_provider,
            model=model,
            system_prompt=system_prompt
        )
        
        score, explanation = _parse_llm_response(output)
        return {
            "score": score,
            "explanation": explanation,
            "raw_output": output
        }
    except Exception as e:
        print(f"[red]Error getting lead score: {e}[/red]")
        return {
            "score": None,
            "explanation": None,
            "error": str(e)
        }


def _parse_llm_response(response: str):
    """
    Parses the LLM response to extract score and explanation.
    Assumes score is a number between 0 and 100.
    """
    import re
    score_match = re.search(r'(\d{1,3})', response)
    score = int(score_match.group(1)) if score_match else None
    return score, response.strip()
