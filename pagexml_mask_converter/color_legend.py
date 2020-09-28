import json

from PIL import Image, ImageDraw


def color_legend(json_file, image_with=1000, image_height=1500, size_of_legend=(130, 130), gap=20, text_gap=20):
    c_image = Image.new("RGB", (image_with, image_height), (255, 255, 255))
    draw = ImageDraw.Draw(c_image)
    start_position = (gap, gap + text_gap)

    c_dict = json.loads(json_file)
    c_dict = c_dict['Color_Map']
    num_colors = 0
    for x in c_dict.keys():
        region = c_dict[x]
        if region['default_color'] is not None:
            num_colors += 1
        for y in region['region_type_colors']:
            num_colors += 1

    for x in c_dict.keys():
        region = c_dict[x]
        if region['default_color'] is not None:
            reg_color = tuple(region['default_color'])
            rec_draw_position = (start_position,
                                 (start_position[0] + size_of_legend[0], start_position[1] + size_of_legend[1]))
            text_draw_position = (rec_draw_position[0][0], rec_draw_position[0][1] - gap / 2)
            draw.rectangle(xy=rec_draw_position,
                           outline=(0, 0, 0),
                           fill=reg_color)
            draw.text(xy=text_draw_position, text=x, fill=(0, 0, 0))
            start_position = (start_position[0] + gap + size_of_legend[0], start_position[1]) \
                if start_position[0] + gap + 2 * size_of_legend[0] < image_with \
                else (gap, start_position[1] + gap + size_of_legend[1])
        for y in region['region_type_colors']:
            rec_draw_position = (start_position,
                                 (start_position[0] + size_of_legend[0], start_position[1] + size_of_legend[1]))
            draw.rectangle(xy=rec_draw_position,
                           outline=(0, 0, 0),
                           fill=tuple(region['region_type_colors'][y]))
            text_draw_position = (rec_draw_position[0][0], rec_draw_position[0][1] - gap / 2)
            draw.text(xy=text_draw_position, text=y, fill=(0, 0, 0))

            start_position = (start_position[0] + gap + size_of_legend[0], start_position[1]) \
                if start_position[0] + gap + 2 * size_of_legend[0] < image_with \
                else (gap, start_position[1] + gap + size_of_legend[1])
    #from matplotlib import pyplot as plt
    #plt.imshow(c_image)
    #plt.show()
    return c_image
