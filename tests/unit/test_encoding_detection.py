# tests/unit/test_encoding_detection.py
"""
Testes consolidados para detecção de MIME type e encoding.
Substitui test_mime_detector.py e test_magic_detection.py.
"""

import pytest
from pathlib import Path
from src.core.content.drivers import LocalFileDriver
from src.core.content.mime_detector import (
    get_mime_detector,
    detect_file_type,
    detect_bytes_type,
    MimeDetector,
    MimeDetectionResult
)


class TestMimeDetectionBasic:
    """Testes básicos de detecção de MIME type."""

    def test_detect_text_files(self, sample_text_files):
        """Testa detecção de arquivos de texto."""
        detector = get_mime_detector()

        # Testa arquivo UTF-8
        result = detector.detect_from_file(sample_text_files['utf8'])
        assert result.is_text
        assert result.mime_type.startswith('text/')
        assert result.encoding in ['utf-8', 'ascii']  # ASCII é subset de UTF-8

        # Testa arquivo ASCII
        result = detector.detect_from_file(sample_text_files['ascii'])
        assert result.is_text
        assert result.mime_type.startswith('text/')

    def test_detect_binary_files(self, sample_binary_files):
        """Testa detecção de arquivos binários."""
        detector = get_mime_detector()

        # Testa PDF
        result = detector.detect_from_file(sample_binary_files['pdf'])
        assert result.is_binary
        assert 'pdf' in result.mime_type.lower()

        # Testa imagens
        for img_type in ['jpg', 'png']:
            result = detector.detect_from_file(sample_binary_files[img_type])
            assert result.is_binary
            assert 'image' in result.mime_type.lower()

    def test_detect_from_bytes(self, sample_text_files):
        """Testa detecção a partir de bytes."""
        # Lê arquivo como bytes
        with open(sample_text_files['utf8'], 'rb') as f:
            content = f.read()

        result = detect_bytes_type(content, 'test.txt')
        assert result.is_text
        assert result.mime_type.startswith('text/')

    def test_convenience_functions(self, sample_text_files):
        """Testa funções de conveniência."""
        # detect_file_type
        result = detect_file_type(sample_text_files['utf8'])
        assert isinstance(result, MimeDetectionResult)
        assert result.is_text

        # Deve sempre retornar algo válido
        assert result.mime_type is not None
        assert result.encoding is not None

    def test_detector_singleton(self):
        """Testa padrão singleton do detector."""
        detector1 = get_mime_detector()
        detector2 = get_mime_detector()

        assert detector1 is detector2  # Mesma instância
        assert isinstance(detector1, MimeDetector)


class TestMimeDetectionIntegration:
    """Testes de integração com LocalFileDriver."""

    def test_driver_uses_detector(self, sample_text_files):
        """Testa que LocalFileDriver usa a biblioteca de detecção."""
        driver = LocalFileDriver(sample_text_files['utf8'])

        # get_file_info deve usar o detector
        info = driver.get_file_info()

        # Campos obrigatórios da detecção
        required_fields = ['mime_type', 'encoding', 'is_text', 'is_binary']
        for field in required_fields:
            assert field in info

        # Se é texto, deve conseguir ler
        if info['is_text']:
            content = driver.get_content_as_text()
            assert isinstance(content, str)
            assert len(content) > 0

    def test_driver_handles_binary(self, sample_binary_files):
        """Testa que driver lida corretamente com arquivos binários."""
        driver = LocalFileDriver(sample_binary_files['pdf'])

        info = driver.get_file_info()
        assert info['is_binary'] == True
        assert info['is_text'] == False

        # get_content deve retornar bytes
        content = driver.get_content()
        assert isinstance(content, bytes)
        assert len(content) > 0

    def test_encoding_detection_accuracy(self, sample_text_files):
        """Testa precisão da detecção de encoding."""
        # UTF-8 normal
        driver_utf8 = LocalFileDriver(sample_text_files['utf8'])
        info_utf8 = driver_utf8.get_file_info()
        content_utf8 = driver_utf8.get_content_as_text()

        assert "configuração" in content_utf8
        assert not content_utf8.startswith('\ufeff')

        # UTF-8 com BOM
        driver_bom = LocalFileDriver(sample_text_files['utf8_bom'])
        info_bom = driver_bom.get_file_info()
        content_bom = driver_bom.get_content_as_text()

        assert "configuração" in content_bom
        # Driver deve remover BOM automaticamente
        assert not content_bom.startswith('\ufeff')


class TestMimeDetectionFallback:
    """Testa comportamento de fallback quando python-magic não está disponível."""

    def test_fallback_behavior(self, sample_text_files):
        """Testa que fallback funciona independente de magic."""
        # Cria detector novo (não singleton)
        detector = MimeDetector()

        # Força fallback
        detector._magic_initialized = True
        detector._magic_available = False

        result = detector.detect_from_file(sample_text_files['utf8'])

        # Fallback deve funcionar
        assert result.magic_available == False
        assert result.detection_method.startswith('fallback')
        assert result.mime_type is not None
        assert result.encoding is not None

    def test_detector_always_works(self, sample_text_files):
        """Testa que detector sempre retorna algo válido."""
        detector = get_mime_detector()

        result = detector.detect_from_file(sample_text_files['utf8'])

        # Independente de magic funcionar ou não
        assert result is not None
        assert hasattr(result, 'mime_type')
        assert hasattr(result, 'encoding')
        assert hasattr(result, 'is_text')
        assert hasattr(result, 'is_binary')

    def test_missing_file_handling(self, tmp_path):
        """Testa tratamento de arquivo inexistente."""
        detector = get_mime_detector()
        missing_file = tmp_path / "nao_existe.txt"

        with pytest.raises(FileNotFoundError):
            detector.detect_from_file(missing_file)


class TestMimeDetectionResults:
    """Testa estrutura e métodos do MimeDetectionResult."""

    def test_result_structure(self, sample_text_files):
        """Testa estrutura do resultado."""
        result = detect_file_type(sample_text_files['utf8'])

        # Propriedades obrigatórias
        assert hasattr(result, 'mime_type')
        assert hasattr(result, 'encoding')
        assert hasattr(result, 'is_text')
        assert hasattr(result, 'is_binary')
        assert hasattr(result, 'magic_available')
        assert hasattr(result, 'detection_method')

    def test_result_to_dict(self, sample_text_files):
        """Testa serialização para dict."""
        result = detect_file_type(sample_text_files['utf8'])
        data = result.to_dict()

        assert isinstance(data, dict)
        assert 'mime_type' in data
        assert 'encoding' in data
        assert 'is_text' in data
        assert 'is_binary' in data

    def test_text_binary_consistency(self, sample_text_files, sample_binary_files):
        """Testa consistência entre is_text e is_binary."""
        # Arquivo de texto
        text_result = detect_file_type(sample_text_files['utf8'])
        assert text_result.is_text != text_result.is_binary  # Mutuamente exclusivos

        # Arquivo binário
        binary_result = detect_file_type(sample_binary_files['pdf'])
        assert binary_result.is_text != binary_result.is_binary  # Mutuamente exclusivos