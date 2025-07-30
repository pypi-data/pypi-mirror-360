from groq import Groq
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

def generate_linkedin_connect_note(profile_traits: dict, target_persona: str, model="gpt-4") -> str:
    """
    Generates a short, natural LinkedIn connection message with no names or sign-offs.
    """

    system_prompt = (
        "You are a professional assistant who writes short, friendly, personalized LinkedIn connection messages "
        "that stay under 300 characters. Be natural, non-salesy, relevant to the recipient's role, and do not include any names or sign-offs."
    )

    user_prompt = (
        f"Target persona: {target_persona}\n\n"
        f"LinkedIn profile: {profile_traits}\n\n"
        f"Write a short connection message without including any names or signatures. "
        f"Keep it under 300 characters and make it feel personal and relevant to their experience."
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        message = response.choices[0].message.content.strip()

        # Ensure no names slipped through
        if any(token in message.lower() for token in ["hi ", "hello", "regards", "best,", "- ", "— ", "cheers"]):
            print("⚠️ Name or sign-off detected in output. You may need stronger prompt filtering.")
        return message[:300]

    except Exception as e:
        print(f"Error generating LinkedIn note: {e}")
        return None

def main():
    # Example profile traits (mocked from a scraped LinkedIn profile)
    profile_traits = {
        "name": "Jane Doe",
        "title": "VP of Product",
        "company_name": "TechNova",
        "location": "San Francisco Bay Area",
        "about": "Passionate about building great product teams and scalable SaaS platforms.",
        "experience": [
            {"title": "VP of Product", "company": "TechNova", "duration": "Jan 2022 - Present", "location": "Remote"},
            {"title": "Product Director", "company": "CloudSnap", "duration": "2019 - 2022"},
            {"title": "Senior PM", "company": "ZetaTech", "duration": "2016 - 2019"}
        ]
    }

    # Define your ideal customer persona
    target_persona = (
        "I am a startup founder and an experienced product leader and am targeting VP-level or senior product leaders at mid-to-large SaaS companies, "
        "who care about product growth, team efficiency, and operational scale."
    )

    # Call the connect note generator
    message = generate_linkedin_connect_note(profile_traits, target_persona)

    # Print the result
    print("\n--- LinkedIn Connection Note ---")
    print(message or "[No message generated]")
