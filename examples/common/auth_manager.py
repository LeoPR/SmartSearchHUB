# examples/common/auth_manager.py
"""
AuthManager - Coordenador centralizado de autenticação para SmartSearchHUB.

Características:
- Detecta automaticamente configurações existentes
- Suporte a flags interactive/save_tokens
- Compatível com estrutura atual do projeto
- Warnings inteligentes antes de abrir navegador
- Fallbacks robustos
"""

from __future__ import annotations
import os
import json
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, Union

# Imports condicionais para evitar dependências quando não usadas
try:
    from src.providers.google_drive.config import Config as GDriveConfig
    from src.providers.config import Config as UnifiedConfig
except ImportError:
    GDriveConfig = None
    UnifiedConfig = None


class AuthManager:
    """
    Coordenador centralizado de autenticação.

    Exemplos de uso:

    # Modo padrão (interativo se necessário)
    auth = AuthManager()
    config = auth.get_gdrive_config()

    # Modo não-interativo (só arquivos existentes)
    auth = AuthManager(interactive=False)
    config = auth.get_gdrive_config()  # Erro se não existir token

    # Personalizado
    auth = AuthManager(interactive=True, save_tokens=True)
    config = auth.get_gdrive_config("./custom/credentials.json")
    """

    def __init__(self,
                 interactive: bool = True,
                 save_tokens: bool = True,
                 config_dir: Optional[Union[str, Path]] = None):
        """
        Inicializa o AuthManager.

        Args:
            interactive: Se True, abre navegador quando necessário. Se False, só usa arquivos existentes.
            save_tokens: Se True, salva tokens para reuso futuro
            config_dir: Diretório base das configurações (default: ./config)
        """
        self.interactive = interactive
        self.save_tokens = save_tokens
        self.config_dir = Path(config_dir or "./config").resolve()

        # Paths padrão
        self.gdrive_auth_file = self.config_dir / "gdrive_auth.json"
        self.credentials_dir = self.config_dir / "credentials"

        # Garante que diretórios existem
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

    def get_gdrive_config(self,
                          credentials_file: Optional[str] = None,
                          force_method: Optional[str] = None) -> Any:
        """
        Obtém configuração válida para Google Drive.

        Args:
            credentials_file: Caminho específico para credenciais (opcional)
            force_method: Força método específico: 'oauth' ou 'service_account' (opcional)

        Returns:
            Objeto Config configurado e válido

        Raises:
            FileNotFoundError: Se interactive=False e arquivos necessários não existem
            ValueError: Se configuração é inválida
        """
        if not GDriveConfig or not UnifiedConfig:
            raise ImportError(
                "Módulos do Google Drive não encontrados. "
                "Verifique se as dependências estão instaladas."
            )

        print("🔐 Configurando autenticação Google Drive...")

        # 1. Tenta carregar configuração existente
        config_data = self._load_gdrive_config()

        # 2. Sobrescreve com parâmetros se fornecidos
        if credentials_file:
            config_data["credentials_file"] = credentials_file
        if force_method:
            config_data["auth_method"] = force_method

        # 3. Valida configuração
        validated_config = self._validate_gdrive_config(config_data)

        # 4. Verifica se precisa de interação
        needs_interaction = self._check_gdrive_interaction_needed(validated_config)

        if needs_interaction and not self.interactive:
            raise FileNotFoundError(
                f"Configuração requer interação (navegador), mas interactive=False. "
                f"Para resolver:\n"
                f"1. Execute com AuthManager(interactive=True), ou\n"
                f"2. Configure tokens manualmente em {validated_config.get('token_file', 'token file')}"
            )

        if needs_interaction and self.interactive:
            print(f"⚠️  ATENÇÃO: Será necessário abrir o navegador para autenticação.")
            print(f"💡 Para evitar isso no futuro, mantenha os arquivos de token.")

            if not self._confirm_browser_interaction():
                raise InterruptedError("Operação cancelada pelo usuário.")

        # 5. Cria e retorna configuração
        try:
            gdrive_config = GDriveConfig(
                auth_method=validated_config["auth_method"],
                credentials_file=validated_config["credentials_file"],
                token_file=validated_config.get("token_file"),
                scopes=tuple(validated_config.get("scopes", ["https://www.googleapis.com/auth/drive.readonly"]))
            )

            # Testa se consegue obter credenciais
            creds = gdrive_config.build_credentials()
            print("✅ Autenticação Google Drive bem-sucedida!")

            return gdrive_config

        except Exception as e:
            print(f"❌ Erro na autenticação Google Drive: {e}")
            raise

    def _load_gdrive_config(self) -> Dict[str, Any]:
        """Carrega configuração do Google Drive de várias fontes."""
        config_data = {}

        # 1. Tenta arquivo de configuração unificado
        if self.gdrive_auth_file.exists():
            try:
                with open(self.gdrive_auth_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    config_data.update(data)
                    print(f"📄 Configuração carregada de: {self.gdrive_auth_file}")
            except Exception as e:
                print(f"⚠️  Erro ao carregar {self.gdrive_auth_file}: {e}")

        # 2. Fallbacks de variáveis de ambiente
        env_service_account = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if env_service_account and not config_data.get("credentials_file"):
            config_data.update({
                "auth_method": "service_account",
                "credentials_file": env_service_account
            })
            print(f"🌍 Service account detectado via GOOGLE_APPLICATION_CREDENTIALS")

        # 3. Detecta arquivos de credenciais na pasta credentials/
        if not config_data.get("credentials_file"):
            detected_file = self._detect_credentials_file()
            if detected_file:
                config_data["credentials_file"] = str(detected_file)
                # Determina método baseado no nome do arquivo
                if "service" in detected_file.name.lower() or "sa-" in detected_file.name.lower():
                    config_data["auth_method"] = "service_account"
                else:
                    config_data["auth_method"] = "oauth"
                print(f"🔍 Credenciais detectadas: {detected_file.name}")

        return config_data

    def _detect_credentials_file(self) -> Optional[Path]:
        """Detecta arquivo de credenciais na pasta credentials/."""
        if not self.credentials_dir.exists():
            return None

        # Padrões de busca (ordem de preferência)
        patterns = [
            "*service*account*.json",  # Service account
            "sa-*.json",  # Service account (padrão projeto)
            "client_secret*.json",  # OAuth client
            "*.json"  # Qualquer JSON
        ]

        for pattern in patterns:
            files = list(self.credentials_dir.glob(pattern))
            # Ignora arquivos de exemplo
            real_files = [f for f in files if "example" not in f.name.lower()]
            if real_files:
                return real_files[0]  # Retorna primeiro encontrado

        return None

    def _validate_gdrive_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e normaliza configuração do Google Drive."""
        validated = config_data.copy()

        # Método de autenticação
        method = validated.get("auth_method", "oauth").lower().replace("-", "_")
        if method not in ["oauth", "service_account"]:
            raise ValueError(f"Método de autenticação inválido: {method}")
        validated["auth_method"] = method

        # Arquivo de credenciais
        cred_file = validated.get("credentials_file")
        if not cred_file:
            raise FileNotFoundError(
                f"Arquivo de credenciais não encontrado. Configure:\n"
                f"1. Variável GOOGLE_APPLICATION_CREDENTIALS, ou\n"
                f"2. Arquivo {self.gdrive_auth_file}, ou\n"
                f"3. Credenciais em {self.credentials_dir}/"
            )

        cred_path = Path(cred_file).expanduser().resolve()
        if not cred_path.exists():
            raise FileNotFoundError(f"Arquivo de credenciais não existe: {cred_path}")
        validated["credentials_file"] = str(cred_path)

        # Token file (só para OAuth)
        if method == "oauth":
            token_file = validated.get("token_file")
            if not token_file:
                # Gera nome baseado no arquivo de credenciais
                token_name = f"token_{cred_path.stem}.json"
                token_file = str(self.credentials_dir / token_name)
            validated["token_file"] = token_file

        # Scopes
        if "scopes" not in validated:
            validated["scopes"] = ["https://www.googleapis.com/auth/drive.readonly"]

        return validated

    def _check_gdrive_interaction_needed(self, config: Dict[str, Any]) -> bool:
        """Verifica se será necessária interação do usuário (navegador)."""
        method = config["auth_method"]

        if method == "service_account":
            return False  # Service account não precisa interação

        if method == "oauth":
            token_file = config.get("token_file")
            if not token_file:
                return True  # Sem token file, precisará de interação

            token_path = Path(token_file).expanduser()
            if not token_path.exists():
                return True  # Token não existe, precisará de interação

            # TODO: Verificar se token é válido/não expirado
            # Por enquanto, assume que se existe, é válido
            return False

        return True  # Por segurança, assume que precisa

    def _confirm_browser_interaction(self) -> bool:
        """Confirma se usuário aceita abrir navegador."""
        try:
            response = input("Pressione ENTER para continuar ou 'n' para cancelar: ").strip().lower()
            return response != 'n'
        except (KeyboardInterrupt, EOFError):
            return False

    def get_url_headers(self,
                        url: Optional[str] = None,
                        auth_file: Optional[str] = None,
                        **extra_headers) -> Dict[str, str]:
        """
        Obtém headers para autenticação em URLs.

        Args:
            url: URL alvo (usado para detectar configuração específica)
            auth_file: Arquivo específico de autenticação
            **extra_headers: Headers adicionais

        Returns:
            Dicionário de headers para requests
        """
        headers = {
            'User-Agent': 'SmartSearchHUB/1.0'
        }

        # TODO: Implementar lógica similar ao GDrive para URLs
        # Por enquanto, suporte básico

        # Headers extras
        headers.update(extra_headers)

        # Variável de ambiente para headers extras
        extra_json = os.getenv("URL_EXTRA_HEADERS")
        if extra_json:
            try:
                extra = json.loads(extra_json)
                if isinstance(extra, dict):
                    headers.update({str(k): str(v) for k, v in extra.items()})
            except json.JSONDecodeError:
                warnings.warn("URL_EXTRA_HEADERS inválido, ignorando.")

        return headers

    def create_example_configs(self) -> None:
        """Cria arquivos de configuração de exemplo."""
        print("📝 Criando arquivos de configuração de exemplo...")

        # Exemplo gdrive_auth.json
        gdrive_example = {
            "auth_method": "oauth",
            "credentials_file": "./config/credentials/client_secret_EXAMPLE.json",
            "token_file": "./config/credentials/client_token.json",
            "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
        }

        example_file = self.config_dir / "gdrive_auth.example.json"
        with open(example_file, 'w', encoding='utf-8') as f:
            json.dump(gdrive_example, f, indent=2)
        print(f"✅ Criado: {example_file}")

        # Instruções
        instructions = self.config_dir / "AUTH_SETUP.md"
        with open(instructions, 'w', encoding='utf-8') as f:
            f.write("""# Configuração de Autenticação

## Google Drive

1. **OAuth (Recomendado para desenvolvimento)**:
   - Baixe `client_secret.json` do Google Console
   - Salve em `./config/credentials/`
   - Copie `gdrive_auth.example.json` para `gdrive_auth.json`
   - Ajuste o caminho do `credentials_file`

2. **Service Account (Para produção)**:
   - Baixe JSON da service account
   - Salve em `./config/credentials/sa-service-account.json`
   - Configure `gdrive_auth.json` com `auth_method: "service_account"`

## Exemplo de uso:

```python
from examples.common.auth_manager import AuthManager

auth = AuthManager(interactive=True)
config = auth.get_gdrive_config()
```
""")
        print(f"✅ Criado: {instructions}")


def quick_test():
    """Teste rápido do AuthManager."""
    print("🧪 Teste rápido do AuthManager...")

    try:
        auth = AuthManager(interactive=False)
        print(f"Config dir: {auth.config_dir}")

        # Tenta detectar configurações
        config_data = auth._load_gdrive_config()
        print(f"Configurações detectadas: {list(config_data.keys())}")

        if not config_data:
            print("⚠️  Nenhuma configuração encontrada.")
            print("💡 Execute create_example_configs() para criar templates.")

    except Exception as e:
        print(f"❌ Erro no teste: {e}")


if __name__ == "__main__":
    # Teste quando executado diretamente
    quick_test()

    # Oferece criar configs de exemplo
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "create-examples":
        auth = AuthManager()
        auth.create_example_configs()