# dedicated just to call perplexity
from perplexity import Perplexity
from config import PERPLEXITY_API_KEY

# initiate client with explicit API key
client = Perplexity(api_key=PERPLEXITY_API_KEY)

# catch response from telebot and GET req from perplexity
async def get_perplexity_response(query: str, chat_history: list=None):
    if chat_history is None:
        chat_history = []

    messages = chat_history + [{
        "role": "user",
        "content": query
    }]

    try:
        response = client.chat.completions.create(
            model="sonar",
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Perplexity API: {e}")
        return "Sorry, I couldn't generate a response right now."