from fastapi import FastAPI, Response
from main import life_wallpaper
import io

app = FastAPI()

@app.get("/wallpaper")
def get_wallpaper(
    done: int,
    total: int = 365,
    width: int = 1080,
    height: int = 1920
):
    """
    Generates the wallpaper on demand and returns it as a PNG image.
    """
    # Generate image object (params: output_path=None returns the PIL Image)
    img = life_wallpaper(
        total=total,
        done=done,
        width=width,
        height=height,
        output_path=None
    )
    
    # Save to in-memory byte buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")
