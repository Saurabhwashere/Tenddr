# Risk Catalog - Simple keyword-based risk definitions
# This file defines what risks we look for and how to find them

RISK_DEFINITIONS = [
    {
        "risk_id": "ld_excessive",
        "risk_name": "Liquidated Damages – Excessive Rate",
        "category": "financial",
        "clause_type": "liquidated_damages",
        "keywords": ["liquidated damages", "delay damages", "ld", "per day", "per week", "% of contract"],
        "search_query": "liquidated damages delay damages daily rate cap uncapped",
        "definition": "A clause requiring the contractor to pay a high predetermined sum (usually per day or week) if completion is delayed beyond the contractual completion date (Practical Completion). This transfers delay risk as a fixed penalty on the contractor.",
        "detection": "Look for terms like 'liquidated damages', '$ per day after PC' or '% of contract per day' under the Time for Completion or Delay Damages clause. Check if the LD amount is specified without cap.",
        "benchmarks": "Industry practice is to cap LDs around 5–10% of the contract sum. Daily LD rates typically reflect expected profit loss – often roughly 0.05–0.1% of contract value per day. Rates or caps significantly above these (or an uncapped provision) are unusually high and risky.",
        "severity_rules": {
            "critical": "LD cap >10% of contract value or uncapped daily rate (risk of insolvency if any delay).",
            "high": "LD cap 5–10% of contract or daily rate around 0.1% of contract value.",
            "medium": "LD cap 2–5% of contract; daily ~0.05%.",
            "low": "LD cap ≤ profit margin (usually <2–3% of contract)."
        },
        "impact": "Excessive LDs can rapidly erode contractor margins. For example, a $1M contract would cap at $50k–$100k total LD. Unusually high LDs (e.g. thousands of dollars per day) on large projects have driven contractors to insolvency in extreme cases.",
        "recommendations": "Negotiate a realistic LD rate: demand a cap around 5%–10% of contract or a daily rate justified by actual loss. Consider replacing LD with alternative remedies (e.g. bonus for early completion or a performance bond). Ensure the contract allows reasonable EOTs to avoid LD for delays outside your control. Never accept uncapped daily LD without a cap (critical risk)."
    },
    {
        "risk_id": "payment_period_excessive", 
        "risk_name": "Payment Terms – Excessive Payment Period",
        "category": "financial",
        "clause_type": "payment_terms",
        "keywords": ["payment due", "net 45", "net 60", "within 60 days", "invoice", "progress payment"],
        "search_query": "payment terms payment due net 45 net 60 progress payment invoice period",
        "definition": "Contract clauses specifying long payment terms (e.g. payment due 45–60 days after invoice or month-end) that delay contractor's cash receipts and strain cash flow.",
        "detection": "Search for phrases like 'payment due within X days' or 'Net 30/45/60' in the Payment or Invoicing clause. Also look for annualized schedules (e.g. bills paid at quarter-end, etc.) and any lack of progress payment schedule.",
        "benchmarks": "Standard payment terms in Australia are around Net 30 days. Net 45 is sometimes seen; Net 60 or longer is high-risk. The Building & Construction industry generally expects prompt payment – under SOPA, statutory deadlines often override overly long terms. Terms beyond 60 days are considered unusual in construction.",
        "severity_rules": {
            "critical": "Terms >60 days (e.g. Net 60+); very risky (cash flow may break).",
            "high": "Terms 45–60 days (significant cash flow strain).",
            "medium": "Terms ~30–45 days (common but negotiate carefully).",
            "low": "Terms ≤30 days (standard; acceptable)."
        },
        "impact": "Long payment cycles can cause severe cash flow problems. Industry analysis shows ~70% of construction firms suffer late payments each year. For example, holding $100k of work for an extra 30 days costs the contractor financing and profit. Late payments are cited as a prime cause of subcontractor insolvency.",
        "recommendations": "Insist on standard terms (Net 30) or earlier. Include interest or penalties for late payment. Do not accept 'pay-when-paid' clauses. If forced to accept longer terms, negotiate early release of partial payments or accelerated payment for critical milestones. Always align terms with SOPA (include reference dates). Keep strict invoicing and follow-up discipline."
    },
    {
        "risk_id": "pay_when_paid",
        "risk_name": "Pay-When-Paid/Pay-If-Paid Clauses", 
        "category": "financial",
        "clause_type": "contingent_payment",
        "keywords": ["pay-when-paid", "pay if paid", "contingent payment", "subject to receipt of funds"],
        "search_query": "contingent payment pay when paid pay if paid receipt of funds",
        "definition": "Clauses stating the contractor will only be paid when (or if) the principal receives payment from the client ('pay-when-paid/if-paid'). These shift payment risk entirely onto the contractor.",
        "detection": "Look for wording such as 'payment to Contractor is contingent on payment to Principal', 'subject to receipt of funds', or clauses titled 'Pay-when-paid' or 'Contingent Payment' in the payment section.",
        "benchmarks": "In Australia's building industry, such clauses are generally unenforceable. For instance, Section 12 of NSW's Security of Payment Act renders pay-when-paid provisions void. Similar prohibitions exist in other jurisdictions.",
        "severity_rules": {
            "critical": "Any pay-when-paid or pay-if-paid clause is critical (effectively void and delays cashflow).",
            "high": "N/A (all such clauses are treated critically).",
            "medium": "N/A",
            "low": "N/A"
        },
        "impact": "A pay-when-paid clause can indefinitely postpone payments. For example, the NSW Security of Payment Act explicitly provides that pay-when-paid provisions 'have no effect', meaning contractors retain the right to claim statutory progress payments regardless. Relying on these clauses can lead to lengthy payment delays and cash flow insolvency if left unchecked.",
        "recommendations": "Demand removal of any contingent payment clause. Under SOPA and equivalent legislation, these clauses cannot excuse late payment, so reinforce your right to issue progress claims on statutory dates. Ensure the contract contains a clear payment schedule and interest on late payments. Never accept pay-if-paid as it grants principal absolute discretion over your payment."
    },
    {
        "risk_id": "retention_excessive",
        "risk_name": "Retention – Excessive or Withheld",
        "category": "financial", 
        "clause_type": "retention",
        "keywords": ["retention", "retainage", "% retained", "release of retention"],
        "search_query": "retention retainage release of retention percent retained",
        "definition": "A retention is a percentage of each progress payment held back by the principal until later (usually practical completion or end of defects liability). Excessive retention amounts or failure to release retention after completion puts undue strain on contractor cash flow.",
        "detection": "Search for the word 'retention' or 'retainage' in the payment clauses. Look for percentages (e.g. 5%, 10%). Check if and when retained amounts are released (e.g. at PC, after defects fixed).",
        "benchmarks": "In Australia, retention is typically around 5% of each payment. Industry sources note retention commonly falls in the 5–10% range. Retention above 10% or being held post-completion is regarded as high risk.",
        "severity_rules": {
            "critical": "Retention >10% of contract value or withheld beyond defects period without rationale.",
            "high": "Retention = 10%; or 5% with no timely release at PC.",
            "medium": "5% retention released on PC and final defects acceptance.",
            "low": "Retention ≤5% with clear partial-release milestones."
        },
        "impact": "Large retentions tie up significant capital (e.g. 5% on a $10M contract = $500k). If retained funds are released only after a long defects period, contractors may face cash shortfalls. Standard forms (AS2124/AS4000) contemplate 5% retention released at PC and after defects. If the contract improperly holds back all retention until long after PC, it can severely impact working cash.",
        "recommendations": "Aim to limit retention to 5%. Negotiate milestone releases (e.g. half at PC, balance after short defects period). Propose alternative security (e.g. bond) if retention must be raised. Ensure the contract clearly ties retention release to completion and defects rectification (as in AS clauses). If retention exceeds industry norms (e.g. >10%), push back or seek compensation elsewhere."
    },
    {
        "risk_id": "unlimited_liability",
        "risk_name": "Liability/Indemnity – Unlimited Liability",
        "category": "legal",
        "clause_type": "liability_indemnity", 
        "keywords": ["unlimited liability", "without limitation", "indemnify", "all losses"],
        "search_query": "unlimited liability indemnity without limitation all losses",
        "definition": "Contract clauses that impose unlimited liability or broad indemnities on the contractor (for example, indemnifying the principal for all losses or damages without a monetary cap). This exposes the contractor to potentially infinite financial risk.",
        "detection": "Search for terms like 'indemnify the Principal', 'all losses, claims, actions', 'without limitation', 'unlimited liability'. Check indemnity sections and any clause specifying liability caps (or lack thereof).",
        "benchmarks": "Australian government procurement now discourages unlimited liability. For example, policy changes since 2006 mean many public contracts now set liability caps based on risk. In practice, contractors often seek a liability cap at the contract sum or obtained insurance levels.",
        "severity_rules": {
            "critical": "Unlimited liability clauses (especially for negligence) – avoid entirely.",
            "high": "Liability capped at multiple times contract value or no realistic cap.",
            "medium": "Liability cap equal to contract sum (if clearly stated).",
            "low": "Liability capped at contract sum and third-party insurance levels."
        },
        "impact": "Unlimited liability can bankrupt a contractor if a major claim arises. Until 2006, Commonwealth projects often required unlimited liability, but reforms now expect risk-based caps. For instance, government contracts used to default to unlimited liability but shifted to capped limits after 2006. Carrying unlimited risk (e.g. large third-party damage or contract damages) can exceed company resources, leading to insolvency.",
        "recommendations": "Always negotiate a cap on liability. A common approach is to tie maximum liability to the contract sum or a fixed dollar amount. Exclude liability for indirect or consequential damages. Ensure any indemnity is limited to specific defined risks and covered by insurance. If the principal insists on open-ended indemnities, require higher fees or seek legal advice to avoid signing. On government jobs, align caps with current policy limits."
    },
    {
        "risk_id": "variations_process",
        "risk_name": "Variations / Scope Creep – Unfavourable Process",
        "category": "operational",
        "clause_type": "variations",
        "keywords": ["variation", "changes to scope", "directed work", "pricing mechanism", "written instruction"],
        "search_query": "variation changes scope valuation pricing written instruction",
        "definition": "Contract clauses governing variations (changes to scope). Risks arise if the variation mechanism is vague, one-sided, or allows the principal to unilaterally expand scope without fair compensation, leading to uncontrolled work and costs.",
        "detection": "Look for a 'Variations' or 'Changes' clause. Check if it requires written instructions for any change (e.g. AS 4000 Clause 36.1) and how values are determined. Watch for phrases like 'the Contractor must perform additional work as directed' without pricing rules.",
        "benchmarks": "Under standard forms, variations are valued by pre-set rates or by cost plus mark-up (AS2124 allows ~8% overhead + 10% profit; AS4000 allows ~15% combined). A properly drafted clause requires written approval before work and provides for fair valuation.",
        "severity_rules": {
            "critical": "Unbounded variation clause (no need for written direction or pricing mechanism).",
            "high": "Variations allowed by principal's instruction but with limited compensation (e.g. no profit).",
            "medium": "Standard variation clause (written instructions required, fair pricing by AS formula).",
            "low": "Strict limits on variation scope or automatic approvals required."
        },
        "impact": "Poorly managed variation terms can destroy profitability. As one construction lawyer warns, 'poorly managed variations can quickly butcher the contractor's profits'. For example, if a contract allows the principal to add extra work without timely agreement on price, the contractor may perform work at cost, eroding margins. Disputes often occur over whether a change is a contractual variation or out-of-scope.",
        "recommendations": "Ensure variations require prior written direction. Insist on clear valuation rules (e.g. AS rates or a fixed mark-up). For any work beyond the original scope, secure a price and time adjustment before proceeding. If the clause is one-sided, negotiate an EOT and cost adjustment for any principal-initiated changes. Document all verbal change requests in writing. Walk away if the client refuses a fair process for agreed changes."
    },
    {
        "risk_id": "termination_convenience",
        "risk_name": "Termination for Convenience",
        "category": "legal",
        "clause_type": "termination_for_convenience",
        "keywords": ["terminate for convenience", "without cause", "at our option"],
        "search_query": "termination for convenience without cause at our option",
        "definition": "A clause granting one party (typically the principal) the right to unilaterally terminate the contract at any time without cause. This can unfairly shift all project risk to the contractor.",
        "detection": "Search for 'terminate for convenience', 'at our option', 'without cause' in termination provisions. Check if there is any compensation mechanism detailed.",
        "benchmarks": "Convenience termination clauses are common in government and EPC contracts, but best practice includes a fair compensation formula (e.g. reimbursing work done plus overheads). Without compensation, such clauses can be void under consumer law for small business contracts.",
        "severity_rules": {
            "critical": "One-sided TFC with no compensation – the contractor bears all loss of expected profit (often unenforceable).",
            "high": "TFC with minimal compensation (e.g. a small percentage of unfinished work).",
            "medium": "TFC with reasonable payment for work completed and losses.",
            "low": "No TFC clause or mutual termination right."
        },
        "impact": "A one-sided termination right can leave a contractor uncompensated. Lawyers note that if the contractor receives no pre-agreed payment on TFC, the contract may lack consideration and be unenforceable. In practice, a contractor may invest in mobilization and design only to have the contract cancelled and be paid only for physical work done, losing anticipated profit.",
        "recommendations": "If a TFC clause exists, insist on a robust compensation formula (e.g. full cost + overheads + a negotiated profit share). Alternatively, negotiate it out of the contract. Always require that termination payments cover work in progress, materials ordered, and a margin. If cancellation rights remain, cap notice periods (e.g. 30 days) and ensure retention is paid out. Evaluate contracts with onerous TFC clauses very cautiously."
    },
    {
        "risk_id": "site_conditions",
        "risk_name": "Site Conditions – Contractor Risk for Unknown Conditions",
        "category": "project",
        "clause_type": "latent_conditions",
        "keywords": ["latent conditions", "contamination", "no warranty", "own investigations"],
        "search_query": "latent conditions contamination unknown site conditions no warranty investigations",
        "definition": "Contract clauses allocating risk of unforeseen site conditions (such as subsurface conditions, contamination, or latent defects) to the contractor. This includes any requirement to remediate or rectify site issues beyond what was known at tender.",
        "detection": "Look for 'latent conditions', 'site to be deemed acceptable', 'contamination warranty', or exclusions of hidden defects. Terms like 'contractor to make own investigations' or 'no warranty by principal' are red flags.",
        "benchmarks": "Best practice is for the principal to provide accurate site information or allow claims for truly unforeseen conditions. AS forms usually allow an extension of time and cost for defined latent conditions, but often exclude contamination unless expressly included.",
        "severity_rules": {
            "critical": "Contractor indemnifies or assumes all latent risks (especially contamination) absolutely.",
            "high": "Limited relief: small cost reimbursed or delay only, no profit on extra work.",
            "medium": "Standard latent conditions clause (time & money for unforeseen physical conditions).",
            "low": "Principal fully responsible or detailed geotech provided."
        },
        "impact": "Unexpected site issues can create massive overruns. In Thiess Services v Mirvac [2006] QCA 50, the contractor had agreed to render a contaminated site 'suitable for any purpose', and the court held the contractor was fully liable for all contamination costs. This meant millions more work at its expense. Such clauses have destroyed project budgets when, for example, deeper rock or toxic soil is encountered.",
        "recommendations": "Negotiate risk sharing. Require the principal to warrant known conditions or adjust price/time for changes. Incorporate a robust latent conditions clause (with documented site data). If contamination risk is present, insist on capped liability or contingency. Always conduct (and price) a thorough geotechnical survey and include it in the contract documents."
    },
    {
        "risk_id": "whs_broad",
        "risk_name": "WHS Compliance – Broad Safety Obligations",
        "category": "compliance",
        "clause_type": "whs_safety",
        "keywords": ["WHS", "safety", "occupational health", "indemnify safety"],
        "search_query": "safety WHS occupational health indemnity safety obligations",
        "definition": "Contract provisions assigning broad workplace health and safety (WHS) duties to the contractor. While contractor obligations are normal, risk arises if the contract unduly shifts principal's or third-party safety liabilities onto the contractor beyond legal standards.",
        "detection": "Search for 'WHS', 'safety', 'occupational health and safety', or clauses requiring compliance with all safety laws. Check if principals attempt to outsource statutory duties (e.g. making contractor responsible for designer's or principal's acts).",
        "benchmarks": "Standard contracts (AS2124/AS4000) require contractors to comply with WHS laws. This is expected; principals typically still carry duties for design/overall site conditions.",
        "severity_rules": {
            "critical": "Contractor assumes safety duties that by law belong to principal (e.g. design safety).",
            "high": "Very heavy indemnities on contractor for third-party safety claims.",
            "medium": "Standard clauses requiring compliance with WHS law (normal duty).",
            "low": "Clearly defined roles: contractor for site safety, principal for design/regulation compliance."
        },
        "impact": "Noncompliance with WHS can cost millions. For example, under WHS laws fines for safety breaches can reach into the millions of dollars. AS2124 explicitly mandates contractor adherence to safety regulations. If a contract tries to waive the principal's responsibility (e.g. contractor indemnifies principal for any incident regardless of fault), this is highly risky. Breach of a safety clause has led to prosecutions and multi-million fines in recent projects.",
        "recommendations": "Ensure the contractor's WHS obligations match legal requirements, but do not contractually waive the principal's duties. Include a clause that each party remains liable for its own statutory obligations. Require the principal to provide safe design and information. Maintain thorough site safety plans (as AS2124 suggests) and consider requiring principal to retain some responsibility (e.g. site access)."
    },
    {
        "risk_id": "insurance_gaps",
        "risk_name": "Insurance Lapse – Coverage Gaps",
        "category": "legal",
        "clause_type": "insurance",
        "keywords": ["insurance", "policy expires", "coverage", "defects period", "builder's risk"],
        "search_query": "insurance coverage lapse defects period policy ends builder's risk",
        "definition": "Contractual or practical gaps in required insurance coverage (e.g. builder's risk, liability) during the project. Risk arises if policies expire or transfer gaps (e.g. at handover) leave the contractor uninsured for losses.",
        "detection": "Check insurance clauses for coverage periods. Watch for triggers (e.g. 'upon practical completion the contractor's insurance ends'). Ensure policies align with contract duration and defects period.",
        "benchmarks": "Contracts generally require continuous insurance throughout construction and defects liability. For example, many forms require builder's risk and liability insurance to cover all works until completion and handover.",
        "severity_rules": {
            "critical": "Insurance ends before project end or defects period, leaving exposures unprotected.",
            "high": "Short lapses in coverage or unclear handover responsibilities.",
            "medium": "Coverage ends at final certificate, but principal promptly takes cover.",
            "low": "Continuous cover with no gaps."
        },
        "impact": "Lapsing insurance can be catastrophic. Industry sources note that builders' risk (contract works) policies typically lapse on takeover by the owner. If not carefully managed, the contractor can unknowingly be uninsured during critical handover. For example, if policies should overlap with the owner's policy to prevent coverage gaps. A recent case saw a contractor uninsured for storm damage during a transfer period, leading to a multi-million loss.",
        "recommendations": "Require that contractor's policies remain in force until after practical completion and through defects period. Insert provisions obligating the principal to provide proof of buyer insurance. Coordinate overlap: align the end of one policy with the start of the next. Always monitor insurance expiry dates and ensure certificates are delivered. Consider extending contractor's liability insurance cover for a period after PC if possible."
    }
]

# Simple keyword mapping for quick categorization
CATEGORY_KEYWORDS = {
    "financial": ["payment", "invoice", "retention", "liquidated damages", "ld", "delay damages", "net 30", "net 45", "net 60"],
    "legal": ["indemnify", "liability", "without limitation", "terminate", "termination", "arbitration", "mediation", "dispute resolution"],
    "compliance": ["WHS", "safety", "compliance", "certificates", "permits", "licenses"],
    "project": ["site conditions", "latent", "contamination", "geotechnical"],
    "operational": ["variation", "changes", "scope", "written instruction"],
    "timeline": ["completion", "time for completion", "milestone", "schedule", "deadline"]
}

# Clause type patterns for better matching
CLAUSE_TYPE_PATTERNS = {
    "liquidated_damages": ["liquidated damages", "delay damages", "ld"],
    "payment_terms": ["payment due", "net 30", "net 45", "net 60", "invoice"],
    "contingent_payment": ["pay-when-paid", "pay if paid", "contingent payment", "subject to receipt of funds"],
    "retention": ["retention", "retainage", "release of retention"],
    "liability_indemnity": ["unlimited liability", "indemnify", "without limitation", "all losses"],
    "variations": ["variation", "changes to scope", "written instruction", "valuation"],
    "termination_for_convenience": ["terminate for convenience", "without cause", "at our option"],
    "latent_conditions": ["latent conditions", "contamination", "own investigations", "no warranty"],
    "whs_safety": ["WHS", "safety", "occupational health"],
    "insurance": ["insurance", "policy", "coverage", "builder's risk", "defects period"],
    "dispute_resolution": ["dispute resolution", "arbitration", "mediation", "conflict resolution"]
}
