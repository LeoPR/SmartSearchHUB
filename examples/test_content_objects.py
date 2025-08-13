# examples/test_content_objects.py
from __future__ import annotations
from src.api.facade import Folder
from src.providers.google_drive.config import Config
from src.core.io.html import Html

# Configuração
cfg = Config(
    auth_method="oauth",
    credentials_file="./config/credentials/client_secret_737482562292-hrpme53jvk24vs2vvucai2h5v0p2b42i.apps.googleusercontent.com.json",
    token_file="./config/credentials/client_token.json",
)
folders = []
with open("./config/docs_sources.csv", mode="r") as f:
    lines=f.readlines()
    folders = [ line.split(",") for line in lines]
    folders = [ [d,l.replace('"','')] for d,l in folders]
    folders = [ f"{d}://{l}" for d,l in folders]

FOLDER_URI = folders[0]



def test_basic_functionality():
    """Testa funcionalidade básica mantendo compatibilidade."""
    print("=== TESTE DE COMPATIBILIDADE ===")

    folder = Folder.from_uri(FOLDER_URI, config=cfg, tmp="./tmp", cache="./cache")

    print(">>> INFO:", folder.info())
    print(">>> HTMLs com método tradicional:")

    for obj in folder.list():
        if isinstance(obj, Html):
            print(f"\n- {obj.name} ({obj.mimetype})")

            # Método antigo ainda funciona
            print("  TEXTO SIMPLES (50 chars):")
            text_simple = obj.get_text_simple(head={"characters": 50})
            print(f"  '{text_simple}'")

            # Método novo usando objetos
            print("  TEXTO VIA OBJETOS (50 chars):")
            text_objects = obj.get_text(head={"characters": 50})
            print(f"  '{text_objects}'")
            break  # Só testa o primeiro


def test_content_objects():
    """Testa extração de objetos estruturados."""
    print("\n=== TESTE DE OBJETOS ESTRUTURADOS ===")

    folder = Folder.from_uri(FOLDER_URI, config=cfg, tmp="./tmp", cache="./cache")

    for obj in folder.list():
        if isinstance(obj, Html):
            print(f"\n>>> ANALISANDO: {obj.name}")

            # Extrai todos os objetos
            all_objects = obj.get_objects()

            print(f"Total de objetos extraídos: {len(all_objects)}")

            # Agrupa por tipo
            by_type = {}
            for content_obj in all_objects:
                obj_type = content_obj.object_type
                if obj_type not in by_type:
                    by_type[obj_type] = []
                by_type[obj_type].append(content_obj)

            print("\nTipos encontrados:")
            for obj_type, objects in by_type.items():
                print(f"  {obj_type}: {len(objects)} objetos")

            # Detalhes dos primeiros objetos de cada tipo
            print("\nExemplos por tipo:")

            # Textos
            if 'text' in by_type:
                texts = by_type['text'][:3]  # Primeiros 3
                print(f"\n  TEXTOS ({len(texts)} exemplos):")
                for i, text_obj in enumerate(texts):
                    content = text_obj.get_content()[:100] + "..." if len(
                        text_obj.get_content()) > 100 else text_obj.get_content()
                    print(f"    {i + 1}. '{content}'")

            # Headings
            if 'heading' in by_type:
                headings = by_type['heading']
                print(f"\n  CABEÇALHOS ({len(headings)} encontrados):")
                for heading in headings:
                    print(f"    H{heading.level}: '{heading.content}'")

            # Links
            if 'link' in by_type:
                links = by_type['link'][:5]  # Primeiros 5
                print(f"\n  LINKS ({len(links)} exemplos):")
                for link in links:
                    url = link.get_url() or "[sem URL]"
                    print(f"    '{link.text}' -> {url}")

            # Imagens
            if 'image' in by_type:
                images = by_type['image']
                print(f"\n  IMAGENS ({len(images)} encontradas):")
                for img in images:
                    alt = img.alt_text or "[sem alt]"
                    src = img.source.url if hasattr(img.source, 'url') else "[sem src]"
                    print(f"    Alt: '{alt}' | Src: {src[:50]}...")

            # Scripts
            if 'code' in by_type:
                scripts = [s for s in by_type['code'] if hasattr(s, 'script_type')]
                if scripts:
                    print(f"\n  SCRIPTS ({len(scripts)} encontrados):")
                    for script in scripts[:3]:  # Primeiros 3
                        if script.is_external:
                            print(f"    Externo: {script.src_url}")
                        else:
                            lines = len(script.content.splitlines())
                            print(f"    Inline: {lines} linhas, tipo {script.script_type}")

            # Estilos
            if 'style' in by_type:
                styles = by_type['style']
                print(f"\n  ESTILOS ({len(styles)} encontrados):")
                for style in styles[:3]:  # Primeiros 3
                    if style.is_inline:
                        print(f"    Inline: {style.content[:50]}...")
                    else:
                        rules = style.get_rule_count()
                        print(f"    Bloco: {rules} regras CSS")

            # Tabelas
            if 'table' in by_type:
                tables = by_type['table']
                print(f"\n  TABELAS ({len(tables)} encontradas):")
                for table in tables:
                    rows = table.get_row_count()
                    cols = table.get_column_count()
                    caption = table.caption or "[sem título]"
                    print(f"    {caption}: {rows}x{cols}")

            break  # Só analisa o primeiro HTML


def test_specific_extractions():
    """Testa métodos específicos de extração."""
    print("\n=== TESTE DE MÉTODOS ESPECÍFICOS ===")

    folder = Folder.from_uri(FOLDER_URI, config=cfg, tmp="./tmp", cache="./cache")

    for obj in folder.list():
        if isinstance(obj, Html):
            print(f"\n>>> MÉTODOS ESPECÍFICOS: {obj.name}")

            # Links
            links = obj.get_links()
            print(f"\nLinks encontrados: {len(links)}")
            for link in links[:3]:
                print(f"  - '{link.text}' -> {link.get_url()}")
                if link.is_external():
                    print(f"    (externo)")
                else:
                    print(f"    (interno)")

            # Imagens
            images = obj.get_images()
            print(f"\nImagens encontradas: {len(images)}")
            for img in images[:3]:
                print(f"  - Alt: '{img.alt_text}'")
                print(f"    Disponível: {img.is_available()}")

            # Cabeçalhos
            headings = obj.get_headings()
            print(f"\nCabeçalhos encontrados: {len(headings)}")
            for heading in headings[:5]:
                print(f"  - H{heading.level}: '{heading.content}'")

            # Scripts
            scripts = obj.get_scripts()
            print(f"\nScripts encontrados: {len(scripts)}")
            for script in scripts[:3]:
                if script.is_external:
                    print(f"  - Externo: {script.src_url}")
                else:
                    funcs = script.get_functions()
                    imports = script.get_imports()
                    print(f"  - Inline: {len(script.content)} chars")
                    if funcs:
                        print(f"    Funções: {', '.join(funcs[:3])}")
                    if imports:
                        print(f"    Imports: {', '.join(imports[:3])}")

            break


def test_filtering_and_queries():
    """Testa filtragem e consultas nos objetos."""
    print("\n=== TESTE DE FILTRAGEM ===")

    folder = Folder.from_uri(FOLDER_URI, config=cfg, tmp="./tmp", cache="./cache")

    for obj in folder.list():
        if isinstance(obj, Html):
            print(f"\n>>> FILTROS: {obj.name}")

            # Só textos
            texts = obj.get_objects(types=['text'])
            print(f"Só textos: {len(texts)} objetos")

            # Só links externos
            all_links = obj.get_links()
            external_links = [link for link in all_links if link.is_external()]
            print(f"Links externos: {len(external_links)}/{len(all_links)}")

            # Cabeçalhos de nível superior (H1, H2)
            headings = obj.get_headings()
            top_headings = [h for h in headings if h.is_top_level()]
            print(f"Cabeçalhos principais: {len(top_headings)}/{len(headings)}")

            # Imagens sem alt-text
            images = obj.get_images()
            no_alt = [img for img in images if not img.alt_text.strip()]
            print(f"Imagens sem alt: {len(no_alt)}/{len(images)}")

            # Scripts que usam jQuery
            scripts = obj.get_scripts()
            jquery_scripts = [s for s in scripts if s.has_jquery()]
            print(f"Scripts com jQuery: {len(jquery_scripts)}/{len(scripts)}")

            break


def test_advanced_features():
    """Testa recursos avançados."""
    print("\n=== TESTE DE RECURSOS AVANÇADOS ===")

    folder = Folder.from_uri(FOLDER_URI, config=cfg, tmp="./tmp", cache="./cache")

    for obj in folder.list():
        if isinstance(obj, Html):
            print(f"\n>>> RECURSOS AVANÇADOS: {obj.name}")

            # Testa com base_url para resolver URLs relativas
            base_url = "https://example.com/"
            objects_with_base = obj.get_objects(base_url=base_url)

            # Análise hierárquica
            headings = obj.get_headings()
            if headings:
                print("\nEstrutura hierárquica:")
                for heading in headings:
                    indent = "  " * (heading.level - 1)
                    print(f"{indent}H{heading.level}: {heading.content}")

            # Metadata dos objetos
            all_objects = obj.get_objects()
            if all_objects:
                print(f"\nMetadata do primeiro objeto ({all_objects[0].object_type}):")
                metadata = all_objects[0].to_dict()
                for key, value in metadata.items():
                    if value:
                        print(f"  {key}: {value}")

            # Posicionamento no documento
            positioned_objects = [o for o in all_objects if o.position and o.position.xpath]
            print(f"\nObjetos com posição XPath: {len(positioned_objects)}")
            for obj_with_pos in positioned_objects[:3]:
                print(f"  {obj_with_pos.object_type}: {obj_with_pos.position.xpath}")

            break


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_content_objects()
        test_specific_extractions()
        test_filtering_and_queries()
        test_advanced_features()

        print("\n=== TODOS OS TESTES CONCLUÍDOS ===")

    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback

        traceback.print_exc()