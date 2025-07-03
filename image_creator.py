from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_image(text, output_path="wayfumo_post.png"):
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
