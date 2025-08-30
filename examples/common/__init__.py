# examples/common/__init__.py
"""
Utilitários comuns para examples do SmartSearchHUB.

Este módulo fornece componentes reutilizáveis para todos os examples:
- AuthManager: Coordenador de autenticação
- ContentExtractor: Extração de conteúdo genérica
- ConfigHelper: Helpers de configuração
"""

from .auth_manager import AuthManager
from .content_extractor import ContentExtractor

__all__ = ['AuthManager', 'ContentExtractor']