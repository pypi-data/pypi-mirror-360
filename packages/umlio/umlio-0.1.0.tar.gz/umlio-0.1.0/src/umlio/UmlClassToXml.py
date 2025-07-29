
from logging import Logger
from logging import getLogger

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from umlshapes.shapes.UmlClass import UmlClass

from umlio.BaseUmlToXml import BaseUmlToXml
from umlio.IOTypes import UmlClasses
from umlio.PyutToXml import PyutToXml
from umlio.XMLConstants import XmlConstants


class UmlClassToXml(BaseUmlToXml):
    def __init__(self):

        super().__init__()

        self.logger:     Logger    = getLogger(__name__)
        self._pyutToXml: PyutToXml = PyutToXml()

    def serialize(self, documentTop: Element, umlClasses: UmlClasses) -> Element:

        for umlClass in umlClasses:
            self._oglClassToXml(documentTop=documentTop, umlClass=umlClass)

        return documentTop

    def _oglClassToXml(self, documentTop: Element, umlClass: UmlClass) -> Element:
        """
        Exports an UmlClass to a minidom Element.

        Args:
            documentTop: The document to append to
            umlClass:    UML Class to serialize

        Returns:
            The newly created `UmlClass` Element
        """
        attributes = self._umlBaseAttributes(umlShape=umlClass)
        oglClassSubElement: Element = SubElement(documentTop, XmlConstants.ELEMENT_UML_CLASS, attrib=attributes)

        self._pyutToXml.pyutClassToXml(graphicElement=oglClassSubElement, pyutClass=umlClass.pyutClass)

        return oglClassSubElement
