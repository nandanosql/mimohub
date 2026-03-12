"""
MiMo Client — Chat with data using Xiaomi MiMo AI via LiteLLM.
"""

import os
from litellm import completion


SYSTEM_PROMPT = """You are MiMo Data Analyst, an expert AI assistant powered by Xiaomi MiMo.
You help users understand, analyze, and extract insights from their Excel data.

Rules:
- Answer based ONLY on the provided dataset context. Do not hallucinate data.
- When the user asks for analysis, provide clear, structured answers with numbers.
- Use markdown formatting: bold for emphasis, tables for comparisons, lists for steps.
- If the user asks to perform a calculation you cannot do, explain what steps they should take.
- Be concise but thorough. Suggest follow-up questions when relevant.
- If you are unsure, say so honestly.

Dataset Context:
{data_context}
"""


def get_api_key(sidebar_key: str = None) -> str:
    """Get API key from sidebar input or environment variable."""
    if sidebar_key and sidebar_key.strip():
        return sidebar_key.strip()
    return os.environ.get("XIAOMI_MIMO_API_KEY", "")


def chat_with_data(messages: list, data_context: str, api_key: str, stream: bool = True):
    """
    Send a chat request to MiMo AI with dataset context.

    Args:
        messages: Conversation history as list of {"role": ..., "content": ...} dicts.
        data_context: Text summary of the dataset.
        api_key: Xiaomi MiMo API key.
        stream: If True, returns a streaming generator.

    Returns:
        If stream=True: generator yielding response chunks.
        If stream=False: complete response string.
    """
    if not api_key:
        raise ValueError("MiMo API key is required. Enter it in the sidebar or set XIAOMI_MIMO_API_KEY env var.")

    system_message = {
        "role": "system",
        "content": SYSTEM_PROMPT.format(data_context=data_context),
    }

    full_messages = [system_message] + messages

    try:
        response = completion(
            model="xiaomi_mimo/mimo-v2-flash",
            messages=full_messages,
            api_key=api_key,
            stream=stream,
            max_tokens=2048,
            temperature=0.4,
            top_p=0.95,
        )

        if stream:
            def _text_stream():
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            return _text_stream()
        else:
            return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)
        if "auth" in error_msg.lower() or "key" in error_msg.lower() or "401" in error_msg:
            raise ValueError("Invalid MiMo API key. Please check your key at platform.xiaomimimo.com")
        raise ValueError(f"MiMo API error: {error_msg}")


SUGGESTED_QUESTIONS = [
    "📊 Summarize this dataset in plain English",
    "🔍 What are the key trends or patterns?",
    "⚠️ Are there any data quality issues I should know about?",
    "📈 Which columns are most correlated?",
    "🏆 What are the top 5 insights from this data?",
    "📋 Describe each column and its significance",
]
