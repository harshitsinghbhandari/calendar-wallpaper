from PIL import Image, ImageDraw, ImageFont
import math
import requests
import textwrap
from datetime import datetime
import calendar

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

def year_wallpaper(
    year=None,
    width=1179,
    height=2556,
    output_path="year_wallpaper.png"
):
    """
    Generates a wallpaper showing the progress of the year with a 3x4 month grid.
    Each month cluster has 7 dots in a row.
    """
    import calendar
    from datetime import datetime
    
    # Defaults
    if year is None:
        now = datetime.now()
        year = now.year
        current_day_of_year = now.timetuple().tm_yday
        # Check for leap year to be precise
        is_leap = calendar.isleap(year)
        total_days_in_year = 366 if is_leap else 365
    else:
        # If a specific year is requested, we might need current date context or just show full/empty
        # For simplicity, if it's the current year, use current progress. 
        # If past, 100%. If future, 0%.
        now = datetime.now()
        if year < now.year:
            current_day_of_year = 367 # All done
        elif year > now.year:
            current_day_of_year = 0
        else:
            current_day_of_year = now.timetuple().tm_yday
    
    # Colors
    BG = (0, 0, 0)
    ORANGE = (255, 165, 0)
    GREY = (50, 50, 50)
    TEXT = (200, 200, 200)

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        header_font = ImageFont.truetype("Zalando.ttf", 80)
        month_font = ImageFont.truetype("Zalando.ttf", 40)
        quote_font = ImageFont.truetype("Zalando.ttf", 40)
        author_font = ImageFont.truetype("Zalando.ttf", 30)
    except:
        header_font = ImageFont.load_default()
        month_font = ImageFont.load_default()
        quote_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Layout Config
    # 3 cols x 4 rows
    # Each month: 7 columns of dots.
    # Max days in a month is 31. 31 / 7 = 4.4 -> 5 rows of dots per month max.
    
    dot_radius = 8
    dot_spacing = 28 # Space between dot centers
    
    # Month block size estimation
    # Width: 7 dots * spacing
    month_block_w = 7 * dot_spacing
    # Height: 5 rows * spacing (approx) + text header
    month_block_h = (6 * dot_spacing) + 40 # +40 for month name
    
    # Grid gaps
    col_gap = 60
    row_gap = 80
    
    # Total grid dimensions
    total_grid_w = (3 * month_block_w) + (2 * col_gap)
    total_grid_h = (4 * month_block_h) + (3 * row_gap)
    
    start_x = (width - total_grid_w) // 2
    # Vertically center but leave space for header/quote
    # specific request: "User wants dots a little below and quote just above it" implicitly from previous context?
    # Let's align similarly to life_wallpaper, centered-ish.
    start_y = (height - total_grid_h) // 2 + 100 

    # --- Header (Year) ---
    header_text = f"{year}"
    bbox = draw.textbbox((0, 0), header_text, font=header_font)
    h_w = bbox[2] - bbox[0]
    draw.text(((width - h_w) // 2, 150), header_text, fill=TEXT, font=header_font)

    # --- Draw Months ---
    # We need to track global day count to know if a dot is "done"
    day_counter = 0
    
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Days in each month
    # calendar.monthrange(year, month) returns (weekday, days_in_month)
    
    for i, month_name in enumerate(months):
        m_idx = i + 1 # 1-12
        _, num_days = calendar.monthrange(year, m_idx)
        
        # Grid position (row 0-3, col 0-2)
        grid_r = i // 3
        grid_c = i % 3
        
        mx = start_x + grid_c * (month_block_w + col_gap)
        my = start_y + grid_r * (month_block_h + row_gap)
        
        # Draw Month Name
        # bbox_m = draw.textbbox((0, 0), month_name, font=month_font)
        # mw = bbox_m[2] - bbox_m[0]
        # Center month name over its block
        # draw.text((mx + (month_block_w - mw)//2, my), month_name, fill=TEXT, font=month_font)
        # Actually user didn't explicitly ask for names, but it helps. Let's keep it minimal or use numbers closer to dots? 
        # Requirement: "Show the year... month clustered".
        # Let's put month name.
        draw.text((mx, my), month_name, fill=TEXT, font=month_font)
        
        dots_start_y = my + 50
        
        # Draw Dots for the month
        for d in range(num_days):
            day_counter += 1
            
            # 7 dots per row within month
            d_row = d // 7
            d_col = d % 7
            
            dx = mx + d_col * dot_spacing
            dy = dots_start_y + d_row * dot_spacing
            
            # Determine color
            # If day_counter <= current_day_of_year -> Orange
            if day_counter < current_day_of_year:
                 color = ORANGE
            elif day_counter == current_day_of_year:
                 # Today is active/orange
                 color = ORANGE 
            else:
                 color = GREY
            
            draw.ellipse(
                [dx, dy, dx + dot_radius * 2, dy + dot_radius * 2],
                fill=color
            )

    # --- Quote (Optional but good for consistency) ---
    quote_data = get_stoic_quote()
    if quote_data:
        q_text, q_auth = quote_data
        q_lines = textwrap.wrap(q_text, width=40)
        
        # Calculate total height
        total_q_h = 0
        line_heights = []
        for line in q_lines:
             bbox = draw.textbbox((0,0), line, font=quote_font)
             lh = bbox[3] - bbox[1]
             line_heights.append(lh)
             total_q_h += lh + 10 # line spacing
        
        # Add author
        q_auth = f"- {q_auth}"
        bbox = draw.textbbox((0,0), q_auth, font=author_font)
        ah = bbox[3] - bbox[1]
        total_q_h += ah + 20 # padding before author
        
        # Position slightly above grid
        # start_y is top of grid. 
        # We want the bottom of the quote block to be e.g. 50px above start_y
        current_y = start_y - total_q_h - 50
        
        # Ensure it doesn't overlap header (header is around y=150 + height ~80 = 230)
        # If current_y < 250, we might need to adjust or clamp. 
        # But let's assume standard mobile dims (height=2556) gives plenty of space.
        
        # Draw
        for idx, line in enumerate(q_lines):
             bbox = draw.textbbox((0,0), line, font=quote_font)
             lw = bbox[2] - bbox[0]
             draw.text(((width - lw)//2, current_y), line, fill=TEXT, font=quote_font)
             current_y += line_heights[idx] + 10
             
        bbox = draw.textbbox((0,0), q_auth, font=author_font)
        aw = bbox[2] - bbox[0]
        draw.text(((width - aw)//2, current_y + 10), q_auth, fill=GREY, font=author_font)

    if output_path:
        img.save(output_path)
        return output_path
    else:
        return img

if __name__ == "__main__":
    life_wallpaper(total=365, done=24, output_path="life_wallpaper.png")
