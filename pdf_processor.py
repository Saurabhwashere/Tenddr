# Extract text from PDF with Hierarchical Chunking
import fitz  # PyMuPDF
import re
import json
from typing import List, Dict, Tuple

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


# ============================================================================
# NEW: HIERARCHICAL CHUNKING IMPLEMENTATION
# ============================================================================

def clean_text(text: str) -> str:
    """
    Clean text by removing excessive newlines and page markers while preserving structure.
    
    Args:
        text: Raw text from PDF
        
    Returns:
        Cleaned text with normalized whitespace
    """
    # Remove page markers like "--- PAGE X ---"
    text = re.sub(r'-{3,}\s*PAGE\s+\d+\s*-{3,}', '', text, flags=re.IGNORECASE)
    
    # Remove excessive newlines (3+ newlines → 2 newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove trailing/leading whitespace
    text = text.strip()
    
    return text


def detect_clause_level(clause_id: str) -> int:
    """
    Determine the hierarchical level of a clause based on its numbering.
    
    Examples:
        "1" → Level 1
        "1.1" → Level 2
        "1.1.2" → Level 3
        "SECTION-1" → Level 1
        
    Args:
        clause_id: The clause identifier (e.g., "1.1.2")
        
    Returns:
        Integer representing the depth level
    """
    # Count dots to determine level
    if '.' in clause_id:
        return clause_id.count('.') + 1
    
    # If no dots, it's a top-level clause
    return 1


def split_by_structure(text: str) -> List[Dict[str, str]]:
    """
    Split document into structural units (clauses, sections) using regex patterns.
    
    This identifies common numbering patterns:
    - "1.", "1.1", "1.1.2" (numeric hierarchies)
    - "Clause 1.1.2"
    - "SECTION-1", "SECTION 1"
    - "Article 1"
    
    Args:
        text: Cleaned full document text
        
    Returns:
        List of dictionaries with 'id', 'heading', and 'content'
    """
    # Enhanced regex pattern to capture various clause/section formats
    # Matches:
    # - Numeric: "1.", "1.1", "1.1.2" followed by heading
    # - With prefix: "Clause 1.1", "SECTION-1", "Article 1"
    # Pattern explanation:
    # - (?m): Multiline mode
    # - ^: Start of line
    # - ((?:Clause|SECTION|Section|Article|ARTICLE)?\s*: Optional prefix
    # - (\d+(?:\.\d+)*): Capture number like 1, 1.1, 1.1.2
    # - \.?: Optional trailing dot
    # - \s+: Required whitespace
    # - ([^\n]+): Capture heading (rest of line)
    pattern = r'(?m)^((?:Clause|SECTION|Section|Article|ARTICLE)?\s*(\d+(?:\.\d+)*)\.?\s+([^\n]+))'
    
    matches = list(re.finditer(pattern, text))
    
    if not matches:
        # If no structure found, return entire document as single chunk
        return [{
            'id': '1',
            'heading': 'Full Document',
            'content': text
        }]
    
    segments = []
    
    for i, match in enumerate(matches):
        # Group 2 is the clause number (e.g., "1.1.2")
        # Group 3 is the heading text
        clause_id = match.group(2).strip()
        heading = match.group(3).strip()
        start_pos = match.end()
        
        # Get content until next clause or end of document
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(text)
        
        content = text[start_pos:end_pos].strip()
        
        segments.append({
            'id': clause_id,
            'heading': heading,
            'content': content
        })
    
    return segments


def build_hierarchical_chunks(segments: List[Dict[str, str]], source_file: str = "contract.pdf") -> List[Dict]:
    """
    Build context-aware chunks by maintaining hierarchical context path.
    
    This is the core of the hierarchical chunking strategy:
    - Maintains a context stack (e.g., ["Section 1", "Clause 1.1", "Clause 1.1.2"])
    - Prefixes each chunk with its full context path
    - Updates context as we traverse the document hierarchy
    
    Args:
        segments: List of clause segments from split_by_structure()
        source_file: Name of source PDF file
        
    Returns:
        List of fully context-aware chunk dictionaries
    """
    chunks = []
    context_stack = []  # Stack of (level, heading) tuples
    
    for segment in segments:
        clause_id = segment['id']
        heading = segment['heading']
        content = segment['content']
        
        # Determine hierarchical level
        level = detect_clause_level(clause_id)
        
        # Update context stack: remove items at same or deeper level
        context_stack = [(l, h) for l, h in context_stack if l < level]
        
        # Add current clause to context
        context_stack.append((level, heading))
        
        # Build context path (e.g., "Section 1 | Clause 1.1 | Clause 1.1.2")
        context_path = " | ".join([h for _, h in context_stack])
        
        # Build final chunk text with context prefix
        if content:
            chunk_text = f"{context_path}: {content}"
        else:
            chunk_text = context_path
        
        # Create chunk dictionary
        chunk = {
            'id': clause_id,
            'heading': heading,
            'text': chunk_text,  # This is what gets embedded
            'content': content,  # Raw content without prefix
            'context_path': context_path,
            'level': level,
            'source_file': source_file,
            'word_count': len(chunk_text.split())
        }
        
        chunks.append(chunk)
    
    return chunks


def create_hierarchical_chunks(pages_data: List[Dict], source_file: str = "contract.pdf") -> List[Dict]:
    """
    Main function: Create hierarchical, context-aware chunks from PDF pages.
    
    This implements the complete hierarchical chunking pipeline:
    1. Merge pages into full document text
    2. Clean text (remove page markers, normalize whitespace)
    3. Split by structural markers (clauses, sections)
    4. Build context-aware chunks with hierarchical prefixes
    5. Add page number metadata
    
    Args:
        pages_data: List of page dictionaries from extract_text_with_pages()
        source_file: Name of source PDF file
        
    Returns:
        List of hierarchical chunk dictionaries ready for vectorization
    """
    print(f"📝 Creating hierarchical chunks...")
    
    # Step 1: Merge all pages into full document
    full_text = "\n\n".join([page['text'] for page in pages_data])
    
    # Step 2: Clean text
    cleaned_text = clean_text(full_text)
    print(f"  ✅ Cleaned text ({len(cleaned_text)} characters)")
    
    # Step 3: Split by structural markers
    segments = split_by_structure(cleaned_text)
    print(f"  ✅ Found {len(segments)} structural segments")
    
    # Step 4: Build hierarchical chunks with context
    chunks = build_hierarchical_chunks(segments, source_file)
    print(f"  ✅ Created {len(chunks)} hierarchical chunks")
    
    # Step 5: Add page number metadata (approximate mapping)
    # Map chunks back to pages based on content position
    chunks_with_pages = add_page_metadata(chunks, pages_data)
    
    return chunks_with_pages


def add_page_metadata(chunks: List[Dict], pages_data: List[Dict]) -> List[Dict]:
    """
    Add page number metadata to chunks by matching content to pages.
    
    Since hierarchical chunks may span multiple pages, we find the page
    where the chunk's content first appears.
    
    Args:
        chunks: List of hierarchical chunks
        pages_data: Original page data with page numbers
        
    Returns:
        Chunks with added 'page_number' field
    """
    # Create a mapping of text snippets to page numbers
    page_map = {}
    for page in pages_data:
        # Store first 100 chars of each page for matching
        snippet = page['text'][:100].strip()
        page_map[snippet] = page['page_number']
    
    # For each chunk, find which page it belongs to
    for i, chunk in enumerate(chunks):
        content_snippet = chunk['content'][:100].strip() if chunk['content'] else ""
        
        # Try to find matching page
        matched_page = None
        for page in pages_data:
            if content_snippet in page['text']:
                matched_page = page['page_number']
                break
        
        # If no match, estimate based on position
        if matched_page is None:
            # Estimate: distribute chunks evenly across pages
            matched_page = min(len(pages_data), max(1, int((i / len(chunks)) * len(pages_data)) + 1))
        
        chunk['page_number'] = matched_page
        chunk['global_chunk_index'] = i
    
    return chunks


# ============================================================================
# LEGACY FUNCTIONS (kept for backward compatibility)
# ============================================================================

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
    Split text into overlapping chunks with metadata (legacy method).
    """
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    chunk_index = 0
    
    for para in paragraphs:
        words = para.split()
        word_count = len(words)
        
        if current_size + word_count > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "chunk_index": chunk_index,
                "word_count": current_size
            })
            
            overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_words + words
            current_size = len(current_chunk)
            chunk_index += 1
        else:
            current_chunk.extend(words)
            current_size += word_count
    
    if current_chunk:
        chunks.append({
            "text": ' '.join(current_chunk),
            "chunk_index": chunk_index,
            "word_count": current_size
        })
    
    return chunks


def create_chunks_with_pages(pages_data: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """
    Create overlapping chunks while preserving page numbers (legacy method).
    """
    all_chunks = []
    global_chunk_index = 0
    
    for page_info in pages_data:
        page_text = page_info["text"]
        page_num = page_info["page_number"]
        
        page_chunks = chunk_text_with_overlap(page_text, chunk_size, overlap)
        
        for chunk in page_chunks:
            chunk["page_number"] = page_num
            chunk["global_chunk_index"] = global_chunk_index
            all_chunks.append(chunk)
            global_chunk_index += 1
    
    return all_chunks


def create_enhanced_chunks_with_pages(pages_data: list[dict], chunk_size: int = 500, overlap: int = 100, use_hybrid: bool = True, use_hierarchical: bool = True) -> list[dict]:
    """
    Create chunks with metadata for better filtering.
    
    NEW: Now supports hierarchical chunking strategy!
    
    Args:
        pages_data: List of page dictionaries with text and page numbers
        chunk_size: Number of words per chunk (ignored if use_hierarchical=True)
        overlap: Number of words to overlap (ignored if use_hierarchical=True)
        use_hybrid: If True, uses hybrid classification
        use_hierarchical: If True, uses new hierarchical chunking (RECOMMENDED)
    """
    from classify import classify_chunks_batch
    
    print(f"📝 Creating chunks (hierarchical={use_hierarchical})...")
    
    # NEW: Use hierarchical chunking if enabled
    if use_hierarchical:
        all_chunks = create_hierarchical_chunks(pages_data)
        print(f"  ✅ Created {len(all_chunks)} hierarchical chunks")
    else:
        # Legacy: overlapping chunks
        all_chunks = []
        global_chunk_index = 0
        
        for page_info in pages_data:
            page_text = page_info["text"]
            page_num = page_info["page_number"]
            
            page_chunks = chunk_text_with_overlap(page_text, chunk_size, overlap)
            
            for chunk in page_chunks:
                chunk["page_number"] = page_num
                chunk["global_chunk_index"] = global_chunk_index
                all_chunks.append(chunk)
                global_chunk_index += 1
        
        print(f"  ✅ Created {len(all_chunks)} overlapping chunks")
    
    # Step 2: Classify all chunks IN PARALLEL
    all_chunks = classify_chunks_batch(all_chunks, use_hybrid=use_hybrid)
    
    return all_chunks


def export_chunks_to_json(chunks: List[Dict], output_file: str = "chunks.json"):
    """
    Export chunks to JSON file for inspection or external use.
    
    Args:
        chunks: List of chunk dictionaries
        output_file: Path to output JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Exported {len(chunks)} chunks to {output_file}")
