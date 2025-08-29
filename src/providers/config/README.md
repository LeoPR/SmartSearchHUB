# src/providers/config

Carregador de configuração de provedores.

- Exporta Config (utilizada em examples e na fachada) que:
  - Lê um arquivo JSON (ex.: ./config/gdrive_auth.json).
  - Resolve e instancia a Config do provider correspondente (ex.: src/providers/google_drive/config.py).
- É a forma recomendada de injetar configuração/autenticação no framework.

Uso
```python
from src.providers.config import Config
cfg = Config(file="./config/gdrive_auth.json")
```