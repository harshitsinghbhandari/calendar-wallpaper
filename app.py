from fastapi import FastAPI, Response
from main import life_wallpaper, year_wallpaper
import io

app = FastAPI()

@app.get("/wallpaper")
def get_wallpaper(
    done: int,
    total: int = 365,
    width: int = 1179,
    height: int = 2556
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

@app.get("/year-wallpaper")
def get_year_wallpaper(
    year: int = None,
    width: int = 1179,
    height: int = 2556
):
    """
    Generates the year wallpaper on demand and returns it as a PNG image.
    """
    img = year_wallpaper(
        year=year,
        width=width,
        height=height,
        output_path=None
    )
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")
