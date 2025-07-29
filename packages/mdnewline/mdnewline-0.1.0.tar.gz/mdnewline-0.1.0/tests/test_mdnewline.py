import pytest
from mdnewline.processor import process_markdown


class TestMarkdownProcessor:
    def test_regular_paragraphs_single_spaces(self):
        """Test paragraphs with 5 sentences separated by single spaces."""
        input_text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four. This is sentence five."
        expected = "This is sentence one.\nThis is sentence two.\nThis is sentence three.\nThis is sentence four.\nThis is sentence five."
        result = process_markdown(input_text)
        assert result == expected

    def test_regular_paragraphs_double_spaces(self):
        """Test paragraphs with sentences separated by double spaces."""
        input_text = "This is sentence one.  This is sentence two.  This is sentence three.  This is sentence four.  This is sentence five."
        expected = "This is sentence one.\nThis is sentence two.\nThis is sentence three.\nThis is sentence four.\nThis is sentence five."
        result = process_markdown(input_text)
        assert result == expected

    def test_paragraph_with_ellipsis(self):
        """Test paragraphs with ellipsis that should not be split."""
        input_text = "This is sentence one. This is sentence two with ellipsis... This is sentence three. This is sentence four. This is sentence five."
        expected = "This is sentence one.\nThis is sentence two with ellipsis...\nThis is sentence three.\nThis is sentence four.\nThis is sentence five."
        result = process_markdown(input_text)
        assert result == expected

    def test_abbreviations_with_periods(self):
        """Test sentences with abbreviations that have periods."""
        input_text = "Dr. Smith went to the store. He bought items for Mrs. Johnson. The U.S. government issued a statement. This is the fourth sentence. This is the fifth sentence."
        expected = "Dr. Smith went to the store.\nHe bought items for Mrs. Johnson.\nThe U.S. government issued a statement.\nThis is the fourth sentence.\nThis is the fifth sentence."
        result = process_markdown(input_text)
        assert result == expected

    def test_decimal_numbers(self):
        """Test sentences with decimal numbers."""
        input_text = "The price is $12.99 for this item. The temperature was 98.6 degrees. The measurement was 3.14159 meters. This is sentence four. This is sentence five."
        expected = "The price is $12.99 for this item.\nThe temperature was 98.6 degrees.\nThe measurement was 3.14159 meters.\nThis is sentence four.\nThis is sentence five."
        result = process_markdown(input_text)
        assert result == expected

    def test_urls_and_email_addresses(self):
        """Test sentences with URLs and email addresses."""
        input_text = "Visit www.example.com for more info. Email us at support@example.com for help. The file is located at /home/user/file.txt on the server. This is sentence four. This is sentence five."
        expected = "Visit www.example.com for more info.\nEmail us at support@example.com for help.\nThe file is located at /home/user/file.txt on the server.\nThis is sentence four.\nThis is sentence five."
        result = process_markdown(input_text)
        assert result == expected

    def test_multiple_paragraphs(self):
        """Test multiple paragraphs with proper separation."""
        input_text = """This is paragraph one sentence one. This is paragraph one sentence two.

This is paragraph two sentence one. This is paragraph two sentence two."""
        expected = """This is paragraph one sentence one.\nThis is paragraph one sentence two.

This is paragraph two sentence one.\nThis is paragraph two sentence two."""
        result = process_markdown(input_text)
        assert result == expected

    def test_markdown_headers_unchanged(self):
        """Test that markdown headers remain unchanged."""
        input_text = """# This is a header

This is a sentence. This is another sentence.

## This is a subheader

This is a third sentence. This is a fourth sentence."""
        expected = """# This is a header

This is a sentence.\nThis is another sentence.

## This is a subheader

This is a third sentence.\nThis is a fourth sentence."""
        result = process_markdown(input_text)
        assert result == expected

    def test_code_blocks_unchanged(self):
        """Test that code blocks remain unchanged."""
        input_text = """This is regular text. This is another sentence.

```python
def hello():
    print("Hello world.")
    return True
```

This is more text. This is the final sentence."""
        expected = """This is regular text.\nThis is another sentence.

```python
def hello():
    print("Hello world.")
    return True
```

This is more text.\nThis is the final sentence."""
        result = process_markdown(input_text)
        assert result == expected

    def test_quoted_text_with_periods(self):
        """Test sentences with quoted text containing periods."""
        input_text = 'He said "Hello world." to everyone. She replied "How are you?" back. This is sentence three. This is sentence four. This is sentence five.'
        expected = 'He said "Hello world." to everyone.\nShe replied "How are you?" back.\nThis is sentence three.\nThis is sentence four.\nThis is sentence five.'
        result = process_markdown(input_text)
        assert result == expected