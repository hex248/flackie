import display
import navigation
from PIL import Image, ImageDraw, ImageFont

#########################
# DISPLAY & IMAGE SETUP #
#########################
top_image = None
top_draw = None
bottom_image = None
bottom_draw = None

padding = 10

font_cache = {}
def get_font(path, size):
    key = (path, size)
    if key not in font_cache:
        font_cache[key] = ImageFont.truetype(path, size)
    return font_cache[key]

second_font = None
main_font = None

def init_ui():
    global top_image, top_draw, bottom_image, bottom_draw, second_font, main_font
    
    display.init([0,1,2])
    images = display.get_images()

    top_image = Image.new("RGB", (images["1"].width, images["1"].height), "BLACK")
    top_draw = ImageDraw.Draw(top_image)
    bottom_image = Image.new("RGB", (images["2"].width, images["2"].height), "BLACK")
    bottom_draw = ImageDraw.Draw(bottom_image)
    
    second_font = get_font("./fonts/JetBrainsMono-Regular.ttf", 12)
    main_font = get_font("./fonts/JetBrainsMono-Regular.ttf", 30)

def draw(current_playback_state, title: str, album: str, artist: str, img: Image.Image, progress, length, displays: list[int] = [0,1,2]):
    current_level_idx = navigation.get_current_level_idx()
    
    if 0 in displays:
        if img is not None:
            #############
            # COVER ART #
            #############
            display.draw_to(0, img)
    
    if 1 in displays:
        # clear image
        top_draw.rectangle((0, 0, top_image.width, top_image.height), fill="BLACK")

        ###############
        # NAV OPTIONS #
        ###############
        top_draw.text((top_image.width/2 - 72, 0), "artist  album  track", "WHITE", font=second_font)
        x_coords = [(8, 51), (66, 101), (116, 152)]
        
        #################
        # NAV SELECTION #
        #################
        if current_level_idx == 0:
            top_draw.rectangle((x_coords[0][0], 16, x_coords[0][1], 17), fill="WHITE")
            text = artist
        elif current_level_idx == 1:
            top_draw.rectangle((x_coords[1][0], 16, x_coords[1][1], 17), fill="WHITE")
            text = album
        elif current_level_idx == 2:
            top_draw.rectangle((x_coords[2][0], 16, x_coords[2][1], 17), fill="WHITE")
            text = title
        else:
            text = "unknown"
        
        #################
        # SELECTED ITEM #
        #################
        font_size = 36
        font = get_font("./fonts/JetBrainsMono-SemiBold.ttf", font_size)

        bbox = top_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        while text_width > top_image.width - 2 * padding and font_size > 6:
            font_size -= 1
            font = get_font("./fonts/JetBrainsMono-SemiBold.ttf", font_size)
            bbox = top_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

        text_x = (top_image.width - text_width) // 2
        text_y = ((top_image.height - text_height) // 2) - (font_size / 4)
        top_draw.text((text_x, text_y + 10), text, "WHITE", font=font, stroke_fill="BLACK", stroke_width=1)

        display.draw_to(1, top_image)
    
    if 2 in displays:
        bottom_draw.rectangle((0, 0, bottom_image.width, bottom_image.height), fill="BLACK")

        if current_playback_state is not None:
            #######################
            # CURRENT TRACK TITLE #
            #######################
            font_size = 36
            font = get_font("./fonts/JetBrainsMono-SemiBold.ttf", font_size)
            bbox = bottom_draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            while text_width > bottom_image.width - 2 * padding and font_size > 10:
                font_size -= 1
                font = get_font("./fonts/JetBrainsMono-SemiBold.ttf", font_size)
                bbox = bottom_draw.textbbox((0, 0), title, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            
            text_x = (bottom_image.width - text_width) // 2
            text_y = ((bottom_image.height - text_height) // 2) - (font_size / 4)
            bottom_draw.text((text_x, text_y), title, "WHITE", font=font, stroke_fill="BLACK", stroke_width=1)
        

            ##########################
            # CURRENT PLAYBACK STATE #
            ##########################
            if current_playback_state == True:
                bottom_draw.text((0, 0), f"PLAYING", "WHITE", font=second_font, stroke_fill="BLACK", stroke_width=1)
            elif current_playback_state == False:
                bottom_draw.text((0, 0), f"PAUSED", "WHITE", font=second_font, stroke_fill="BLACK", stroke_width=1)
        
        else:
            bottom_draw.text((0, 0 ), "none", "WHITE", font=second_font, stroke_fill="BLACK", stroke_width=1)

        ################
        # PROGRESS BAR #
        ################
        if length > 0:
            progress_percent = progress / length
        else:
            progress_percent = 0

        progress_bar_height = 6

        start_x = padding
        start_y = bottom_image.height - padding - progress_bar_height
        end_x = bottom_image.width - padding
        end_y = start_y + progress_bar_height

        progress_width = int((end_x-start_x) * progress_percent)
        bottom_draw.rectangle((start_x, start_y, start_x + progress_width, end_y), fill="#c13f3f")
        bottom_draw.rectangle((start_x, start_y, end_x, end_y), outline="#c13f3f")


        #########################
        # DRAW IMAGE TO DISPLAY #
        #########################
        display.draw_to(2, bottom_image)
