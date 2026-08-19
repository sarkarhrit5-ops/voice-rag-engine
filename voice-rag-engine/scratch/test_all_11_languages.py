import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from dotenv import load_dotenv
load_dotenv()

from rag.pipeline import TextRAGPipeline
from voice.voice_rag import VoiceRAG
from voice.stt.sarvam import SarvamSTT
from voice.tts.sarvam import SarvamTTS

pipeline = TextRAGPipeline(llm_provider='groq', llm_model='groq/compound-mini')
stt = SarvamSTT()
tts = SarvamTTS()
voice_rag = VoiceRAG(stt=stt, rag_pipeline=pipeline, tts=tts)

ALL_LANGUAGES = [
    ("hi", "Hindi"),
    ("en", "English"),
    ("bn", "Bengali"),
    ("ta", "Tamil"),
    ("te", "Telugu"),
    ("mr", "Marathi"),
    ("gu", "Gujarati"),
    ("kn", "Kannada"),
    ("ml", "Malayalam"),
    ("pa", "Punjabi"),
    ("ur", "Urdu"),
]

results = []
for code, name in ALL_LANGUAGES:
    # Test RAG answer generation
    rag_res = pipeline.answer("भौमिक आकृतियाँ अक्सर कैसे बनती हैं?", language=code)
    ans = rag_res["answer"]
    
    # Test TTS audio synthesis
    tts_lang = f"{code}-IN"
    tts_res = tts.synthesize(ans, language_code=tts_lang)
    audio_len = len(tts_res.audio)
    
    status_str = f"[{code}] {name}: Answer length={len(ans)}, Audio bytes={audio_len}"
    results.append(status_str)
    print(status_str)

with open("scratch/all_11_languages_verified.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
