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
            TextPageXMLTypes.PARAGRAPH: RegionColor((85, 107, 47), (255, 0, 0)),
            TextPageXMLTypes.HEADING: RegionColor((128, 0, 0), (255, 0, 0)),
            TextPageXMLTypes.HEADER: RegionColor((72, 61, 139), (255, 0, 0)),
            TextPageXMLTypes.CATCH_WORD: RegionColor((119, 136, 153), (255, 0, 0)),
            TextPageXMLTypes.PAGE_NUMBER: RegionColor((0, 128, 0), (255, 0, 0)),
            TextPageXMLTypes.SIGNATURE_MARK: RegionColor((60, 179, 113), (255, 0, 0)),
            TextPageXMLTypes.MARGINALIA: RegionColor((184, 134, 11), (255, 0, 0)),
            TextPageXMLTypes.OTHER: RegionColor((32, 178, 170), (255, 0, 0)),
            TextPageXMLTypes.DROP_CAPITAL: RegionColor((0, 0, 139), (0, 255, 0)),
            TextPageXMLTypes.FLOATING: RegionColor((50, 205, 50), (255, 0, 0)),
            TextPageXMLTypes.CAPTION: RegionColor((139, 0, 139), (255, 0, 0)),
            TextPageXMLTypes.ENDNOTE: RegionColor((176, 48, 96), (255, 0, 0)),
            TextPageXMLTypes.FOOTNOTE: RegionColor((210, 180, 140), (255, 0, 0)),
            TextPageXMLTypes.FOOTNOTE_CONTINUED: RegionColor((255, 69, 0), (255, 0, 0)),
            TextPageXMLTypes.FOOTER: RegionColor((255, 140, 0), (255, 0, 0)),

        }[self]


class GraphicRegionPageXMLTypes(enum.Enum):
    STAMP = "stamp"
    HANDWRITTEN_ANNOTATION = "handwritten-annotation"
    DECORATION = "decoration"
    BARCODE = "barcode"
    OTHER = "other"

    def color(self):
        return {
            GraphicRegionPageXMLTypes.STAMP: RegionColor((0, 255, 0), (0, 255, 0)),
            GraphicRegionPageXMLTypes.HANDWRITTEN_ANNOTATION: RegionColor((148, 0, 211), (255, 0, 0)),
            GraphicRegionPageXMLTypes.DECORATION: RegionColor((0, 250, 154), (0, 255, 0)),
            GraphicRegionPageXMLTypes.BARCODE: RegionColor((220, 20, 60), (0, 255, 0)),
            GraphicRegionPageXMLTypes.OTHER: RegionColor((0, 191, 255), (0, 255, 0)),
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
            PageXMLRegionType.TEXTREGION: RegionColor((0, 0, 255), (255, 0, 0)),
            PageXMLRegionType.IMAGEREGION: RegionColor((173, 255, 47), (0, 255, 0)),
            PageXMLRegionType.GRAPHICREGION: RegionColor((255, 0, 255), (0, 255, 0)),
            PageXMLRegionType.SEPERATORREGION: RegionColor((250, 128, 114), (0, 255, 0)),
            PageXMLRegionType.READINGORDER: RegionColor(None, None),
            PageXMLRegionType.BORDER: RegionColor((255, 255, 255), (255, 255, 255)),
            PageXMLRegionType.MATHSREGION: RegionColor((255, 255, 84), (0, 255, 0)),
            PageXMLRegionType.TABLEREGION: RegionColor((100, 149, 237), (0, 255, 0)),
            PageXMLRegionType.RELATIONS: RegionColor((176, 224, 230), (0, 255, 0)),
            PageXMLRegionType.PRINTSPACE: RegionColor((255, 255, 255), (255, 255, 255)),
            PageXMLRegionType.MUSICREGION: RegionColor((123, 104, 238), (0, 255, 0)),
            PageXMLRegionType.NOISEREGION: RegionColor((238, 130, 238), (0, 255, 0)),

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
