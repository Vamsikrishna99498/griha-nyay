"""Language detection (code, not the model) and the few strings that code writes itself.

Code-written text exists in English, Hindi and Telugu. Hinglish/Tenglish users get English
for these strings (they read Latin script); the model writes everything else in their style.
Hindi/Telugu strings were written once and should be reviewed by a fluent speaker.
"""
from __future__ import annotations

import re

LANGS = ["English", "Hindi", "Telugu", "Hinglish", "Tenglish"]
TELUGU_RE = re.compile(r"[ఀ-౿]")
DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")
TENGLISH = re.compile(r"\b(nenu|naaku|naku|ledu|undi|kaavali|kavali|cheyyali|ivvaledu|ivvatledu|chesanu|kattanu|"
                      r"enti|mee|meeru|ayindi|cheppandi|kaadu|ippudu)\b", re.I)
HINGLISH = re.compile(r"\b(hai|hain|nahi|nahin|mera|meri|mujhe|kya|paise|paisa|diya|kiya|abhi|wapas|chahiye|"
                      r"bilkul|lekin|aur|kab|kyun|tha|thi|raha|rahi)\b", re.I)


def detect_language(text: str, current: str | None = None) -> str:
    """Script first, then romanised marker words. Short messages ("ok", "40 lakh") keep the
    language already in use, so a Telugu user typing a number doesn't flip to English."""
    t = text or ""
    te, hi = len(TELUGU_RE.findall(t)), len(DEVANAGARI_RE.findall(t))
    if te or hi:
        return "Telugu" if te >= hi else "Hindi"
    words = re.findall(r"[A-Za-z]+", t)
    if len(words) < 4 and current:
        return current
    n_te, n_hi = len(TENGLISH.findall(t)), len(HINGLISH.findall(t))
    if n_te >= 2 and n_te >= n_hi:
        return "Tenglish"
    if n_hi >= 2:
        return "Hinglish"
    return "English" if words or not current else current


def code_lang(language: str | None) -> str:
    return {"Hindi": "hi", "Telugu": "te"}.get(language or "", "en")


STRINGS = {
    "welcome": {
        "en": "Namaste / నమస్కారం 🙏 I help homebuyers in **Telangana** whose builder **delayed possession** or left **defects** in the flat. Tell me your story in your own words - English, Hindi, Telugu or mixed.",
        "hi": "नमस्ते 🙏 मैं तेलंगाना के उन घर ख़रीदारों की मदद करता हूँ जिनके बिल्डर ने कब्ज़ा देर से दिया या फ़्लैट में ख़राबियाँ छोड़ीं।",
        "te": "నమస్కారం 🙏 బిల్డర్ ఫ్లాట్ ఇవ్వడంలో ఆలస్యం చేసిన లేదా ఫ్లాట్‌లో లోపాలు వదిలిన తెలంగాణ కొనుగోలుదారులకు నేను సహాయం చేస్తాను.",
    },
    "privacy": {
        "en": "🔒 Please don't type Aadhaar, PAN, bank account or phone numbers - I remove them anyway. Your messages are processed by an AI provider; nothing is saved after you close this tab.",
        "hi": "🔒 कृपया आधार, PAN, बैंक खाता या फ़ोन नंबर न लिखें - मैं उन्हें वैसे भी हटा देता हूँ। आपके संदेश एक AI प्रदाता प्रोसेस करता है; टैब बंद करने के बाद कुछ भी सेव नहीं रहता।",
        "te": "🔒 దయచేసి ఆధార్, PAN, బ్యాంక్ ఖాతా లేదా ఫోన్ నంబర్లు టైప్ చేయకండి - నేను వాటిని తీసేస్తాను. మీ సందేశాలను ఒక AI సంస్థ ప్రాసెస్ చేస్తుంది; ఈ ట్యాబ్ మూసిన తర్వాత ఏదీ సేవ్ అవ్వదు.",
    },
    "removed_ids": {
        "en": "🔒 I removed some personal numbers from your message ({kinds}) before processing it. I don't need them to help you.",
        "hi": "🔒 मैंने आपके संदेश से कुछ निजी नंबर ({kinds}) हटा दिए। आपकी मदद के लिए इनकी ज़रूरत नहीं है।",
        "te": "🔒 మీ సందేశం నుండి కొన్ని వ్యక్తిగత నంబర్లను ({kinds}) తీసేశాను. మీకు సహాయం చేయడానికి అవి అవసరం లేదు.",
    },
    "too_long": {
        "en": "Your message is very long ({n} characters). Please send it in shorter parts (under {max} characters each) so I don't miss anything.",
        "hi": "आपका संदेश बहुत लंबा है ({n} अक्षर)। कृपया इसे छोटे हिस्सों में भेजें (हर हिस्सा {max} अक्षरों से कम)।",
        "te": "మీ సందేశం చాలా పొడవుగా ఉంది ({n} అక్షరాలు). దయచేసి చిన్న భాగాలుగా ({max} అక్షరాల లోపు) పంపండి.",
    },
    "need": {
        "en": "Thanks, that helps. To work out your options I still need: {items}.",
        "hi": "धन्यवाद। आपके विकल्प समझने के लिए मुझे अभी ये चाहिए: {items}।",
        "te": "ధన్యవాదాలు. మీ ఎంపికలు చెప్పడానికి నాకు ఇంకా ఇవి కావాలి: {items}.",
    },
    "need_plain": {
        "en": "To work out your options I still need: {items}.",
        "hi": "आपके विकल्प समझने के लिए मुझे अभी ये चाहिए: {items}।",
        "te": "మీ ఎంపికలు చెప్పడానికి నాకు ఇంకా ఇవి కావాలి: {items}.",
    },
    "hello": {"en": "Hello 🙏 ", "hi": "नमस्ते 🙏 ", "te": "నమస్కారం 🙏 "},
    "tell_me": {
        "en": "I can help with two problems in **Telangana**: a builder **delaying possession** of your flat or house, or **defects after possession**. Tell me what happened in your own words - the builder and project, the city, the date possession was promised (or the date you got the flat), how much you have paid, and what you want.",
        "hi": "मैं **तेलंगाना** में दो समस्याओं में मदद कर सकता हूँ: बिल्डर का फ़्लैट या घर का **कब्ज़ा देर से देना**, या **कब्ज़े के बाद ख़राबियाँ**। अपने शब्दों में बताइए कि क्या हुआ - बिल्डर और प्रोजेक्ट का नाम, शहर, कब्ज़े की वादा की गई तारीख़ (या जिस तारीख़ को फ़्लैट मिला), अब तक कितना भुगतान किया, और आप क्या चाहते हैं।",
        "te": "నేను **తెలంగాణ**లో రెండు సమస్యలకు సహాయం చేయగలను: బిల్డర్ ఫ్లాట్ లేదా ఇంటి **స్వాధీనం ఆలస్యం చేయడం**, లేదా **స్వాధీనం తర్వాత లోపాలు**. ఏం జరిగిందో మీ మాటల్లో చెప్పండి - బిల్డర్, ప్రాజెక్ట్ పేరు, ఊరు, స్వాధీనం ఇస్తామన్న తేదీ (లేదా ఫ్లాట్ అందిన తేదీ), ఇప్పటివరకు ఎంత చెల్లించారు, మీకు ఏం కావాలి.",
    },
    "tell_me_other": {
        "en": "If your problem is a different one, free help is available here:",
        "hi": "अगर आपकी समस्या कुछ और है, तो मुफ़्त मदद यहाँ मिलेगी:",
        "te": "మీ సమస్య వేరేదైతే, ఉచిత సహాయం ఇక్కడ దొరుకుతుంది:",
    },
    "updated_case": {
        "en": "📝 **Updated your case file:** {changes}",
        "hi": "📝 **आपकी केस फ़ाइल अपडेट की:** {changes}",
        "te": "📝 **మీ కేసు ఫైల్ అప్‌డేట్ చేశాను:** {changes}",
    },
    "need_lawyer": {
        "en": "**I need to be honest: this part needs a real lawyer.**",
        "hi": "**मुझे साफ़ कहना होगा: इसके लिए असली वकील की ज़रूरत है।**",
        "te": "**నిజాయితీగా చెప్పాలి: దీనికి నిజమైన న్యాయవాది అవసరం.**",
    },
    "where_help": {"en": "**Where to get help:**", "hi": "**मदद कहाँ मिलेगी:**", "te": "**సహాయం ఎక్కడ దొరుకుతుంది:**"},
    "take_summary": {
        "en": "**Take this case summary with you:**",
        "hi": "**यह केस सारांश साथ ले जाएँ:**",
        "te": "**ఈ కేసు సారాంశాన్ని మీతో తీసుకెళ్లండి:**",
    },
    "off_topic": {
        "en": "I'm sorry you're dealing with this. I can only help with two problems: **a builder delaying possession** of a flat/house, or **defects after possession**, in **Telangana**. Your problem ({topic}) is outside what I cover, and I'd rather not guess about law I haven't checked.",
        "hi": "मुझे खेद है कि आप इस परेशानी में हैं। मैं सिर्फ़ दो समस्याओं के लिए बना हूँ: तेलंगाना में **बिल्डर का कब्ज़ा देर से देना** या **कब्ज़े के बाद ख़राबियाँ**। आपकी समस्या ({topic}) मेरे दायरे से बाहर है, और जो क़ानून मैंने जाँचा नहीं उस पर मैं अनुमान नहीं लगाना चाहता।",
        "te": "మీకు ఈ ఇబ్బంది వచ్చినందుకు బాధగా ఉంది. నేను రెండు సమస్యలకే: తెలంగాణలో **బిల్డర్ స్వాధీనం ఆలస్యం** లేదా **స్వాధీనం తర్వాత లోపాలు**. మీ సమస్య ({topic}) నా పరిధిలో లేదు; నేను సరిచూడని చట్టం గురించి ఊహించి చెప్పను.",
    },
    "off_topic_tail": {
        "en": "If your problem *is* about a delayed or defective flat from a builder, tell me more and I'll help.",
        "hi": "अगर आपकी समस्या बिल्डर से देर या ख़राब फ़्लैट की है, तो और बताइए, मैं मदद करूँगा।",
        "te": "మీ సమస్య బిల్డర్ ఆలస్యం లేదా లోపాలున్న ఫ్లాట్ గురించే అయితే, మరింత చెప్పండి, సహాయం చేస్తాను.",
    },
    "out_of_state_portal": {
        "en": "Your state's RERA website: {url}",
        "hi": "आपके राज्य की RERA वेबसाइट: {url}",
        "te": "మీ రాష్ట్ర RERA వెబ్‌సైట్: {url}",
    },
    "out_of_state_generic": {
        "en": "Search for your state's RERA website (it ends in .gov.in) for its forms and interest rule.",
        "hi": "अपने राज्य की RERA वेबसाइट (जो .gov.in पर ख़त्म होती है) खोजें, वहाँ फ़ॉर्म और ब्याज नियम मिलेंगे।",
        "te": "మీ రాష్ట్ర RERA వెబ్‌సైట్ (.gov.in తో ముగుస్తుంది) వెతకండి; అక్కడ ఫారాలు, వడ్డీ నియమం ఉంటాయి.",
    },
    "central_law": {
        "en": "What the central RERA Act says about delay (this applies in every state):",
        "hi": "देरी पर केंद्रीय RERA क़ानून क्या कहता है (यह हर राज्य में लागू है):",
        "te": "ఆలస్యం గురించి కేంద్ర RERA చట్టం ఏమి చెబుతుంది (ఇది ప్రతి రాష్ట్రంలో వర్తిస్తుంది):",
    },
    "central_law_defects": {
        "en": "What the central RERA Act says about defects after possession (this applies in every state):",
        "hi": "कब्ज़े के बाद की ख़राबियों पर केंद्रीय RERA क़ानून क्या कहता है (यह हर राज्य में लागू है):",
        "te": "స్వాధీనం తర్వాత లోపాల గురించి కేంద్ర RERA చట్టం ఏమి చెబుతుంది (ఇది ప్రతి రాష్ట్రంలో వర్తిస్తుంది):",
    },
    "unverified_amount": {"en": "⚠ unverified - not from my calculator", "hi": "⚠ असत्यापित - मेरे कैलकुलेटर से नहीं", "te": "⚠ ధృవీకరించలేదు - నా కాలిక్యులేటర్ నుండి కాదు"},
    "not_exact_law": {"en": "⚠ not exact law text", "hi": "⚠ यह क़ानून का सटीक पाठ नहीं", "te": "⚠ ఇది చట్టం యొక్క ఖచ్చిత పాఠం కాదు"},
    "unsupported_claim": {"en": "⚠ I couldn't confirm this against the law text", "hi": "⚠ मैं इसे क़ानून के पाठ से पुष्ट नहीं कर सका", "te": "⚠ దీన్ని చట్టం పాఠంతో నిర్ధారించలేకపోయాను"},
    "cut_short": {"en": "(My reply was cut short - ask me to continue.)", "hi": "(मेरा जवाब अधूरा रह गया - आगे बताने को कहें।)", "te": "(నా సమాధానం మధ్యలో ఆగిపోయింది - కొనసాగించమని అడగండి.)"},
    "sources_head": {
        "en": "**Sources used** (official text, checked):",
        "hi": "**इस्तेमाल किए गए स्रोत** (आधिकारिक पाठ, जाँचा हुआ):",
        "te": "**వాడిన మూలాలు** (అధికారిక పాఠం, సరిచూసినవి):",
    },
    "checks_head": {"en": "**Checks:**", "hi": "**जाँच:**", "te": "**తనిఖీలు:**"},
    "no_law": {
        "en": "I don't have verified law on this question, so I won't guess.",
        "hi": "इस सवाल पर मेरे पास जाँचा हुआ क़ानून नहीं है, इसलिए मैं अनुमान नहीं लगाऊँगा।",
        "te": "ఈ ప్రశ్నపై నా దగ్గర సరిచూసిన చట్టం లేదు, అందుకే ఊహించి చెప్పను.",
    },
    "setup": {"en": "⚙️ The AI model is not set up yet, so I can't answer: {detail}. Fix it in the `.env` file (see `.env.example`) and restart the app."},
    "error": {
        "en": "Sorry, I had a technical problem reaching the AI service. Please try again in a moment.",
        "hi": "माफ़ कीजिए, AI सेवा से जुड़ने में तकनीकी दिक़्क़त हुई। कृपया थोड़ी देर में फिर कोशिश करें।",
        "te": "క్షమించండి, AI సేవను చేరుకోవడంలో సాంకేతిక సమస్య వచ్చింది. కాసేపట్లో మళ్లీ ప్రయత్నించండి.",
    },
}

FIELD_LABELS = {
    "state": {"en": "which state the flat is in", "hi": "फ़्लैट किस राज्य में है", "te": "ఫ్లాట్ ఏ రాష్ట్రంలో ఉంది"},
    "promised_possession_date": {"en": "the possession date promised in your agreement", "hi": "एग्रीमेंट में वादा की गई कब्ज़े की तारीख़", "te": "అగ్రిమెంట్‌లో వాగ్దానం చేసిన స్వాధీన తేదీ"},
    "amount_paid_rupees": {"en": "how much you have paid the builder so far", "hi": "अब तक बिल्डर को कितना भुगतान किया", "te": "ఇప్పటివరకు బిల్డర్‌కు ఎంత చెల్లించారు"},
    "possession_handed_over_date": {"en": "the date you got possession of the flat", "hi": "फ़्लैट का कब्ज़ा किस तारीख़ को मिला", "te": "ఫ్లాట్ స్వాధీనం ఏ తేదీన పొందారు"},
    "defects": {"en": "what the defects are (e.g. cracks, leakage)", "hi": "क्या ख़राबियाँ हैं (जैसे दरारें, लीकेज)", "te": "లోపాలు ఏమిటి (ఉదా. పగుళ్లు, లీకేజీ)"},
}

ESC_LABELS = {
    "insolvency": {"en": "builder insolvency", "hi": "बिल्डर दिवालिया", "te": "బిల్డర్ దివాలా"},
    "already_in_court": {"en": "case already in court", "hi": "केस पहले से कोर्ट में", "te": "కేసు ఇప్పటికే కోర్టులో"},
    "criminal": {"en": "possible crime", "hi": "संभावित अपराध", "te": "నేరం అయ్యే అవకాశం"},
    "title_dispute": {"en": "land title dispute", "hi": "ज़मीन का विवाद", "te": "భూమి హక్కు వివాదం"},
    "unregistered": {"en": "project not under RERA", "hi": "प्रोजेक्ट RERA में नहीं", "te": "ప్రాజెక్ట్ RERAలో లేదు"},
    "high_value": {"en": "high-value claim", "hi": "बड़ी रक़म का दावा", "te": "పెద్ద మొత్తం క్లెయిమ్"},
    "out_of_state": {"en": "flat outside Telangana", "hi": "फ़्लैट तेलंगाना से बाहर", "te": "ఫ్లాట్ తెలంగాణ బయట"},
    "defect_window_passed": {"en": "5-year defect window passed", "hi": "5 साल की ख़राबी अवधि बीत गई", "te": "5 ఏళ్ల లోప గడువు దాటింది"},
}


def T(key: str, language: str | None = "English", **kw) -> str:
    s = STRINGS[key]
    return s.get(code_lang(language), s["en"]).format(**kw)


def field_label(field: str, language: str | None) -> str:
    d = FIELD_LABELS[field]
    return d.get(code_lang(language), d["en"])
