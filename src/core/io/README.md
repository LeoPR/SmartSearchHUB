# src/core/io

Wrappers tipados sobre arquivos base (ex.: GDriveFile):
- baseobj.FileObject: wrapper genérico com delegação (get_raw/clean).
- html.Html, pdf.Pdf, video.Video: especializações simples de exemplo.
- factory.wrap_typed(base_file): retorna o wrapper apropriado com base no mimetype/nome.

Uso
```python
from src.core.io.factory import wrap_typed
typed = wrap_typed(base_file)  # retorna Html/Pdf/Video/FileObject
text = typed.get_raw(head={"lines": 20, "characters": 80})
```