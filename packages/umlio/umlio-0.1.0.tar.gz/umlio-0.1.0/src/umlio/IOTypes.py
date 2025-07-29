
from typing import Dict
from typing import List
from typing import NewType

from enum import Enum

from dataclasses import dataclass
from dataclasses import field

from pathlib import Path

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase

from umlshapes.links.UmlLink import UmlLink

UML_VERSION: str = '12.0'

UmlDiagramTitle = NewType('UmlDiagramTitle', str)
UmlClasses      = NewType('UmlClasses',      List[UmlClass])
UmlUseCases     = NewType('UmlUseCases',     List[UmlUseCase])
UmlActors       = NewType('UmlActors',       List[UmlActor])
UmlNotes        = NewType('UmlNotes',        List[UmlNote])
UmlTexts        = NewType('UmlTexts',        List[UmlText])
UmlLinks        = NewType('UmlLinks',        List[UmlLink])

ElementAttributes = NewType('ElementAttributes', Dict[str, str])


class UmlDiagramType(Enum):
    CLASS_DIAGRAM    = 'Class Diagram'
    USE_CASE_DIAGRAM = 'Use Case Diagram'
    SEQUENCE_DIAGRAM = 'Sequence Diagram'
    NOT_SET          = 'Not Set'


def umlClassesFactory() -> UmlClasses:
    """
    Factory method to create  the UmlClasses data structure;

    Returns:  A new data structure
    """
    return UmlClasses([])


def umlUseCasesFactory() -> UmlUseCases:
    return UmlUseCases([])


def umlActorsFactory() -> UmlActors:
    return UmlActors([])


def umlNotesFactory() -> UmlNotes:
    return UmlNotes([])


def umlTextsFactory() -> UmlTexts:
    return UmlTexts([])


def umlLinksFactory() -> UmlLinks:
    return UmlLinks([])


@dataclass
class UmlDiagram:
    diagramType:     UmlDiagramType  = UmlDiagramType.NOT_SET
    diagramTitle:    UmlDiagramTitle = UmlDiagramTitle('')
    scrollPositionX: int = 1
    scrollPositionY: int = 1
    pixelsPerUnitX:  int = 1
    pixelsPerUnitY:  int = 1
    umlClasses:      UmlClasses  = field(default_factory=umlClassesFactory)
    umlUseCases:     UmlUseCases = field(default_factory=umlUseCasesFactory)
    umlActors:       UmlActors   = field(default_factory=umlActorsFactory)
    umlNotes:        UmlNotes    = field(default_factory=umlNotesFactory)
    umlTexts:        UmlTexts    = field(default_factory=umlTextsFactory)
    umlLinks:        UmlLinks    = field(default_factory=umlLinksFactory)


UmlDiagrams = NewType('UmlDiagrams', Dict[UmlDiagramTitle, UmlDiagram])


def createUmlDiagramsFactory() -> UmlDiagrams:
    return UmlDiagrams({})


@dataclass
class UmlProject:
    fileName:    str  = ''
    version:     str  = UML_VERSION
    codePath:    Path = Path('')
    umlDiagrams: UmlDiagrams = field(default_factory=createUmlDiagramsFactory)
