"""
Testes para detecção de MIME type e encoding com python-magic.
Testa a biblioteca mime_detector e sua integração com LocalFileDriver.
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


class TestMimeDetector:
    """Testa a biblioteca mime_detector diretamente."""

    def test_detector_singleton(self):
        """Testa padrão singleton do detector."""
        detector1 = get_mime_detector()
        detector2 = get_mime_detector()

        assert detector1 is detector2  # Mesma instância
        assert isinstance(detector1, MimeDetector)

    def test_detect_file_type_convenience(self):
        """Testa função de conveniência detect_file_type."""
        result = detect_file_type('test_pt.txt')

        assert isinstance(result, MimeDetectionResult)
        assert result.mime_type is not None
        assert result.encoding is not None

        print(f"\n✅ detect_file_type: {result.mime_type}, {result.encoding}")
        print(f"✅ Método: {result.detection_method}")
        print(f"✅ Magic disponível: {result.magic_available}")

    def test_detect_from_file_direct(self):
        """Testa detecção direta de arquivo."""
        detector = get_mime_detector()
        result = detector.detect_from_file('test_pt.txt')

        assert result.is_text or result.is_binary  # Sempre um dos dois
        assert 'text' in result.mime_type or 'application' in result.mime_type

        # Se for texto, deve ter encoding específico
        if result.is_text:
            assert result.encoding != 'binary'
            assert result.encoding in ['utf-8', 'utf-16-le', 'utf-16-be', 'windows-1252', 'ascii']

        print(f"\n✅ Arquivo detectado como: {result.mime_type}")
        print(f"✅ Encoding: {result.encoding}")
        print(f"✅ É texto: {result.is_text}")

    def test_detect_from_bytes(self):
        """Testa detecção de bytes em memória."""
        # Lê conteúdo do arquivo teste
        with open('test_pt.txt', 'rb') as f:
            content = f.read()

        detector = get_mime_detector()
        result = detector.detect_from_bytes(content, 'test_pt.txt')

        assert result.mime_type is not None
        assert result.detection_method in ['python-magic-buffer', 'fallback-bytes']

        print(f"\n✅ Bytes detectados como: {result.mime_type}")
        print(f"✅ Método: {result.detection_method}")

    def test_magic_initialization(self):
        """Testa inicialização do python-magic."""
        detector = get_mime_detector()

        # Força inicialização
        magic_works = detector._try_init_magic()

        print(f"\n✅ Magic inicializado: {magic_works}")

        if magic_works:
            assert detector._magic_mime is not None
            assert detector._magic_encoding is not None
            print("✅ Python-magic funcionando perfeitamente")
        else:
            print("ℹ️  Magic não disponível - usando fallback (isso é OK)")

        # Independente de magic funcionar, detector deve sempre funcionar
        result = detector.detect_from_file('test_pt.txt')
        assert result.mime_type is not None

    def test_fallback_robustness(self):
        """Testa que fallback funciona independente de magic."""
        detector = MimeDetector()  # Nova instância

        # Força fallback (não inicializa magic)
        detector._magic_initialized = True
        detector._magic_available = False

        result = detector.detect_from_file('test_pt.txt')

        assert result.magic_available == False
        assert result.detection_method.startswith('fallback')
        assert result.mime_type is not None
        assert result.encoding is not None

        print(f"\n✅ Fallback funcionou: {result.mime_type}, {result.encoding}")


class TestLocalFileDriverIntegration:
    """Testa integração do LocalFileDriver com mime_detector."""

    def test_driver_uses_detector(self):
        """Testa que driver usa a nova biblioteca."""
        driver = LocalFileDriver('test_pt.txt')
        info = driver.get_file_info()

        # Deve ter campos da nova biblioteca
        required_fields = [
            'mime_type', 'encoding', 'is_text', 'is_binary',
            'magic_available', 'detection_method'
        ]

        for field in required_fields:
            assert field in info, f"Campo '{field}' faltando"

        print(f"\n✅ Driver integrado - MIME: {info['mime_type']}")
        print(f"✅ Encoding: {info['encoding']}")
        print(f"✅ Método: {info['detection_method']}")
        print(f"✅ Magic: {info['magic_available']}")

    def test_driver_content_extraction(self):
        """Testa extração de conteúdo usando nova biblioteca."""
        driver = LocalFileDriver('test_pt.txt')

        info = driver.get_file_info()
        if info['is_text']:
            content = driver.get_content_as_text()

            # Validações essenciais
            assert 'configuração' in content
            assert not content.startswith('\ufeff')  # Sem BOM

            # Caracteres portugueses preservados
            portuguese_chars = ['ç', 'ã', 'é', 'ú']
            found_chars = [char for char in portuguese_chars if char in content]
            assert len(found_chars) >= 3

            print(f"\n✅ Conteúdo extraído: {repr(content[:50])}")
            print(f"✅ Caracteres portugueses: {found_chars}")

    def test_driver_backward_compatibility(self):
        """Testa que API do driver não quebrou."""
        driver = LocalFileDriver('test_pt.txt')

        # Métodos antigos devem funcionar
        assert driver.can_handle('test_pt.txt') == True
        assert driver.is_available() == True

        raw_content = driver.get_content()
        assert isinstance(raw_content, bytes)
        assert len(raw_content) > 0

        metadata = driver.get_metadata()
        assert isinstance(metadata, dict)
        assert 'size' in metadata

        print("✅ Compatibilidade mantida - todos os métodos funcionam")

    @pytest.mark.parametrize("test_file,expected_encoding", [
        ("test_utf8_puro.txt", "utf-8"),
        ("test_ascii.txt", "utf-8"),  # ASCII é subset de UTF-8
    ])
    def test_multiple_file_types(self, test_file, expected_encoding):
        """Testa detecção com múltiplos tipos de arquivo."""
        # Criar arquivo se não existir
        if not Path(test_file).exists():
            with open(test_file, 'w', encoding=expected_encoding) as f:
                f.write("configuração técnica")

        driver = LocalFileDriver(test_file)
        info = driver.get_file_info()
        content = driver.get_content_as_text()

        print(f"\n📄 {test_file}:")
        print(f"  MIME: {info['mime_type']}")
        print(f"  Encoding: {info['encoding']}")
        print(f"  Método: {info['detection_method']}")

        assert info['is_text'] == True
        assert 'configuração' in content or 'configuracao' in content
        assert not content.startswith('\ufeff')


class TestMimeDetectionComparison:
    """Compara resultados entre magic e fallback."""

    def test_consistency_between_methods(self):
        """Testa consistência entre diferentes métodos de detecção."""
        # Teste com arquivo conhecido
        file_path = 'test_pt.txt'

        # Via função de conveniência
        result1 = detect_file_type(file_path)

        # Via detector direto
        detector = get_mime_detector()
        result2 = detector.detect_from_file(file_path)

        # Via bytes
        with open(file_path, 'rb') as f:
            content = f.read()
        result3 = detect_bytes_type(content, 'test_pt.txt')

        # Todos devem detectar como texto
        assert result1.is_text
        assert result2.is_text
        assert result3.is_text

        # Encoding deve ser compatível
        encodings = {result1.encoding, result2.encoding, result3.encoding}
        print(f"\n✅ Encodings detectados: {encodings}")

        # Pelo menos um deve detectar UTF-16 ou UTF-8
        utf_encodings = {'utf-8', 'utf-16-le', 'utf-16-be', 'utf-8-sig'}
        assert len(encodings.intersection(utf_encodings)) > 0

        print(f"✅ Métodos consistentes:")
        print(f"  Arquivo: {result1.detection_method}")
        print(f"  Detector: {result2.detection_method}")
        print(f"  Bytes: {result3.detection_method}")