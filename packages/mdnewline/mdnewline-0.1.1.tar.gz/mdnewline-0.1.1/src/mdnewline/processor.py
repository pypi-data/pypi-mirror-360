import re
from typing import List


def is_abbreviation(word: str) -> bool:
    """Check if a word is likely an abbreviation."""
    abbreviations = {
        'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Sr.', 'Jr.',
        'U.S.', 'U.K.', 'U.N.', 'Ph.D.', 'M.D.', 'B.A.', 'M.A.',
        'Inc.', 'Corp.', 'Ltd.', 'Co.', 'vs.', 'etc.', 'i.e.', 'e.g.',
        'a.m.', 'p.m.', 'A.M.', 'P.M.'
    }
    return word in abbreviations


def is_decimal_number(prev_char: str, next_char: str) -> bool:
    """Check if a period is part of a decimal number."""
    return prev_char.isdigit() and next_char.isdigit()


def is_file_extension(text: str, pos: int) -> bool:
    """Check if a period is part of a file extension or URL."""
    # Look for patterns like .com, .org, .txt, etc.
    if pos + 1 < len(text):
        remaining = text[pos + 1:]
        # Check for common file extensions or domain endings
        extension_match = re.match(r'^[a-zA-Z0-9]{1,5}(?:\s|$)', remaining)
        if extension_match:
            # Check if preceded by alphanumeric (no space before period)
            if pos > 0 and text[pos - 1].isalnum():
                return True
    return False


def split_paragraph_into_sentences(paragraph: str) -> List[str]:
    """Split a paragraph into sentences, handling edge cases."""
    if not paragraph.strip():
        return []
    
    # First, protect abbreviations, decimals, and URLs by temporarily replacing them
    protected_text = paragraph
    abbreviations = [
        'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Sr.', 'Jr.',
        'U.S.', 'U.K.', 'U.N.', 'Ph.D.', 'M.D.', 'B.A.', 'M.A.',
        'Inc.', 'Corp.', 'Ltd.', 'Co.', 'vs.', 'etc.', 'i.e.', 'e.g.',
        'a.m.', 'p.m.', 'A.M.', 'P.M.'
    ]
    
    # Create placeholder mappings for abbreviations
    placeholders = {}
    for i, abbr in enumerate(abbreviations):
        placeholder = f"__ABBR_{i}__"
        placeholders[placeholder] = abbr
        protected_text = protected_text.replace(abbr, placeholder)
    
    # Protect decimal numbers
    decimal_pattern = r'\d+\.\d+'
    decimal_matches = re.findall(decimal_pattern, protected_text)
    for i, match in enumerate(decimal_matches):
        placeholder = f"__DECIMAL_{i}__"
        placeholders[placeholder] = match
        protected_text = protected_text.replace(match, placeholder)
    
    # Protect file extensions and URLs
    file_pattern = r'\w+\.\w+'
    file_matches = re.findall(file_pattern, protected_text)
    for i, match in enumerate(file_matches):
        if '.' in match and not match.endswith('.'):
            placeholder = f"__FILE_{i}__"
            placeholders[placeholder] = match
            protected_text = protected_text.replace(match, placeholder)
    
    # Now split on sentence boundaries: period followed by space and capital letter
    sentences = []
    current_sentence = ""
    
    words = protected_text.split()
    for i, word in enumerate(words):
        current_sentence += word
        
        # Check if this word ends with a period and is followed by a capitalized word
        if word.endswith('.'):
            # Check if next word starts with capital letter
            if i + 1 < len(words) and words[i + 1][0].isupper():
                # This is end of sentence
                sentence = current_sentence.strip()
                # Restore all placeholders
                for placeholder, original in placeholders.items():
                    sentence = sentence.replace(placeholder, original)
                sentences.append(sentence)
                current_sentence = ""
            elif i + 1 == len(words):
                # End of paragraph
                sentence = current_sentence.strip()
                # Restore all placeholders
                for placeholder, original in placeholders.items():
                    sentence = sentence.replace(placeholder, original)
                sentences.append(sentence)
                current_sentence = ""
            else:
                # Not end of sentence, add space
                current_sentence += " "
        else:
            # Not ending with period, add space
            current_sentence += " "
    
    # Handle any remaining text
    if current_sentence.strip():
        sentence = current_sentence.strip()
        # Restore all placeholders
        for placeholder, original in placeholders.items():
            sentence = sentence.replace(placeholder, original)
        sentences.append(sentence)
    
    # Filter out empty sentences
    sentences = [s for s in sentences if s.strip()]
    
    # If no sentences were found, return the original text
    if not sentences:
        return [paragraph]
    
    return sentences


def process_markdown(text: str) -> str:
    """Process markdown text to add line breaks after sentences."""
    lines = text.split('\n')
    processed_lines = []
    in_code_block = False
    
    for line in lines:
        # Check for code block markers
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            processed_lines.append(line)
            continue
        
        # Skip processing if we're in a code block
        if in_code_block:
            processed_lines.append(line)
            continue
        
        # Skip empty lines, headers, and indented code blocks
        if (not line.strip() or 
            line.strip().startswith('#') or
            line.strip().startswith('    ')):  # Code blocks with indentation
            processed_lines.append(line)
            continue
        
        # Process regular text lines
        sentences = split_paragraph_into_sentences(line)
        if sentences:
            processed_lines.append('\n'.join(sentences))
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)