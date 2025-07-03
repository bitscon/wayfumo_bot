import textwrap
from image_config import IMAGE_GENERATOR

# Import Pillow functions
from PIL import Image, ImageDraw, ImageFont

def create_image_pillow(text, output_path="wayfumo_post.png"):
    """
    Generates image using Pillow (default local text-based generator).
    """
    img = Image.new('RGB', (1080, 1080), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    lines = textwrap.wrap(text, width=20)
    y_text = 200
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        draw.text(((1080 - width) / 2, y_text), line, font=font, fill=(255, 255, 255))
        y_text += height + 10
    img.save(output_path)
    return output_path

def create_image_dalle(text, output_path="wayfumo_post.png"):
    """
    Placeholder function for DALL-E integration.
    To implement: call your DALL-E API, save output to output_path.
    """
    print("⚠️ DALL-E image generation not implemented yet.")
    return None

def create_image_sd(text, output_path="wayfumo_post.png"):
    """
    Placeholder function for Stable Diffusion integration.
    To implement: call your SD API, save output to output_path.
    """
    print("⚠️ Stable Diffusion image generation not implemented yet.")
    return None

def create_image(text, output_path="wayfumo_post.png"):
    """
    Master image creation function that routes to selected generator.
    """
    if IMAGE_GENERATOR == "pillow":
        return create_image_pillow(text, output_path)
    elif IMAGE_GENERATOR == "dalle":
        return create_image_dalle(text, output_path)
    elif IMAGE_GENERATOR == "stablediffusion":
        return create_image_sd(text, output_path)
    else:
        print("⚠️ Unknown image generator selected in config. Defaulting to Pillow.")
        return create_image_pillow(text, output_path)
