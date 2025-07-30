import argparse
import os
from artbot.fetch_images import ImageFetcher
from artbot.pixel_to_ascii import PixelToASCII
from PIL import Image, ImageFilter

def cli_mode(args):
    """Mode CLI pour le traitement d'images

    Args:
        args (argparse.Namespace): Les arguments de la ligne de commande
    """
    try:
        img_urls = ImageFetcher.scrape_images(args.url)
        if len(img_urls) < args.index or args.index < 1:
            print(f" Il n’y a que {len(img_urls)} images trouvees, impossible d’acceder à l’index {args.index}")
            return

        img_url = img_urls[args.index - 1]
        image_path = os.path.join("img", "img.jpg")
        os.makedirs("img", exist_ok=True)

        response = ImageFetcher.download_single_image(img_url, image_path)
        if not response:
            print(" Telechargement echoue.")
            return

        image = Image.open(image_path)

        # Resize
        aspect_ratio = image.height / image.width
        new_height = int(aspect_ratio * args.size)
        image = image.resize((args.size, new_height))

        if args.blur > 0:
            image = image.filter(ImageFilter.GaussianBlur(args.blur))

        # Enregistrer image traitee
        processed_image_path = os.path.join("img", "processed_img.jpg")
        image = image.convert("L")  # Convertit en niveaux de gris
        image.save(processed_image_path)

        # ASCII
        ascii_art = PixelToASCII.image_to_ascii(image, width=args.size)
        os.makedirs("result", exist_ok=True)
        output_path = "result/ascii_art.html"
        PixelToASCII.save_ascii_to_html(ascii_art, output_path)

        print(f" ASCII art genere dans {output_path}")

    except Exception as e:
        print(f" Erreur : {e}")

def serve_api():
    """    Lancer l'API FastAPI pour servir l'ASCII art
    """
    import uvicorn
    uvicorn.run("artbot.api:app", host="0.0.0.0", port=8000, reload=True)

def main():
    """Point d'entrée principal pour l'application Artbot.
    """
    parser = argparse.ArgumentParser(description="Artbot CLI et API")
    parser.add_argument("--serve", action="store_true", help="Lancer l’API FastAPI")
    parser.add_argument("--url", help="URL de la page web contenant des images")
    parser.add_argument("--index", type=int, help="Indice de l’image à utiliser (commence à 1)")
    parser.add_argument("--blur", type=int, default=0, help="Flou gaussien")
    parser.add_argument("--size", type=int, default=100, help="Largeur de l’ASCII art")

    args = parser.parse_args()

    if args.serve:
        serve_api()
    elif args.url and args.index:
        cli_mode(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
