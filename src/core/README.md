# src/core

Abstrações e utilitários independentes de provider.

Principais componentes
- file.BaseFile
  - Lida com:
    - get_raw(head=None, permanent=False): baixa (se necessário), aplica head, retorna texto.
    - clean(): remove arquivos temporários/cache/salvos relacionados.
  - Força provedores a implementarem _download_to(dest).
- io/
  - baseobj.FileObject e wrappers tipados (Html, Pdf, Video).
  - factory.wrap_typed: detecta o tipo a partir de mimetype/filename e retorna wrapper adequado.
- folder.BaseFolder (Protocol): interface de pastas, usada por provedores.

Convenção
- Providers devem estender BaseFile para herdar comportamento de cache/download.
- Tipagem de IO é feita externamente (wrap_typed) para desacoplar provider do consumo.