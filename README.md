# 🏗️ Tenddr - AI-Powered Contract Analysis Platform

**Enterprise-grade contract analysis system with hybrid RAG architecture**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Setup & Installation](#setup--installation)
6. [API Documentation](#api-documentation)
7. [Hybrid RAG System](#hybrid-rag-system)
8. [Security & User Isolation](#security--user-isolation)
9. [Testing](#testing)
10. [Performance](#performance)
11. [Deployment](#deployment)

---

## 🎯 Overview

Tenddr is an AI-powered contract analysis platform that helps contractors identify risks, unfair clauses, and financial exposures in construction contracts. The system uses a sophisticated **Hybrid RAG (Retrieval-Augmented Generation)** architecture to provide comprehensive, accurate contract analysis comparable to commercial AI solutions like ContraVault.

### Key Capabilities:
- ✅ **Comprehensive Contract Analysis** - 7 different analysis types
- ✅ **Risk Detection** - Identifies 20+ risk categories with severity scoring
- ✅ **Q&A System** - Natural language questions about contracts
- ✅ **Hybrid RAG** - LLM-powered + domain-specific query expansion
- ✅ **Smart Reranking** - Preserves high-confidence results, ensures diversity
- ✅ **User Isolation** - Complete data segregation with RLS policies
- ✅ **Production-Ready** - Enterprise-grade security and performance

---

## 🏛️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  - Contract Upload  - Results View  - Q&A Interface         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  - PDF Processing  - Analysis  - RAG Pipeline               │
└─────────┬───────────┬───────────┬───────────────────────────┘
          │           │           │
          ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌──────────┐
    │Supabase │ │Pinecone │ │ OpenAI   │
    │Database │ │ Vector  │ │ GPT-4o   │
    │& Storage│ │   DB    │ │Embeddings│
    └─────────┘ └─────────┘ └──────────┘
```

### Data Flow

1. **Upload** → PDF → Supabase Storage
2. **Extract** → Text + Pages → Chunks (500 words, 100 overlap)
3. **Classify** → Chunks → Categories (financial, legal, timeline, etc.)
4. **Vectorize** → Chunks → OpenAI Embeddings → Pinecone
5. **Analyze** → 7 Analysis Types → Supabase Database
6. **Query** → Hybrid RAG → Smart Reranking → LLM Response

---

## ✨ Features

### 1. **Contract Analysis (7 Types)**

| Analysis Type | Description |
|--------------|-------------|
| **Risk Analysis** | Identifies 20+ risk categories with severity scoring |
| **Compliance Checklist** | Verifies mandatory clauses and requirements |
| **Clause Summaries** | Summarizes key contract clauses |
| **Scope Alignment** | Checks if scope matches tender requirements |
| **Completeness Check** | Identifies missing or ambiguous clauses |
| **Timeline & Milestones** | Extracts deadlines and completion dates |
| **Financial Risks** | Analyzes payment terms, penalties, withholding |

### 2. **Risk Detection**

Automatically detects and scores risks:
- Liquidated damages (excessive rates)
- Payment terms (excessive periods)
- Retention provisions (unfair terms)
- Termination clauses (one-sided)
- Indemnity provisions (unlimited liability)
- Insurance requirements (excessive coverage)
- Warranty periods (unreasonable duration)
- And 13+ more risk categories

### 3. **Q&A System**

Ask natural language questions:
- "What are the penalties for delayed payments by the client?"
- "What certifications are required?"
- "What are the key deadlines?"

**Performance:** Matches ContraVault AI in finding critical clauses with exact page citations.

### 4. **Contract Management**

- Upload contracts (PDF)
- View analysis results
- Ask questions
- Delete contracts (with cascade deletion)
- Track analysis history

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.13** - Latest Python version
- **PyMuPDF** - PDF text extraction
- **OpenAI GPT-4o** - LLM for analysis and embeddings
- **Pinecone** - Vector database for RAG
- **ZeroEntropy** - Reranking service
- **Supabase** - PostgreSQL database + storage

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS
- **Clerk** - Authentication
- **Shadcn/UI** - Component library

### Infrastructure
- **Supabase** - Hosted PostgreSQL + Storage
- **Pinecone** - Managed vector database
- **Vercel** - Frontend hosting (optional)

---

## 🚀 Setup & Installation

### Prerequisites

```bash
# Required
- Python 3.13+
- Node.js 18+
- Supabase account
- Pinecone account
- OpenAI API key
- ZeroEntropy API key (optional, for reranking)
- Clerk account (for auth)
```

### Backend Setup

```bash
# 1. Clone the repository
cd Tenddr

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
ZEROENTROPY_API_KEY=your_zeroentropy_api_key  # Optional
EOF

# 5. Run the server
./start.sh
# Or manually: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd tenddr-frontend

# 1. Install dependencies
npm install

# 2. Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_key
CLERK_SECRET_KEY=your_clerk_secret
EOF

# 3. Run development server
npm run dev
```

### Database Setup

Run these SQL commands in Supabase SQL Editor:

```sql
-- 1. Create tables (if not exists)
-- See database.py for schema

-- 2. Enable Row Level Security
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE contract_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_questions ENABLE ROW LEVEL SECURITY;

-- 3. Create RLS policies (see Security section below)
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### **Upload Contract**
```http
POST /upload
Content-Type: multipart/form-data
Headers: X-User-Id: {clerk_user_id}

Body:
  file: PDF file
  
Response:
  {
    "contract_id": "uuid",
    "message": "Contract uploaded successfully"
  }
```

#### **Get Analysis Results**
```http
GET /results/{contract_id}
Headers: X-User-Id: {clerk_user_id}

Response:
  {
    "id": "uuid",
    "filename": "contract.pdf",
    "risk_analysis": {...},
    "compliance_checklist": "...",
    "financial_risks": "...",
    ...
  }
```

#### **Ask Question**
```http
POST /qa/{contract_id}
Headers: X-User-Id: {clerk_user_id}
Content-Type: application/json

Body:
  {
    "question": "What are the penalties for delayed payments?"
  }
  
Response:
  {
    "answer": "1. No Interest on Withheld Amounts..."
  }
```

#### **List Contracts**
```http
GET /contracts
Headers: X-User-Id: {clerk_user_id}

Response:
  [
    {
      "id": "uuid",
      "filename": "contract.pdf",
      "uploaded_at": "2024-01-01T00:00:00Z",
      "status": "completed"
    }
  ]
```

#### **Delete Contract**
```http
DELETE /contracts/{contract_id}
Headers: X-User-Id: {clerk_user_id}

Response:
  {
    "message": "Contract deleted successfully"
  }
```

#### **Debug Query** (Development)
```http
POST /debug/query/{contract_id}
Content-Type: application/json

Body:
  {
    "question": "test query"
  }
  
Response:
  {
    "pipeline_summary": {
      "step_1_retrieved": 50,
      "step_2_filtered": 50,
      "step_3_reranked": 40,
      "final_chunks_used": 30
    },
    "pinecone_top_20": [...]
  }
```

---

## 🧠 Hybrid RAG System

### Overview

The Hybrid RAG system combines **LLM intelligence** with **domain knowledge** for comprehensive and accurate retrieval.

### Architecture

```
User Question
     ↓
┌────────────────────────────────────────┐
│  1. Domain Classification              │
│     → financial, timeline, compliance  │
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│  2. LLM Query Decomposition            │
│     → 4-5 diverse sub-queries          │
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│  3. Domain-Specific Expansion          │
│     → 6 targeted queries per domain    │
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│  4. Query Deduplication                │
│     → 8 unique diverse queries         │
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│  5. Multi-Query Retrieval              │
│     → 15 chunks per query × 8 queries  │
│     → ~120 total chunks retrieved      │
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│  6. Content Deduplication              │
│     → Remove duplicate chunks          │
│     → Keep diverse content             │
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│  7. Smart Reranking (ZeroEntropy)      │
│     → Preserve high confidence (>0.78) │
│     → Rerank medium/low confidence     │
│     → Ensure page diversity            │
│     → Final: 40 chunks                 │
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│  8. LLM Generation (GPT-4o)            │
│     → Use top 30 chunks as context     │
│     → Generate structured answer       │
└────────────────────────────────────────┘
```

### Key Components

#### 1. **Domain Classification**
```python
classify_question_type(question) → 'financial' | 'timeline' | 'compliance' | 'risk' | 'scope' | 'general'
```

Classifies questions to apply domain-specific strategies.

#### 2. **LLM Query Decomposition**
```python
decompose_question_with_llm(question) → List[str]
```

Uses GPT-4o-mini to break down complex questions into 4-5 diverse sub-queries.

Example:
```
Input: "What are the penalties for delayed payments by the client?"

Output:
1. "What interest or compensation is payable on delayed payments?"
2. "Are there any penalties on the client for late payment?"
3. "What are the withholding and lien provisions?"
4. "Can the client withhold payments without penalty?"
```

#### 3. **Domain-Specific Expansion**
```python
expand_query_by_domain(question, domain) → List[str]
```

Adds 6 targeted queries based on domain knowledge:

**Financial Domain:**
- "interest compensation penalties late payment"
- "withholding retention lien no interest whatsoever"
- "audit overpayment recovery technical examination"
- "cross-contract lien other contracts claims"
- etc.

#### 4. **Smart Reranking**
```python
rerank_with_zeroentropy(query, documents) → List[dict]
```

**Strategy:**
1. Separate by Pinecone confidence:
   - High (>0.78): Keep as-is
   - Medium/Low (≤0.78): Rerank with ZeroEntropy
2. Merge results with page diversity
3. Ensure different pages are represented
4. Return top 40 diverse chunks

#### 5. **Metadata Filtering**

Applies domain-specific filters to Pinecone queries:

```python
# Financial questions
metadata_filter = {
    "category": {"$in": ["financial", "legal", "payment"]}
}

# Timeline questions
metadata_filter = {
    "category": {"$in": ["timeline", "schedule", "milestone"]}
}
```

### Performance Comparison

| Metric | Before Hybrid | After Hybrid | Improvement |
|--------|--------------|--------------|-------------|
| **Queries per Question** | 1 | 8 | +700% |
| **Chunks Retrieved** | 20 | 120 → 40 | +100% |
| **Critical Clauses Found** | 2/4 | 4/4 | +100% |
| **Page Citations** | Sometimes | Always | ✅ |
| **Matches ContraVault** | ❌ | ✅ | ✅ |

### Cost Analysis

**Per Question:**
- LLM Decomposition: ~$0.001 (GPT-4o-mini)
- 8 × Embeddings: ~$0.002 (text-embedding-3-small)
- Pinecone Queries: ~$0.001
- Reranking: ~$0.002 (ZeroEntropy)
- Answer Generation: ~$0.020 (GPT-4o)
- **Total: ~$0.026 per question**

**Per Contract Analysis:**
- Chunking + Classification: ~$0.005
- Embeddings (200 chunks): ~$0.050
- 7 Analysis Types: ~$0.180
- **Total: ~$0.235 per contract**

---

## 🔒 Security & User Isolation

### Row-Level Security (RLS)

Complete data isolation using Supabase RLS policies:

```sql
-- Users can only see their own contracts
CREATE POLICY "Users can view own contracts"
ON contracts FOR SELECT
USING (uploaded_by = current_setting('request.jwt.claims', true)::json->>'sub');

-- Users can only insert contracts with their user_id
CREATE POLICY "Users can insert own contracts"
ON contracts FOR INSERT
WITH CHECK (uploaded_by = current_setting('request.jwt.claims', true)::json->>'sub');

-- Similar policies for contract_analyses, risk_analyses, user_questions
```

### Pinecone Metadata Filtering

All vector queries include user_id filter:

```python
query_contract(contract_id, query, user_id) {
    metadata_filter = {
        "contract_id": contract_id,
        "user_id": user_id  # Ensures user isolation
    }
}
```

### Authentication Flow

```
1. User logs in → Clerk JWT
2. Frontend → API call with X-User-Id header
3. Backend validates user_id
4. Supabase RLS enforces isolation
5. Pinecone filters by user_id
```

### Data Deletion

Complete cascade deletion across all systems:

```python
delete_contract(contract_id, user_id):
    1. Delete from Supabase Database (4 tables)
    2. Delete from Supabase Storage (PDF)
    3. Delete from Pinecone (all vectors)
```

---

## 🧪 Testing

### Test Scripts

#### 1. **API Test Suite** (Recommended)
```bash
cd Tenddr
./test_hybrid_api.sh <contract_id> <user_id>
```

Tests:
- ✅ Financial questions (penalties, withholding, audit)
- ✅ Timeline questions (deadlines, milestones)
- ✅ Compliance questions (certifications, licenses)
- ✅ Debug pipeline (retrieval stats)

#### 2. **Hybrid RAG Test**
```bash
cd Tenddr
./run_test.sh
```

Tests:
- ✅ LLM query decomposition
- ✅ Domain classification
- ✅ Query expansion
- ✅ Multi-query retrieval
- ✅ Deduplication

### Manual Testing

```bash
# Test upload
curl -X POST http://localhost:8000/upload \
  -H "X-User-Id: user_123" \
  -F "file=@contract.pdf"

# Test Q&A
curl -X POST http://localhost:8000/qa/{contract_id} \
  -H "X-User-Id: user_123" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the payment terms?"}'

# Test debug
curl -X POST http://localhost:8000/debug/query/{contract_id} \
  -H "Content-Type: application/json" \
  -d '{"question": "test query"}'
```

---

## 📊 Performance

### System Performance

| Metric | Value |
|--------|-------|
| **Contract Upload** | ~5-10 seconds |
| **PDF Processing** | ~2-5 seconds |
| **Vectorization** | ~10-20 seconds (200 chunks) |
| **Analysis (7 types)** | ~30-60 seconds |
| **Q&A Response** | ~3-5 seconds |
| **Total (Upload → Results)** | ~60-90 seconds |

### RAG Performance

| Metric | Value |
|--------|-------|
| **Retrieval Accuracy** | 4/4 critical clauses found |
| **Page Citation Accuracy** | 100% |
| **Query Diversity** | 8 unique queries |
| **Context Size** | 30 chunks (~15,000 tokens) |
| **Reranking Precision** | 40 chunks from 120 |

### Scalability

- **Concurrent Users**: Tested with 10+ simultaneous uploads
- **Database**: Supabase scales automatically
- **Vector DB**: Pinecone handles millions of vectors
- **API**: FastAPI async for high throughput

---

## 🚀 Deployment

### Backend Deployment

**Option 1: Railway / Render**
```bash
# 1. Create account on Railway/Render
# 2. Connect GitHub repo
# 3. Set environment variables
# 4. Deploy with: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Option 2: AWS / GCP / Azure**
```bash
# 1. Create VM instance
# 2. Install Python 3.13
# 3. Clone repo and setup venv
# 4. Run with systemd/supervisor
# 5. Setup nginx reverse proxy
```

### Frontend Deployment

**Vercel (Recommended)**
```bash
# 1. Push to GitHub
# 2. Import project in Vercel
# 3. Set environment variables
# 4. Deploy automatically
```

### Environment Variables

**Backend (.env)**
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
ZEROENTROPY_API_KEY=...
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=https://api.tenddr.com
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

---

## 📝 Development Notes

### Code Structure

```
Tenddr/
├── main.py              # FastAPI app, all endpoints
├── rag.py              # Vector search, embeddings, reranking
├── query_expansion.py  # Hybrid multi-query retrieval
├── prompts.py          # All LLM prompts
├── analyzers.py        # Contract analysis functions
├── pdf_processor.py    # PDF extraction and chunking
├── classify.py         # Chunk classification
├── risk_catalog.py     # Risk definitions
├── risk_detector.py    # Risk analysis
├── database.py         # Supabase database operations
├── storage.py          # Supabase storage operations
└── supabase_client.py  # Supabase client initialization

tenddr-frontend/
├── app/
│   ├── upload/         # Upload page
│   ├── contracts/      # Contracts list
│   ├── results/[id]/   # Results view
│   └── page.tsx        # Landing page
├── components/
│   ├── FileUpload.tsx
│   ├── ContractsList.tsx
│   ├── ResultsView.tsx
│   └── RiskDashboard.tsx
└── middleware.ts       # Clerk auth middleware
```

### Key Functions

**RAG Pipeline:**
- `hybrid_multi_query_retrieval()` - Main retrieval orchestrator
- `query_contract()` - Pinecone query with metadata filtering
- `rerank_with_zeroentropy()` - Smart reranking with diversity
- `generate_response()` - LLM answer generation

**Analysis:**
- `run_comprehensive_analysis()` - Runs all 7 analysis types
- `run_risk_analysis()` - Detects and scores risks
- `analyze_financial_risks()` - Financial provision analysis

**Processing:**
- `extract_text_with_pages()` - PDF → text with page numbers
- `create_enhanced_chunks_with_pages()` - Chunking + classification
- `store_in_pinecone()` - Batch upsert to Pinecone

---

## 🎯 Roadmap

### Completed ✅
- [x] Hybrid RAG implementation
- [x] Smart reranking with diversity
- [x] User isolation with RLS
- [x] Contract deletion with cascade
- [x] 7 analysis types
- [x] Risk detection (20+ categories)
- [x] Q&A system matching ContraVault

### In Progress 🚧
- [ ] Frontend improvements
- [ ] Batch contract analysis
- [ ] Export reports (PDF/Word)

### Planned 📋
- [ ] Contract comparison
- [ ] Clause library
- [ ] Custom risk definitions
- [ ] Multi-language support
- [ ] Mobile app

---

## 📞 Support

For issues or questions:
1. Check the test scripts: `./test_hybrid_api.sh`
2. Review debug endpoint: `/debug/query/{contract_id}`
3. Check backend logs: `uvicorn main:app --reload`

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- OpenAI for GPT-4o and embeddings
- Pinecone for vector database
- Supabase for database and storage
- ZeroEntropy for reranking
- Clerk for authentication

---

**Built with ❤️ for contractors who deserve fair contracts**

