"""Offline retrieval evaluation on labelled questions in five language styles.
Measures the code-only path (exact lookup + multilingual keywords + links), i.e. what the bot
retrieves even when the model's index picks are missing. Run: python -m tests.eval_retrieval"""
from core.retrieve import retrieve

# (question, language style, expected entry ids - any hit counts; [] = should retrieve nothing)
CASES = [
    ("Builder did not give possession on time, I want my money back", "English", ["RERA-18-1", "RERA-19-4"]),
    ("What interest rate does the builder have to pay in Telangana?", "English", ["TS-R15"]),
    ("Builder says the delay was due to covid lockdown, is that valid?", "English", ["RERA-6-FM"]),
    ("Which form do I use to file a complaint and what is the fee?", "English", ["TS-R34-1", "TS-R35-1"]),
    ("How many days do I have to appeal against the RERA order?", "English", ["RERA-44-2"]),
    ("The builder is not paying even after the RERA order, how to recover?", "English", ["RERA-40-1"]),
    ("How much compensation will I get?", "English", ["RERA-72", "RERA-71-1"]),
    ("Can I go to consumer court instead of RERA?", "English", ["CPA-2-7", "RERA-88", "CPA-2-42"]),
    ("Which consumer commission, I paid 1.2 crore?", "English", ["CPJUR-3-5"]),
    ("Is there a time limit for a consumer complaint?", "English", ["CPA-69-1"]),
    ("The builder took 20% advance without any agreement", "English", ["RERA-13-1"]),
    ("Is it compulsory for the project to be registered?", "English", ["RERA-3-1"]),
    ("Cracks in the walls and water leakage after we moved in", "English", ["RERA-14-3"]),
    ("The lift is not working, builder says warranty is with the lift company", "English", ["TS-AGMT-12"]),
    ("Can I get a free lawyer? I cannot afford lawyer fees", "English", ["LSA-12"]),
    ("What does section 79 say?", "English", ["RERA-79"]),
    ("What is rule 15?", "English", ["TS-R15"]),
    ("My builder is not paying the monthly interest automatically", "English", ["FAQ-8"]),
    ("बिल्डर ने समय पर कब्जा नहीं दिया, मुझे पैसा वापस चाहिए", "Hindi", ["RERA-18-1", "RERA-19-4"]),
    ("दीवारों में दरार और सीलन है", "Hindi", ["RERA-14-3"]),
    ("मुफ्त वकील कैसे मिलेगा?", "Hindi", ["LSA-12"]),
    ("బిల్డర్ ఫ్లాట్ ఇవ్వలేదు, ఆలస్యం అయ్యింది, డబ్బు తిరిగి కావాలి", "Telugu", ["RERA-18-1", "RERA-19-4"]),
    ("గోడల్లో పగుళ్లు, బాత్రూమ్‌లో లీకేజీ", "Telugu", ["RERA-14-3"]),
    ("వడ్డీ రేటు ఎంత?", "Telugu", ["TS-R15"]),
    ("ఫిర్యాదు ఎలా చేయాలి?", "Telugu", ["RERA-31-1", "TS-R34-1"]),
    ("builder ne possession nahi diya, paisa wapas chahiye", "Hinglish", ["RERA-18-1", "RERA-19-4"]),
    ("complaint kaise kare RERA mein?", "Hinglish", ["RERA-31-1"]),
    ("flat lo leakage undi, cracks kuda unnayi", "Tenglish", ["RERA-14-3"]),
    ("nenu late payment chesanu, interest kattali aa?", "Tenglish", ["RERA-19-7"]),
    ("What is the weather in Hyderabad today?", "English", []),
    ("My landlord won't return my deposit", "English", []),
    ("How do I apply for a passport?", "English", []),
]


def main():
    hit = total = abstain_ok = abstain_total = 0
    for q, lang, want in CASES:
        _, why = retrieve(None, q)
        got = list(why)
        if want:
            total += 1
            ok = any(w in got for w in want)
            hit += ok
        else:
            abstain_total += 1
            ok = not got
            abstain_ok += ok
        print(f"{'✓' if ok else '✗'} [{lang:8}] {q[:55]:55} -> {got}")
    print(f"\nrecall@6 (any expected entry retrieved): {hit}/{total} = {hit / total:.0%}")
    print(f"correct abstain on off-topic: {abstain_ok}/{abstain_total}")
    return hit, total, abstain_ok, abstain_total


if __name__ == "__main__":
    main()
