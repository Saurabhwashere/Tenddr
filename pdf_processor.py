# Extract text from PDF
import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    
    for page in doc:
        text += page.get_text()
    
    doc.close()
    return text

def extract_text_with_pages(pdf_path: str) -> list[dict]:
    """Extract text with page numbers for better metadata."""
    doc = fitz.open(pdf_path)
    pages_data = []
    
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():  # Only add non-empty pages
            pages_data.append({
                "page_number": page_num,
                "text": text.strip()
            })
    
    doc.close()
    return pages_data

def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
    """Split text into chunks for embedding (legacy method)."""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks

def chunk_text_with_overlap(text: str, chunk_size: int = 300, overlap: int = 100) -> list[dict]:
    """
    Split text into overlapping chunks with metadata.
    
    Args:
        text: The text to chunk
        chunk_size: Target words per chunk (smaller = more precise retrieval)
        overlap: Number of words to overlap between chunks (prevents info loss)
    
    Returns:
        List of chunk dictionaries with text and metadata
    """
    # Split by paragraphs first (better semantic boundaries)
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    chunk_index = 0
    
    for para in paragraphs:
        words = para.split()
        word_count = len(words)
        
        # If adding this paragraph exceeds chunk_size, save current chunk
        if current_size + word_count > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "chunk_index": chunk_index,
                "word_count": current_size
            })
            
            # Keep last 'overlap' words for context continuity
            overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_words + words
            current_size = len(current_chunk)
            chunk_index += 1
        else:
            current_chunk.extend(words)
            current_size += word_count
    
    # Add last chunk
    if current_chunk:
        chunks.append({
            "text": ' '.join(current_chunk),
            "chunk_index": chunk_index,
            "word_count": current_size
        })
    
    return chunks

def create_chunks_with_pages(pages_data: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """
    Create overlapping chunks while preserving page numbers.
    
    This is the BEST approach - combines page metadata with smart chunking.
    """
    all_chunks = []
    global_chunk_index = 0
    
    for page_info in pages_data:
        page_text = page_info["text"]
        page_num = page_info["page_number"]
        
        # Create overlapping chunks for this page
        page_chunks = chunk_text_with_overlap(page_text, chunk_size, overlap)
        
        # Add page number to each chunk
        for chunk in page_chunks:
            chunk["page_number"] = page_num
            chunk["global_chunk_index"] = global_chunk_index
            all_chunks.append(chunk)
            global_chunk_index += 1
    
    return all_chunks

def create_enhanced_chunks_with_pages(pages_data: list[dict], chunk_size: int = 500, overlap: int = 100, use_hybrid: bool = True) -> list[dict]:
    """
    Create chunks with metadata for better filtering.
    NOW WITH PARALLEL CLASSIFICATION FOR 10x SPEEDUP!
    
    This adds classification metadata to each chunk:
    - primary_category: financial, legal, compliance, etc.
    - clause_type: specific type like payment_terms, liquidated_damages
    - risk_tags: list of risk IDs this chunk relates to
    - keywords: keywords found in this chunk (or topics if LLM-classified)
    
    Args:
        pages_data: List of page dictionaries with text and page numbers
        chunk_size: Number of words per chunk
        overlap: Number of words to overlap between chunks
        use_hybrid: If True, uses hybrid classification (LLM for critical chunks, keywords for others)
                   If False, uses keyword-only classification (faster, free)
    """
    from classify import classify_chunks_batch  # Use new parallel function
    
    all_chunks = []
    global_chunk_index = 0
    
    print(f"📝 Creating chunks (size={chunk_size}, overlap={overlap})...")
    
    # Step 1: Create basic chunks with page info (fast, no API calls)
    for page_info in pages_data:
        page_text = page_info["text"]
        page_num = page_info["page_number"]
        
        # Create overlapping chunks for this page
        page_chunks = chunk_text_with_overlap(page_text, chunk_size, overlap)
        
        # Add basic metadata
        for chunk in page_chunks:
            chunk["page_number"] = page_num
            chunk["global_chunk_index"] = global_chunk_index
            all_chunks.append(chunk)
            global_chunk_index += 1
    
    print(f"  ✅ Created {len(all_chunks)} chunks")
    
    # Step 2: Classify all chunks IN PARALLEL (much faster!)
    all_chunks = classify_chunks_batch(all_chunks, use_hybrid=use_hybrid)
    
    return all_chunks
