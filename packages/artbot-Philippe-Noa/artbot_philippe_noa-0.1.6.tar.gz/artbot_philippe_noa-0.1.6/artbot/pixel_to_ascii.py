from PIL import Image
from PIL import ImageFilter
import html

class PixelToASCII:
    """A class to convert images to ASCII art."""

    def pixel_to_ascii(image):
        ascii_chars = "@%#*+=-:. "
        width, height = image.size
        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                gray = int((pixel[0] + pixel[1] + pixel[2]) / 3)
                yield ascii_chars[gray // 32]
            yield "\n"

    @staticmethod
    def image_to_ascii(image_input, width=100):
        from PIL import Image

        try:
            # Charger l’image si c’est un chemin
            if isinstance(image_input, str):
                image = Image.open(image_input)
            else:
                image = image_input
        except Exception as e:
            print(f"Error opening image: {e}")
            return ""

        aspect_ratio = image.height / image.width
        height = int(aspect_ratio * width)
        image = image.resize((width, height))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        ascii_str = PixelToASCII.pixel_to_ascii(image)
        ascii_str = ''.join(ascii_str)
        ascii_lines = [ascii_str[i:i + width] for i in range(0, len(ascii_str), width)]
        print("\n".join(ascii_lines))
        return "\n".join(ascii_lines)



    def save_ascii_to_html(ascii_str, output_path):
        escaped_ascii = html.escape(ascii_str)

        html_content = f"""<pre>{escaped_ascii}</pre>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ ASCII art saved to {output_path}")
