# tests/unit/test_encoding_compatibility.py
"""
Testes de compatibilidade de encoding com caracteres portugueses.
"""
import pytest
from pathlib import Path
from src.core.content.drivers import LocalFileDriver


class TestEncodingCompatibility:
    """Testes robustos com caracteres portugueses reais."""

    def test_utf8_portuguese(self, tmp_path):
        """Testa leitura de arquivo UTF-8 com acentos portugueses."""
        content = "configuração técnica açúcar não coração"
        test_file = tmp_path / "test_utf8.txt"
        test_file.write_text(content, encoding='utf-8')

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text(encoding='utf-8')

        # Verifica caracteres específicos
        assert "configuração" in result
        assert "técnica" in result
        assert "açúcar" in result
        assert "não" in result
        assert "coração" in result

    def test_windows1252_fallback(self, tmp_path):
        """Simula arquivo Windows-1252 e testa fallback."""
        # Conteúdo em Windows-1252 (bytes específicos para acentos)
        content_1252 = "configura\xe7\xe3o t\xe9cnica a\xe7\xfacar n\xe3o cora\xe7\xe3o"
        test_file = tmp_path / "test_1252.txt"
        test_file.write_bytes(content_1252.encode('latin1'))

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text(encoding='windows-1252')

        # Deve conseguir ler os caracteres especiais
        assert "ção" in result  # de "configuração"
        assert "não" in result
        assert "técnica" in result

    def test_auto_detection(self, tmp_path):
        """Testa detecção automática de encoding."""
        content = "configuração técnica"
        test_file = tmp_path / "test_auto.txt"
        test_file.write_text(content, encoding='utf-8')

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text(encoding='auto')

        # Deve detectar UTF-8 e ler corretamente
        assert "configuração" in result
        assert "técnica" in result
        assert not result.startswith('\ufeff')  # Sem BOM

    def test_bom_removal(self, tmp_path):
        """Testa remoção de BOM (Byte Order Mark)."""
        content = "configuração"
        test_file = tmp_path / "test_bom.txt"

        # Escreve com BOM UTF-8
        test_file.write_text(content, encoding='utf-8-sig')

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text()

        # BOM deve ser removido automaticamente
        assert not result.startswith('\ufeff')
        assert result.startswith('configuração')

    def test_mixed_characters(self, tmp_path):
        """Testa mistura de caracteres ASCII e acentuados."""
        content = "config ASCII + configuração UTF-8 + símbolos: € £ ¥"
        test_file = tmp_path / "test_mixed.txt"
        test_file.write_text(content, encoding='utf-8')

        driver = LocalFileDriver(test_file)
        result = driver.get_content_as_text()

        # Deve preservar tudo
        assert "config ASCII" in result
        assert "configuração UTF-8" in result
        assert "€" in result or "EUR" in str(result.encode('ascii', errors='replace'))