import pytest
from src.core.content.text import TextObject, HeadingObject
from src.core.content.link import LinkObject, UrlObject
from src.core.content.media import ImageObject
from src.core.content.structure import TableObject, ListObject


class TestContentObjects:
    def test_text_object_creation(self):
        """Testa criação de objeto de texto."""
        text_obj = TextObject(content="Teste de conteúdo")
        assert text_obj.get_content() == "Teste de conteúdo"
        assert text_obj.object_type == "text"
        assert not text_obj.is_empty()

    def test_heading_object_levels(self):
        """Testa níveis de cabeçalhos."""
        h1 = HeadingObject(content="Título", level=1)
        h3 = HeadingObject(content="Subtítulo", level=3)

        assert h1.is_top_level()
        assert not h3.is_top_level()
        assert h1.to_markdown() == "# Título"
        assert h3.to_markdown() == "### Subtítulo"

    def test_link_object_types(self):
        """Testa diferentes tipos de links."""
        # Link externo
        external = LinkObject.create_from_url("Google", "https://google.com")
        assert external.is_external()
        assert not external.is_internal_anchor()

        # Link interno
        internal = LinkObject.create_anchor("Seção", "intro")
        assert internal.is_internal_anchor()
        assert not internal.is_external()

    def test_table_object_operations(self):
        """Testa operações de tabela."""
        table = TableObject(headers=["Nome", "Idade"])
        table.add_row(["João", "30"])
        table.add_row(["Maria", "25"])

        assert table.get_row_count() == 2
        assert table.get_column_count() == 2
        assert table.get_cell(0, 0) == "João"

        # Testa conversão para dict
        dict_data = table.to_dict_list()
        assert len(dict_data) == 2
        assert dict_data[0]["Nome"] == "João"