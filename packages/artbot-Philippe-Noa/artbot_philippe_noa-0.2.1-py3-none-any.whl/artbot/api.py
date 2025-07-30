from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

@app.post("/convert", response_class=HTMLResponse)
async def post_ascii_html():
    """Générer de l'ASCII art à partir d'une image

    Raises:
        HTTPException: Si le fichier HTML n'est pas trouvé

    Returns:
        HTMLResponse: La réponse contenant l'ASCII art
        
    Cette route génère de l'ASCII art à partir d'une image et renvoie le contenu HTML.
    Elle lit le fichier `ascii_art.html` depuis le répertoire `result` et le renvoie en tant que réponse HTML.
    """
    file_path = "result/ascii_art.html"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="ascii_art.html non trouve")

    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content, status_code=200)

