# src/core/content/structure.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Union
from .base import ContentObject, ContainerObject, ObjectType


@dataclass
class TableObject(ContainerObject):
    """Objeto para tabelas."""

    caption: Optional[str] = None
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)

    object_type: str = ObjectType.TABLE

    def get_content(self) -> str:
        """Retorna representação textual da tabela."""
        lines = []

        if self.caption:
            lines.append(f"[TABELA: {self.caption}]")
        else:
            lines.append("[TABELA]")

        # Headers
        if self.headers:
            lines.append(" | ".join(self.headers))
            lines.append("-" * len(" | ".join(self.headers)))

        # Rows
        for row in self.rows:
            lines.append(" | ".join(str(cell) for cell in row))

        lines.append("[/TABELA]")
        return "\n".join(lines)

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'caption': self.caption,
            'headers': self.headers,
            'rows': self.rows,
            'dimensions': (len(self.rows), len(self.headers) if self.headers else 0)
        }

    def add_header(self, header: str) -> None:
        """Adiciona uma coluna ao cabeçalho."""
        self.headers.append(header)

    def add_row(self, row: List[str]) -> None:
        """Adiciona uma linha à tabela."""
        self.rows.append(row)

    def get_cell(self, row_idx: int, col_idx: int) -> Optional[str]:
        """Obtém conteúdo de uma célula específica."""
        try:
            return self.rows[row_idx][col_idx]
        except (IndexError, TypeError):
            return None

    def set_cell(self, row_idx: int, col_idx: int, value: str) -> None:
        """Define conteúdo de uma célula específica."""
        # Garante que existam linhas suficientes
        while len(self.rows) <= row_idx:
            self.rows.append([])

        # Garante que a linha tenha colunas suficientes
        while len(self.rows[row_idx]) <= col_idx:
            self.rows[row_idx].append("")

        self.rows[row_idx][col_idx] = value

    def get_column_count(self) -> int:
        """Retorna número de colunas."""
        if self.headers:
            return len(self.headers)
        elif self.rows:
            return max(len(row) for row in self.rows) if self.rows else 0
        return 0

    def get_row_count(self) -> int:
        """Retorna número de linhas (sem contar headers)."""
        return len(self.rows)

    def to_dict_list(self) -> List[Dict[str, str]]:
        """Converte tabela para lista de dicionários."""
        if not self.headers:
            return []

        result = []
        for row in self.rows:
            row_dict = {}
            for i, header in enumerate(self.headers):
                value = row[i] if i < len(row) else ""
                row_dict[header] = value
            result.append(row_dict)

        return result

    def to_csv(self, delimiter: str = ",") -> str:
        """Converte tabela para formato CSV."""
        lines = []

        if self.headers:
            lines.append(delimiter.join(self.headers))

        for row in self.rows:
            # Escapa valores que contenham o delimitador
            escaped_row = []
            for cell in row:
                cell_str = str(cell)
                if delimiter in cell_str or '"' in cell_str:
                    cell_str = f'"{cell_str.replace('"', '""')}"'
                escaped_row.append(cell_str)
            lines.append(delimiter.join(escaped_row))

        return "\n".join(lines)


@dataclass
class ListObject(ContainerObject):
    """Objeto para listas (ul, ol)."""

    list_type: str = "unordered"  # "ordered" ou "unordered"
    start_number: int = 1  # Para listas ordenadas

    object_type: str = ObjectType.LIST

    def get_content(self) -> str:
        """Retorna representação textual da lista."""
        lines = []

        for i, child in enumerate(self.children):
            if isinstance(child, ListItemObject):
                if self.list_type == "ordered":
                    marker = f"{self.start_number + i}. "
                else:
                    marker = "• "

                # Primeira linha do item
                item_lines = child.get_content().split('\n')
                if item_lines:
                    lines.append(f"{marker}{item_lines[0]}")
                    # Linhas adicionais com indentação
                    for line in item_lines[1:]:
                        lines.append(f"   {line}")
            else:
                # Item não é ListItemObject, adiciona diretamente
                lines.append(f"• {child.get_content()}")

        return "\n".join(lines)

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'list_type': self.list_type,
            'start_number': self.start_number,
            'item_count': len(self.children)
        }

    def add_item(self, item: Union[str, ListItemObject]) -> None:
        """Adiciona um item à lista."""
        if isinstance(item, str):
            item = ListItemObject(content=item)
        self.add_child(item)

    def get_items(self) -> List[ListItemObject]:
        """Retorna apenas os itens que são ListItemObject."""
        return [child for child in self.children if isinstance(child, ListItemObject)]

    def is_ordered(self) -> bool:
        """Verifica se a lista é ordenada."""
        return self.list_type == "ordered"

    def set_ordered(self, ordered: bool = True, start: int = 1) -> None:
        """Define se a lista é ordenada."""
        self.list_type = "ordered" if ordered else "unordered"
        self.start_number = start if ordered else 1


@dataclass
class ListItemObject(ContentObject):
    """Objeto para itens de lista (li)."""

    content: str = ""

    object_type: str = ObjectType.LIST_ITEM

    def get_content(self) -> str:
        """Retorna o conteúdo do item."""
        # Se tem filhos, concatena com o conteúdo próprio
        if self.children:
            child_content = "\n".join(child.get_content() for child in self.children)
            if self.content:
                return f"{self.content}\n{child_content}"
            return child_content
        return self.content

    def get_raw_data(self) -> str:
        return self.content

    def add_sublist(self, sublist: ListObject) -> None:
        """Adiciona uma sublista ao item."""
        self.add_child(sublist)

    def has_sublists(self) -> bool:
        """Verifica se o item tem sublistas."""
        return any(isinstance(child, ListObject) for child in self.children)

    def get_sublists(self) -> List[ListObject]:
        """Retorna sublistas do item."""
        return [child for child in self.children if isinstance(child, ListObject)]


@dataclass
class SectionObject(ContainerObject):
    """Objeto para seções de documento."""

    title: Optional[str] = None
    level: int = 1  # Nível hierárquico
    section_id: Optional[str] = None

    object_type: str = "section"

    def get_content(self) -> str:
        """Retorna representação textual da seção."""
        lines = []

        if self.title:
            # Formata título baseado no nível
            if self.level == 1:
                lines.append(f"\n=== {self.title.upper()} ===\n")
            elif self.level == 2:
                lines.append(f"\n--- {self.title} ---\n")
            else:
                prefix = "#" * self.level
                lines.append(f"\n{prefix} {self.title}\n")

        # Adiciona conteúdo dos filhos
        for child in self.children:
            lines.append(child.get_content())

        return "\n".join(lines)

    def get_raw_data(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'level': self.level,
            'section_id': self.section_id,
            'child_count': len(self.children)
        }

    def add_content(self, content: ContentObject) -> None:
        """Adiciona conteúdo à seção."""
        self.add_child(content)

    def get_headings(self) -> List[Any]:  # Evita import circular
        """Retorna cabeçalhos dentro da seção."""
        from .text import HeadingObject
        return [child for child in self.children if isinstance(child, HeadingObject)]

    def get_subsections(self) -> List[SectionObject]:
        """Retorna subseções."""
        return [child for child in self.children if isinstance(child, SectionObject)]