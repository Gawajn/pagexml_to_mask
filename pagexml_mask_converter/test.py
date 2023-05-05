from pagexml_mask_converter.pagexml_to_mask import MaskGenerator, MaskSetting, MaskType
from  PIL import Image

if __name__ == "__main__":
    path = "/tmp/0009.xml"
    mask_gen = MaskGenerator(MaskSetting(MASK_TYPE=MaskType.BASE_LINE))
    image = mask_gen.get_mask(path)
    pil1 = Image.open("/tmp/0009.png").convert("RGBA")
    pil2 = Image.fromarray(image).convert("RGBA")
    alpha = Image.blend(pil1, pil2, 0.5)
    alpha.show()



    pass