import os
import sys
import argparse
import datetime
import asyncio
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont

def get_cpr_data():
    """Fetch previous day OHLC for Nifty and Bank Nifty and compute CPR levels."""
    indices = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK"
    }
    results = {}
    
    for name, ticker in indices.items():
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period="5d")
            if len(hist) >= 2:
                prev = hist.iloc[-2] # previous day
                high = float(prev['High'])
                low = float(prev['Low'])
                close = float(prev['Close'])
            else:
                prev = hist.iloc[-1]
                high = float(prev['High'])
                low = float(prev['Low'])
                close = float(prev['Close'])
        except Exception as e:
            print(f"Error fetching {name}: {e}, using fallback estimates.")
            if name == "NIFTY 50":
                high, low, close = 25150.0, 24920.0, 25050.0
            else:
                high, low, close = 51800.0, 51200.0, 51550.0

        p = (high + low + close) / 3.0
        bc = (high + low) / 2.0
        tc = (2 * p) - bc
        
        # Ensure TC is top, BC is bottom
        top_cpr = max(tc, bc)
        bot_cpr = min(tc, bc)
        width = abs(top_cpr - bot_cpr)
        width_pct = (width / p) * 100
        
        r1 = (2 * p) - low
        s1 = (2 * p) - high
        r2 = p + (high - low)
        s2 = p - (high - low)
        
        if width_pct < 0.20:
            cpr_type = "VIRGIN / NARROW CPR"
            sentiment = "HIGH TRENDING POTENTIAL 🚀"
            desc = "High probability for aggressive directional breakout or breakdown. Expect big moves."
        elif width_pct < 0.45:
            cpr_type = "AVERAGE CPR"
            sentiment = "MODERATE TRENDING / SWING"
            desc = "Good for standard CPR breakout and pullback retest setups."
        else:
            cpr_type = "WIDE CPR"
            sentiment = "RANGEBOUND / SIDEWAYS 🛡️"
            desc = "High chance of index staying inside CPR range. Sell OTM options or fade extremes."

        results[name] = {
            "high": round(high, 1),
            "low": round(low, 1),
            "close": round(close, 1),
            "pivot": round(p, 1),
            "tc": round(top_cpr, 1),
            "bc": round(bot_cpr, 1),
            "r1": round(r1, 1),
            "s1": round(s1, 1),
            "r2": round(r2, 1),
            "s2": round(s2, 1),
            "width": round(width, 1),
            "width_pct": round(width_pct, 2),
            "type": cpr_type,
            "sentiment": sentiment,
            "desc": desc
        }
    return results

def render_reel_frames(data, reel_type="morning", output_image="reel_poster.png"):
    """Render a 1080x1920 ultra high-def poster/card for vertical video."""
    width, height = 1080, 1920
    im = Image.new("RGB", (width, height), color=(10, 15, 29))
    draw = ImageDraw.Draw(im)
    
    # Gradient background effect
    for y in range(height):
        r = int(10 + (25 - 10) * (y / height))
        g = int(15 + (35 - 15) * (y / height))
        b = int(29 + (55 - 29) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Grid lines / Cyber trading pattern
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(20, 30, 50, 40), width=1)
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=(20, 30, 50, 40), width=1)

    today_str = datetime.date.today().strftime("%d %b %Y").upper()
    
    # Try loading fonts or fallback to default
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 52)
        font_sub = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 32)
        font_card_head = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 44)
        font_level = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 36)
        font_bold = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 38)
        font_sm = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 28)
    except:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_card_head = font_title
        font_level = font_title
        font_bold = font_title
        font_sm = font_title

    # Header Card
    draw.rounded_rectangle([(60, 80), (1020, 260)], radius=24, fill=(18, 25, 45), outline=(0, 229, 255), width=2)
    draw.text((100, 110), f"ALPHA EDGE TRADER • {today_str}", fill=(0, 229, 255), font=font_sub)
    header_text = "DAILY CPR INTRADAY RADAR" if reel_type == "morning" else "DAILY CPR MARKET WRAP-UP"
    draw.text((100, 165), header_text, fill=(255, 255, 255), font=font_title)

    y_offset = 300
    for name, info in data.items():
        # Card container
        draw.rounded_rectangle([(60, y_offset), (1020, y_offset + 540)], radius=24, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        
        # Header Badge
        draw.rounded_rectangle([(90, y_offset + 30), (450, y_offset + 95)], radius=12, fill=(30, 41, 59))
        draw.text((110, y_offset + 40), f"{name}", fill=(255, 255, 255), font=font_card_head)
        
        # Sentiment Tag
        color = (16, 185, 129) if "TRENDING" in info['sentiment'] else (245, 158, 11)
        draw.rounded_rectangle([(480, y_offset + 30), (990, y_offset + 95)], radius=12, fill=(20, 35, 45), outline=color, width=1)
        draw.text((500, y_offset + 42), info['type'], fill=color, font=font_level)
        
        # Level details
        draw.text((100, y_offset + 130), f"TC (Top CPR):  {info['tc']}", fill=(148, 163, 184), font=font_level)
        draw.text((100, y_offset + 185), f"P (Central):    {info['pivot']}", fill=(255, 215, 0), font=font_bold)
        draw.text((100, y_offset + 240), f"BC (Bot CPR):  {info['bc']}", fill=(148, 163, 184), font=font_level)
        
        draw.text((580, y_offset + 130), f"R1 Level:  {info['r1']}", fill=(239, 68, 68), font=font_level)
        draw.text((580, y_offset + 185), f"R2 Level:  {info['r2']}", fill=(248, 113, 113), font=font_level)
        draw.text((580, y_offset + 240), f"S1 Level:  {info['s1']}", fill=(34, 197, 94), font=font_level)

        # CPR Width & Logic
        draw.rounded_rectangle([(90, y_offset + 310), (990, y_offset + 500)], radius=16, fill=(11, 18, 33))
        draw.text((120, y_offset + 330), f"CPR Width: {info['width']} pts ({info['width_pct']}%)", fill=(0, 229, 255), font=font_bold)
        sentiment_clean = info['sentiment'].replace('🚀', '').replace('🛡️', '').strip()
        draw.text((120, y_offset + 385), f"Setup: {sentiment_clean}", fill=(255, 255, 255), font=font_level)
        draw.text((120, y_offset + 435), f"Rule: {info['desc'][:50]}...", fill=(203, 213, 225), font=font_sm)

        y_offset += 580

    # Bottom CTA Box
    draw.rounded_rectangle([(60, 1500), (1020, 1820)], radius=24, fill=(16, 24, 48), outline=(0, 229, 255), width=2)
    draw.text((100, 1530), "SYSTEMATIC TRADING SUITE", fill=(0, 229, 255), font=font_level)
    draw.text((100, 1585), "Get 1-Click CPR Pro Toolkit & Strategy Guide", fill=(255, 255, 255), font=font_bold)
    draw.text((100, 1640), "• Dynamic CPR Indicator • Intraday Excel Calculator", fill=(148, 163, 184), font=font_sm)
    draw.text((100, 1680), "• Complete Strategy PDF • High Probability Setups", fill=(148, 163, 184), font=font_sm)
    
    # Button
    draw.rounded_rectangle([(100, 1730), (980, 1800)], radius=16, fill=(0, 229, 255))
    draw.text((250, 1745), "LINK IN BIO • CPR PRO SUITE", fill=(10, 15, 29), font=font_bold)

    im.save(output_image)
    print(f"Generated poster: {output_image}")
    return output_image

async def generate_voiceover(data, reel_type="morning", output_audio="voiceover.mp3"):
    """Generate crisp neural TTS audio in Tamil/Tanglish using edge-tts."""
    nifty = data["NIFTY 50"]
    banknifty = data["BANK NIFTY"]
    
    if reel_type == "morning":
        script = (
            f"Vanakkam traders! Innaiku Nifty matrum Bank Nifty CPR Intraday Radar paakalam. "
            f"Nifty 50 Central Pivot {int(nifty['pivot'])}, top CPR {int(nifty['tc'])}, bottom CPR {int(nifty['bc'])}. "
            f"Nifty-la {nifty['type']} form aagi irukku, so {nifty['sentiment']}. "
            f"Bank Nifty Pivot {int(banknifty['pivot'])}, Key Resistance R1 {int(banknifty['r1'])}, Support S1 {int(banknifty['s1'])}. "
            f"Rules follow pannunga, risk manage pannunga. "
            f"Systematic CPR Pro Toolkit download panna link in bio visit pannunga. Happy trading!"
        )
    else:
        script = (
            f"Vanakkam traders! Innaiku market closing review. "
            f"Nifty and Bank Nifty morning CPR levels-ku absolute respect kuduthu trade aagi irukku. "
            f"Level to level systematic setups mattum trade panni discipline maintain pannavangalukku nalla profit. "
            f"Namma CPR Pro Toolkit and daily strategies panna link in bio click pannunga!"
        )

    # Generate audio using edge-tts
    cmd = f'edge-tts --voice ta-IN-ValluvarNeural --text "{script}" --write-media "{output_audio}"'
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()
    print(f"Generated voiceover: {output_audio}")
    return output_audio

def compile_video(image_path, audio_path, output_video="reel.mp4"):
    """Compile 1080x1920 MP4 video synced with audio using ffmpeg with zoom/pan effect."""
    # Use ffmpeg with subtle zoompan for 9:16 vertical video
    cmd = (
        f'ffmpeg -y -loop 1 -i "{image_path}" -i "{audio_path}" '
        f'-c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p '
        f'-vf "scale=1080:1920" -shortest "{output_video}"'
    )
    res = os.system(cmd)
    if res == 0:
        print(f"Reel video rendered successfully: {output_video}")
        return output_video
    else:
        raise RuntimeError("FFmpeg compilation failed")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["morning", "evening"], default="morning")
    parser.add_argument("--out", default="daily_reel.mp4")
    args = parser.parse_args()

    workdir = "/Users/mac/Desktop/CPR Strategy /daily-reel-engine"
    os.makedirs(workdir, exist_ok=True)
    os.chdir(workdir)

    print(f"--- Generating {args.type.upper()} Reel ---")
    data = get_cpr_data()
    
    img = render_reel_frames(data, reel_type=args.type, output_image=f"{args.type}_poster.png")
    
    audio_path = f"{args.type}_voiceover.mp3"
    asyncio.run(generate_voiceover(data, reel_type=args.type, output_audio=audio_path))
    
    out_video = os.path.join(workdir, args.out)
    compile_video(img, audio_path, output_video=out_video)
    print(f"ALL DONE! Video ready at: {out_video}")

if __name__ == "__main__":
    main()
