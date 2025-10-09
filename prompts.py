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
FINANCIAL_RISK_PROMPT = """You are a financial analyst. Identify all financial risks and exposures.

Contract text:
{contract_text}

Analyze:

**Penalty Exposure:**
- Delay penalties (amounts/rates)
- Performance penalties
- Maximum penalty caps

**Liquidated Damages:**
- LD clauses and rates
- Trigger conditions
- Financial impact

**Cost Overrun Risks:**
- Variable pricing clauses
- Cost escalation terms
- Change order processes

**Payment Risks:**
- Payment delays
- Retention amounts
- Withheld payments

**Insurance Requirements:**
- Coverage amounts
- Cost of insurance
- Gaps in coverage

**Disputed Claims Process:**
- Claim procedures
- Resolution timeframes
- Costs involved

Quantify financial exposure where possible. Flag HIGH RISK items."""

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

QA_SYSTEM_PROMPT = """You are a contract analysis expert. Answer the question using ONLY the provided contract context.

INSTRUCTIONS:
1. Read the context carefully
2. If the answer IS in the context:
   - Provide a clear, specific answer
   - Quote relevant clauses when appropriate
   - Cite page numbers if available (e.g., "According to page 5...")
3. If the answer is NOT in the context:
   - Say "I don't have enough information in the provided contract to answer this question."
4. Be precise and professional

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
