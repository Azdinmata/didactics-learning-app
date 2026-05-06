from openai import OpenAI
import streamlit as st

if "GROQ_API_KEY" in st.secrets:
    API_KEY = st.secrets["GROQ_API_KEY"]


client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)
MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an elite, highly supportive and engaging personal Didactics & Pedagogy Tutor.
Your mission is to help the user deeply master educational theories, classroom management techniques, and teaching methodologies.

CRITICAL TUTORING RULES:
1. TUTOR PERSONA & DEPTH: Be warm, encouraging, and deeply educational. Provide complete, rich, and detailed explanations. Do NOT restrict your answers to short sentences; instead, take the necessary length to thoroughly unpack concepts, theories, and instructional practices.
2. CONCRETE EXAMPLES: For every theoretical concept you explain, always provide a practical, real-world classroom scenario, teaching example, or actionable strategy that shows how it works in practice.
3. INTEGRATE LESSON QUOTES: Draw directly from the active lesson context. Always cite or quote exact phrases, terminology, or definitions from the provided lesson text to ground your teaching, formatting them clearly as markdown quotes (e.g., `> "quoted text"`).
4. ACTIVE ENGAGEMENT: End your responses with an insightful, friendly guiding question or a mini-scenario challenge to check for understanding and prompt active reflection.
5. ON-TOPIC FOCUS: Keep the discussion centered on pedagogy, didactic models, and teaching practices. If the user asks about unrelated topics, guide them gently back to the educational material.
"""

def get_real_response(messages, current_mod=None):
    import re
    
    lesson_context = ""
    if current_mod:
        title = current_mod.get("title", "Unknown Lesson")
        description = current_mod.get("description", "")
        raw_lesson = current_mod.get("structured_lesson", "")
        
        # Clean HTML tags to provide clean textbook-style lesson text
        clean_lesson = re.sub(r'<[^>]*>', ' ', raw_lesson)
        clean_lesson = re.sub(r'\s+', ' ', clean_lesson).strip()
        
        # Extract quiz questions for context to help with assessments
        quiz_list = current_mod.get("quiz", [])
        quiz_context = ""
        if quiz_list:
            quiz_context = "\nQuiz questions and correct answers for this lesson:\n"
            for q_idx, q in enumerate(quiz_list):
                q_text = q.get("question", "")
                options = q.get("options", [])
                correct_idx = q.get("correct_index", 0)
                feedback = q.get("feedback", "")
                correct_ans = options[correct_idx] if correct_idx < len(options) else "Unknown"
                quiz_context += f"Question {q_idx+1}: {q_text}\nCorrect Answer: {correct_ans}\nFeedback: {feedback}\n\n"
        
        lesson_context = f"""

=========================================
CURRENT TARGET LESSON CONTEXT:
=========================================
Active Lesson Title: "{title}"
Lesson Description: {description}
Key Lesson Contents (Textbook):
{clean_lesson}
{quiz_context}

CRITICAL RULES FOR THIS SESSION:
1. Your sole objective is to tutor the user on the active lesson: "{title}".
2. DETAILED EXPLANATIONS: Do NOT use strict brevity. Elaborate with thorough explanations, structuring your response with clear headings, bullet points, and steps.
3. INCLUDE LESSON QUOTES: Identify key parts of the "Key Lesson Contents" above and quote them directly in your response using markdown quotes, such as:
   > "[Insert exact quote from lesson content here]"
   Explain how this quote applies to real teaching.
4. CLASSROOM EXAMPLES: Provide vivid, concrete classroom examples or scenarios illustrating the concepts discussed.
5. SOCRATIC GUIDANCE: Speak like a master teacher. Encourage active learning. If they ask about a quiz question, offer small clues, theoretical hints, and guidance from the quoted text rather than just giving the direct answer.
6. If they ask about an entirely different lesson, another model, or an unrelated topic, politely guide them back to the current module:
   "As your Didactics Tutor for {title}, I am dedicated to helping you master this specific module! Let's stay focused on the concepts of {title}. How can I help you with [mention a concept from {title}]?"
"""

    system_prompt = SYSTEM_PROMPT + (lesson_context if lesson_context else "")
    api_messages = [{"role": "system", "content": system_prompt}]
    
    # Exclude any previous system messages from the Streamlit UI history if they exist
    for m in messages:
        if m["role"] in ["user", "assistant"]:
            api_messages.append({"role": m["role"], "content": m["content"]})
            
    # Clean all message contents of surrogate characters to avoid UTF-8 encoding issues
    for msg in api_messages:
        if "content" in msg and msg["content"]:
            msg["content"] = "".join(c for c in msg["content"] if not (0xD800 <= ord(c) <= 0xDFFF))
            
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=api_messages,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
            return "⚠️ The AI service is temporarily unavailable. Please check your API key or billing settings."
        return f"⚠️ I'm sorry, I encountered an error while trying to process your request: {str(e)}"
