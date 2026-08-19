# Multi-language system prompts and refusals for the RAG pipeline

LANGUAGE_INFO = {
    "hi": ("Hindi", "हिंदी", "उपलब्ध जानकारी के आधार पर इस प्रश्न का उत्तर नहीं दिया जा सकता है।"),
    "en": ("English", "English", "I cannot answer this question based on the retrieved context."),
    "bn": ("Bengali", "বাংলা", "প্রদত্ত তথ্যের ভিত্তিতে এই প্রশ্নের উত্তর দেওয়া সম্ভব নয়।"),
    "ta": ("Tamil", "தமிழ்", "வழங்கப்பட்ட தகவலின் அடிப்படையில் இந்தக் கேள்விக்கு பதிலளிக்க முடியாது."),
    "te": ("Telugu", "తెలుగు", "అందించిన సమాచారం ఆధారంగా ఈ ప్రశ్నకు సమాధానం ఇవ్వలేము."),
    "mr": ("Marathi", "मराठी", "उपलब्ध माहितीच्या आधारे या प्रश्नाचे उत्तर देता येत नाही."),
    "gu": ("Gujarati", "ગુજરાતી", "આપેલી માહિતીના આધારે આ પ્રશ્નનો જવાબ આપી શકાતો નથી."),
    "kn": ("Kannada", "ಕನ್ನಡ", "ನೀಡಿರುವ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ಈ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ."),
    "ml": ("Malayalam", "മലയാളം", "ലഭ്യമായ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ ഈ ചോദ്യത്തിന് ഉത്തരം നൽകാൻ കഴിയില്ല."),
    "pa": ("Punjabi", "ਪੰਜਾਬੀ", "ਦਿੱਤੀ ਗਈ ਜਾਣਕਾਰੀ ਦੇ ਆਧਾਰ 'ਤੇ ਇਸ ਸਵਾਲ ਦਾ ਜਵਾਬ ਨਹੀਂ ਦਿੱਤਾ ਜਾ ਸਕਦਾ।"),
    "ur": ("Urdu", "اردو", "فراہم کردہ معلومات کی بنیاد پر اس سوال کا جواب نہیں دیا جا سکتا۔"),
    "as": ("Assamese", "অসমীয়া", "প্ৰদত্ত তথ্যৰ ভিত্তিত এই প্ৰশ্নৰ উত্তৰ দিয়া সম্ভৱ নহয়।"),
    "ne": ("Nepali", "नेपाली", "उपलब्ध जानकारीको आधारमा यस प्रश्नको उत्तर दिन सकिँदैन।"),
    "od": ("Odia", "ଓଡ଼ିଆ", "ଦିଆଯାଇଥିବା ତଥ୍ୟ ଆଧାରରେ ଏହି ପ୍ରଶ୍ନର ଉତ୍ତର ଦେବା ସମ୍ଭବ ନୁହେଁ।"),
    "sa": ("Sanskrit", "संस्कृतम्", "उपलब्धसूचनायाः आधारे अस्य प्रश्नस्य उत्तरं दातुं न शक्यते।"),
}

def get_system_prompt(language: str = "hi") -> str:
    """
    Returns the appropriate system prompt based on language code.
    """
    lang = str(language).lower().strip()
    info = LANGUAGE_INFO.get(lang) or LANGUAGE_INFO.get(lang.split("-")[0]) or LANGUAGE_INFO["hi"]
    name_en, name_native, refusal = info

    if lang.startswith("en"):
        return f"""You are a helpful, low-latency assistant.
Your task is to answer the user's question ONLY using the provided evidence context.
Do not use any outside knowledge or make assumptions.
If the retrieved context does not contain enough information to answer the question, you MUST refuse and output exactly: "{refusal}"
Keep your answer extremely concise (maximum 1-2 short sentences).
Never invent facts or citations.
Answer strictly in English."""

    return f"""You are a helpful, accurate assistant.
Your task is to answer the user's question ONLY using the provided Evidence context.
Do not use any outside knowledge or assumptions.
If the retrieved context does not contain enough information to answer the question, output exactly: "{refusal}"
Keep your answer extremely concise (1-2 sentences).
Answer strictly in {name_en} ({name_native}). Do not mix English thinking words into the answer."""

def get_refusal_response(language: str = "hi") -> str:
    """
    Returns the standard refusal response based on language code.
    """
    lang = str(language).lower().strip()
    info = LANGUAGE_INFO.get(lang) or LANGUAGE_INFO.get(lang.split("-")[0]) or LANGUAGE_INFO["hi"]
    return info[2]
