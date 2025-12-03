# dedicated just to call perplexity
import re, json
import asyncio
from perplexity import Perplexity
from config import PERPLEXITY_API_KEY
from storeUserData import GetUserProfile
from telegram import Update
from telegram.ext import ContextTypes

# initiate client with explicit API key
client = Perplexity(api_key=PERPLEXITY_API_KEY)

# ===
# handlers/menu.py for fact_check_trend()
def tokenize_and_filter(text):
    tokens = re.findall(r"\w+", text.lower())   #tokenize words for ltr
    # i want to find out all the stopwords as they are useless for querying ltr
    stopwords = {'is', 'the', 'to', 'a', 'and', 'of', 'that', 'this', 'for', 'in', 'on', 'with'}
    filtered = [t for t in tokens if t not in stopwords]

    return filtered

# draft a LLM propmt template for keyword extraction
# prompt guide based on perplexity reccs: https://perplexity.mintlify.app/guides/prompt-guide
keyword_extraction_prompt = """
From the following user claim, please identify the top 3-4 scientific search terms that would yield credible, evidence-based, factual results, and clearly state if certain details are not available.
Return ONLY a JSON array of phrases, no commentary.

User claim: "{}"
"""

# build trusted search query
# see https://docs.perplexity.ai/guides/search-best-practices#query-optimization
def build_trusted_search_query(keywords, trusted_sites):
    sites_filter = " OR ".join([f"site:{site}" for site in trusted_sites])

    # join the keywords with quotes and spaces in between
    joined_keywords = '" "'.join(keywords)
    query = f"{sites_filter} \"{joined_keywords}\""
    return query 

# create a pipeline to run fact checker
async def run_fact_check_pipeline(update: Update, context: ContextTypes.DEFAULT_TYPE, claim, trusted_sites, menu_keyboard):
    # get user details first
    user_id = update.effective_user.id
    profile = GetUserProfile(user_id)

    # extract user details first, with fallbacks
    name = profile.get("NAME", "friend") if profile else "friend"
    age = profile.get("AGE", "unknown") if profile else "unknown"
    sex = profile.get("SEX", "") if profile else ""
    height = profile.get("HEIGHT", "") if profile else ""
    weight = profile.get("WEIGHT", "") if profile else ""
    goal = profile.get("GOAL", "") if profile else ""
    activity_level = profile.get("ACTIVITY_LEVEL", "") if profile else ""
    diet_style = profile.get("DIET_STYLE", "") if profile else ""
    allergies = profile.get("ALLERGIES", "") if profile else ""
    bmr = profile.get("BMR", "") if profile else ""
    tdee = profile.get("TDEE", "") if profile else ""
    slump_check = profile.get("SLUMP_CHECK", "") if profile else ""
    morning_kick = profile.get("MORNING_KICK", "") if profile else ""
    hydration = profile.get("HYDRATION_CHECK", "") if profile else ""

    # tokenize
    tokens = tokenize_and_filter(claim)
    if not tokens:
        await update.message.reply_text("No meaningful keywords found.")
        return
    
    # build a source truth search string
    search_query = build_trusted_search_query(tokens, trusted_sites)
    # search_query = build_trusted_search_query(keywords, trusted_sites)

    # fact check with perplexity api
    factcheck_prompt = """
        You are an friendly, conversational nutrition coach talking to {name}, who has these details:
        - Age: {age}. Sex: {sex}, Height: {height}cm, Weight: {weight}kg
        - Goal: {goal}, Activity Level: {activity_level}, Diet: {diet_style}
        - Allergies: {allergies}, BMR: {bmr}, TDEE: {tdee}
        - User often feel a 'crash' or low energy in the mid-afternoon? (around 2-4 PM): {slump_check}
        - User feels {morning_kick} when he/she wakes up.
        - Daily plain water consumption in LITRES: {hydration} 

        **3 SENTENCES MAX.**Fact-check this claim using ONLY the search query. Verdict on "{claim}" using "{search_query}". NO questions. NO meal suggestions. NO citations. Plain text + emojis only. NO bold/italics.:
        1. Verdict ✅❌ + 1 sentence why
        2. 1 personalized tip for {goal}

        Make it:
        1. **Personalized** - Reference their profile ("With your fat loss goal...")
        2. **Actionable** - "Try this instead", "This fits your diet because..."
        3. **Engaging** - Casual tone, questions, emojis ✅❌, but NO bold/italics. Keep it plain text.

        Respond conversationally like: "Hey {name}, about that brown sugar claim... ❌ Here's what fits YOUR goals better:". NO citations. NO meal pushes. NO bold/italics.
    """.format(
        name=name, age=age, sex=sex, height=height, weight=weight,
        goal=goal, activity_level=activity_level, diet_style=diet_style,
        allergies=allergies, bmr=bmr, tdee=tdee, slump_check = slump_check, 
        morning_kick = morning_kick, hydration = hydration,
        claim=claim, search_query=search_query
    )

    factcheck_messages = [
        {"role": "system", "content": factcheck_prompt},
        {"role": "user", "content": "Please evaluate the truthfullness of the claim."}
    ]

    try:
        factcheck_response = await asyncio.to_thread(
            client.chat.completions.create,
            model='sonar-pro',
            messages=factcheck_messages,
            extra_body={"include_citations": False}
        )
        await update.message.reply_text(factcheck_response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Error during fact check: {e}")

    # include the main menu after showing
    await update.message.reply_text(
        "Back to main menu. Please choose an option:",
        reply_markup=menu_keyboard
    )
# ===



# handlers/menu.py for fix_my_energy()
async def get_snack_recommendations(snack_list: str, profile) -> str:
    # extract user details first, with fallbacks
    name = profile.get("NAME", "friend") if profile else "friend"
    age = profile.get("AGE", "unknown") if profile else "unknown"
    sex = profile.get("SEX", "") if profile else ""
    height = profile.get("HEIGHT", "") if profile else ""
    weight = profile.get("WEIGHT", "") if profile else ""
    goal = profile.get("GOAL", "") if profile else ""
    activity_level = profile.get("ACTIVITY_LEVEL", "") if profile else ""
    diet_style = profile.get("DIET_STYLE", "") if profile else ""
    allergies = profile.get("ALLERGIES", "") if profile else ""
    bmr = profile.get("BMR", "") if profile else ""
    tdee = profile.get("TDEE", "") if profile else ""
    slump_check = profile.get("SLUMP_CHECK", "") if profile else ""
    morning_kick = profile.get("MORNING_KICK", "") if profile else ""
    hydration = profile.get("HYDRATION_CHECK", "") if profile else ""
    
    
    energyFix_prompt = """
        You are a friendly, conversational nutrition coach advising {name} with these details:
        - Age: {age}, Sex: {sex}, Height: {height} cm, Weight: {weight} kg
        - Goal: {goal}, Activity Level: {activity_level}, Diet: {diet_style}
        - Allergies: {allergies}, BMR: {bmr}, TDEE: {tdee}
        - Afternoon energy crash: {slump_check}
        - Morning feeling: {morning_kick}
        - Daily water intake in liters: {hydration}

        From the following list of snacks, pick exactly 3 options best suited for {name}'s goals and profile to help maintain stable energy levels during the afternoon slump. Use plain text and emojis only. Do NOT include questions, meal suggestions, citations, or any markdown formatting.

        Snacks list:
        {snack_list}

        Format your response exactly like this — a numbered list with the following pattern for each snack:

        1. [Food Name] ([kcal] kcal, [protein]g protein) - [a brief explanation of how it helps stabilize energy]

        Make the explanations:
        - Personalized, referencing the user's profile (e.g., "With your {goal} goal...")
        - Actionable and practical (e.g., "Try this instead...", "Fits your {diet_style} diet...")
        - Casual and friendly in tone with appropriate emojis ✅❌

        Example response style:

        1. Apple slices (95 kcal, 1g protein) - The fiber slows sugar absorption, helping keep your energy steady ✅
        2. Greek yogurt (120 kcal, 10g protein) - Provides slow-digesting protein to avoid afternoon crashes 🍽️
        3. Almonds (170 kcal, 6g protein) - Healthy fats and protein keep you full and energized without spikes ⚡

        Remember: NO citations, NO meal plans, NO bold or italics. Just clear, helpful snack choices.

        Respond now with the numbered list tailored to {name}.
        """.format(
            name=name, age=age, sex=sex, height=height, weight=weight,
            goal=goal, activity_level=activity_level, diet_style=diet_style,
            allergies=allergies, bmr=bmr, tdee=tdee, slump_check = slump_check, 
            morning_kick = morning_kick, hydration = hydration, snack_list = snack_list
        )
    
    messages = [{"role": "user", "content": energyFix_prompt}]
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="sonar-pro",
        messages=messages,
        temperature=0.1
    )
    return response.choices[0].message.content







# catch response from telebot and GET req from perplexity
# async def get_perplexity_response(query: str, chat_history: list=None):
#     if chat_history is None:
#         chat_history = []

#     messages = chat_history + [{
#         "role": "user",
#         "content": query
#     }]

#     try:
#         response = client.chat.completions.create(
#             model="sonar",
#             messages=messages,
#             stream=False
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"Error calling Perplexity API: {e}")
#         return "Sorry, I couldn't generate a response right now."