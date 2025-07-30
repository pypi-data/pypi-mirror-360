from PIL import Image
import html


class PixelToASCII:
    """A class to convert images to ASCII art."""

    ASCII_CHARS = "@%#*+=-:. "

    @staticmethod
    def pixel_to_ascii(image):
        """Convert pixels of an image to ASCII characters.

        Args:
            image (PIL.Image): The input image to convert.

        Yields:
            str: The corresponding ASCII character for each pixel.
        """
        width, height = image.size
        for y in range(height):
            for x in range(width):
                r, g, b = image.getpixel((x, y))
                gray = int((r + g + b) / 3)
                yield PixelToASCII.ASCII_CHARS[gray * len(PixelToASCII.ASCII_CHARS) // 256]
            yield "\n"

    @staticmethod
    def image_to_ascii(image_input, width=100):
        """Convert an image to ASCII art.

        Args:
            image_input (Union[str, PIL.Image]): The input image to convert.
            width (int, optional): The width of the ASCII art. Defaults to 100.

        Returns:
            str: The generated ASCII art.
        """
        try:
            if isinstance(image_input, str):
                image = Image.open(image_input)
            else:
                image = image_input
        except Exception as e:
            print(f" Error opening image: {e}")
            return ""

        aspect_ratio = image.height / image.width
        height = max(1, int(aspect_ratio * width * 0.5))  # empêche height = 0
        image = image.resize((width, height))


        if image.mode != 'RGB':
            image = image.convert('RGB')

        ascii_str = ''.join(PixelToASCII.pixel_to_ascii(image))
        print(ascii_str)  # Debug: print the ASCII string to console
        return ascii_str

    @staticmethod
    def save_ascii_to_html(ascii_str, output_path):
        """Save ASCII art to an HTML file.
        Args:
            ascii_str (str): The ASCII art string to save.
            output_path (str): The path where the HTML file will be saved.
            
        Returns:
            None
        """
        escaped_ascii = html.escape(ascii_str)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ASCII Art</title>
    <style>
        body {{
            background-color: #111;
            color: #eee;
            padding: 20px;
            margin: 0;
        }}
        pre {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 10px;
            white-space: pre;
            line-height: 1em;
        }}
    </style>
</head>
<body>
    <pre>{escaped_ascii}</pre>
</body>
</html>
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f" ASCII art saved to {output_path}")
