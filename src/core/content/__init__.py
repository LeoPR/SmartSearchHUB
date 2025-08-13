# src/core/content/__init__.py
# Exporta os principais objetos para facilitar imports

from .base import ContentObject, Position, ContainerObject, ObjectType
from .text import TextObject, HeadingObject
from .media import ImageObject, VideoObject, AudioObject
from .structure import TableObject, ListObject, ListItemObject, SectionObject
from .code import CodeObject, StyleObject, ScriptObject
from .link import UrlObject, LinkObject
from .drivers import ContentDriver, DriverFactory, LocalFileDriver, UrlDriver, InlineContentDriver

__all__ = [
    # Base
    'ContentObject', 'Position', 'ContainerObject', 'ObjectType',

    # Text objects
    'TextObject', 'HeadingObject',

    # Media objects
    'ImageObject', 'VideoObject', 'AudioObject',

    # Structure objects
    'TableObject', 'ListObject', 'ListItemObject', 'SectionObject',

    # Code objects
    'CodeObject', 'StyleObject', 'ScriptObject',

    # Link objects
    'UrlObject', 'LinkObject',

    # Drivers
    'ContentDriver', 'DriverFactory', 'LocalFileDriver', 'UrlDriver', 'InlineContentDriver'
]