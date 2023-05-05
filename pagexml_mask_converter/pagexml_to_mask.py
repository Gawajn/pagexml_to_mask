import enum
import json
import xml.etree.ElementTree as ET
from typing import NamedTuple, List, Tuple
from PIL import Image, ImageDraw
import glob
import multiprocessing
import argparse
import os
import numpy as np
from dataclasses import dataclass

from pagexml_mask_converter.data import PageXMLRegionType
import logging

logger = logging.getLogger(__name__)


class MaskType(enum.Enum):
    ALLTYPES = 'all_types'
    TEXT_NONTEXT = 'text_non_text'
    BASE_LINE = 'baseline'
    TEXT_LINE = 'text_line'


class PCGTSVersion(enum.Enum):
    PCGTS2017 = '2017'
    PCGTS2013 = '2013'
    PCGTS2019 = '2019'
    PCGTS2019S = '2019s'
    PCGTS2013S = '2013s'
    PCGTS2017S = '2017s'

    def get_namespace(self):
        return {
            PCGTSVersion.PCGTS2017: 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15',
            PCGTSVersion.PCGTS2013: 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15',
            PCGTSVersion.PCGTS2019: 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15',

            PCGTSVersion.PCGTS2013S: 'https://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15',
            PCGTSVersion.PCGTS2017S: 'https://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15',
            PCGTSVersion.PCGTS2019S: 'https://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15',
        }[self]


@dataclass
class MaskSetting():
    MASK_EXTENSION: str = 'png'
    MASK_TYPE: MaskType = MaskType.ALLTYPES
    PCGTS_VERSION: PCGTSVersion = PCGTSVersion.PCGTS2017
    LINEWIDTH: int = 5
    BASELINELENGTH: int = 20
    SETTING_OUTPUT: bool = False

    def to_dict(self):
        json_dict = {}
        for x in list(self.__dict__.keys()):
            # if x == "DECODER_CHANNELS":
            #    print(x)
            if x in ['PSEUDO_DATASET', 'CUSTOM_MODEL', 'TRAIN_DATASET', 'VAL_DATASET']:
                continue
            else:
                if isinstance(self.__dict__[x], enum.Enum):
                    json_dict[x] = self.__dict__[x].value
                    continue
                json_dict[x] = self.__dict__[x]
        return json_dict


class RegionType(NamedTuple):
    polygon: List[Tuple[int, int]]
    region: str
    r_type: str

    def get_scaled_image_region(self, scale):
        return (np.array(self.polygon) * scale).astype(int)


class PageRegions(NamedTuple):
    image_size: Tuple[int, int]
    xml_regions: List[RegionType]
    filename: str

    def get_scaled_image_size(self, scale):
        return (np.array(self.image_size) * scale).astype(int)


from abc import ABC, abstractmethod


class BaseMaskGenerator(ABC):
    @abstractmethod
    def get_mask(self, file, scale: float = 1.0):
        pass


class MaskGenerator(BaseMaskGenerator):
    def __init__(self, settings: MaskSetting):
        self.settings = settings
        self.xml_namespace = self.settings.PCGTS_VERSION.get_namespace()

    def save(self, file, output_dir):
        logger.info("Processing: {}".format(file))
        a = self.get_xml_regions(file, self.settings)
        mask_pil = page_region_to_mask(a, self.settings)
        filename_wo_ext = os.path.splitext(a.filename)[0]
        mask_pil.save(output_dir + filename_wo_ext + '.mask.' + self.settings.MASK_EXTENSION)

    def get_mask(self, file, scale=1.0):
        a = self.get_xml_regions(file, self.settings)
        mask_pil = page_region_to_mask(a, self.settings, scale=scale)
        return np.array(mask_pil)

    def get_xml_regions(self, xml_file, setting: MaskSetting) -> PageRegions:
        namespaces = {'pcgts': self.xml_namespace}
        root = ET.parse(xml_file).getroot()
        region_by_types = []
        for name, value in namespaces.items():
            ET.register_namespace(name, value)

        page = root.find('.//pcgts:Page', namespaces)
        if page is None:
            # sadly pagexml inconsistent (http, https, ..) -> check all namespaces
            for i in PCGTSVersion:
                namespaces['pcgts'] = i.get_namespace()
                page = root.find('.//pcgts:Page', namespaces)
                if page is not None:  # Todo synchronize across processes
                    self.xml_namespace = i.get_namespace()
                    break

        page_height = page.get('imageHeight')
        page_width = page.get('imageWidth')
        xml_f_name = page.get('imageFilename')
        f_name = os.path.splitext(os.path.basename(xml_file))[0]
        xml_f_name = os.path.splitext(os.path.basename(xml_f_name))[0]
        if f_name != xml_f_name:
            logger.info("Basename of file: {} is different than XML Filename: {}".format(f_name, xml_f_name))
        for x in page.getchildren():
            region = x.tag.split("}")[-1]
            if region not in PageXMLRegionType.get_region_types():
                logger.warning("{} Not defined. Skipping Region Type".format(region))
            #print(region)
                #print(child)
            if setting.MASK_TYPE == setting.MASK_TYPE.TEXT_NONTEXT or setting.MASK_TYPE == \
                    setting.MASK_TYPE.ALLTYPES:
                coords = x.find('pcgts:Coords', namespaces)
                if coords is not None:
                    polyline = string_to_lp(coords.get('points'))
                    xml_type = x.get('type')
                    region_by_types.append(RegionType(polygon=polyline,
                                                      region=region,
                                                      r_type=xml_type))

            if setting.MASK_TYPE == setting.MASK_TYPE.TEXT_LINE:
                for textline in x.findall('pcgts:TextLine', namespaces):
                    if textline is not None:
                        coords = textline.find('pcgts:Coords', namespaces)
                        if coords is not None:
                            polyline = string_to_lp(coords.get('points'))
                            xml_type = x.get('type')
                            region_by_types.append(RegionType(polygon=polyline,
                                                              region=region,
                                                              r_type=xml_type))

            if setting.MASK_TYPE == setting.MASK_TYPE.BASE_LINE:
                for textline in x.findall('pcgts:TextLine', namespaces):
                    if textline is not None:
                        baseline = textline.find('pcgts:Baseline', namespaces)
                        if baseline is not None:
                            polyline = string_to_lp(baseline.get('points'))
                            xml_type = x.get('type')
                            region_by_types.append(RegionType(polygon=polyline,
                                                              region=region,
                                                              r_type=xml_type))
        return PageRegions(image_size=(int(page_height), int(page_width)), xml_regions=region_by_types, filename=f_name)


def string_to_lp(points: str):
    lp_points: List[Tuple[int, int]] = []
    if points is not None:
        for point in points.split(' '):
            x, y = point.split(',')
            lp_points.append((int(x), int(y)))
    return lp_points


def page_region_to_mask(page_region: PageRegions, setting: MaskSetting, scale: float = 1.0) -> Image:
    height, width = page_region.get_scaled_image_size(scale)
    pil_image = Image.new('RGB', (width, height), (255, 255, 255))
    for x in page_region.xml_regions:
        polygon = x.get_scaled_image_region(scale)
        if setting.MASK_TYPE is MaskType.ALLTYPES:
            if len(polygon) >= 2:
                ImageDraw.Draw(pil_image).polygon(polygon.flatten().tolist(),
                                                  outline=PageXMLRegionType(x.region).get_region_type_color(x.r_type),
                                                  fill=PageXMLRegionType(x.region).get_region_type_color(x.r_type))
        elif setting.MASK_TYPE is MaskType.TEXT_NONTEXT:
            if len(polygon) >= 2:
                ImageDraw.Draw(pil_image).polygon(polygon.flatten().tolist(),
                                                  outline=PageXMLRegionType(x.region).
                                                  get_region_type_color(x.r_type, color_text_non_text=True),
                                                  fill=PageXMLRegionType(x.region).
                                                  get_region_type_color(x.r_type, color_text_non_text=True)),
        elif setting.MASK_TYPE is MaskType.BASE_LINE:
            if len(polygon) >= 2:
                ImageDraw.Draw(pil_image).line(polygon.flatten().tolist(),
                                               fill=PageXMLRegionType("TextRegion").
                                               get_region_type_color(None, color_text_non_text=True),
                                               width=setting.LINEWIDTH)
                if setting.BASELINELENGTH != 0:
                    from math import sqrt

                    def getPoint(p1, p2, length=20, max_width=None, max_height=None, lw=5):
                        x1, y1 = p1
                        x2, y2 = p2

                        x3 = x2 - x1
                        y3 = y2 - y1
                        lw = lw + 1
                        if x2 > x1:
                            if max_width > x2 + lw / 2:
                                x2 = x2 + lw / 2
                        if x2 < x1:
                            if 0 < x2 - lw / 2:
                                x2 = x2 - lw / 2
                        mag = sqrt(x3 * x3 + y3 * y3)
                        x3 = x3 / mag
                        y3 = y3 / mag

                        temp = x3
                        x3 = -y3
                        y3 = temp

                        xl1 = x2 + x3 * length
                        xl2 = x2 + x3 * -length

                        yl1 = y2 + y3 * length
                        yl2 = y2 + y3 * -length

                        return (xl1, yl1), (xl2, yl2)

                    start, end = polygon[0], polygon[-1]
                    l1 = getPoint(start, end, setting.BASELINELENGTH, max_width=width, max_height=height,lw=setting.LINEWIDTH)
                    l2 = getPoint(end, start, setting.BASELINELENGTH, max_width=width, max_height=height, lw=setting.LINEWIDTH)

                    ImageDraw.Draw(pil_image).line(l1,
                                                   fill=PageXMLRegionType("GraphicRegion").
                                                   get_region_type_color(None,
                                                                         color_text_non_text=True),
                                                   width=setting.LINEWIDTH)
                    ImageDraw.Draw(pil_image).line(l2,
                                                   fill=PageXMLRegionType("GraphicRegion").
                                                   get_region_type_color(None,
                                                                         color_text_non_text=True),
                                                   width=setting.LINEWIDTH)

        elif setting.MASK_TYPE is MaskType.TEXT_LINE:
            if len(polygon) >= 2:
                ImageDraw.Draw(pil_image).polygon(polygon.flatten().tolist(),
                                                  outline=PageXMLRegionType(x.region).get_region_type_color(x.r_type),
                                                  fill=PageXMLRegionType(x.region).get_region_type_color(x.r_type))

    return pil_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True,
                        help="Image directory to process")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="The output dir for the mask files")
    parser.add_argument("--processes", type=int, default=4,
                        help="The output dir for the mask files")
    parser.add_argument('--setting',
                        default='all_types',
                        const='all_types',
                        nargs='?',
                        choices=['all_types', 'text_non_text', 'baseline', 'text_line'],
                        help='Settings for the mask generation (default: %(default)s)')
    parser.add_argument('--mask_extension',
                        default='png',
                        const='png',
                        nargs='?',
                        choices=['png', 'dib', 'eps', 'gif', 'icns', 'ico', 'im', 'jpeg', 'msp',
                                 'pcx', 'ppm', 'sgi', 'tga', 'tiff', 'webp', 'xbm'],
                        help='Mask extension Setting')
    parser.add_argument('--pcgts_version',
                        default='2017',
                        const='2017',
                        nargs='?',
                        choices=['2017', '2013', '2019'],
                        help='PCGTS Version')
    parser.add_argument('--line_width', type=int, default=7, help='Width of the line to be drawn')
    parser.add_argument('--baseline_length', type=int, default=15, help='Length of the line to be drawn at '
                                                                        'the end of the baseline')
    parser.add_argument('--scale', type=float, default=1.0, help='Scalefactor')
    parser.add_argument('--setting_output', action="store_true")
    parser.add_argument('--color_legend', action="store_true")
    args = parser.parse_args()
    pool = multiprocessing.Pool(int(args.processes))
    mask_gen = MaskGenerator(MaskSetting(MASK_TYPE=MaskType(args.setting), MASK_EXTENSION=args.mask_extension,
                                         PCGTS_VERSION=PCGTSVersion(args.pcgts_version), LINEWIDTH=args.line_width,
                                         BASELINELENGTH=args.baseline_length))
    files = glob.glob(args.input_dir)
    from pagexml_mask_converter.data import PageXMLRegionType
    if args.setting_output or args.color_legend:
        t_nt = False if mask_gen.settings.MASK_TYPE is MaskType.ALLTYPES else True
        color_dict = PageXMLRegionType.to_dict(color_text_non_text=t_nt)
        setting_dict = mask_gen.settings.to_dict()
        _comp = {**setting_dict, **{'Color_Map': color_dict}}
        t = json.dumps(_comp, indent=4)
        from pagexml_mask_converter.color_legend import color_legend
        if args.setting_output:
            with open(os.path.join(args.output_dir, "mask_setting.json"), "w") as file_to_write:
                file_to_write.write(t)
        if args.color_legend:
            image = color_legend(t)
            image.save(os.path.join(args.output_dir, "image_palette.png"))

    from itertools import product
    pool.starmap(mask_gen.save, product(files, [args.output_dir]))


if __name__ == '__main__':
    main()
