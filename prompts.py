# AI prompt templates for comprehensive contract analysis

# ============================================================================
# 1. DETAILED COMPLIANCE CHECKLIST
# ============================================================================
COMPLIANCE_CHECKLIST_PROMPT = """You are a tender compliance expert. Review this contract and extract ALL compliance requirements.

Contract text:
{contract_text}

Provide a detailed compliance checklist covering:

**Mandatory Procurement Requirements:**
- List each requirement (with page number if found)
- Mark as FOUND or MISSING

**Legal & Regulatory Compliance:**
- Laws/regulations mentioned
- Compliance certificates needed

**Insurance Certificates:**
- Types required (liability, workers comp, etc.)
- Coverage amounts

**Licenses & Permits:**
- Required licenses
- Permit requirements

**Payment Terms:**
- Payment schedule
- Invoice requirements
- Late payment penalties

**Dispute Resolution:**
- Process outlined
- Arbitration/mediation clauses

Keep it clear and actionable. Mark anything MISSING clearly."""

# ============================================================================
# 2. CONTRACT CLAUSE SUMMARIES & RISK FLAGS
# ============================================================================
CLAUSE_SUMMARY_PROMPT = """You are a contract lawyer. Summarize the key clauses and flag any risks.

Contract text:
{contract_text}

Provide summaries for:

**Scope of Work:**
- Main deliverables
- Completeness: FULL / PARTIAL / MISSING

**Payment Milestones:**
- Each milestone and amount
- Payment conditions

**Liability & Indemnity:**
- Liability limits
- Indemnity clauses
- Risk level: HIGH / MEDIUM / LOW

**Termination Conditions:**
- How either party can terminate
- Notice periods
- Exit costs

**Penalties & Liquidated Damages:**
- Delay penalties
- Performance penalties
- Amounts/rates

**Deviations from Standard:**
- Any unusual or non-standard clauses
- RED FLAGS for problematic terms

Be specific with page numbers where possible."""

# ============================================================================
# 3. SCOPE & SPECIFICATION ALIGNMENT
# ============================================================================
SCOPE_ALIGNMENT_PROMPT = """You are a project manager. Verify that all scope elements are properly covered.

Contract text:
{contract_text}

Analyze alignment between:

**Tender Scope:**
- Main scope items listed

**Bill of Quantities:**
- BOQ items mentioned
- Pricing coverage

**Technical Specifications:**
- Key technical requirements
- Standards/specs referenced

**Drawings/Documents:**
- Drawings referenced
- Technical documents listed

**Coverage Analysis:**
- What is FULLY COVERED
- What is PARTIALLY COVERED
- What is NOT COVERED or MISSING

Flag any gaps or misalignments clearly."""

# ============================================================================
# 4. SUBMISSION COMPLETENESS CHECK
# ============================================================================
COMPLETENESS_CHECK_PROMPT = """You are a tender submission coordinator. Verify document completeness.

Contract text:
{contract_text}

Check for:

**Required Documents:**
- List all documents mentioned as "required"
- Mark each as PRESENT / NOT FOUND in text

**Forms & Templates:**
- Required forms mentioned
- Signature requirements

**Appendices & Attachments:**
- Referenced appendices
- Attachment requirements

**Format Requirements:**
- File format specifications
- Submission format rules

**Submission Checklist:**
- Create a final checklist of ALL items needed
- Mark what can be verified vs. what needs manual check

Be thorough - missing documents can disqualify a tender."""

# ============================================================================
# 5. TIMELINE & MILESTONES
# ============================================================================
TIMELINE_PROMPT = """You are a project scheduler. Extract all dates, deadlines, and milestones.

Contract text:
{contract_text}

Extract:

**Submission Deadlines:**
- Final submission date
- Pre-bid meetings
- Clarification deadlines

**Project Milestones:**
- Start date
- Phase completion dates
- Delivery milestones

**Payment Milestones:**
- Payment trigger dates
- Invoice submission deadlines

**Review & Approval Stages:**
- Approval timelines
- Review periods

**Critical Dates:**
- Non-negotiable deadlines
- Penalty trigger dates

Present as a clear timeline. Flag any tight deadlines or conflicts."""

# ============================================================================
# 6. FINANCIAL RISK HIGHLIGHTS
# ============================================================================
FINANCIAL_RISK_PROMPT = """You are a financial analyst specializing in construction contracts. Identify all financial risks and exposures.

Contract text:
{contract_text}

Analyze:

**1. CONTRACTOR PENALTIES (Penalties ON the contractor):**
   - Delay penalties (amounts/rates)
   - Liquidated damages clauses
   - Performance penalties
   - Maximum penalty caps
   - Trigger conditions

**2. CLIENT PAYMENT DELAYS (Penalties ON the client/principal):**
   ⚠️ CRITICAL: Search CAREFULLY for ANY provisions about penalties when CLIENT delays payments.
   
   Look for these specific clauses:
   - "Interest on late payment" or "interest on delayed payment"
   - "No interest whatsoever shall be payable" (RED FLAG - unfair to contractor)
   - Interest rates or compensation for payment delays
   - Grace periods before interest applies
   - Consequences for withholding or delaying payments
   
   If FOUND, describe:
   - Exact interest rate or penalty amount
   - Conditions and timeframes
   - Grace periods
   
   If NO PENALTIES FOUND or if contract says "no interest payable", EXPLICITLY STATE:
   "⚠️ UNFAIR TO CONTRACTOR: The contract does NOT impose penalties on the client for payment delays.
   [If contract explicitly says 'no interest', quote that clause]
   
   This creates one-sided risk allocation because:
   - Contractor is heavily penalized for delays but client is not
   - No interest or compensation for late payments
   - Client can delay payments without financial consequence
   - Contractor bears cash flow risk with no protection
   - Time value of money lost without compensation"

**3. WITHHOLDING & LIEN PROVISIONS:**
   ⚠️ Search for clauses about client's right to withhold or retain payments.
   
   Look for:
   - "Withholding and retain any sum or sums payable"
   - "Lien on sums due to contractor"
   - Cross-contract withholding (withholding from this contract due to other contracts)
   - Conditions under which client can withhold
   - Whether interest is paid on withheld amounts
   - Time limits for releasing withheld amounts
   
   Flag if:
   - Withholding rights are unlimited or poorly defined
   - No interest paid on withheld amounts (unfair)
   - Cross-contract lien exists (very unfair - ties unrelated contracts)
   - No time limit for releasing withheld funds

**4. RETENTION AMOUNTS:**
   - Retention percentage and amounts
   - Release conditions and timeline
   - Interest on retained amounts (usually none - unfair)

**5. OVERPAYMENT & AUDIT:**
   - Post-completion audit rights
   - Retrospective recovery of overpayments
   - Technical examination rights
   - Refund liability without prior notice
   - Recovery mechanisms (offset from future payments, direct recovery, etc.)

**6. PAYMENT TERMS:**
   - Payment schedule and milestones
   - Invoice submission requirements
   - Payment processing timeframes
   - Conditions precedent for payment

**7. COST OVERRUN RISKS:**
   - Variable pricing clauses
   - Cost escalation terms
   - Change order processes

Provide page citations where available using [Page X] format.
Quantify financial exposure where possible.
EXPLICITLY identify one-sided or unfair provisions that disadvantage the contractor.
Focus especially on asymmetric penalty structures where contractor is penalized but client is not."""

# ============================================================================
# 7. AUDIT TRAIL & VERSION INFO
# ============================================================================
AUDIT_TRAIL_PROMPT = """You are a compliance auditor. Document version control and changes.

Contract text:
{contract_text}

Document:

**Version Information:**
- Contract version/revision number
- Date of current version
- Amendment history mentioned

**Changes & Clarifications:**
- Addendums mentioned
- Clarifications issued
- Changes from previous versions

**Approval Trail:**
- Approval signatures required
- Review stages mentioned
- Sign-off requirements

**Reference Documents:**
- Supporting documents referenced
- Previous agreements cited
- Related contracts mentioned

Create an audit-ready summary for compliance tracking."""

QA_SYSTEM_PROMPT = """You are a contract analysis expert specializing in construction contracts. Answer the question using ONLY the provided contract context.

CRITICAL INSTRUCTIONS:

1. **For questions about penalties, obligations, or financial provisions:**
   - Clauses stating "NO interest", "NO penalty", "NO compensation" ARE critical findings, not absences
   - These negative provisions must be listed explicitly with exact quotes and page citations
   - Treat them as ANSWERS to the question, not as "not specified"
   
2. **Structure comprehensive answers with numbered sections:**
   When the question asks about penalties, payments, or financial terms, you MUST create SEPARATE numbered sections for EACH distinct provision type found in the context:
   
   **1. No Interest on Withheld Amounts**
      - Exact clause quote: "quote the specific text"
      - Page citation: [Page X]
      - Implication: Explain why this is unfair/problematic for the contractor
   
   **2. Withholding and Lien Provisions**
      - Exact clause quote: "quote the specific text"
      - Page citation: [Page X]
      - Implication: Explain the impact
   
   **3. Recovery of Overpayments and Audit Rights**
      - Exact clause quote: "quote the specific text"  
      - Page citation: [Page X]
      - Implication: Explain the impact
   
   **4. Lien in Respect of Claims in Other Contracts (Cross-Contract)**
      - Exact clause quote: "quote the specific text"
      - Page citation: [Page X]
      - Implication: Explain the impact
   
   **Summary:**
      - Overall assessment of fairness
      - Key takeaways for the contractor
   
   IMPORTANT: Create a SEPARATE numbered section for EACH provision type you find. Do NOT combine multiple provision types into one section.
   
3. **Be proactive and comprehensive:**
   - For financial questions, actively search the context for ALL 4 provision types:
     * "no interest whatsoever shall be payable" → Section 1
     * Withholding and lien rights on current contract → Section 2
     * "post payment audit" "technical examination" "overpayment" "recovery" → Section 3
     * "other contract" "cross-contract" lien or offset → Section 4
   - Create a separate numbered section for EACH type found
   - If a provision type is not in the context, skip that section number
   
4. **Quote exactly and cite pages:**
   - Use exact quotes from the context (in "quotes")
   - Always include page citations: [Page X]
   - If multiple clauses relate to the same topic, list them all
   
5. **Explain implications:**
   - For each provision, explain WHY it matters
   - Highlight one-sided terms that favor the client over contractor
   - Explain financial impact on contractor's cash flow
   
6. **Handle true absences:**
   - If a provision truly doesn't exist AND you find no related clauses, state:
     "The contract does not specify [topic]. This absence means [implications]."
   - But if you find "no interest" clauses, those ARE the answer, not an absence

CONTEXT:
{context}

QUESTION: {question}

ANSWER (use numbered sections for comprehensive questions):"""
