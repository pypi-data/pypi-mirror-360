
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Point

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

from umlshapes.links.DeltaXY import DeltaXY
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.links.UmlLink import UmlLink
from umlshapes.links.eventhandlers.UmlLinkEventHandler import LineControlPoints

from umlshapes.types.Common import EndPoints
from umlshapes.types.UmlPosition import UmlPosition

from umlio.BaseUmlToXml import BaseUmlToXml

from umlio.IOTypes import ElementAttributes
from umlio.IOTypes import UmlLinks
from umlio.PyutToXml import PyutToXml

from umlio.XMLConstants import XmlConstants


class UmlLinksToXml(BaseUmlToXml):
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._pyutToXml: PyutToXml = PyutToXml()

    def serialize(self, documentTop: Element, umlLinks: UmlLinks) -> Element:

        for umlLink in umlLinks:
            #     if isinstance(oglLink, OglInterface2):
            #         self._oglInterface2ToXml(documentElement=documentTop, oglInterface=oglLink)
            #     else:
            self._oglLinkToXml(documentElement=documentTop, umlLink=umlLink)

        return documentTop

    def _oglLinkToXml(self, documentElement: Element, umlLink: UmlLink) -> Element:

        attributes:        ElementAttributes = self._umlLinkAttributes(umlLink=umlLink)
        oglLinkSubElement: Element           = SubElement(documentElement, XmlConstants.ELEMENT_UML_LINK, attrib=attributes)

        if isinstance(umlLink, UmlAssociation):

            associationName: UmlAssociationLabel = umlLink.associationName
            src:             UmlAssociationLabel = umlLink.sourceCardinality
            dst:             UmlAssociationLabel = umlLink.destinationCardinality
            associationLabels = {
                XmlConstants.ELEMENT_ASSOCIATION_LABEL:      associationName,
                XmlConstants.ELEMENT_ASSOCIATION_SOURCE_LABEL:      src,
                XmlConstants.ELEMENT_ASSOCIATION_DESTINATION_LABEL: dst
            }
            for eltName in associationLabels:
                umlAssociationLabel: UmlAssociationLabel = associationLabels[eltName]

                linkDelta: DeltaXY = umlAssociationLabel.linkDelta

                labelAttributes: ElementAttributes = ElementAttributes({
                    XmlConstants.ATTRIBUTE_DELTA_X: str(linkDelta.deltaX),
                    XmlConstants.ATTRIBUTE_DELTA_Y: str(linkDelta.deltaY),
                })
                # noinspection PyUnusedLocal
                labelElement: Element = SubElement(oglLinkSubElement, eltName, attrib=labelAttributes)

        lineControlPoints: LineControlPoints = umlLink.GetLineControlPoints()
        realControlPoints: LineControlPoints = self._removeEndPoints(umlLink=umlLink, lineControlPoints=lineControlPoints)
        for pt in realControlPoints:
            wxPoint: Point = cast(Point, pt)
            controlPointAttributes: ElementAttributes = ElementAttributes({
                XmlConstants.ATTRIBUTE_X: str(wxPoint.x),
                XmlConstants.ATTRIBUTE_Y: str(wxPoint.y),
            })
            SubElement(oglLinkSubElement, XmlConstants.ELEMENT_MODEL_LINE_CONTROL_POINT, attrib=controlPointAttributes)

        self._pyutToXml.pyutLinkToXml(pyutLink=umlLink.pyutLink, oglLinkElement=oglLinkSubElement)

        return oglLinkSubElement

    # def _oglInterface2ToXml(self, documentElement: Element, oglInterface: OglInterface2) -> Element:
    #     """
    #
    #     Args:
    #         documentElement:  untangler element for document
    #         oglInterface:     Lollipop to serialize
    #     Returns:
    #         New untangle element
    #     """
    #     destAnchor:      SelectAnchorPoint = oglInterface.destinationAnchor
    #     attachmentPoint: AttachmentSide    = destAnchor.attachmentPoint
    #     x, y = destAnchor.GetPosition()
    #
    #     attributes: ElementAttributes = ElementAttributes({
    #         XmlConstants.ATTR_LOLLIPOP_ATTACHMENT_POINT: attachmentPoint.__str__(),
    #         XmlConstants.ATTR_X:                         str(x),
    #         XmlConstants.ATTR_Y:                         str(y),
    #     })
    #     oglInterface2: Element = SubElement(documentElement, XmlConstants.ELEMENT_OGL_INTERFACE2, attrib=attributes)
    #
    #     self._pyutToXml.pyutInterfaceToXml(oglInterface.pyutInterface, oglInterface2)
    #     return oglInterface2
    #
    def _umlLinkAttributes(self, umlLink: UmlLink) -> ElementAttributes:

        # srcX, srcY   = umlLink.sourceAnchor.model.GetPosition()
        # destX, destY = umlLink.destinationAnchor.model.GetPosition()

        umlLinkId:    str         = str(umlLink.id)
        endPoints:    EndPoints   = umlLink.endPoints
        fromPosition: UmlPosition = endPoints.fromPosition
        toPosition:   UmlPosition = endPoints.toPosition

        attributes: ElementAttributes = ElementAttributes({
            XmlConstants.ATTRIBUTE_ID:          umlLinkId,
            XmlConstants.ATTRIBUTE_LINK_FROM_X: str(fromPosition.x),
            XmlConstants.ATTRIBUTE_LINK_FROM_Y: str(fromPosition.y),
            XmlConstants.ATTRIBUTE_LINK_TO_X:   str(toPosition.x),
            XmlConstants.ATTRIBUTE_LINK_TO_Y:   str(toPosition.y),
            XmlConstants.ATTRIBUTE_SPLINE:      str(umlLink.spline)   # piecewise polynomial function
        })

        return attributes

    def _removeEndPoints(self, umlLink: 'UmlLink', lineControlPoints: LineControlPoints) -> LineControlPoints:
        """
        Do not consider the end points

        Args:
            umlLink:
            lineControlPoints:

        Returns:  The control points less the 2 end points
        """

        realControlPoints: LineControlPoints = LineControlPoints(lineControlPoints[:])

        x1, y1, x2, y2 = umlLink.FindLineEndPoints()

        pt1: Point = Point(x1, y1)
        pt2: Point = Point(x2, y2)

        realControlPoints.remove(pt1)
        realControlPoints.remove(pt2)

        return realControlPoints
