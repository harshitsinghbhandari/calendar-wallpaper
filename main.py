from PIL import Image, ImageDraw, ImageFont
import math
import requests
import textwrap
from datetime import datetime

def get_stoic_quote(max_retries=5):
    """
    Fetches a Stoic quote.
    Retries if the quote is too long (roughly > 2 lines).
    Returns (quote, author) or None if failed.
    """
    url = "https://stoic.tekloon.net/stoic-quote"
    
    # Approx char limit for 2 lines at large font sizes
    # We'll refine this logic, but let's say ~140 chars is a safe bet for 2 lines 
    # dependent on font size, but the user asked for "if bigger than a specific length (two lines) then retry".
    MAX_LENGTH = 80

    for _ in range(max_retries):
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                quote = data.get("quote", "")
                author = data.get("author", "")
                if quote and len(quote) <= MAX_LENGTH:
                    return quote, author
        except:
            pass
            
    return None

def life_wallpaper(
    total,
    done,
    width=1179,
    height=2556,
    output_path="life_wallpaper.png"
):
    assert 0 <= done <= total

    # Colors
    BG = (0, 0, 0)
    ORANGE = (255, 165, 0)
    GREY = (120, 120, 120)
    TEXT = (200, 200, 200)

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # ---- Fonts (fallback-safe) ----
    try:
        year_font = ImageFont.truetype("Zalando.ttf", 100)
        quote_font = ImageFont.truetype("Zalando.ttf", 48)
        author_font = ImageFont.truetype("Zalando.ttf", 36)
        percent_font = ImageFont.truetype("Zalando.ttf", 56)
    except:
        year_font = ImageFont.load_default()
        quote_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        percent_font = ImageFont.load_default()

    # ---- 1. Calculate Grid Dimensions ----
    if total <= 40:
        dots_per_row = 5
    elif total <= 100:
        dots_per_row = 10
    else:
        dots_per_row = 20

    rows = math.ceil(total / dots_per_row)

    dot_radius = 10
    spacing = dot_radius * 3

    grid_width = dots_per_row * spacing
    grid_height = rows * spacing
    
    # ---- 2. Prepare Quote Content (Measure, don't draw yet) ----
    quote_data = get_stoic_quote()
    quote_lines = []
    author_text = ""
    quote_block_height = 0
    
    if quote_data:
        quote_text, author_raw = quote_data
        author_text = f"- {author_raw}"
        
        # Approx 30 chars per line
        quote_lines = textwrap.wrap(quote_text, width=30)
        
        # Calculate total height of quote block
        temp_y = 0
        for line in quote_lines:
            # Measure line height
            bbox = draw.textbbox((0, 0), line, font=quote_font)
            line_h = bbox[3] - bbox[1]
            temp_y += line_h + 10 # line spacing
            
        # Add author spacing + height
        temp_y += 10 # padding before author
        bbox_auth = draw.textbbox((0, 0), author_text, font=author_font)
        temp_y += (bbox_auth[3] - bbox_auth[1])
        
        quote_block_height = temp_y

    # ---- 3. Calculate Positions ----
    # User wants dots "a little below" and quote "just above it".
    # Let's center the grid roughly at 60% of the screen height.
    grid_center_y = int(height * 0.6)
    start_y = grid_center_y - (grid_height // 2)
    start_x = (width - grid_width) // 2
    
    # Quote sits above the grid
    quote_start_y = start_y - quote_block_height - 80 # 80px padding between quote and dots

    # ---- 4. Draw Quote ----
    if quote_data:
        current_qy = quote_start_y
        for line in quote_lines:
            w, h = draw.textbbox((0, 0), line, font=quote_font)[2:]
            draw.text(((width - w) // 2, current_qy), line, fill=TEXT, font=quote_font)
            current_qy += (h + 10)
            
        current_qy += 10
        w, h = draw.textbbox((0, 0), author_text, font=author_font)[2:]
        draw.text(((width - w) // 2, current_qy), author_text, fill=GREY, font=author_font)

    # ---- 5. Draw Grid ----
    for i in range(total):
        row = i // dots_per_row
        col = i % dots_per_row

        x = start_x + col * spacing
        y = start_y + row * spacing

        color = ORANGE if i < done else GREY

        draw.ellipse(
            [
                x - dot_radius,
                y - dot_radius,
                x + dot_radius,
                y + dot_radius
            ],
            fill=color
        )

    # ---- Bottom: Percentage ----
    percent = int((done / total) * 100)
    percent_text = f"{percent}% completed"

    p_w, p_h = draw.textbbox((0, 0), percent_text, font=percent_font)[2:]
    
    # Position: Halfway between end of dots and end of page
    dots_bottom_y = start_y + grid_height
    available_bottom_space = height - dots_bottom_y
    percent_y = dots_bottom_y + (available_bottom_space - p_h) // 2
    
    draw.text(
        ((width - p_w) // 2, percent_y),
        percent_text,
        fill=TEXT,
        font=percent_font
    )

    if output_path:
        img.save(output_path)
        return output_path
    else:
        return img

if __name__ == "__main__":
    life_wallpaper(total=365, done=24, output_path="life_wallpaper.png")
