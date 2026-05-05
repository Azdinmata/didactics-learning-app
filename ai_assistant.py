from openai import OpenAI
import streamlit as st

API_KEY = api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)

SYSTEM_PROMPT = """You are a highly specialized AI Assistant focusing exclusively on Pedagogy and Didactics.
Your role is to help teachers and students master teaching methodologies, learning theories, and classroom management.

CRITICAL RULES:
1. NEVER answer questions outside of education, pedagogy, or didactics (e.g., sports, coding, recipes). If asked, politely refuse and steer the conversation back to teaching.
2. Provide clear, well-structured explanations using markdown (bullet points, bold text).
3. Provide concrete examples when explaining abstract theories.
4. If the user asks for a quiz or to check their understanding, give them a multiple-choice scenario-based question, and wait for them to answer.
"""

def get_real_response(messages):
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Exclude any previous system messages from the Streamlit UI history if they exist
    for m in messages:
        if m["role"] in ["user", "assistant"]:
            api_messages.append({"role": m["role"], "content": m["content"]})
            
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
            return "⚠️ The AI service is temporarily unavailable. Please check your API key or billing settings."
        return "⚠️ I'm sorry, I encountered an error while trying to process your request. Please try again later."
