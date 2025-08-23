# tests/unit/test_mime_detector.py

from src.core.content.mime_detector import MimeDetector

def test_mime_detector():
    detector = MimeDetector()
    result = detector.detect_from_file('document.pdf')
    assert result.mime_type == 'application/pdf'