"""Indian-language vocabulary for the offline rule-based planner (and for repairing Gemma plans).

Each concept maps to word stems per language. Matching is by substring, so inflected forms still match.
This is keyword coverage for common phrasings, not translation: Gemma 4 handles free-form wording.
The lists were written carefully but should be reviewed by native speakers before production use."""
from __future__ import annotations

LANGUAGES = {  # display name -> (ISO code for speech recognition, script check)
    "English": "en", "Hindi": "hi", "Gujarati": "gu", "Tamil": "ta", "Punjabi": "pa",
    "Marathi": "mr", "Bengali": "bn", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml",
}

LEX: dict[str, list[str]] = {
    # --- metrics ---
    "electric": ["बिजली", "વીજળી", "વીજ", "மின்சாரம்", "மின்", "ਬਿਜਲੀ", "वीज", "বিদ্যুৎ", "విద్యుత్", "ವಿದ್ಯುತ್", "വൈദ്യുതി"],
    "water": ["पानी", "પાણી", "தண்ணீர்", "நீர்", "ਪਾਣੀ", "पाणी", "জল", "পানি", "నీరు", "నీళ్ల", "ನೀರು", "വെള്ളം", "ജലം"],
    # --- ranking ---
    "most": ["ज्यादा", "ज़्यादा", "सबसे", "अधिक", "સૌથી વધુ", "વધુ", "அதிக", "ਸਭ ਤੋਂ ਵੱਧ", "ਵੱਧ", "सर्वाधिक", "जास्त", "সবচেয়ে বেশি", "বেশি",
             "అత్యధిక", "ఎక్కువ", "ಅತಿ ಹೆಚ್ಚು", "ಹೆಚ್ಚು", "ഏറ്റവും കൂടുതൽ", "കൂടുതൽ"],
    "least": ["कम", "સૌથી ઓછ", "ઓછું", "ઓછા", "குறைவு", "குறைந்த", "ਸਭ ਤੋਂ ਘੱਟ", "ਘੱਟ", "सर्वात कमी", "कमी", "সবচেয়ে কম", "কম",
              "అత్యల్ప", "తక్కువ", "ಅತಿ ಕಡಿಮೆ", "ಕಡಿಮೆ", "ഏറ്റവും കുറവ്", "കുറവ്", "കുറഞ്ഞ"],
    "which": ["कौन", "कौनसी", "કયું", "કઈ", "કયા", "எந்த", "எது", "ਕਿਹੜ", "ਕੌਣ", "कोणत", "কোন", "ఏ భవనం", "ఏది", "ಯಾವ", "ഏത്"],
    # --- question types ---
    "compare": ["तुलना", "સરખામણી", "ஒப்பிட", "ஒப்பீ", "ਤੁਲਨਾ", "तुलना", "তুলনা", "పోల్చ", "పోలిక", "ಹೋಲಿಸ", "ಹೋಲಿಕೆ", "താരതമ്യ"],
    "trend": ["रुझान", "ट्रेंड", "વલણ", "ટ્રેન્ડ", "போக்கு", "ਰੁਝਾਨ", "ਟ੍ਰੈਂਡ", "ट्रेंड", "প্রবণতা", "ধারা", "ధోరణి", "ట్రెండ్", "ಪ್ರವೃತ್ತಿ", "ಟ್ರೆಂಡ್", "പ്രവണത", "ട്രെൻഡ്"],
    "total": ["कुल", "કુલ", "மொத்த", "ਕੁੱਲ", "एकूण", "মোট", "మొత్తం", "ಒಟ್ಟು", "ആകെ"],
    "average": ["औसत", "સરેરાશ", "சராசரி", "ਔਸਤ", "सरासरी", "গড়", "సగటు", "ಸರಾಸರಿ", "ശരാശരി"],
    "unusual": ["असामान्य", "बर्बादी", "बर्बाद", "અસામાન્ય", "વેડફાટ", "அசாதாரண", "வழக்கத்திற்கு மாறான", "வீண்", "ਅਸਾਧਾਰਨ", "ਬਰਬਾਦ", "असामान्य",
               "অস্বাভাবিক", "অপচয়", "అసాధారణ", "వృథా", "ಅಸಾಮಾನ್ಯ", "ವ್ಯರ್ಥ", "അസാധാരണ", "പാഴ്"],
    # --- time ---
    "lastmonth": ["पिछले महीने", "पिछले माह", "ગયા મહિને", "கடந்த மாதம்", "ਪਿਛਲੇ ਮਹੀਨੇ", "मागील महिन्यात", "गेल्या महिन्यात", "गेल्या महिन्यात", "গত মাসে",
                  "గత నెల", "ಕಳೆದ ತಿಂಗಳು", "കഴിഞ്ഞ മാസം"],
    # --- things the dataset usually cannot answer ---
    "student": ["छात्र", "विद्यार्थी", "વિદ્યાર્થી", "மாணவ", "ਵਿਦਿਆਰਥੀ", "ছাত্র", "শিক্ষার্থী", "విద్యార్థి", "ವಿದ್ಯಾರ್ಥಿ", "വിദ്യാർത്ഥി"],
    "cost": ["खर्च", "लागत", "ખર્ચ", "செலவு", "கட்டணம்", "ਖਰਚ", "ਬਿੱਲ", "খরচ", "ఖర్చు", "బిల్లు", "ವೆಚ್ಚ", "ചെലവ്"],
    "carbon": ["कार्बन", "કાર્બન", "கார்பன்", "ਕਾਰਬਨ", "কার্বন", "కార్బన్", "ಕಾರ್ಬನ್", "കാർബൺ"],
}

MONTHS: dict[int, list[str]] = {  # month number -> native names (Hindi, Gujarati, Tamil, Punjabi, Marathi, Bengali, Telugu, Kannada, Malayalam)
    1: ["जनवरी", "જાન્યુઆરી", "ஜனவரி", "ਜਨਵਰੀ", "जानेवारी", "জানুয়ারি", "జనవరి", "ಜನವರಿ", "ജനുവരി"],
    2: ["फरवरी", "ફેબ્રુઆરી", "பிப்ரவரி", "ਫ਼ਰਵਰੀ", "ਫਰਵਰੀ", "फेब्रुवारी", "ফেব্রুয়ারি", "ఫిబ్రవరి", "ಫೆಬ್ರವರಿ", "ഫെബ്രുവരി"],
    3: ["मार्च", "માર્ચ", "மார்ச்", "ਮਾਰਚ", "মার্চ", "మార్చి", "ಮಾರ್ಚ್", "മാർച്ച്"],
    4: ["अप्रैल", "એપ્રિલ", "ஏப்ரல்", "ਅਪ੍ਰੈਲ", "ਅਪ੍ਰੈਲ", "एप्रिल", "এপ্রিল", "ఏప్రిల్", "ಏಪ್ರಿಲ್", "ഏപ്രിൽ"],
    5: ["मई", "મે", "மே", "ਮਈ", "मे", "মে", "మే", "ಮೇ", "മെയ്"],
    6: ["जून", "જૂન", "ஜூன்", "ਜੂਨ", "জুন", "జూన్", "ಜೂನ್", "ജൂൺ"],
    7: ["जुलाई", "જુલાઈ", "ஜூலை", "ਜੁਲਾਈ", "जुलै", "জুলাই", "జులై", "జూలై", "ಜುಲೈ", "ജൂലൈ"],
    8: ["अगस्त", "ઓગસ્ટ", "ஆகஸ்ட்", "ਅਗਸਤ", "ऑगस्ट", "আগস্ট", "ఆగస్టు", "ಆಗಸ್ಟ್", "ഓഗസ്റ്റ്"],
    9: ["सितंबर", "सितम्बर", "સપ્ટેમ્બર", "செப்டம்பர்", "ਸਤੰਬਰ", "सप्टेंबर", "সেপ্টেম্বর", "సెప్టెంబర్", "ಸೆಪ್ಟೆಂಬರ್", "സെപ്റ്റംബർ"],
    10: ["अक्टूबर", "ઓક્ટોબર", "அக்டோபர்", "ਅਕਤੂਬਰ", "ऑक्टोबर", "অক্টোবর", "అక్టోబర్", "ಅಕ್ಟೋಬರ್", "ഒക്ടോബർ"],
    11: ["नवंबर", "नवम्बर", "નવેમ્બર", "நவம்பர்", "ਨਵੰਬਰ", "नोव्हेंबर", "নভেম্বর", "నవంబర్", "ನವೆಂಬರ್", "നവംബർ"],
    12: ["दिसंबर", "दिसम्बर", "ડિસેમ્બર", "டிசம்பர்", "ਦਸੰਬਰ", "डिसेंबर", "ডিসেম্বর", "డిసెంబర్", "ಡಿಸೆಂಬರ್", "ഡിസംബർ"],
}

_SCRIPT_RANGES = [(0x0900, 0x0DFF)]   # Devanagari through Malayalam


def is_indic(text: str) -> bool:
    """True when the text contains any Indic-script character."""
    return any(lo <= ord(c) <= hi for c in text for lo, hi in _SCRIPT_RANGES)


_CASE_SUFFIXES = ("માં", "में", "मध्ये", "मध्ये", "లో", "ில்", "ல்", "ನಲ್ಲಿ", "ൽ", "ਵਿੱਚ", "ना", "ની", "નો", "का", "की")


def find_native_months(text: str) -> list[tuple[int, int]]:
    """(position, month_number) for native month names.
    Names of 3+ characters match as substrings (so inflected forms work). Very short names, which are
    mostly the word for May, must be a whole token, optionally with a common case suffix."""
    import re
    found: list[tuple[int, int]] = []
    tokens = [(m.start(), m.group(0)) for m in re.finditer(r"[^\s,.;:?!()\-–/]+", text)]
    for num, names in MONTHS.items():
        for name in names:
            if len(name) <= 2:
                for pos, tok in tokens:
                    if tok == name or (tok.startswith(name) and tok[len(name):] in _CASE_SUFFIXES):
                        found.append((pos, num))
            else:
                i = text.find(name)
                if i >= 0:
                    found.append((i, num))
    return found


import re as _re
# "bill" in several scripts, excluding the word for "building" (बिल्डिंग, બિલ્ડિંગ, বিল্ডিং, ಬಿಲ್ಡಿಂಗ್, ബിൽഡിംഗ്, பில்டிங்)
BILL_RE = _re.compile(r"(?:बिल(?!\u094d)|બિલ(?!\u0acd)|বিল(?!\u09cd)|ಬಿಲ್(?!ಡ)|ബിൽ(?!ഡ)|பில்(?!டி))")
