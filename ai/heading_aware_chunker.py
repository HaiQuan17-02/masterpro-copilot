"""
HeadingAwareChunker Module for MasterPro Copilot (Week 3).

Provides hierarchical, structure-aware Markdown document chunking tailored
for Vietnamese Enterprise ERP/POS documentation.

Preserves:
- Heading hierarchy (H1 to H6) and breadcrumb heading_path
- Markdown tables, lists (bullet and numbered), and code blocks
- Unicode NFC normalization and Vietnamese diacritics
- Complete metadata tracking across chunks
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple, Union


class MarkdownBlock:
    """Represents an atomic semantic block within a Markdown document."""
    def __init__(self, block_type: str, text: str, extra: Optional[Dict[str, Any]] = None):
        self.block_type = block_type  # "heading", "paragraph", "list", "table", "code", "blockquote"
        self.text = text
        self.extra = extra or {}

    def __repr__(self) -> str:
        return f"<MarkdownBlock type={self.block_type} len={len(self.text)}>"


class MarkdownSection:
    """Represents a section in Markdown bounded by a heading or document start."""
    def __init__(
        self,
        level: Optional[int],
        title: Optional[str],
        heading_line: Optional[str],
        heading_path: str,
        blocks: Optional[List[MarkdownBlock]] = None
    ):
        self.level = level
        self.title = title
        self.heading_line = heading_line
        self.heading_path = heading_path
        self.blocks = blocks if blocks is not None else []

    def __repr__(self) -> str:
        return f"<MarkdownSection path='{self.heading_path}' blocks={len(self.blocks)}>"


class HeadingAwareChunker:
    """
    HeadingAwareChunker for Markdown documents in MasterPro Copilot.
    
    Adheres to MasterPro Copilot Week 3 specifications:
    1. Accepts Markdown content and document metadata.
    2. Identifies headings H1 to H6 (# to ######) while ignoring code fences.
    3. Builds hierarchical heading_path (e.g., 'H1 > H2 > H3').
    4. Prioritizes chunking by section and paragraph boundaries.
    5. Preserves bullet lists, numbered lists, tables, and code blocks as atomic units.
    6. Configurable chunk_size and chunk_overlap limits.
    7. Gracefully decomposes oversized sections, tables, lists, and code blocks.
    8. Preserves Unicode NFC normalization and Vietnamese accents.
    9. Strict non-modification of business content.
    10. Attaches required metadata:
       - document_id, version_id, category, module, title,
       - heading_path, chunk_index, content, source, page.
    """

    HEADING_REGEX = re.compile(r'^(#{1,6})\s+(.+?)(?:\s+#+)?$')
    TABLE_DELIMITER_REGEX = re.compile(r'^\s*\|?(\s*:?-+:?\s*\|)+(\s*:?-+:?\s*)?\|?\s*$')
    LIST_ITEM_REGEX = re.compile(r'^\s*(?:[-*+]|\d+[\.\)])\s+(.*)')
    CITATION_REGEX = re.compile(r'\[cite:\s*([^\]]+)\]')
    PAGE_COMMENT_REGEX = re.compile(r'<!--\s*page:\s*(\d+)\s*-->', re.IGNORECASE)

    def __init__(
        self,
        chunk_size: int = 600,
        chunk_overlap: int = 100,
        min_chunk_size: int = 50,
        include_heading_in_content: bool = True,
        heading_path_separator: str = " > "
    ):
        """
        Initialize the HeadingAwareChunker.

        :param chunk_size: Maximum character count per chunk.
        :param chunk_overlap: Desired overlap in characters between chunks of an oversized section.
        :param min_chunk_size: Minimum characters to avoid micro-chunks unless standalone.
        :param include_heading_in_content: Whether to retain the section heading line in chunk text.
        :param heading_path_separator: Separator used for breadcrumb path (default ' > ').
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            chunk_overlap = int(chunk_size * 0.2)

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.include_heading_in_content = include_heading_in_content
        self.heading_path_separator = heading_path_separator

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def chunk_document(
        self,
        markdown_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Main entry point for chunking a Markdown document.
        Returns a list of chunk dictionaries with required metadata fields.
        """
        if not markdown_text or not markdown_text.strip():
            return []

        # 1. Unicode NFC normalization (preserving Vietnamese diacritics)
        normalized_text = unicodedata.normalize('NFC', markdown_text)
        base_meta = metadata or {}

        # 2. Parse Markdown into sections governed by H1..H6 headings
        sections, doc_h1 = self._parse_markdown_into_sections(normalized_text, base_meta)

        # 3. Extract top-level document properties from metadata
        doc_id = base_meta.get("document_id") or base_meta.get("id")
        version_id = base_meta.get("version_id") or base_meta.get("version")
        category = base_meta.get("category")
        module = base_meta.get("module")
        title = base_meta.get("title") or doc_h1 or "Tài liệu MasterPro"
        source = base_meta.get("source")

        # 4. Chunk sections into structured chunk dictionaries
        all_chunks: List[Dict[str, Any]] = []
        chunk_idx = 1

        for section in sections:
            section_chunks = self._chunk_section(section)
            for c_text in section_chunks:
                clean_content = c_text.strip()
                if not clean_content:
                    continue

                page = self._extract_page(base_meta, clean_content)
                chunk_id = f"{doc_id or 'doc'}_chunk_{chunk_idx:03d}"

                chunk_dict = {
                    "document_id": doc_id,
                    "version_id": version_id,
                    "category": category,
                    "module": module,
                    "title": title,
                    "heading_path": section.heading_path,
                    "chunk_index": chunk_idx,
                    "content": clean_content,
                    "source": source,
                    "page": page,
                    # Extended attributes for RAG & monitoring compatibility
                    "chunk_id": chunk_id,
                    "char_count": len(clean_content),
                    "approx_tokens": int(len(clean_content.split()) * 1.3),
                    "metadata": {
                        **base_meta,
                        "document_id": doc_id,
                        "version_id": version_id,
                        "category": category,
                        "module": module,
                        "title": title,
                        "heading_path": section.heading_path,
                        "chunk_index": chunk_idx,
                        "source": source,
                        "page": page,
                    }
                }
                all_chunks.append(chunk_dict)
                chunk_idx += 1

        return all_chunks

    def split_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Alias for backward compatibility with DocumentChunker."""
        return self.chunk_document(text, metadata)

    # =========================================================================
    # PARSING LOGIC: HEADINGS & SECTIONS
    # =========================================================================

    def _parse_markdown_into_sections(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> Tuple[List[MarkdownSection], Optional[str]]:
        """
        Parses Markdown text into sections while tracking H1-H6 heading hierarchy
        and avoiding heading detection inside fenced code blocks.
        """
        lines = text.splitlines()
        sections: List[MarkdownSection] = []
        heading_stack: List[Tuple[int, str]] = []  # List of (level, heading_text)
        
        fallback_title = metadata.get("title") or ""
        doc_first_h1: Optional[str] = None

        current_level: Optional[int] = None
        current_title: Optional[str] = None
        current_heading_line: Optional[str] = None
        current_path: str = fallback_title
        current_lines: List[str] = []

        in_code_block = False
        code_fence_char = ""

        def flush_section(is_final: bool = False):
            nonlocal current_lines, current_path, current_level, current_title, current_heading_line
            blocks = self._parse_lines_into_blocks(current_lines)
            
            # If section has body content, or if it is the only heading in document at EOF:
            if blocks:
                if self.include_heading_in_content and current_heading_line:
                    blocks.insert(0, MarkdownBlock("heading", current_heading_line))
                sections.append(MarkdownSection(
                    level=current_level,
                    title=current_title,
                    heading_line=current_heading_line,
                    heading_path=current_path,
                    blocks=blocks
                ))
            elif is_final and not sections and current_heading_line:
                # Document consists solely of a heading line
                h_block = [MarkdownBlock("heading", current_heading_line)]
                sections.append(MarkdownSection(
                    level=current_level,
                    title=current_title,
                    heading_line=current_heading_line,
                    heading_path=current_path,
                    blocks=h_block
                ))

            current_lines = []

        for line in lines:
            stripped = line.strip()

            # Check code fence state
            if stripped.startswith('```') or stripped.startswith('~~~'):
                fence_tag = stripped[:3]
                if not in_code_block:
                    in_code_block = True
                    code_fence_char = fence_tag
                else:
                    if fence_tag == code_fence_char:
                        in_code_block = False
                        code_fence_char = ""
                current_lines.append(line)
                continue

            if in_code_block:
                current_lines.append(line)
                continue

            # Heading detection (H1 to H6) outside code blocks
            heading_match = self.HEADING_REGEX.match(line)
            if heading_match:
                # Flush previous section
                flush_section(is_final=False)

                level = len(heading_match.group(1))
                raw_h_title = heading_match.group(2).strip()

                # Clean citations or comments from heading title for breadcrumb
                h_title = re.sub(r'\[cite:\s*[^\]]+\]', '', raw_h_title)
                h_title = re.sub(r'<!--.*?-->', '', h_title).strip()

                if level == 1 and not doc_first_h1:
                    doc_first_h1 = h_title

                # Maintain heading stack hierarchy
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, h_title))

                # Build hierarchical heading_path
                current_path = self.heading_path_separator.join(item[1] for item in heading_stack)
                current_level = level
                current_title = h_title
                current_heading_line = line.strip()
                current_lines = []
            else:
                current_lines.append(line)

        # Flush final section
        flush_section(is_final=True)

        # Handle case: document has no headings at all
        if not sections and lines:
            all_blocks = self._parse_lines_into_blocks(lines)
            if all_blocks:
                sections.append(MarkdownSection(
                    level=None,
                    title=None,
                    heading_line=None,
                    heading_path=fallback_title,
                    blocks=all_blocks
                ))

        return sections, doc_first_h1

    # =========================================================================
    # PARSING LOGIC: SEMANTIC BLOCKS (TABLES, CODE, LISTS, PARAGRAPHS)
    # =========================================================================

    def _parse_lines_into_blocks(self, lines: List[str]) -> List[MarkdownBlock]:
        """
        Groups lines into structured MarkdownBlocks:
        - code: Fenced code block (``` ... ``` or ~~~ ... ~~~)
        - table: Markdown tables with headers and rows
        - list: Ordered or unordered list sequences
        - blockquote: Blockquote paragraphs
        - paragraph: Standard text paragraphs separated by empty lines
        """
        blocks: List[MarkdownBlock] = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            # 1. Code Block
            if stripped.startswith('```') or stripped.startswith('~~~'):
                fence = stripped[:3]
                code_lines = [line]
                i += 1
                while i < n:
                    code_lines.append(lines[i])
                    if lines[i].strip().startswith(fence):
                        i += 1
                        break
                    i += 1
                blocks.append(MarkdownBlock("code", "\n".join(code_lines)))
                continue

            # 2. Table Block
            if "|" in line and (i + 1 < n) and self.TABLE_DELIMITER_REGEX.match(lines[i + 1]):
                table_lines = [line]
                i += 1
                while i < n and ("|" in lines[i] or lines[i].strip().startswith("|")):
                    table_lines.append(lines[i])
                    i += 1
                blocks.append(MarkdownBlock("table", "\n".join(table_lines)))
                continue

            # 3. List Block (bullet or numbered)
            if self.LIST_ITEM_REGEX.match(line):
                list_lines = [line]
                i += 1
                while i < n:
                    nxt = lines[i]
                    nxt_s = nxt.strip()
                    if not nxt_s:
                        if (i + 1 < n) and (self.LIST_ITEM_REGEX.match(lines[i + 1]) or lines[i + 1].startswith("  ") or lines[i + 1].startswith("\t")):
                            list_lines.append(nxt)
                            i += 1
                            continue
                        else:
                            break
                    if self.LIST_ITEM_REGEX.match(nxt) or nxt.startswith("  ") or nxt.startswith("\t"):
                        list_lines.append(nxt)
                        i += 1
                    else:
                        break
                blocks.append(MarkdownBlock("list", "\n".join(list_lines).rstrip()))
                continue

            # 4. Blockquote
            if stripped.startswith('>'):
                bq_lines = [line]
                i += 1
                while i < n and (lines[i].strip().startswith('>') or lines[i].startswith('  ')):
                    bq_lines.append(lines[i])
                    i += 1
                blocks.append(MarkdownBlock("blockquote", "\n".join(bq_lines)))
                continue

            # 5. Regular Paragraph
            para_lines = [line]
            i += 1
            while i < n:
                curr = lines[i]
                curr_s = curr.strip()
                if not curr_s:
                    break
                if curr_s.startswith('```') or curr_s.startswith('~~~') or self.LIST_ITEM_REGEX.match(curr) or (("|" in curr) and (i + 1 < n and self.TABLE_DELIMITER_REGEX.match(lines[i + 1]))):
                    break
                para_lines.append(curr)
                i += 1
            blocks.append(MarkdownBlock("paragraph", "\n".join(para_lines)))

        return blocks

    # =========================================================================
    # CHUNKING LOGIC: SECTION & PARAGRAPH ASSEMBLY WITH OVERLAP
    # =========================================================================

    def _chunk_section(self, section: MarkdownSection) -> List[str]:
        """
        Chunks a MarkdownSection.
        - If the entire section fits in chunk_size (or within a modest tolerance),
          keeps it as 1 intact chunk.
        - Avoids isolating headings as orphan chunks without body content.
        - Preserves tables and code blocks cleanly without injecting corrupting overlap.
        """
        blocks = section.blocks
        if not blocks:
            if section.heading_line and self.include_heading_in_content:
                return [section.heading_line]
            return []

        # If section total length is within reasonable tolerance (up to 1.25x chunk_size),
        # keep intact to prevent splitting small sections or orphan headings
        total_len = sum(len(b.text) for b in blocks) + (len(blocks) - 1) * 2
        if total_len <= int(self.chunk_size * 1.25):
            return ["\n\n".join(b.text for b in blocks)]

        chunks: List[str] = []
        current_blocks: List[str] = []
        current_len = 0
        overlap_to_inject = ""

        def flush_current():
            nonlocal current_blocks, current_len, overlap_to_inject
            if not current_blocks:
                return
            combined = "\n\n".join(current_blocks).strip()
            if overlap_to_inject and not combined.startswith(overlap_to_inject):
                combined = f"{overlap_to_inject}\n\n{combined}".strip()
            chunks.append(combined)
            overlap_to_inject = self._extract_clean_overlap(combined, self.chunk_overlap)
            current_blocks = []
            current_len = 0

        for block in blocks:
            block_len = len(block.text)

            is_only_heading_pending = (
                len(current_blocks) == 1 and
                blocks[0].block_type == "heading" and
                current_blocks[0] == blocks[0].text
            )

            if block_len > self.chunk_size:
                heading_prefix = ""
                if is_only_heading_pending:
                    heading_prefix = current_blocks[0]
                    current_blocks = []
                    current_len = 0
                else:
                    flush_current()

                sub_chunks = self._split_oversized_block(block)
                for s_idx, sc in enumerate(sub_chunks):
                    sc_clean = sc.strip()
                    if not sc_clean:
                        continue
                    if s_idx == 0 and heading_prefix:
                        sc_clean = f"{heading_prefix}\n\n{sc_clean}".strip()

                    # Only inject overlap between paragraph sub-chunks, NOT tables or code blocks
                    if block.block_type not in ("table", "code"):
                        if overlap_to_inject and not sc_clean.startswith(overlap_to_inject):
                            if len(overlap_to_inject) + len(sc_clean) + 2 <= int(self.chunk_size * 1.25):
                                sc_clean = f"{overlap_to_inject}\n\n{sc_clean}".strip()

                    chunks.append(sc_clean)

                    if block.block_type not in ("table", "code"):
                        overlap_to_inject = self._extract_clean_overlap(sc_clean, self.chunk_overlap)
                    else:
                        overlap_to_inject = ""
            else:
                projected = current_len + (2 if current_blocks else 0) + block_len
                if overlap_to_inject and not current_blocks:
                    projected += len(overlap_to_inject) + 2

                threshold = int(self.chunk_size * 1.25) if is_only_heading_pending else self.chunk_size

                if projected <= threshold:
                    current_blocks.append(block.text)
                    current_len = projected
                else:
                    flush_current()
                    current_blocks.append(block.text)
                    current_len = block_len

        flush_current()
        return chunks

    # =========================================================================
    # OVERSIZED BLOCK SPLITTERS (TABLES, CODE, LISTS, PARAGRAPHS)
    # =========================================================================

    def _split_oversized_block(self, block: MarkdownBlock) -> List[str]:
        """Splits an oversized block while preserving structural syntax."""
        if block.block_type == "table":
            return self._split_oversized_table(block.text)
        elif block.block_type == "code":
            return self._split_oversized_code(block.text)
        elif block.block_type == "list":
            return self._split_oversized_list(block.text)
        else:
            return self._split_oversized_paragraph(block.text)

    def _split_oversized_table(self, table_text: str) -> List[str]:
        """
        Splits an oversized Markdown table by rows while repeating
        the table header and column delimiter on every chunk.
        """
        lines = [l for l in table_text.splitlines() if l.strip()]
        if len(lines) <= 2:
            return [table_text]

        header = f"{lines[0]}\n{lines[1]}"
        data_rows = lines[2:]

        chunks: List[str] = []
        curr_rows: List[str] = []
        curr_len = len(header)

        for row in data_rows:
            if curr_len + len(row) + 1 <= self.chunk_size:
                curr_rows.append(row)
                curr_len += len(row) + 1
            else:
                if curr_rows:
                    chunks.append(f"{header}\n" + "\n".join(curr_rows))
                curr_rows = [row]
                curr_len = len(header) + len(row) + 1

        if curr_rows:
            chunks.append(f"{header}\n" + "\n".join(curr_rows))

        return chunks if chunks else [table_text]

    def _split_oversized_code(self, code_text: str) -> List[str]:
        """
        Splits an oversized code block by lines while maintaining
        code block fences (``` ... ```) on each chunk.
        """
        lines = code_text.splitlines()
        if len(lines) <= 2:
            return [code_text]

        opening_fence = lines[0]
        closing_fence = lines[-1] if lines[-1].strip().startswith(('```', '~~~')) else '```'
        body_lines = lines[1:-1] if lines[-1].strip().startswith(('```', '~~~')) else lines[1:]

        chunks: List[str] = []
        curr_lines: List[str] = []
        curr_len = len(opening_fence) + len(closing_fence) + 2

        for l in body_lines:
            if curr_len + len(l) + 1 <= self.chunk_size:
                curr_lines.append(l)
                curr_len += len(l) + 1
            else:
                if curr_lines:
                    chunks.append(f"{opening_fence}\n" + "\n".join(curr_lines) + f"\n{closing_fence}")
                curr_lines = [l]
                curr_len = len(opening_fence) + len(closing_fence) + len(l) + 3

        if curr_lines:
            chunks.append(f"{opening_fence}\n" + "\n".join(curr_lines) + f"\n{closing_fence}")

        return chunks if chunks else [code_text]

    def _split_oversized_list(self, list_text: str) -> List[str]:
        """
        Splits an oversized list by list items so bullet/numbered items
        are not severed mid-sentence.
        """
        raw_lines = list_text.splitlines()
        items: List[str] = []
        curr_item_lines: List[str] = []

        for line in raw_lines:
            if self.LIST_ITEM_REGEX.match(line):
                if curr_item_lines:
                    items.append("\n".join(curr_item_lines))
                curr_item_lines = [line]
            else:
                curr_item_lines.append(line)
        if curr_item_lines:
            items.append("\n".join(curr_item_lines))

        chunks: List[str] = []
        curr_items: List[str] = []
        curr_len = 0

        for item in items:
            item_len = len(item)
            if item_len > self.chunk_size:
                if curr_items:
                    chunks.append("\n".join(curr_items))
                    curr_items = []
                    curr_len = 0
                sub_sents = self._split_oversized_paragraph(item)
                chunks.extend(sub_sents)
            elif curr_len + (1 if curr_items else 0) + item_len <= self.chunk_size:
                curr_items.append(item)
                curr_len += (1 if curr_items else 0) + item_len
            else:
                if curr_items:
                    chunks.append("\n".join(curr_items))
                curr_items = [item]
                curr_len = item_len

        if curr_items:
            chunks.append("\n".join(curr_items))

        return chunks if chunks else [list_text]

    def _split_oversized_paragraph(self, para_text: str) -> List[str]:
        """
        Splits an oversized paragraph into sentences, then words if necessary.
        Preserves Vietnamese diacritics and sentence boundaries.
        """
        sentences = re.split(r'(?<=[.!?])\s+', para_text)
        chunks: List[str] = []
        curr = ""

        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue

            if len(s_clean) > self.chunk_size:
                if curr:
                    chunks.append(curr)
                    curr = ""
                words = s_clean.split(" ")
                word_chunk = ""
                for w in words:
                    if len(word_chunk) + len(w) + 1 <= self.chunk_size:
                        word_chunk = f"{word_chunk} {w}".strip() if word_chunk else w
                    else:
                        if word_chunk:
                            chunks.append(word_chunk)
                        word_chunk = w
                if word_chunk:
                    chunks.append(word_chunk)
            elif len(curr) + len(s_clean) + 1 <= self.chunk_size:
                curr = f"{curr} {s_clean}".strip() if curr else s_clean
            else:
                if curr:
                    chunks.append(curr)
                curr = s_clean

        if curr:
            chunks.append(curr)

        return chunks if chunks else [para_text]

    # =========================================================================
    # OVERLAP EXTRACTION & UTILITIES
    # =========================================================================

    def _extract_clean_overlap(self, text: str, max_overlap: int) -> str:
        """
        Extracts up to max_overlap characters from the tail of text
        without severing words, sentences, or UTF-8 characters.
        """
        if not text or max_overlap <= 0:
            return ""
        if len(text) <= max_overlap:
            lines = [l for l in text.splitlines() if l.strip()]
            return lines[-1].strip() if len(lines) > 1 else text.strip()

        candidate = text[-max_overlap:]

        # 1. Look for paragraph break (\n\n)
        p_idx = candidate.find("\n\n")
        if p_idx != -1 and p_idx + 2 < len(candidate):
            return candidate[p_idx + 2:].strip()

        # 2. Look for line break (\n)
        l_idx = candidate.find("\n")
        if l_idx != -1 and l_idx + 1 < len(candidate):
            return candidate[l_idx + 1:].strip()

        # 3. Look for sentence ender (. ! ?)
        sent_match = re.search(r'[.!?]\s+', candidate)
        if sent_match and sent_match.end() < len(candidate):
            return candidate[sent_match.end():].strip()

        # 4. Look for word boundary (space)
        space_idx = candidate.find(" ")
        if space_idx != -1 and space_idx + 1 < len(candidate):
            return candidate[space_idx + 1:].strip()

        return candidate.strip()

    def _extract_page(self, metadata: Dict[str, Any], content: str) -> Optional[Any]:
        """
        Extracts reliable page citation from metadata or inline content.
        Supports explicit page number, [cite: X], or <!-- page: X -->.
        """
        if metadata.get("page") is not None:
            return metadata.get("page")
        if metadata.get("page_number") is not None:
            return metadata.get("page_number")

        # Check metadata note or citation fields
        for field in ["note", "citation", "source_citation"]:
            val = metadata.get(field)
            if val:
                match = self.CITATION_REGEX.search(str(val))
                if match:
                    return match.group(1).strip()

        # Check inline citation tags in chunk content
        match_content = self.CITATION_REGEX.search(content)
        if match_content:
            return match_content.group(1).strip()

        # Check inline page comments
        page_comment = self.PAGE_COMMENT_REGEX.search(content)
        if page_comment:
            return int(page_comment.group(1))

        return None
