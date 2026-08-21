import re

with open("voice-rag-engine/src/config/predefinedQueries.ts", "r", encoding="utf-8") as f:
    code = f.read()

GREETINGS = {
    "hi": "नमस्ते",
    "en": "Hello",
    "bn": "নমস্কার",
    "mr": "नमस्कार",
    "gu": "નમસ્તે",
    "ta": "வணக்கம்",
    "te": "నమస్కారం",
    "kn": "ನಮಸ್ಕಾರ",
    "ml": "നമസ്കാരം",
    "pa": "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ",
    "ur": "السلام علیکم",
    "or": "ନମସ୍କାର",
    "as": "নমস্কাৰ",
    "ne": "नमस्ते",
    "sa": "नमो नमः",
}

# Regex to find each greeting entry
for lang, word in GREETINGS.items():
    # Replace question and transcription in <lang>-greeting
    pattern = rf'(id:\s*"{lang}-greeting",\s*category:\s*"Greeting",\s*question:\s*")[^"]+(",\s*response:\s*\{{\s*transcription:\s*")[^"]+(")'
    def repl(m):
        return f'{m.group(1)}{word}{m.group(2)}{word}{m.group(3)}'
    
    code, count = re.subn(pattern, repl, code)
    print(f"Replaced greeting for {lang}: {count} replacements")

with open("voice-rag-engine/src/config/predefinedQueries.ts", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated predefinedQueries.ts successfully!")
