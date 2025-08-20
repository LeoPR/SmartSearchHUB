import pytest
from unittest.mock import Mock, patch
from src.providers.google_drive.client import DriveClient
from src.providers.google_drive.config import Config


class TestGDriveIntegration:
    @patch('src.providers.google_drive.client.build')
    def test_list_children_with_mock(self, mock_build):
        """Testa listagem usando mock do Google API."""
        # Mock da resposta da API
        mock_service = Mock()
        mock_files = Mock()
        mock_list = Mock()

        mock_list.execute.return_value = {
            'files': [
                {'id': '123', 'name': 'test.html', 'mimeType': 'text/html'},
                {'id': '456', 'name': 'doc.pdf', 'mimeType': 'application/pdf'}
            ]
        }
        mock_files.list.return_value = mock_list
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service

        # Teste
        config = Mock()
        config.build_credentials.return_value = Mock()

        client = DriveClient(config)
        result = client.list_children("folder123")

        assert len(result) == 2
        assert result[0]['name'] == 'test.html'