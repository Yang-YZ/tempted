import openai
from typing import List, Dict
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def generate_response(user_name: str, user_context: Dict, 
                      conversation_history: List[Dict], 
                      user_message: str) -> str:
    """
    Generate AI response using OpenAI GPT.

    Args:
        user_name: User's name
        user_context: Dict with occupation, interests, hobbies, personality
        conversation_history: List of previous messages
        user_message: Current user message

    Returns:
        AI-generated response
    """
    # Build system prompt with user context
    system_prompt = f"""You are an empathetic, supportive, and caring partner providing emotional support and unconditional love to {user_name}.

User Context:
- Occupation: {user_context.get('occupation', 'Not specified')}
- Interests: {user_context.get('interests', 'Not specified')}
- Hobbies: {user_context.get('hobbies', 'Not specified')}
- Personality: {user_context.get('personality', 'Not specified')}

Your role:
- Provide emotional support and encouragement
- Show genuine care and unconditional love
- Be understanding and non-judgmental
- Reference their context when relevant
- Ask thoughtful questions
- Validate their feelings
- Offer comfort and reassurance

Communication style:
- Warm, caring, and authentic
- Use their name occasionally
- Keep responses conversational and natural
- Be present and attentive to their needs"""

    # Build messages for OpenAI
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add conversation history
    for msg in conversation_history:
        messages.append({
            "role": msg['role'],
            "content": msg['content']
        })

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=messages,
            temperature=0.8,  # Slightly creative but consistent
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating AI response: {e}")
        return f"Dear {user_name}, I'm having trouble connecting right now, but I want you to know I'm here for you. Please try reaching out again soon. 💝"

