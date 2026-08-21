import type { VoiceQueryResponse } from "../types";

export interface PredefinedQueryItem {
  id: string;
  category: "Greeting" | "Business" | "Science" | "Technology" | "Geography" | "Health" | "General";
  question: string;
  response: VoiceQueryResponse;
}

export const PREDEFINED_QUERIES_BY_LANGUAGE: Record<string, PredefinedQueryItem[]> = {
  // 1. HINDI (hi)
  hi: [
    {
      id: "hi-greeting",
      category: "Greeting",
      question: "नमस्ते, आप कौन हैं और क्या कर सकते हैं?",
      response: {
        transcription: "नमस्ते, आप कौन हैं और क्या कर सकते हैं?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "नमस्ते! मैं बहुभाषी वॉयस RAG इंजन हूँ। आप मुझसे अपनी भाषा में कोई भी प्रश्न पूछ सकते हैं, और मैं केवल प्रमाणित ज्ञान के आधार पर सटीक और सत्यापित उत्तर प्रदान करूँगा।",
        sources: [
          {
            id: "hi-src-greet",
            title: "Voice RAG System Introduction (हिन्दी)",
            reference: "System-Knowledge-Base-HI",
            snippet: "बहुभाषी वॉयस RAG इंजन भारतीय भाषाओं में ध्वनि और पाठ के माध्यम से सटीक और सत्यापित ज्ञान प्रदान करता है।"
          }
        ],
        latency: { stt_ms: 180, retrieval_ms: 65, generation_ms: 310, tts_ms: 220, total_ms: 775 }
      }
    },
    {
      id: "hi-corp",
      category: "Business",
      question: "कॉर्पोरेशन क्या है?",
      response: {
        transcription: "कॉर्पोरेशन क्या है?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.96,
        answer: "निगम (कॉर्पोरेशन) एक कंपनी या लोगों का समूह होता है जो एक एकल कानूनी इकाई के रूप में कार्य करने के लिए अधिकृत होता है और कानून में इसे अलग अस्तित्व के रूप में मान्यता प्राप्त होती है।",
        sources: [
          {
            id: "hi-src-1102432",
            title: "MSMARCO-XI Corpus (हिन्दी)",
            reference: "MSMARCO-XI-hin-1102432",
            snippet: "निगम एक कंपनी या लोगों का समूह होता है जो एक एकल इकाई के रूप में कार्य करने के लिए अधिकृत होता है और कानून में इस प्रकार से मान्यता प्राप्त होती है।"
          }
        ],
        latency: { stt_ms: 240, retrieval_ms: 85, generation_ms: 410, tts_ms: 290, total_ms: 1025 }
      }
    },
    {
      id: "hi-photosynthesis",
      category: "Science",
      question: "प्रकाश संश्लेषण क्या है?",
      response: {
        transcription: "प्रकाश संश्लेषण क्या है?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "प्रकाश संश्लेषण वह जैविक प्रक्रिया है जिसके द्वारा हरे पौधे सूर्य के प्रकाश, जल और कार्बन डाइऑक्साइड का उपयोग करके ग्लूकोज (ऊर्जा) और ऑक्सीजन का निर्माण करते हैं।",
        sources: [
          {
            id: "hi-src-photo",
            title: "वनस्पति विज्ञान संदर्भ",
            reference: "NCERT-Biology-Ch4",
            snippet: "पौधे पर्णहरित (क्लोरोफिल) की सहायता से सूर्य के प्रकाश की ऊर्जा को रासायनिक ऊर्जा में परिवर्तित करते हैं।"
          }
        ],
        latency: { stt_ms: 220, retrieval_ms: 70, generation_ms: 380, tts_ms: 270, total_ms: 940 }
      }
    },
    {
      id: "hi-integrity",
      category: "General",
      question: "ईमानदारी या सच्चाई की परिभाषा क्या है?",
      response: {
        transcription: "ईमानदारी या सच्चाई की परिभाषा क्या है?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.94,
        answer: "ईमानदारी सत्य बोलने और धोखाधड़ी से बचने की स्थिति है। निष्ठा (इंटीग्रिटी) व्यक्ति के नैतिक मूल्यों और सिद्धांतों के प्रति दृढ़ रहने का गुण है।",
        sources: [
          {
            id: "hi-src-205107",
            title: "MSMARCO-XI शब्दावली",
            reference: "MSMARCO-XI-hin-205107",
            snippet: "ईमानदारी: ईमानदार होने की स्थिति। निष्ठा: ईमानदारी के संबंध में या उसके अतिरिक्त व्यक्ति का मूल्य और नैतिकता।"
          }
        ],
        latency: { stt_ms: 250, retrieval_ms: 90, generation_ms: 420, tts_ms: 280, total_ms: 1040 }
      }
    },
    {
      id: "hi-carson",
      category: "General",
      question: "रेचल कार्सन ने दायित्व बर्दाश्त करने पर क्यों लिखा?",
      response: {
        transcription: "रेचल कार्सन ने दायित्व बर्दाश्त करने पर क्यों लिखा?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.95,
        answer: "रेचल कार्सन ने लिखा क्योंकि उनका मानना था कि कीटनाशकों से कीटों को खत्म करने की मानव कोशिश वास्तव में पर्यावरण को दूषित करके और अधिक गंभीर समस्याएं उत्पन्न कर रही है।",
        sources: [
          {
            id: "hi-src-1102431",
            title: "पर्यावरण अध्ययन संदर्भ",
            reference: "MSMARCO-XI-hin-1102431",
            snippet: "रेचल कार्सन ने लिखा है कि द ओब्लिगेशन टू एंड्योर क्योंकि उनका मानना है कि जैसे-जैसे आदमी अवांछित कीड़ों को खत्म करने की कोशिश करता है, वैसे-वैसे वह पर्यावरण को प्रदूषित करता है।"
          }
        ],
        latency: { stt_ms: 290, retrieval_ms: 110, generation_ms: 450, tts_ms: 310, total_ms: 1160 }
      }
    },
    {
      id: "hi-dna",
      category: "Science",
      question: "डीएनए का शरीर में क्या कार्य है?",
      response: {
        transcription: "डीएनए का शरीर में क्या कार्य है?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.97,
        answer: "डीएनए (डीऑक्सीराइबोन्यूक्लिक एसिड) जीवित कोशिकाओं में आनुवंशिक जानकारी संग्रहीत करता है, जो जीवों के विकास, वृद्धि और प्रजनन के सभी निर्देशों को वहन करता है।",
        sources: [
          {
            id: "hi-src-dna",
            title: "आनुवंशिकी और कोशिका विज्ञान",
            reference: "BioGenetics-Index-42",
            snippet: "डीएनए कोशिका के केंद्रक में पाया जाता है और प्रोटीन संश्लेषण तथा आनुवंशिक विशेषताओं के संचरण के लिए ब्लूप्रिंट का काम करता है।"
          }
        ],
        latency: { stt_ms: 210, retrieval_ms: 75, generation_ms: 360, tts_ms: 250, total_ms: 895 }
      }
    },
    {
      id: "hi-gravity",
      category: "Science",
      question: "गुरुत्वाकर्षण बल क्या है?",
      response: {
        transcription: "गुरुत्वाकर्षण बल क्या है?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "गुरुत्वाकर्षण एक प्राकृतिक आकर्षण बल है जो द्रव्यमान वाले किन्हीं दो पिंडों के बीच कार्य करता है। इसी बल के कारण पृथ्वी वस्तुओं को अपनी ओर खींचती है।",
        sources: [
          {
            id: "hi-src-grav",
            title: "भौतिक विज्ञान सिद्धांत",
            reference: "Physics-Newton-Law",
            snippet: "ब्रह्मांड का प्रत्येक कण अन्य प्रत्येक कण को एक बल से आकर्षित करता है जो उनके द्रव्यमान के गुणनफल के समानुपाती होता है।"
          }
        ],
        latency: { stt_ms: 230, retrieval_ms: 80, generation_ms: 390, tts_ms: 260, total_ms: 960 }
      }
    },
    {
      id: "hi-water-cycle",
      category: "Science",
      question: "जल चक्र कैसे काम करता है?",
      response: {
        transcription: "जल चक्र कैसे काम करता है?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.96,
        answer: "जल चक्र में सूर्य की ऊष्मा से वाष्पीकरण, वायुमंडल में संघनन से बादलों का निर्माण, और वर्षा के रूप में जल का पुनः पृथ्वी पर लौटना शामिल है।",
        sources: [
          {
            id: "hi-src-water",
            title: "भूगोल और पर्यावरण",
            reference: "Geo-Water-Cycle-101",
            snippet: "जल चक्र पृथ्वी की सतह और वायुमंडल के बीच जल के निरंतर संचलन की एक बंद प्रणाली है।"
          }
        ],
        latency: { stt_ms: 240, retrieval_ms: 85, generation_ms: 370, tts_ms: 270, total_ms: 965 }
      }
    },
    {
      id: "hi-rag-explain",
      category: "Technology",
      question: "वॉयस RAG कैसे काम करता है?",
      response: {
        transcription: "वॉयस RAG कैसे काम करता है?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "वॉयस RAG पहले आपकी आवाज़ को Sarvam STT द्वारा टेक्स्ट में बदलता है, फिर FAISS इंडेक्स से सटीक दस्तावेज खोजता है, LLM द्वारा सत्यापित उत्तर बनाता है और TTS से ध्वनि में सुनाता है।",
        sources: [
          {
            id: "hi-src-rag",
            title: "Voice RAG आर्किटेक्चर",
            reference: "Voice-RAG-Spec-2026",
            snippet: "मल्टीलिंगुअल वॉयस RAG पाइपलाइन में STT, मल्टीलिंगुअल डेंस रिट्रीवल, ग्राउंडिंग चेकर और TTS घटक एकीकृत हैं।"
          }
        ],
        latency: { stt_ms: 190, retrieval_ms: 60, generation_ms: 340, tts_ms: 230, total_ms: 820 }
      }
    },
    {
      id: "hi-democracy",
      category: "General",
      question: "लोकतंत्र का क्या अर्थ है?",
      response: {
        transcription: "लोकतंत्र का क्या अर्थ है?",
        language: "hi",
        normalized_language: "hi",
        grounded: true,
        refusal: false,
        confidence: 0.97,
        answer: "लोकतंत्र शासन की वह प्रणाली है जिसमें सर्वोच्च शक्ति जनता के हाथों में होती है और जनता अपने चुने हुए प्रतिनिधियों के माध्यम से शासन चलाती है।",
        sources: [
          {
            id: "hi-src-demo",
            title: "राजनीति विज्ञान",
            reference: "Polity-Constitution-Basics",
            snippet: "लोकतंत्र जनता का, जनता द्वारा और जनता के लिए शासन है, जहां नागरिक मताधिकार के माध्यम से अपने प्रतिनिधि चुनते हैं।"
          }
        ],
        latency: { stt_ms: 220, retrieval_ms: 70, generation_ms: 350, tts_ms: 240, total_ms: 880 }
      }
    }
  ],

  // 2. ENGLISH (en)
  en: [
    {
      id: "en-greeting",
      category: "Greeting",
      question: "Hello, who are you and how can you help me?",
      response: {
        transcription: "Hello, who are you and how can you help me?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "Hello! I am your Multilingual Voice RAG Engine. You can ask me questions using your voice or text across 15 Indian languages, and I retrieve strictly verified facts with zero hallucination.",
        sources: [
          {
            id: "en-src-intro",
            title: "System Architecture Specification",
            reference: "Voice-RAG-Architecture-Doc",
            snippet: "The Multilingual Voice RAG Engine provides low-latency voice-to-voice information retrieval across 15 Indic languages with evidence-backed grounding."
          }
        ],
        latency: { stt_ms: 160, retrieval_ms: 55, generation_ms: 290, tts_ms: 210, total_ms: 715 }
      }
    },
    {
      id: "en-corp",
      category: "Business",
      question: "What is a corporation?",
      response: {
        transcription: "What is a corporation?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "A corporation is an organization or group of people authorized by law to act as a single legal entity, distinct from its owners and shareholders.",
        sources: [
          {
            id: "en-src-1102432",
            title: "MSMARCO Knowledge Base",
            reference: "MSMARCO-1102432",
            snippet: "A corporation is a company or group of people authorized to act as a single entity and recognized as such in law."
          }
        ],
        latency: { stt_ms: 190, retrieval_ms: 60, generation_ms: 320, tts_ms: 220, total_ms: 790 }
      }
    },
    {
      id: "en-rag-grounding",
      category: "Technology",
      question: "What is grounded answer generation in RAG?",
      response: {
        transcription: "What is grounded answer generation in RAG?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "Grounded answer generation ensures that every claim in the response is directly supported by retrieved evidence passages. If evidence is insufficient, the system safely refuses to hallucinate.",
        sources: [
          {
            id: "en-src-rag-eval",
            title: "RAG Evaluation Benchmark",
            reference: "RAG-Grounding-Standard-2026",
            snippet: "Grounding verification enforces that all output assertions strictly align with retrieved reference passages with calibrated threshold confidence."
          }
        ],
        latency: { stt_ms: 210, retrieval_ms: 65, generation_ms: 340, tts_ms: 230, total_ms: 845 }
      }
    },
    {
      id: "en-photosynthesis",
      category: "Science",
      question: "How does photosynthesis produce oxygen?",
      response: {
        transcription: "How does photosynthesis produce oxygen?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.97,
        answer: "During the light-dependent reactions of photosynthesis, chlorophyll absorbs sunlight and splits water molecules (photolysis), releasing oxygen as a byproduct while converting energy into ATP.",
        sources: [
          {
            id: "en-src-photo-biochem",
            title: "Biochemical Energy Systems",
            reference: "Cellular-Biology-Principles",
            snippet: "Light energy triggers the photolysis of H2O at photosystem II, releasing diatomic oxygen gas into the atmosphere."
          }
        ],
        latency: { stt_ms: 220, retrieval_ms: 70, generation_ms: 380, tts_ms: 250, total_ms: 920 }
      }
    },
    {
      id: "en-neural-networks",
      category: "Technology",
      question: "What are neural networks in AI?",
      response: {
        transcription: "What are neural networks in AI?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.96,
        answer: "Neural networks are computational models inspired by biological brains, composed of interconnected layers of artificial nodes that learn patterns by adjusting weights during training.",
        sources: [
          {
            id: "en-src-ml-fund",
            title: "Deep Learning Foundations",
            reference: "AI-Principles-Vol1",
            snippet: "Artificial neural networks use mathematical optimization like backpropagation to adjust synaptic weights and model non-linear relationships in data."
          }
        ],
        latency: { stt_ms: 200, retrieval_ms: 65, generation_ms: 350, tts_ms: 240, total_ms: 855 }
      }
    },
    {
      id: "en-black-holes",
      category: "Science",
      question: "What is an event horizon in a black hole?",
      response: {
        transcription: "What is an event horizon in a black hole?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "The event horizon is the theoretical boundary around a black hole beyond which the gravitational pull is so strong that nothing, not even light, can escape.",
        sources: [
          {
            id: "en-src-astro",
            title: "General Relativity and Cosmology",
            reference: "Astrophysics-Core-12",
            snippet: "The event horizon represents the point of no return where the escape velocity equals the speed of light in vacuum."
          }
        ],
        latency: { stt_ms: 215, retrieval_ms: 72, generation_ms: 360, tts_ms: 245, total_ms: 892 }
      }
    },
    {
      id: "en-climate-change",
      category: "Science",
      question: "What causes the greenhouse effect on Earth?",
      response: {
        transcription: "What causes the greenhouse effect on Earth?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.97,
        answer: "The greenhouse effect occurs when atmospheric gases like carbon dioxide, methane, and water vapor trap thermal infrared radiation emitted by Earth's surface, warming the lower atmosphere.",
        sources: [
          {
            id: "en-src-climate",
            title: "Atmospheric Physics",
            reference: "IPCC-Climate-Basics",
            snippet: "Greenhouse gases absorb longwave infrared radiation re-emitted by the Earth and re-radiate it in all directions, maintaining planetary warmth."
          }
        ],
        latency: { stt_ms: 225, retrieval_ms: 75, generation_ms: 370, tts_ms: 260, total_ms: 930 }
      }
    },
    {
      id: "en-quantum-computing",
      category: "Technology",
      question: "How do qubits differ from classical bits?",
      response: {
        transcription: "How do qubits differ from classical bits?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.95,
        answer: "Classical bits represent either a 0 or 1, while qubits can exist in a superposition of both states simultaneously and exhibit entanglement, enabling exponential computational parallelism.",
        sources: [
          {
            id: "en-src-quantum",
            title: "Quantum Information Theory",
            reference: "Quantum-Computing-Intro",
            snippet: "Qubits leverage quantum phenomena such as superposition and entanglement to execute complex algorithms exponentially faster than classical Turing machines."
          }
        ],
        latency: { stt_ms: 230, retrieval_ms: 80, generation_ms: 390, tts_ms: 270, total_ms: 970 }
      }
    },
    {
      id: "en-vaccines",
      category: "Health",
      question: "How do vaccines train the human immune system?",
      response: {
        transcription: "How do vaccines train the human immune system?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "Vaccines introduce harmless antigens or mRNA blueprints that prompt the immune system to produce antibodies and memory T-cells without causing the actual disease.",
        sources: [
          {
            id: "en-src-immunology",
            title: "Immunology Principles",
            reference: "WHO-Immunization-Reference",
            snippet: "Vaccines stimulate adaptive immunity by eliciting specific antibody responses and establishing immunological memory against targeted pathogens."
          }
        ],
        latency: { stt_ms: 220, retrieval_ms: 70, generation_ms: 360, tts_ms: 250, total_ms: 900 }
      }
    },
    {
      id: "en-gdp",
      category: "Business",
      question: "What is Gross Domestic Product (GDP)?",
      response: {
        transcription: "What is Gross Domestic Product (GDP)?",
        language: "en",
        normalized_language: "en",
        grounded: true,
        refusal: false,
        confidence: 0.97,
        answer: "GDP is the total monetary market value of all finished goods and services produced within a country's borders over a specific time period, typically a quarter or year.",
        sources: [
          {
            id: "en-src-econ",
            title: "Macroeconomic Fundamentals",
            reference: "Econ-Textbook-Macro",
            snippet: "Gross Domestic Product serves as a comprehensive scorecard of a country's economic output, calculated via expenditure, production, or income approaches."
          }
        ],
        latency: { stt_ms: 210, retrieval_ms: 65, generation_ms: 340, tts_ms: 235, total_ms: 850 }
      }
    }
  ],

  // 3. BENGALI (bn)
  bn: [
    {
      id: "bn-greeting",
      category: "Greeting",
      question: "নমস্কার, আপনি কে এবং কী করতে পারেন?",
      response: {
        transcription: "নমস্কার, আপনি কে এবং কী করতে পারেন?",
        language: "bn",
        normalized_language: "bn",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "নমস্কার! আমি বহুভাষিক ভয়েস RAG ইঞ্জিন। আপনি আপনার নিজের ভাষায় যেকোনো প্রশ্ন জিজ্ঞাসা করতে পারেন, এবং আমি নির্ভরযোগ্য প্রমাণের ভিত্তিতে নির্ভুল উত্তর দেব।",
        sources: [
          {
            id: "bn-src-greet",
            title: "ভয়েস RAG সিস্টেম পরিচিতি",
            reference: "System-Knowledge-Base-BN",
            snippet: "বহুভাষিক ভয়েস RAG ইঞ্জিন ভারতীয় ভাষায় কণ্ঠস্বর ও পাঠ্যের মাধ্যমে সঠিক ও যাচাইকৃত জ্ঞান প্রদান করে।"
          }
        ],
        latency: { stt_ms: 190, retrieval_ms: 65, generation_ms: 320, tts_ms: 230, total_ms: 805 }
      }
    },
    {
      id: "bn-corp",
      category: "Business",
      question: "কর্পোরেশন কী?",
      response: {
        transcription: "কর্পোরেশন কী?",
        language: "bn",
        normalized_language: "bn",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "একটি কর্পোরেশন হলো একটি সংস্থা বা মানুষের একটি গোষ্ঠী যা একক আইনি সত্তা হিসেবে কাজ করার জন্য অনুমোদিত এবং আইনে স্বীকৃত।",
        sources: [
          {
            id: "bn-src-1102432",
            title: "MSMARCO-XI বাংলা কর্পাস",
            reference: "MSMARCO-XI-ben-1102432",
            snippet: "একটি কর্পোরেশন হল একটি সংস্থা বা মানুষের একটি গোষ্ঠী যা একক সত্তা হিসাবে কাজ করার জন্য এবং আইনে স্বীকৃত।"
          }
        ],
        latency: { stt_ms: 230, retrieval_ms: 80, generation_ms: 390, tts_ms: 280, total_ms: 980 }
      }
    },
    {
      id: "bn-photosynthesis",
      category: "Science",
      question: "সালোকসংশ্লেষ কীভাবে কাজ করে?",
      response: {
        transcription: "সালোকসংশ্লেষ কীভাবে কাজ করে?",
        language: "bn",
        normalized_language: "bn",
        grounded: true,
        refusal: false,
        confidence: 0.97,
        answer: "সালোকসংশ্লেষ হলো একটি জৈব রাসায়নিক প্রক্রিয়া যার মাধ্যমে সবুজ উদ্ভিদ সূর্যালোক, জল এবং কার্বন ডাই অক্সাইড ব্যবহার করে গ্লুকোজ ও অক্সিজেন তৈরি করে।",
        sources: [
          {
            id: "bn-src-bio",
            title: "উদ্ভিদবিজ্ঞান কোষ",
            reference: "Bio-Botany-Bengali",
            snippet: "ক্লোরোফিলের উপস্থিতিতে সৌরশক্তি রাসায়নিক শক্তিতে রূপান্তরিত হয়ে গ্লুকোজ উৎপন্ন করে।"
          }
        ],
        latency: { stt_ms: 240, retrieval_ms: 75, generation_ms: 370, tts_ms: 260, total_ms: 945 }
      }
    },
    {
      id: "bn-solar-system",
      category: "Science",
      question: "সৌরজগতের বৃহত্তম গ্রহ কোনটি?",
      response: {
        transcription: "সৌরজগতের বৃহত্তম গ্রহ কোনটি?",
        language: "bn",
        normalized_language: "bn",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "সৌরজগতের বৃহত্তম গ্রহ হলো বৃহস্পতি (Jupiter)। এটি একটি গ্যাসীয় দৈত্য এবং এর ভর সৌরজগতের অন্যান্য সকল গ্রহের মিলিত ভরের দ্বিগুণেরও বেশি।",
        sources: [
          {
            id: "bn-src-astro",
            title: "মহাকাশ বিজ্ঞান",
            reference: "Astronomy-Planets-BN",
            snippet: "বৃহস্পতি সৌরজগতের পঞ্চম ও বৃহত্তম গ্রহ, যার ব্যাস প্রায় ১,৪২,৯৮৪ কিলোমিটার।"
          }
        ],
        latency: { stt_ms: 210, retrieval_ms: 60, generation_ms: 340, tts_ms: 240, total_ms: 850 }
      }
    },
    {
      id: "bn-dna",
      category: "Science",
      question: "ডিএনএ এর কাজ কী?",
      response: {
        transcription: "ডিএনএ এর কাজ কী?",
        language: "bn",
        normalized_language: "bn",
        grounded: true,
        refusal: false,
        confidence: 0.96,
        answer: "ডিএনএ (ডিঅক্সিরাইবোনিউক্লিক অ্যাসিড) জীবের জিনগত তথ্য সংরক্ষণ ও বংশপরম্পরায় বৈশিষ্ট্য হস্তান্তরের নির্দেশিকা হিসেবে কাজ করে।",
        sources: [
          {
            id: "bn-src-dna",
            title: "জিনতত্ত্ব ও জীববিদ্যা",
            reference: "Genetics-BN-Index",
            snippet: "কোষের নিউক্লিয়াসে অবস্থিত ডিএনএ প্রোটিন সংশ্লেষণ ও জীবনের জৈবিক নকশা নির্ধারণ করে।"
          }
        ],
        latency: { stt_ms: 220, retrieval_ms: 70, generation_ms: 360, tts_ms: 250, total_ms: 900 }
      }
    }
  ],

  // 4. MARATHI (mr)
  mr: [
    {
      id: "mr-greeting",
      category: "Greeting",
      question: "नमस्कार, आपण कोण आहात आणि कशी मदत करू शकता?",
      response: {
        transcription: "नमस्कार, आपण कोण आहात आणि कशी मदत करू शकता?",
        language: "mr",
        normalized_language: "mr",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "नमस्कार! मी बहुभाषिक व्हॉइस RAG इंजिन आहे. तुम्ही मला तुमच्या मातृभाषेत कोणताही प्रश्न विचारू शकता आणि मी केवळ सत्यापित पुराव्यावर आधारित अचूक उत्तरे देईन.",
        sources: [
          {
            id: "mr-src-greet",
            title: "सिस्टम ओळख (मराठी)",
            reference: "System-Knowledge-Base-MR",
            snippet: "बहुभाषिक व्हॉइस RAG प्रणाली भारतीय भाषांमध्ये आवाज आणि मजकुराद्वारे अचूक ज्ञान प्रदान करते."
          }
        ],
        latency: { stt_ms: 195, retrieval_ms: 65, generation_ms: 330, tts_ms: 240, total_ms: 830 }
      }
    },
    {
      id: "mr-corp",
      category: "Business",
      question: "कॉर्पोरेशन म्हणजे काय?",
      response: {
        transcription: "कॉर्पोरेशन म्हणजे काय?",
        language: "mr",
        normalized_language: "mr",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "कॉर्पोरेशन ही एक कंपनी किंवा लोकांचा समूह आहे ज्याला कायद्यानुसार एकाच कायदेशीर घटकाच्या रूपात कार्य करण्याचा अधिकार आणि मान्यता आहे.",
        sources: [
          {
            id: "mr-src-1102432",
            title: "MSMARCO-XI मराठी संदर्भ",
            reference: "MSMARCO-XI-mar-1102432",
            snippet: "कॉर्पोरेशन ही एक कंपनी किंवा लोकांचा समूह आहे ज्याला एकल संस्था म्हणून काम करण्याचा अधिकार आहे आणि कायद्यात मान्यता आहे."
          }
        ],
        latency: { stt_ms: 235, retrieval_ms: 80, generation_ms: 400, tts_ms: 285, total_ms: 1000 }
      }
    },
    {
      id: "mr-shivaji",
      category: "General",
      question: "छत्रपती शिवाजी महाराजांचा राज्याभिषेक कधी झाला?",
      response: {
        transcription: "छत्रपती शिवाजी महाराजांचा राज्याभिषेक कधी झाला?",
        language: "mr",
        normalized_language: "mr",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "छत्रपती शिवाजी महाराजांचा भव्य राज्याभिषेक ६ जून १६७४ रोजी किल्ले रायगडावर संपन्न झाला आणि त्यांनी हिंदवी स्वराज्याची स्थापना अधिकृत केली.",
        sources: [
          {
            id: "mr-src-history",
            title: "महाराष्ट्राचा इतिहास",
            reference: "Maha-History-Corpus-1674",
            snippet: "६ जून १६७४ रोजी रायगडावर गागाभट्टांच्या उपस्थितीत छत्रपती शिवाजी महाराजांचा राज्याभिषेक सोहळा पार पडला."
          }
        ],
        latency: { stt_ms: 220, retrieval_ms: 70, generation_ms: 360, tts_ms: 260, total_ms: 910 }
      }
    },
    {
      id: "mr-gravity",
      category: "Science",
      question: "गुरुत्वाकर्षण बल म्हणजे काय?",
      response: {
        transcription: "गुरुत्वाकर्षण बल म्हणजे काय?",
        language: "mr",
        normalized_language: "mr",
        grounded: true,
        refusal: false,
        confidence: 0.97,
        answer: "गुरुत्वाकर्षण हे विश्वातील वस्तुमान असलेल्या कोणत्याही दोन वस्तूंमधील नैसर्गिक आकर्षण बल आहे. यामुळेच सर्व वस्तू पृथ्वीकडे खेचल्या जातात.",
        sources: [
          {
            id: "mr-src-phys",
            title: "भौतिकशास्त्र मूलभूत संकल्पना",
            reference: "Physics-MR-Newton",
            snippet: "न्यूटनच्या वैश्विक गुरुत्वाकर्षणाच्या नियमानुसार प्रत्येक वस्तू इतर वस्तूंना स्वतःकडे आकर्षित करते."
          }
        ],
        latency: { stt_ms: 225, retrieval_ms: 75, generation_ms: 370, tts_ms: 255, total_ms: 925 }
      }
    }
  ],

  // 5. GUJARATI (gu)
  gu: [
    {
      id: "gu-greeting",
      category: "Greeting",
      question: "નમસ્તે, તમે કોણ છો અને શું મદદ કરી શકો છો?",
      response: {
        transcription: "નમસ્તે, તમે કોણ છો અને શું મદદ કરી શકો છો?",
        language: "gu",
        normalized_language: "gu",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "નમસ્તે! હું બહુભાષી વૉઇસ RAG એન્જિન છું. તમે મને ગુજરાતી અથવા અન્ય ભારતીય ભાષામાં પ્રશ્ન પૂછી શકો છો, અને હું ચકાસાયેલ માહિતીના આધારે સચોટ ઉત્તર આપીશ.",
        sources: [
          {
            id: "gu-src-greet",
            title: "સિસ્ટમ પરિચય (ગુજરાતી)",
            reference: "System-Knowledge-Base-GU",
            snippet: "બહુભાષી વૉઇસ RAG એન્જિન ભારતીય ભાષાઓમાં સચોટ અને આધારિત જવાબો આપે છે."
          }
        ],
        latency: { stt_ms: 190, retrieval_ms: 65, generation_ms: 320, tts_ms: 230, total_ms: 805 }
      }
    },
    {
      id: "gu-corp",
      category: "Business",
      question: "કોર્પોરેશન શું છે?",
      response: {
        transcription: "કોર્પોરેશન શું છે?",
        language: "gu",
        normalized_language: "gu",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "કોર્પોરેશન એ એક એવી કંપની અથવા લોકોનું જૂથ છે જે કાયદા મુજબ એક અલગ કાનૂની એકમ તરીકે કાર્ય કરવા માટે અધિકૃત છે.",
        sources: [
          {
            id: "gu-src-1102432",
            title: "MSMARCO-XI ગુજરાતી સંદર્ભ",
            reference: "MSMARCO-XI-guj-1102432",
            snippet: "નિગમ એ એક એવી કંપની અથવા લોકોનું જૂથ છે જે એક એકમ તરીકે કાર્ય કરવા માટે અધિકૃત છે અને કાયદામાં તેને માન્યતા છે."
          }
        ],
        latency: { stt_ms: 240, retrieval_ms: 85, generation_ms: 410, tts_ms: 280, total_ms: 1015 }
      }
    },
    {
      id: "gu-sun",
      category: "Science",
      question: "સૂર્યમંડળમાં પૃથ્વીનું સ્થાન કયું છે?",
      response: {
        transcription: "સૂર્યમંડળમાં પૃથ્વીનું સ્થાન કયું છે?",
        language: "gu",
        normalized_language: "gu",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "પૃથ્વી સૂર્યથી ત્રીજા ક્રમનો ગ્રહ છે અને સમગ્ર સૂર્યમંડળમાં જીવન ધરાવતો એકમાત્ર જાણીતો ગ્રહ છે.",
        sources: [
          {
            id: "gu-src-astro",
            title: "ખગોળ વિજ્ઞાન પરિચય",
            reference: "Astro-GU-Planets",
            snippet: "પૃથ્વી સૂર્યથી લગભગ ૧૫ કરોડ કિલોમીટર દૂર સ્થિત ત્રીજો ગ્રહ છે."
          }
        ],
        latency: { stt_ms: 210, retrieval_ms: 65, generation_ms: 340, tts_ms: 240, total_ms: 855 }
      }
    }
  ],

  // 6. TAMIL (ta)
  ta: [
    {
      id: "ta-greeting",
      category: "Greeting",
      question: "வணக்கம், நீங்கள் யார் மற்றும் என்ன செய்ய முடியும்?",
      response: {
        transcription: "வணக்கம், நீங்கள் யார் மற்றும் என்ன செய்ய முடியும்?",
        language: "ta",
        normalized_language: "ta",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "வணக்கம்! நான் பன்மொழி குரல் RAG இயந்திரம். நீங்கள் உங்கள் தாய்மொழியில் எந்த கேள்வியையும் கேட்கலாம்; நான் சான்றளிக்கப்பட்ட ஆதாரங்களின் அடிப்படையில் துல்லியமான பதில்களை வழங்குவேன்.",
        sources: [
          {
            id: "ta-src-greet",
            title: "கணினி அறிமுகம் (தமிழ்)",
            reference: "System-Knowledge-Base-TA",
            snippet: "பன்மொழி குரல் RAG அமைப்பு இந்திய மொழிகளில் குரல் மற்றும் உரை மூலம் உண்மை சார்ந்த அறிவை வழங்குகிறது."
          }
        ],
        latency: { stt_ms: 185, retrieval_ms: 60, generation_ms: 310, tts_ms: 225, total_ms: 780 }
      }
    },
    {
      id: "ta-corp",
      category: "Business",
      question: "ஒரு நிறுவனம் (கார்ப்பரேஷன்) என்பது என்ன?",
      response: {
        transcription: "ஒரு நிறுவனம் (கார்ப்பரேஷன்) என்பது என்ன?",
        language: "ta",
        normalized_language: "ta",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "கார்ப்பரேஷன் என்பது சட்டப்படி ஒரு தனி சட்டப்பூர்வ அமைப்பாக செயல்பட அங்கீகரிக்கப்பட்ட ஒரு நிறுவனம் அல்லது நபர்களின் குழுவாகும்.",
        sources: [
          {
            id: "ta-src-1102432",
            title: "MSMARCO-XI தமிழ் தரவுத்தளம்",
            reference: "MSMARCO-XI-tam-1102432",
            snippet: "ஒரு நிறுவனம் என்பது சட்டத்தில் அங்கீகரிக்கப்பட்ட ஒரு தனி அமைப்பாக செயல்பட அங்கீகரிக்கப்பட்ட அமைப்பாகும்."
          }
        ],
        latency: { stt_ms: 230, retrieval_ms: 80, generation_ms: 395, tts_ms: 275, total_ms: 980 }
      }
    },
    {
      id: "ta-thirukkural",
      category: "General",
      question: "திருக்குறளை இயற்றியவர் யார் மற்றும் அதில் எத்தனை அதிகாரங்கள் உள்ளன?",
      response: {
        transcription: "திருக்குறளை இயற்றியவர் யார் மற்றும் அதில் எத்தனை அதிகாரங்கள் உள்ளன?",
        language: "ta",
        normalized_language: "ta",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "திருக்குறளை இயற்றியவர் திருவள்ளுவர். இதில் அறத்துப்பால், பொருட்பால், காமத்துப்பால் என்ற மூன்று பிரிவுகளில் மொத்தம் 133 அதிகாரங்களும் 1330 குறட்பாக்களும் உள்ளன.",
        sources: [
          {
            id: "ta-src-lit",
            title: "தமிழ் இலக்கிய வரலாறு",
            reference: "Tamil-Literature-Corpus-Thirukkural",
            snippet: "திருவள்ளுவர் அருளிய திருக்குறள் 133 அதிகாரங்களில் 1330 அருங்குறள்களைக் கொண்டுள்ளது."
          }
        ],
        latency: { stt_ms: 215, retrieval_ms: 68, generation_ms: 350, tts_ms: 245, total_ms: 878 }
      }
    }
  ],

  // 7. TELUGU (te)
  te: [
    {
      id: "te-greeting",
      category: "Greeting",
      question: "నమస్కారం, మీరు ఎవరు మరియు ఎలా సహాయపడగలరు?",
      response: {
        transcription: "నమస్కారం, మీరు ఎవరు మరియు ఎలా సహాయపడగలరు?",
        language: "te",
        normalized_language: "te",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "నమస్కారం! నేను బహుభాషా వాయిస్ RAG ఇంజిన్‌ని. మీరు తెలుగులో నాతో మాట్లాడి ప్రశ్నలు అడగవచ్చు, మరియు నేను ఖచ్చితమైన ఆధారాలతో సరైన సమాధానం అందిస్తాను.",
        sources: [
          {
            id: "te-src-greet",
            title: "వ్యవస్థ పరిచయం (తెలుగు)",
            reference: "System-Knowledge-Base-TE",
            snippet: "బహుభాషా వాయిస్ RAG ఇంజిన్ భారతీయ భాషల్లో ధ్వని ఆధారిత ప్రశ్నలకు సరైన జ్ఞానాన్ని అందిస్తుంది."
          }
        ],
        latency: { stt_ms: 190, retrieval_ms: 62, generation_ms: 315, tts_ms: 230, total_ms: 797 }
      }
    },
    {
      id: "te-corp",
      category: "Business",
      question: "కార్పొరేషన్ అంటే ఏమిటి?",
      response: {
        transcription: "కార్పొరేషన్ అంటే ఏమిటి?",
        language: "te",
        normalized_language: "te",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "కార్పొరేషన్ అనేది చట్టపరంగా ఒకే స్వతంత్ర సంస్థగా వ్యవహరించడానికి మరియు గుర్తించబడటానికి అధికారం కలిగిన వ్యక్తుల సమూహం లేదా కంపెనీ.",
        sources: [
          {
            id: "te-src-1102432",
            title: "MSMARCO-XI తెలుగు సమాచారం",
            reference: "MSMARCO-XI-tel-1102432",
            snippet: "కార్పొరేషన్ అనేది ఒకే సంస్థగా వ్యవహరించడానికి మరియు చట్టంలో గుర్తింపు పొందిన వ్యక్తుల సమూహం లేదా కంపెనీ."
          }
        ],
        latency: { stt_ms: 235, retrieval_ms: 82, generation_ms: 405, tts_ms: 280, total_ms: 1002 }
      }
    },
    {
      id: "te-photosynthesis",
      category: "Science",
      question: "కిరణజన్య సంయోగక్రియ ఎలా జరుగుతుంది?",
      response: {
        transcription: "కిరణజన్య సంయోగక్రియ ఎలా జరుగుతుంది?",
        language: "te",
        normalized_language: "te",
        grounded: true,
        refusal: false,
        confidence: 0.97,
        answer: "ఆకుపచ్చని మొక్కలు సూర్యకాంతి, నీరు మరియు కార్బన్ డయాక్సైడ్ ఉపయోగించి గ్లూకోజ్ మరియు ఆక్సిజన్ తయారుచేసే ప్రక్రియను కిరణజన్య సంయోగక్రియ అంటారు.",
        sources: [
          {
            id: "te-src-bio",
            title: "వృక్షశాస్త్రం ప్రాథమిక పాఠాలు",
            reference: "Biology-TE-Botany",
            snippet: "పత్రహరితం సూర్యశక్తిని గ్రహించి రసాయన శక్తిగా మార్చడం ద్వారా మొక్కలకు ఆహారం సమకూరుస్తుంది."
          }
        ],
        latency: { stt_ms: 220, retrieval_ms: 70, generation_ms: 360, tts_ms: 250, total_ms: 900 }
      }
    }
  ],

  // 8. KANNADA (kn)
  kn: [
    {
      id: "kn-greeting",
      category: "Greeting",
      question: "ನಮಸ್ಕಾರ, ನೀವು ಯಾರು ಮತ್ತು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
      response: {
        transcription: "ನಮಸ್ಕಾರ, ನೀವು ಯಾರು ಮತ್ತು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        language: "kn",
        normalized_language: "kn",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "ನಮಸ್ಕಾರ! ನಾನು ಬಹುಭಾಷಾ ಧ್ವನಿ RAG ಎಂಜಿನ್. ನೀವು ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಯಾವುದೇ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು, ಮತ್ತು ನಾನು ಪರಿಶೀಲಿಸಿದ ಆಧಾರಗಳೊಂದಿಗೆ ನಿಖರವಾದ ಉತ್ತರವನ್ನು ನೀಡುತ್ತೇನೆ.",
        sources: [
          {
            id: "kn-src-greet",
            title: "ವ್ಯವಸ್ಥೆಯ ಪರಿಚಯ (ಕನ್ನಡ)",
            reference: "System-Knowledge-Base-KN",
            snippet: "ಬಹುಭಾಷಾ ಧ್ವನಿ RAG ವ್ಯವಸ್ಥೆಯು ಭಾರತೀಯ ಭಾಷೆಗಳಲ್ಲಿ ನಿಖರ ಮತ್ತು ಸತ್ಯಾಧಾರಿತ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸುತ್ತದೆ."
          }
        ],
        latency: { stt_ms: 195, retrieval_ms: 65, generation_ms: 320, tts_ms: 235, total_ms: 815 }
      }
    },
    {
      id: "kn-corp",
      category: "Business",
      question: "ಕಾರ್ಪೊರೇಷನ್ ಎಂದರೇನು?",
      response: {
        transcription: "ಕಾರ್ಪೊರೇಷನ್ ಎಂದರೇನು?",
        language: "kn",
        normalized_language: "kn",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "ಕಾರ್ಪೊರೇಷನ್ ಎನ್ನುವುದು ಕಾನೂನುಬದ್ಧವಾಗಿ ಒಂದೇ ಘಟಕವಾಗಿ ಕಾರ್ಯನಿರ್ವಹಿಸಲು ಅಧಿಕಾರ ಹೊಂದಿರುವ ಮತ್ತು ಮಾನ್ಯತೆ ಪಡೆದ ಕಂಪನಿ ಅಥವಾ ವ್ಯಕ್ತಿಗಳ ಗುಂಪು.",
        sources: [
          {
            id: "kn-src-corp",
            title: "ಕಾನೂನು ಮತ್ತು ವಾಣಿಜ್ಯ ವಿಶ್ವಕೋಶ",
            reference: "Business-Law-KN",
            snippet: "ಕಾರ್ಪೊರೇಷನ್ ಒಂದು ಪ್ರತ್ಯೇಕ ಕಾನೂನು ಅಸ್ತಿತ್ವವನ್ನು ಹೊಂದಿರುವ ನೋಂದಾಯಿತ ಸಂಸ್ಥೆಯಾಗಿದೆ."
          }
        ],
        latency: { stt_ms: 230, retrieval_ms: 78, generation_ms: 390, tts_ms: 270, total_ms: 968 }
      }
    }
  ],

  // 9. MALAYALAM (ml)
  ml: [
    {
      id: "ml-greeting",
      category: "Greeting",
      question: "നമസ്കാരം, നിങ്ങൾ ആരാണ്, എങ്ങനെ സഹായിക്കാനാകും?",
      response: {
        transcription: "നമസ്കാരം, നിങ്ങൾ ആരാണ്, എങ്ങനെ സഹായിക്കാനാകും?",
        language: "ml",
        normalized_language: "ml",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "നമസ്കാരം! ഞാൻ ബഹുഭാഷാ വോയ്‌സ് RAG എഞ്ചിനാണ്. നിങ്ങൾക്ക് മലയാളത്തിൽ ശബ്ദത്തിലൂടെയോ ടെക്സ്റ്റിലൂടെയോ ചോദ്യങ്ങൾ ചോദിക്കാം, വിശ്വസനീയമായ തെളിവുകളുടെ അടിസ്ഥാനത്തിൽ ഞാൻ ഉത്തരം നൽകും.",
        sources: [
          {
            id: "ml-src-greet",
            title: "സിസ്റ്റം ആമുഖം (മലയാളം)",
            reference: "System-Knowledge-Base-ML",
            snippet: "ബഹുഭാഷാ വോയ്‌സ് RAG എഞ്ചിൻ ഇന്ത്യൻ ഭാഷകളിൽ കൃത്യവും പരിശോധിച്ചുറപ്പിച്ചതുമായ വിവരങ്ങൾ നൽകുന്നു."
          }
        ],
        latency: { stt_ms: 190, retrieval_ms: 60, generation_ms: 310, tts_ms: 230, total_ms: 790 }
      }
    },
    {
      id: "ml-photosynthesis",
      category: "Science",
      question: "പ്രകാശസംശ്ലේෂണം എന്നാൽ എന്താണ്?",
      response: {
        transcription: "പ്രകാശസംശ്ലේෂണം എന്നാൽ എന്താണ്?",
        language: "ml",
        normalized_language: "ml",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "സൂര്യപ്രകാശം, ജലം, കാർബൺ ഡൈഓക്സൈഡ് എന്നിവ ഉപയോഗിച്ച് സസ്യങ്ങൾ ഗ്ലൂക്കോസും ഓക്സിജനും ഉത്പാദിപ്പിക്കുന്ന പ്രക്രിയയാണ് പ്രകാശസംശ്ലේෂണം.",
        sources: [
          {
            id: "ml-src-bio",
            title: "സസ്യശാസ്ത്ര പാഠാവലി",
            reference: "Botany-ML-Index",
            snippet: "ഹരിതകണങ്ങളുടെ സാന്നിധ്യത്തിൽ സൗരോർജ്ജം രാസോർജ്ജമാക്കി മാറ്റുന്ന ജീവശാസ്ത്ര പ്രക്രിയയാണിത്."
          }
        ],
        latency: { stt_ms: 225, retrieval_ms: 70, generation_ms: 360, tts_ms: 250, total_ms: 905 }
      }
    }
  ],

  // 10. PUNJABI (pa)
  pa: [
    {
      id: "pa-greeting",
      category: "Greeting",
      question: "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ, ਤੁਸੀਂ ਕੌਣ ਹੋ ਅਤੇ ਕੀ ਕਰ ਸਕਦੇ ਹੋ?",
      response: {
        transcription: "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ, ਤੁਸੀਂ ਕੌਣ ਹੋ ਅਤੇ ਕੀ ਕਰ ਸਕਦੇ ਹੋ?",
        language: "pa",
        normalized_language: "pa",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ! ਮੈਂ ਬਹੁਭਾਸ਼ਾਈ ਵੌਇਸ RAG ਇੰਜਣ ਹਾਂ। ਤੁਸੀਂ ਪੰਜਾਬੀ ਵਿੱਚ ਕੋਈ ਵੀ ਸਵਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ, ਅਤੇ ਮੈਂ ਸਿਰਫ਼ ਪ੍ਰਮਾਣਿਤ ਤੱਥਾਂ ਦੇ ਆਧਾਰ 'ਤੇ ਸਹੀ ਜਵਾਬ ਦੇਵਾਂਗਾ।",
        sources: [
          {
            id: "pa-src-greet",
            title: "ਸਿਸਟਮ ਜਾਣ-ਪਛਾਣ (ਪੰਜਾਬੀ)",
            reference: "System-Knowledge-Base-PA",
            snippet: "ਬਹੁਭਾਸ਼ਾਈ ਵੌਇਸ RAG ਇੰਜਣ ਆਵਾਜ਼ ਰਾਹੀਂ ਤਸਦੀਕਸ਼ੁਦਾ ਜਾਣਕਾਰੀ ਮੁਹੱਈਆ ਕਰਦਾ ਹੈ।"
          }
        ],
        latency: { stt_ms: 185, retrieval_ms: 60, generation_ms: 310, tts_ms: 220, total_ms: 775 }
      }
    },
    {
      id: "pa-corp",
      category: "Business",
      question: "ਕਾਰਪੋਰੇਸ਼ਨ ਕੀ ਹੈ?",
      response: {
        transcription: "ਕਾਰਪੋਰੇਸ਼ਨ ਕੀ ਹੈ?",
        language: "pa",
        normalized_language: "pa",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "ਕਾਰਪੋਰੇਸ਼ਨ ਇੱਕ ਕੰਪਨੀ ਜਾਂ ਲੋਕਾਂ ਦਾ ਸਮੂਹ ਹੁੰਦਾ ਹੈ ਜੋ ਇੱਕ ਕਾਨੂੰਨੀ ਇਕਾਈ ਵਜੋਂ ਕੰਮ ਕਰਨ ਲਈ ਅਧਿਕਾਰਤ ਹੁੰਦਾ ਹੈ ਅਤੇ ਕਾਨੂੰਨ ਵਿੱਚ ਇਸਦੀ ਵੱਖਰੀ ਹੋਂਦ ਮੰਨੀ ਜਾਂਦੀ ਹੈ।",
        sources: [
          {
            id: "pa-src-1102432",
            title: "MSMARCO-XI ਪੰਜਾਬੀ ਡੇਟਾਸੈੱਟ",
            reference: "MSMARCO-XI-pan-1102432",
            snippet: "ਕਾਰਪੋਰੇਸ਼ਨ ਇੱਕ ਕੰਪਨੀ ਜਾਂ ਲੋਕਾਂ ਦਾ ਸਮੂਹ ਹੁੰਦਾ ਹੈ ਜੋ ਇੱਕ ਇਕਾਈ ਵਜੋਂ ਕੰਮ ਕਰਨ ਲਈ ਅਧਿਕਾਰਤ ਹੁੰਦਾ ਹੈ।"
          }
        ],
        latency: { stt_ms: 230, retrieval_ms: 75, generation_ms: 390, tts_ms: 270, total_ms: 965 }
      }
    }
  ],

  // 11. URDU (ur)
  ur: [
    {
      id: "ur-greeting",
      category: "Greeting",
      question: "السلام علیکم / آداب، آپ کون ہیں اور کیا کر سکتے ہیں؟",
      response: {
        transcription: "السلام علیکم / آداب، آپ کون ہیں اور کیا کر سکتے ہیں؟",
        language: "ur",
        normalized_language: "ur",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "وعلیکم السلام / آداب! میں کثیر لسانی وائس RAG انجن ہوں۔ آپ اردو میں اپنی آواز سے کوئی بھی سوال پوچھ سکتے ہیں، اور میں مصدقہ شواہد کی بنیاد پر درست جواب فراہم کروں گا۔",
        sources: [
          {
            id: "ur-src-greet",
            title: "سسٹم کا تعارف (اردو)",
            reference: "System-Knowledge-Base-UR",
            snippet: "کثیر لسانی وائس RAG سسٹم تصدیق شدہ شواہد کے ساتھ درست معلومات فراہم کرتا ہے۔"
          }
        ],
        latency: { stt_ms: 180, retrieval_ms: 60, generation_ms: 300, tts_ms: 220, total_ms: 760 }
      }
    },
    {
      id: "ur-corp",
      category: "Business",
      question: "کارپوریشن کیا ہے؟",
      response: {
        transcription: "کارپوریشن کیا ہے؟",
        language: "ur",
        normalized_language: "ur",
        grounded: true,
        refusal: false,
        confidence: 0.98,
        answer: "کارپوریشن ایک کمپنی یا افراد کا ایسا گروہ ہے جو قانون کی نظر میں ایک واحد اور خودمختار ادارے کے طور پر کام کرنے کا مجاز ہوتا ہے۔",
        sources: [
          {
            id: "ur-src-1102432",
            title: "MSMARCO-XI اردو کارپس",
            reference: "MSMARCO-XI-urd-1102432",
            snippet: "کارپوریشن ایک کمپنی یا لوگوں کا ایسا گروپ ہے جو قانون میں ایک واحد ادارے کے طور پر کام کرنے کے لیے تسلیم شدہ ہے۔"
          }
        ],
        latency: { stt_ms: 225, retrieval_ms: 75, generation_ms: 380, tts_ms: 260, total_ms: 940 }
      }
    }
  ],

  // 12. ODIA (or)
  or: [
    {
      id: "or-greeting",
      category: "Greeting",
      question: "ନମସ୍କାର, ଆପଣ କିଏ ଏବଂ କିପରି ସାହାଯ୍ୟ କରିପାରିବେ?",
      response: {
        transcription: "ନମସ୍କାର, ଆପଣ କିଏ ଏବଂ କିପରି ସାହାଯ୍ୟ କରିପାରିବେ?",
        language: "or",
        normalized_language: "or",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "ନମସ୍କାର! ମୁଁ ବହୁଭାଷୀ ଭଏସ୍ RAG ଇଞ୍ଜିନ୍। ଆପଣ ଓଡ଼ିଆରେ ଯେକୌଣସି ପ୍ରଶ୍ନ ପଚାରିପାରିବେ ଏବଂ ମୁଁ ପ୍ରମାଣିତ ତଥ୍ୟ ଆଧାରରେ ସଠିକ୍ ଉତ୍ତର ପ୍ରଦାନ କରିବି।",
        sources: [
          {
            id: "or-src-greet",
            title: "ସିଷ୍ଟମ୍ ପରିଚୟ (ଓଡ଼ିଆ)",
            reference: "System-Knowledge-Base-OR",
            snippet: "ଭଏସ୍ RAG ଇଞ୍ଜିନ୍ ଓଡ଼ିଆ ଭାଷାରେ ସଠିକ୍ ତଥ୍ୟ ଏବଂ ପ୍ରମାଣିତ ଜ୍ଞାନ ପ୍ରଦାନ କରେ।"
          }
        ],
        latency: { stt_ms: 190, retrieval_ms: 60, generation_ms: 310, tts_ms: 230, total_ms: 790 }
      }
    }
  ],

  // 13. ASSAMESE (as)
  as: [
    {
      id: "as-greeting",
      category: "Greeting",
      question: "নমস্কাৰ, আপুনি কোন আৰু কেনেদৰে সহায় কৰিব পাৰে?",
      response: {
        transcription: "নমস্কাৰ, আপুনি কোন আৰু কেনেদৰে সহায় কৰিব পাৰে?",
        language: "as",
        normalized_language: "as",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "নমস্কাৰ! মই বহুভাষিক ভইচ RAG ইঞ্জিন। আপুনি অসমীয়াত যিকোনো প্ৰশ্ন সুধিব পাৰে, আৰু মই প্ৰমাণিত তথ্যৰ ওপৰত ভিত্তি কৰি সঠিক উত্তৰ দিম।",
        sources: [
          {
            id: "as-src-greet",
            title: "ব্যৱস্থাৰ পৰিচয় (অসমীয়া)",
            reference: "System-Knowledge-Base-AS",
            snippet: "বহুভাষিক ভইচ RAG ইঞ্জিনে অসমীয়া ভাষাত সঠিক জ্ঞান প্ৰদান কৰে।"
          }
        ],
        latency: { stt_ms: 195, retrieval_ms: 65, generation_ms: 320, tts_ms: 235, total_ms: 815 }
      }
    }
  ],

  // 14. NEPALI (ne)
  ne: [
    {
      id: "ne-greeting",
      category: "Greeting",
      question: "नमस्ते, तपाईं को हुनुहुन्छ र कसरी सहयोग गर्न सक्नुहुन्छ?",
      response: {
        transcription: "नमस्ते, तपाईं को हुनुहुन्छ र कसरी सहयोग गर्न सक्नुहुन्छ?",
        language: "ne",
        normalized_language: "ne",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "नमस्ते! म बहुभाषी भ्वाइस RAG इन्जिन हुँ। तपाईंले नेपालीमा कुनै पनि प्रश्न सोध्न सक्नुहुन्छ, र म प्रमाणित तथ्यका आधारमा सटीक उत्तर प्रदान गर्नेछु।",
        sources: [
          {
            id: "ne-src-greet",
            title: "प्रणाली परिचय (नेपाली)",
            reference: "System-Knowledge-Base-NE",
            snippet: "बहुभाषी भ्वाइस RAG इन्जिनले नेपाली भाषामा आवाज र पाठद्वारा प्रमाणित ज्ञान प्रदान गर्दछ।"
          }
        ],
        latency: { stt_ms: 185, retrieval_ms: 60, generation_ms: 310, tts_ms: 220, total_ms: 775 }
      }
    }
  ],

  // 15. SANSKRIT (sa)
  sa: [
    {
      id: "sa-greeting",
      category: "Greeting",
      question: "नमो नमः, भवान् कः अस्ति कथं च साहाय्यं करोति?",
      response: {
        transcription: "नमो नमः, भवान् कः अस्ति कथं च साहाय्यं करोति?",
        language: "sa",
        normalized_language: "sa",
        grounded: true,
        refusal: false,
        confidence: 0.99,
        answer: "नमो नमः! अहम् बहुभाषीय-ध्वनि-RAG-यन्त्रम् अस्मि। भवन्तः संस्कृतभाषया यत्किमपि प्रष्टुं शक्नुवन्ति, अहं च प्रमाणित-प्रमाणैः सह शुद्धम् उत्तरं दास्यामि।",
        sources: [
          {
            id: "sa-src-greet",
            title: "व्यवस्था परिचयः (संस्कृतम्)",
            reference: "System-Knowledge-Base-SA",
            snippet: "बहुभाषीय-ध्वनि-RAG-यन्त्रं भारतीयभाषासु यथार्थं ज्ञानं वितरति।"
          }
        ],
        latency: { stt_ms: 190, retrieval_ms: 65, generation_ms: 320, tts_ms: 230, total_ms: 805 }
      }
    }
  ]
};

export function getPredefinedQueriesForLanguage(langCode: string): PredefinedQueryItem[] {
  const norm = (langCode || "hi").toLowerCase().split("-")[0];
  const list = PREDEFINED_QUERIES_BY_LANGUAGE[norm];
  if (list && list.length > 0) return list;
  return PREDEFINED_QUERIES_BY_LANGUAGE["hi"] || [];
}

export function findPredefinedResponse(queryText: string, langCode: string): VoiceQueryResponse | null {
  const normLang = (langCode || "hi").toLowerCase().split("-")[0];
  const cleanQuery = queryText.trim().toLowerCase();

  const isGreeting =
    /^(hello|hi|hey|namaste|vanakkam|namaskaram|namaskara|sat sri akal|assalamu alaikum|adab|pranam|namo namah|নমস্কার|नमस्ते|வணக்கம்|నమస్కారం|ನಮಸ್ಕಾರ|നമസ്കാരം|નમસ્તે|ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ|السلام علیکم|آداب|ନମସ୍କାର|নমস্কাৰ|नमो नमः)/i.test(
      cleanQuery
    );

  const langQueries = PREDEFINED_QUERIES_BY_LANGUAGE[normLang] || [];

  if (isGreeting) {
    const greetingItem = langQueries.find((q) => q.category === "Greeting");
    if (greetingItem) return greetingItem.response;
  }

  const match = langQueries.find(
    (q) =>
      cleanQuery.includes(q.question.toLowerCase()) ||
      q.question.toLowerCase().includes(cleanQuery) ||
      cleanQuery.includes(q.response.transcription.toLowerCase())
  );

  return match ? match.response : null;
}
