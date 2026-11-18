"""Builder: cut each quote out of the official page text by start/end anchors,
so no quote is typed by hand. Writes knowledge/law.json. Run: python -m tools.build_law"""
import json
import sys

sys.path.insert(0, ".")
from core.lawtext import norm, pages


def cut(doc, start, end):
    ps = pages(doc)
    joined, offs = "", []
    for i, p in enumerate(ps, 1):
        offs.append((len(joined), i))
        joined += norm(p) + " "
    s = joined.find(norm(start))
    assert s >= 0, (doc, start)
    e = joined.find(norm(end), s)
    assert e >= 0, (doc, end)
    e += len(norm(end))
    starts = [o for o, _ in offs] + [len(joined)]
    pg = [n for k, (o, n) in enumerate(offs) if o < e and starts[k + 1] > s]
    return joined[s:e], pg


E = []


def add(id, doc, section, title, parts, gist, cats, tags, practice_note=None, see_also=(), chapter=""):
    quotes, pgs = [], []
    for st, en in parts:
        q, p = cut(doc, st, en)
        quotes.append(q)
        pgs += [x for x in p if x not in pgs]
    E.append(dict(id=id, doc=doc, section=section, chapter=chapter, title=title, quote=quotes, pdf_pages=pgs,
                  gist=gist, practice_note=practice_note, categories=cats, tags=tags, see_also=list(see_also)))


# ---------------- RERA Act ----------------
add("RERA-3-1", "RERA_ACT", "Section 3(1)", "Projects must be registered with RERA",
    [("3. (1) No promoter shall advertise", "established under this Act")],
    "A builder cannot advertise, book or sell flats in a project without first registering it with RERA.",
    ["delay", "defects"], ["registration", "registered", "unregistered", "not registered", "rera number", "rera registration", "రిజిస్ట్రేషన్", "पंजीकरण", "registration nahi"],
    chapter="Chapter II - Registration of real estate project", see_also=["RERA-3-2A", "TS-R2-ONGOING"])
add("RERA-3-2A", "RERA_ACT", "Section 3(2)(a)", "Small projects that need no registration",
    [("(2) Notwithstanding anything contained in sub-section (1), no registration", "eight inclusive of all phases")],
    "Registration is not needed if the land is 500 sq m or less, or the project has 8 or fewer apartments in all phases.",
    ["delay", "defects"], ["small project", "500", "eight apartments", "exempt", "exemption"],
    chapter="Chapter II - Registration of real estate project")
add("RERA-6-FM", "RERA_ACT", "Section 6, Explanation", "Meaning of force majeure",
    [("Explanation.- For the purpose of this section, the expression \"force majeure", "development of the real estate project.")],
    "Under RERA, 'force majeure' means war, flood, drought, fire, cyclone, earthquake or another natural calamity that affects the project. Whether a builder's excuse counts is for TG-RERA to decide.",
    ["delay"], ["force majeure", "covid", "pandemic", "lockdown", "extension", "act of god", "natural calamity", "కరోనా", "लॉकडाउन", "corona"],
    chapter="Chapter II - Registration of real estate project")
add("RERA-11-4A", "RERA_ACT", "Section 11(4)(a)", "Builder stays responsible until conveyance",
    [("(4) The promoter shall- (a) be responsible for all obligations", "competent authority, as the case may be:")],
    "The builder remains responsible for everything promised in the agreement for sale until the flats (and common areas) are conveyed.",
    ["delay", "defects"], ["obligation", "responsible", "promise", "agreement", "conveyance", "common area", "బాధ్యత", "जिम्मेदार"],
    chapter="Chapter III - Functions and duties of promoter")
add("RERA-13-1", "RERA_ACT", "Section 13(1)", "No more than 10% advance without a registered agreement",
    [("13. (1) A promoter shall not accept a sum more than ten per cent", "under any law for the time being in force.")],
    "A builder cannot take more than 10% of the price as advance before signing and registering an agreement for sale.",
    ["delay"], ["advance", "10%", "ten percent", "booking amount", "without agreement", "no agreement", "అడ్వాన్స్", "एडवांस"],
    chapter="Chapter III - Functions and duties of promoter")
add("RERA-14-3", "RERA_ACT", "Section 14(3)", "Defects reported within 5 years must be fixed in 30 days",
    [("(3) In case any structural defect", "in the manner as provided under this Act.")],
    "If you report a structural defect or poor workmanship, quality or services to the builder within 5 years of getting possession, the builder must fix it free within 30 days; if not, you can claim compensation.",
    ["defects"], ["defect", "crack", "cracks", "leak", "leakage", "seepage", "dampness", "poor quality", "workmanship", "structural", "plumbing", "lift not working",
                  "లీకేజీ", "పగుళ్లు", "లోపం", "నాణ్యత", "दरार", "लीकेज", "सीलन", "खराब क्वालिटी", "kharab", "darar", "seelan"],
    chapter="Chapter III - Functions and duties of promoter", see_also=["TS-AGMT-12", "TS-R34-1", "TS-R35-1"])
add("RERA-18-1", "RERA_ACT", "Section 18(1)", "Delay in possession: refund with interest, or interest for every month of delay",
    [("18. (1) If the promoter fails to complete", "at such rate as may be prescribed.")],
    "If the builder does not give possession by the date in the agreement, you can either withdraw and get your money back with interest (plus compensation), or stay in the project and get interest for every month of delay until handover.",
    ["delay"], ["delay", "delayed", "possession", "handover", "not handed over", "refund", "money back", "withdraw", "interest", "late",
                "ఆలస్యం", "డబ్బు తిరిగి", "వడ్డీ", "ఫ్లాట్ ఇవ్వలేదు", "देरी", "पैसा वापस", "ब्याज", "कब्जा", "paisa wapas", "possession nahi", "late possession"],
    chapter="Chapter III - Functions and duties of promoter", see_also=["TS-R15", "TS-R34-1", "TS-R35-1"])
add("RERA-19-4", "RERA_ACT", "Section 19(4)", "Buyer's right to refund with interest and compensation",
    [("(4) The allottee shall be entitled to claim the refund", "rules or regulations made thereunder.")],
    "A buyer can claim a refund with interest and compensation if the builder fails to give possession as agreed.",
    ["delay"], ["refund", "money back", "withdraw", "cancel", "compensation", "డబ్బు తిరిగి", "पैसा वापस", "रिफंड", "paisa wapas"],
    chapter="Chapter IV - Rights and duties of allottees", see_also=["TS-R15"])
add("RERA-19-7", "RERA_ACT", "Section 19(7)", "Buyer must also pay on time",
    [("(7) The allottee shall be liable to pay interest", "under sub-section (6).")],
    "If the buyer delays their own payments, the buyer also owes interest at the prescribed rate.",
    ["delay"], ["late payment", "my payment", "instalment", "installment", "i paid late", "emi", "బకాయి", "किस्त"],
    chapter="Chapter IV - Rights and duties of allottees")
add("RERA-31-1", "RERA_ACT", "Section 31(1)", "Who can file a complaint, and where",
    [("31. (1) Any aggrieved person may file a complaint", "registered under any law for the time being in force.")],
    "Any aggrieved buyer (or an association of buyers) can file a complaint with the Authority or the adjudicating officer.",
    ["delay", "defects"], ["complaint", "file", "how to file", "where to complain", "tg-rera", "rera complaint", "association", "ఫిర్యాదు", "शिकायत", "complaint kaise"],
    chapter="Chapter VII - Offences, penalties and adjudication (complaints)", see_also=["TS-R34-1", "TS-R35-1"])
add("RERA-40-1", "RERA_ACT", "Section 40(1)", "Recovering money the builder is ordered to pay",
    [("40. (1) If a promoter or an allottee", "as an arrears of land revenue.")],
    "If the builder does not pay interest or compensation ordered by RERA, it can be recovered from the builder like arrears of land revenue.",
    ["delay", "defects"], ["recover", "recovery", "not paying", "order not followed", "execution", "after order", "వసూలు", "वसूली"],
    chapter="Chapter V - Real Estate Regulatory Authority")
add("RERA-43-5", "RERA_ACT", "Section 43(5), proviso", "Builder must deposit before appealing",
    [("Provided that where a promoter files an appeal", "before the said appeal is heard.")],
    "A builder who appeals a RERA order must first deposit at least 30% of the penalty, or the full amount payable to the buyer, with the Appellate Tribunal.",
    ["delay", "defects"], ["appeal", "builder appealed", "appellate tribunal", "deposit before appeal", "అప్పీల్", "अपील"],
    chapter="Chapter VII - Appellate Tribunal")
add("RERA-44-2", "RERA_ACT", "Section 44(2)", "Time limit to appeal: 60 days",
    [("(2) Every appeal made under sub-section (1) shall be preferred within a period of sixty days", "accompanied by such fee, as may be prescribed:")],
    "An appeal against a RERA order must be filed within 60 days of receiving a copy of the order.",
    ["delay", "defects"], ["appeal", "time limit", "how many days", "60 days", "sixty days", "అప్పీల్", "अपील"],
    chapter="Chapter VII - Appellate Tribunal")
add("RERA-71-1", "RERA_ACT", "Section 71(1)", "Compensation is decided by the adjudicating officer",
    [("71. (1) For the purpose of adjudging compensation under sections 12, 14, 18 and section 19", "a reasonable opportunity of being heard:")],
    "Compensation claims (for delay, defects and other violations) are decided by an adjudicating officer, a serving or former District Judge.",
    ["delay", "defects"], ["compensation", "adjudicating officer", "damages", "mental agony", "పరిహారం", "मुआवजा", "harjana"],
    chapter="Chapter VIII - Offences, penalties and adjudication", see_also=["RERA-72", "TS-R35-1"])
add("RERA-72", "RERA_ACT", "Section 72", "What decides the amount of compensation",
    [("72. While adjudging the quantum of compensation", "made as a result of the default;"),
     ("(b) the amount of loss caused as a result of the default;", "in furtherance of justice.")],
    "The officer looks at the builder's unfair gain, your loss, whether the default is repeated, and other relevant factors. There is no fixed formula, so the bot does not estimate compensation.",
    ["delay", "defects"], ["how much compensation", "compensation amount", "factors", "quantum", "ఎంత పరిహారం", "कितना मुआवजा"],
    chapter="Chapter VIII - Offences, penalties and adjudication")
add("RERA-79", "RERA_ACT", "Section 79", "Civil courts cannot hear RERA matters",
    [("79. No civil court shall have jurisdiction", "conferred by or under this Act.")],
    "A civil court cannot hear a suit on matters RERA can decide. (This bars civil courts, not consumer commissions.)",
    ["delay", "defects"], ["civil court", "court case", "sue", "suit", "కోర్టు", "अदालत", "court"],
    chapter="Chapter X - Miscellaneous", see_also=["RERA-88"])
add("RERA-88", "RERA_ACT", "Section 88", "Other laws still apply",
    [("88. The provisions of this Act shall be in addition to", "for the time being in force.")],
    "RERA adds to other laws; it does not replace them. So other routes, such as a consumer commission, can remain open.",
    ["delay", "defects"], ["consumer court", "consumer forum", "other remedy", "consumer commission", "కన్స్యూమర్", "उपभोक्ता"],
    chapter="Chapter X - Miscellaneous", see_also=["CPA-2-7", "CPJUR-3-5"])

# ---------------- TS RERA Rules ----------------
add("TS-R15", "TS_RULES", "Rule 15", "Interest rate in Telangana: highest SBI MCLR + 2%",
    [("15. Interest payable by promoter and allottee.", "lending to the general public.")],
    "In Telangana, interest owed by the builder (or the buyer) is SBI's highest Marginal Cost of Lending Rate plus 2% a year. The final rate and period are set by the order in your case.",
    ["delay"], ["interest", "rate", "how much interest", "mclr", "percent", "calculation", "వడ్డీ రేటు", "ब्याज दर", "byaj"],
    chapter="Chapter IV - Interest")
add("TS-R2-ONGOING", "TS_RULES", "Rule 2(1), 'Ongoing Project'", "Projects approved before 01.01.2017 are excluded",
    [("Ongoing Project\" means, a Project where development is going on", "as the case may be.")],
    "In Telangana, an 'ongoing project' (one that must register) excludes projects whose building permission was approved before 1 January 2017.",
    ["delay", "defects"], ["2016", "2015", "2014", "old project", "before 2017", "permission approved", "ongoing project", "పాత ప్రాజెక్ట్"],
    chapter="Chapter I - Preliminary", see_also=["RERA-3-1"])
add("TS-R34-1", "TS_RULES", "Rule 34(1)", "Complaint to TG-RERA (Form M)",
    [("(1) Any aggrieved person may file a complaint with the Authority for any violation", "payable at the branch of that bank")],
    "A complaint to the Authority is made in Form 'M' with a fee of Rs 1,000. The portal now takes complaints online.",
    ["delay", "defects"], ["form m", "complaint", "file", "fee", "how to file", "procedure", "tg-rera", "ఫారం", "फॉर्म"],
    chapter="Chapter VIII - Complaints",
    practice_note="The Rule's text sends interest and compensation claims to the adjudicating officer (Form N). Since a 2021 Supreme Court ruling, refund and delay-interest complaints are decided by the Authority (Form M), and compensation by the adjudicating officer (Form N). A lawyer, or the TG-RERA complaint page, can confirm the route for your case.",
    see_also=["TS-R35-1"])
add("TS-R35-1", "TS_RULES", "Rule 35(1)", "Claim to the adjudicating officer (Form N)",
    [("(1) Any aggrieved person may file a complaint with the adjudicating officer for interest and compensation", "online payment, as the case may be.")],
    "A claim to the adjudicating officer is made in Form 'N' with a fee of Rs 1,000.",
    ["delay", "defects"], ["form n", "compensation", "adjudicating officer", "claim", "పరిహారం", "मुआवजा"],
    chapter="Chapter VIII - Complaints",
    practice_note="The Rule's text sends interest and compensation claims here (Form N). Since a 2021 Supreme Court ruling, refund and delay-interest complaints are decided by the Authority (Form M), and compensation by the adjudicating officer (Form N). A lawyer, or the TG-RERA complaint page, can confirm the route for your case.",
    see_also=["TS-R34-1", "RERA-71-1"])
add("TS-AGMT-12", "TS_RULES", "Annexure (model agreement for sale), clause 12", "Defect liability and its exclusions",
    [("2. Notwithstanding anything contained in the above clause the following exclusions are made", "which are subject to wear and tear.")],
    "The Telangana model agreement excludes from free repair: equipment under the maker's guarantee (lifts, generators, motors etc.), fittings with natural wear and tear, allowable structural deformations, and painting-type wear.",
    ["defects"], ["lift", "generator", "motor", "fittings", "tap", "painting", "paint", "wear and tear", "warranty", "guarantee", "పెయింట్", "पेंट"],
    chapter="Annexure - Model agreement for sale", see_also=["RERA-14-3"])

# ---------------- TG-RERA FAQ (guidance) ----------------
add("FAQ-3", "TG_FAQ", "FAQ 3", "How to check if a project is registered",
    [("Ans: The Flat/Plot Buyer should visit TG RERA website", "must carry the TG RERA registration number.")],
    "Check the TG-RERA website for the project; its ads must show the TG-RERA registration number.",
    ["delay", "defects"], ["check registration", "rera number", "how to check", "website", "portal", "registered or not"],
    chapter="FAQ (guidance)")
add("FAQ-8", "TG_FAQ", "FAQ 8(ii)", "Delay interest should be paid automatically",
    [("Ans: The interest payment is in accordance with the agreement", "if there is a grievance/ fail to comply.")],
    "TG-RERA's FAQ says delay interest should be paid automatically under the agreement; if not, the buyer may file a complaint.",
    ["delay"], ["automatic", "interest not paid", "builder not paying interest", "monthly interest"],
    chapter="FAQ (guidance)")
add("FAQ-20", "TG_FAQ", "FAQ 20", "Agreement signed before registration can still complain",
    [("Ans: TG RERA empowers any aggrieved person to file a complaint with respect to a registered real estate project.", "Ans: TG RERA empowers any aggrieved person to file a complaint with respect to a registered real estate project.")],
    "TG-RERA says any aggrieved person, including a buyer whose agreement was signed before the project registered, can complain about a registered project.",
    ["delay", "defects"], ["before registration", "old agreement", "agreement before rera"],
    chapter="FAQ (guidance)")

# ---------------- Consumer Protection Act 2019 + 2021 Rules ----------------
add("CPA-2-7", "CPA_2019", "Section 2(7)(ii)", "Who is a 'consumer' (services)",
    [("(ii) hires or avails of any service for a consideration", "avails of such service for any commercial purpose.")],
    "A buyer who pays for a service is a consumer, but not if it is for a commercial purpose (for example, buying flats as an investment business).",
    ["delay", "defects"], ["consumer", "consumer court", "consumer forum", "consumer commission", "investor", "investment", "కన్స్యూమర్", "उपभोक्ता"],
    chapter="Consumer Protection Act - Definitions", see_also=["CPA-2-42", "CPJUR-3-5", "CPA-69-1"])
add("CPA-2-42", "CPA_2019", "Section 2(42)", "'Service' includes housing construction",
    [("(42) \"service\" means service of any description", "under a contract of personal service;")],
    "Housing construction counts as a 'service', so a homebuyer can use a consumer commission for deficient service.",
    ["delay", "defects"], ["consumer court", "consumer forum", "housing", "service"],
    chapter="Consumer Protection Act - Definitions")
add("CPA-2-11", "CPA_2019", "Section 2(11)", "What 'deficiency' in service means",
    [("(11) \"deficiency\" means any fault, imperfection", "which causes loss or injury to the consumer;")],
    "A 'deficiency' is any fault or shortcoming in the quality or manner of a service promised under a contract or required by law.",
    ["delay", "defects"], ["deficiency", "poor service", "consumer court"],
    chapter="Consumer Protection Act - Definitions")
add("CPA-34-2", "CPA_2019", "Section 34(2)(d)", "You can file in the district where you live",
    [("(c) the cause of action, wholly or in part, arises; or (d) the complainant resides or personally works for gain.", "(d) the complainant resides or personally works for gain.")],
    "A consumer complaint can be filed in the district where the cause of action arose, or where you live or work.",
    ["delay", "defects"], ["which district", "where to file consumer", "consumer court location"],
    chapter="Consumer Protection Act - District Commission")
add("CPA-69-1", "CPA_2019", "Section 69(1)", "Two-year limit for consumer complaints",
    [("69. (1) The District Commission, the State Commission or the National Commission shall not admit a complaint", "from the date on which the cause of action has arisen.")],
    "A consumer complaint must normally be filed within 2 years of the cause of action. When that period starts for a delay case is a legal question a lawyer should confirm.",
    ["delay", "defects"], ["time limit", "limitation", "two years", "too late", "how long", "deadline"],
    chapter="Consumer Protection Act - Limitation")
add("CPJUR-3-5", "CP_JUR_2021", "Rules 3, 4 and 5", "Which consumer commission: by amount paid",
    [("3. Jurisdiction of District Commission.", "does not exceed fifty lakh rupees."),
     ("4. Jurisdiction of State Commission.", "does not exceed two crore rupees."),
     ("5. Jurisdiction of National Commission.", "exceeds two crore rupees.")],
    "The commission depends on the value paid as consideration: up to Rs 50 lakh, District; above Rs 50 lakh up to Rs 2 crore, State; above Rs 2 crore, National.",
    ["delay", "defects"], ["district commission", "state commission", "national commission", "50 lakh", "2 crore", "which commission", "pecuniary"],
    chapter="Consumer Protection Jurisdiction Rules 2021", see_also=["CPA-2-7"])

# ---------------- Legal Services Authorities Act ----------------
add("LSA-12", "LSA_1987", "Section 12", "Who gets free legal services",
    [("Every person who has to file or defend a case shall be entitled to legal services", "(f) An industrial workman; or"),
     ("(h) in receipt of annual income less than rupees nine thousand", "if the case is before the Supreme Court.]")],
    "Free legal services are for, among others, SC/ST members, women, children, persons with disability, disaster victims, industrial workers, and people below an income limit that each state sets. The DLSA confirms eligibility; anyone can get basic legal advice there.",
    ["delay", "defects"], ["free lawyer", "legal aid", "dlsa", "cannot afford", "free legal", "nalsa", "ఉచిత న్యాయ", "मुफ्त वकील", "free help", "lawyer fees"],
    chapter="Legal Services Authorities Act - Chapter IV")

out = {"_note": "Every quote is cut from data/laws/text/<doc>.pages.json by tools; tests/test_law_quotes.py re-checks each one. 'gist' and 'practice_note' are plain-language explanations, not law text.",
       "entries": E}
open("knowledge/law.json", "w").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
print(len(E), "entries")
for e in E:
    print(e["id"], e["pdf_pages"], len(" ".join(e["quote"])), "chars")
