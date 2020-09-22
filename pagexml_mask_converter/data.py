import abc
import enum
from abc import ABC

import logging

logger = logging.getLogger(__name__)


class RegionColor:
    def __init__(self, color=None, text_non_text_color=None):
        self.color = color
        self.text_non_text_color = text_non_text_color


class TextPageXMLTypes(enum.Enum):
    PARAGRAPH = 'paragraph'
    HEADING = 'heading'
    HEADER = 'header'
    CATCH_WORD = 'catch-word'
    PAGE_NUMBER = 'page-number'
    SIGNATURE_MARK = 'signature-mark'
    MARGINALIA = 'marginalia'
    OTHER = 'other'
    DROP_CAPITAL = 'drop-capital'
    FLOATING = 'floating'
    CAPTION = 'caption'
    ENDNOTE = 'endnote'
    FOOTNOTE = 'footnote'
    FOOTNOTE_CONTINUED = 'footnote-continued'
    FOOTER = 'footer'

    def color(self):
        return {
            TextPageXMLTypes.PARAGRAPH: RegionColor((255, 128, 0), (255, 0, 0)),
            TextPageXMLTypes.HEADING: RegionColor((255, 128, 128), (255, 0, 0)),
            TextPageXMLTypes.HEADER: RegionColor((255, 64, 128), (255, 0, 0)),
            TextPageXMLTypes.CATCH_WORD: RegionColor((255, 128, 64), (255, 0, 0)),
            TextPageXMLTypes.PAGE_NUMBER: RegionColor((255, 32, 128), (255, 0, 0)),
            TextPageXMLTypes.SIGNATURE_MARK: RegionColor((255, 128, 32), (255, 0, 0)),
            TextPageXMLTypes.MARGINALIA: RegionColor((255, 64, 32), (255, 0, 0)),
            TextPageXMLTypes.OTHER: RegionColor((255, 32, 64), (255, 0, 0)),
            TextPageXMLTypes.DROP_CAPITAL: RegionColor((255, 64, 64), (0, 255, 0)),
            TextPageXMLTypes.FLOATING: RegionColor((255, 0, 128), (255, 0, 0)),
            TextPageXMLTypes.CAPTION: RegionColor((255, 64, 0), (255, 0, 0)),
            TextPageXMLTypes.ENDNOTE: RegionColor((255, 0, 64), (255, 0, 0)),
            TextPageXMLTypes.FOOTNOTE: RegionColor((255, 32, 0), (255, 0, 0)),
            TextPageXMLTypes.FOOTNOTE_CONTINUED: RegionColor((255, 0, 32), (255, 0, 0)),
            TextPageXMLTypes.FOOTER: RegionColor((255, 32, 32), (255, 0, 0)),

        }[self]


class GraphicRegionPageXMLTypes(enum.Enum):
    STAMP = "stamp"
    HANDWRITTEN_ANNOTATION = "handwritten-annotation"
    DECORATION = "decoration"
    BARCODE = "barcode"
    OTHER = "other"

    def color(self):
        return {
            GraphicRegionPageXMLTypes.STAMP: RegionColor((128, 0, 255), (0, 255, 0)),
            GraphicRegionPageXMLTypes.HANDWRITTEN_ANNOTATION: RegionColor((0, 128, 255), (255, 0, 0)),
            GraphicRegionPageXMLTypes.DECORATION: RegionColor((128, 0, 255), (0, 255, 0)),
            GraphicRegionPageXMLTypes.BARCODE: RegionColor((128, 128, 255), (0, 255, 0)),
            GraphicRegionPageXMLTypes.OTHER: RegionColor((128, 64, 255), (0, 255, 0)),
        }[self]


class PageXMLRegionType(enum.Enum):
    TEXTREGION = "TextRegion"
    IMAGEREGION = "ImageRegion"
    GRAPHICREGION = "GraphicRegion"
    SEPERATORREGION = "SeparatorRegion"
    READINGORDER = "ReadingOrder"
    BORDER = "Border"
    MATHSREGION = "MathsRegion"
    TABLEREGION = "TableRegion"
    RELATIONS = "Relations"
    PRINTSPACE = "PrintSpace"
    MUSICREGION = "MusicRegion"
    NOISEREGION = "NoiseRegion"

    @staticmethod
    def get_region_types():
        return list(map(lambda k: k.value, PageXMLRegionType))

    def get_attribute_class_of_region(self):
        return {
            PageXMLRegionType.TEXTREGION: TextPageXMLTypes,
            PageXMLRegionType.GRAPHICREGION: GraphicRegionPageXMLTypes,
        }[self]

    def region_color(self):
        return {
            PageXMLRegionType.TEXTREGION: RegionColor((255, 0, 0), (255, 0, 0)),
            PageXMLRegionType.IMAGEREGION: RegionColor((0, 255, 0), (0, 255, 0)),
            PageXMLRegionType.GRAPHICREGION: RegionColor((0, 0, 255), (0, 255, 0)),
            PageXMLRegionType.SEPERATORREGION: RegionColor((255, 255, 0), (0, 255, 0)),
            PageXMLRegionType.READINGORDER: RegionColor(None, None),
            PageXMLRegionType.BORDER: RegionColor((255, 255, 255), (255, 255, 255)),
            PageXMLRegionType.MATHSREGION: RegionColor((128, 255, 255), (0, 255, 0)),
            PageXMLRegionType.TABLEREGION: RegionColor((64, 255, 255), (0, 255, 0)),
            PageXMLRegionType.RELATIONS: RegionColor((64, 255, 255), (0, 255, 0)),
            PageXMLRegionType.PRINTSPACE: RegionColor((255, 255, 255), (255, 255, 255)),
            PageXMLRegionType.MUSICREGION: RegionColor((32, 255, 255), (0, 255, 0)),
            PageXMLRegionType.NOISEREGION: RegionColor((255, 32, 255), (0, 255, 0)),

        }[self]

    def get_region_type_color(self, att_type, color_text_non_text=False, regions_only=False):
        try:
            return self.get_attribute_class_of_region()(att_type).color().color if color_text_non_text is False else \
                self.get_attribute_class_of_region()(att_type).color().text_non_text_color
        except:
            if att_type is not None:
                logger.warning("{} not known for region {}. Using default value of region".format(att_type, self.value))
            return self.region_color().color if color_text_non_text is False else self.region_color().text_non_text_color

    @staticmethod
    def to_dict(color_text_non_text=False, regions_only=False):
        color_dict = {}
        for x in PageXMLRegionType:
            att_dict = {}
            if color_text_non_text:
                att_dict["default_color"] = PageXMLRegionType(x).region_color().text_non_text_color
            else:
                att_dict["default_color"] = PageXMLRegionType(x).region_color().color

            att_colors = {}
            try:
                for t in PageXMLRegionType(x).get_attribute_class_of_region():
                    if color_text_non_text:
                        att_colors[t.value] = PageXMLRegionType(x) \
                            .get_attribute_class_of_region()(t).color().text_non_text_color
                    else:
                        att_colors[t.value] = PageXMLRegionType(x).get_attribute_class_of_region()(t).color().color
            except:
                pass
            att_dict["region_type_colors"] = att_colors
            color_dict[x.value] = att_dict
        return color_dict


class RegionAttributes(ABC):
    @abc.abstractmethod
    def get_color(self):
        pass


class TextAttributes(RegionAttributes):

    def __init__(self, text_type: TextPageXMLTypes):
        self.text_type = text_type

    def get_color(self):
        return self.text_type.color()


class BorderAttributes(RegionAttributes):
    def __init__(self, text_type: TextPageXMLTypes):
        self.text_type = text_type

    def get_color(self):
        return self.text_type.color()
