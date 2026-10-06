import os
import sys
import argparse
import datetime
import asyncio
from PIL import Image, ImageDraw, ImageFont

def render_trade_reel_poster(chart_image_path, trade_info, output_poster="trade_poster.png"):
    """
    Renders a stunning 1080x1920 vertical reel poster incorporating the real TradingView screenshot.
    """
    width, height = 1080, 1920
    im = Image.new("RGB", (width, height), color=(10, 15, 29))
    draw = ImageDraw.Draw(im)

    # Dark cyber trading gradient background
    for y in range(height):
        r = int(10 + (22 - 10) * (y / height))
        g = int(14 + (30 - 14) * (y / height))
        b = int(28 + (48 - 28) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Grid background pattern
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(20, 30, 50), width=1)
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=(20, 30, 50), width=1)

    today_str = datetime.date.today().strftime("%d %b %Y").upper()

    try:
        font_badge = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 30)
        font_title = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 50)
        font_hero = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 64)
        font_card_head = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 38)
        font_bold = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 40)
        font_val = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 34)
        font_sm = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 26)
    except:
        font_badge = ImageFont.load_default()
        font_title = font_badge
        font_hero = font_badge
        font_card_head = font_badge
        font_bold = font_badge
        font_val = font_badge
        font_sm = font_badge

    is_evening = (trade_info.get("mode") == "evening")
    status_label = "TARGET HIT • 100% PROFIT" if is_evening else "NEW INTRADAY CPR ENTRY"
    status_color = (16, 185, 129) if is_evening else (0, 229, 255)

    # 1. Header Section
    draw.rounded_rectangle([(60, 60), (1020, 240)], radius=24, fill=(18, 25, 45), outline=status_color, width=2)
    draw.text((100, 85), f"ALPHA EDGE TRADER • {today_str}", fill=(0, 229, 255), font=font_badge)
    header_title = f"{trade_info.get('index', 'BANK NIFTY')} CPR STRATEGY"
    draw.text((100, 130), header_title, fill=(255, 255, 255), font=font_title)
    draw.text((100, 190), f"STATUS: {status_label}", fill=status_color, font=font_badge)

    # 2. Embed Actual TradingView Chart Screenshot
    chart = Image.open(chart_image_path)
    # Target chart area inside vertical reel: width 960, height ~600
    target_chart_w = 960
    aspect = chart.height / chart.width
    target_chart_h = int(target_chart_w * aspect)
    chart_resized = chart.resize((target_chart_w, target_chart_h), Image.Resampling.LANCZOS)

    chart_y = 270
    # Outer glow box for screenshot
    draw.rounded_rectangle([(55, chart_y - 5), (1025, chart_y + target_chart_h + 5)], radius=20, fill=(15, 23, 42), outline=status_color, width=3)
    im.paste(chart_resized, (60, chart_y))

    # 3. Big Metric Profit Cards below screenshot
    stats_y = chart_y + target_chart_h + 40
    
    if is_evening:
        # Big Green Profit Hero Banner
        draw.rounded_rectangle([(60, stats_y), (1020, stats_y + 150)], radius=20, fill=(10, 40, 30), outline=(16, 185, 129), width=2)
        draw.text((100, stats_y + 20), "NET TRADE PROFIT", fill=(148, 163, 184), font=font_sm)
        draw.text((100, stats_y + 55), f"+Rs {trade_info.get('profit', '1,610')}", fill=(16, 185, 129), font=font_hero)
        draw.text((650, stats_y + 20), "POINTS CAPTURED", fill=(148, 163, 184), font=font_sm)
        draw.text((650, stats_y + 55), f"+{trade_info.get('points', '107.3')} pts", fill=(0, 229, 255), font=font_hero)

        # Execution Details Grid
        grid_y = stats_y + 180
        draw.rounded_rectangle([(60, grid_y), (520, grid_y + 160)], radius=18, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        draw.text((90, grid_y + 25), "ENTRY PRICE", fill=(148, 163, 184), font=font_sm)
        draw.text((90, grid_y + 65), f"Rs {trade_info.get('entry', '55,080')}", fill=(255, 255, 255), font=font_bold)
        draw.text((90, grid_y + 115), "Trigger: 1-Hr CPR Breakout", fill=(0, 229, 255), font=font_sm)

        draw.rounded_rectangle([(560, grid_y), (1020, grid_y + 160)], radius=18, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        draw.text((590, grid_y + 25), "TARGET EXIT", fill=(148, 163, 184), font=font_sm)
        draw.text((590, grid_y + 65), f"Rs {trade_info.get('exit', '55,194')}", fill=(16, 185, 129), font=font_bold)
        draw.text((590, grid_y + 115), "Win Rate: 100% (1/1)", fill=(16, 185, 129), font=font_sm)
        
        card_end_y = grid_y + 160
    else:
        # Morning Entry Banner
        draw.rounded_rectangle([(60, stats_y), (1020, stats_y + 150)], radius=20, fill=(16, 30, 50), outline=(0, 229, 255), width=2)
        draw.text((100, stats_y + 20), "NEW ENTRY TRIGGERED", fill=(148, 163, 184), font=font_sm)
        draw.text((100, stats_y + 55), f"BUY @ {trade_info.get('entry', '55,080')}", fill=(0, 229, 255), font=font_hero)
        draw.text((650, stats_y + 20), "TARGET LEVEL", fill=(148, 163, 184), font=font_sm)
        draw.text((650, stats_y + 55), f"{trade_info.get('exit', '55,194')}", fill=(16, 185, 129), font=font_hero)

        grid_y = stats_y + 180
        draw.rounded_rectangle([(60, grid_y), (1020, grid_y + 140)], radius=18, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        draw.text((90, grid_y + 25), "SETUP RULES", fill=(148, 163, 184), font=font_sm)
        draw.text((90, grid_y + 65), "CPR Breakout Confirmed • Strict SL Maintained", fill=(255, 255, 255), font=font_bold)
        card_end_y = grid_y + 140

    # 4. Strategy & Call to Action Box
    cta_y = max(card_end_y + 40, 1540)
    draw.rounded_rectangle([(60, cta_y), (1020, 1820)], radius=24, fill=(16, 24, 48), outline=(0, 229, 255), width=2)
    draw.text((100, cta_y + 25), "SYSTEMATIC CPR MASTER STRATEGY", fill=(0, 229, 255), font=font_card_head)
    draw.text((100, cta_y + 75), "Want this Exact Pine Script Indicator & Strategy?", fill=(255, 255, 255), font=font_bold)
    draw.text((100, cta_y + 125), "• Complete Pine Script Code • Daily Intraday Calculator • PDF Guide", fill=(148, 163, 184), font=font_sm)
    
    # Button
    draw.rounded_rectangle([(100, cta_y + 180), (980, cta_y + 245)], radius=16, fill=(0, 229, 255))
    draw.text((230, cta_y + 195), "LINK IN BIO • GET CPR PRO TOOLKIT", fill=(10, 15, 29), font=font_bold)

    im.save(output_poster)
    print(f"Generated trade reel poster: {output_poster}")
    return output_poster

async def generate_trade_voiceover(trade_info, output_audio="trade_voiceover.mp3"):
    """Generate Tamil AI voiceover for the trade result or entry."""
    is_evening = (trade_info.get("mode") == "evening")
    index = trade_info.get("index", "Bank Nifty")
    pts = trade_info.get("points", "107.3")
    profit = trade_info.get("profit", "1,610")
    entry = trade_info.get("entry", "55,080")
    exit_p = trade_info.get("exit", "55,194")

    if is_evening:
        script = (
            f"Vanakkam traders! Innaiku namma {index} 1-Hour CPR Master Strategy-la awesome target hit aagi irukku! "
            f"Entry {entry}-la buy panni, exact-aa target {exit_p} hit panniduchu. "
            f"Single trade-la plus {pts} points capture aagi, total profit {profit} rupees book panniyachi! "
            f"No emotion, hundred percent math and discipline. "
            f"Indha exact Pine Script and CPR Pro Toolkit-ah link in bio click panni download pannunga!"
        )
    else:
        script = (
            f"Vanakkam traders! Innaiku {index}-la fresh CPR breakout entry trigger aagi irukku. "
            f"Entry level {entry}, target level {exit_p}. Strict stop loss maintain panni discipline-aa trade execute panniyachi. "
            f"Target hit aagudhaannu evening wrap-up reel-la paakalam. Happy trading!"
        )

    cmd = f'edge-tts --voice ta-IN-ValluvarNeural --text "{script}" --write-media "{output_audio}"'
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()
    print(f"Generated voiceover: {output_audio}")
    return output_audio

def compile_trade_video(image_path, audio_path, output_video="trade_reel.mp4"):
    """Compile 1080x1920 MP4 video synced with audio using ffmpeg."""
    cmd = (
        f'ffmpeg -y -loop 1 -i "{image_path}" -i "{audio_path}" '
        f'-c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p '
        f'-vf "scale=1080:1920" -shortest "{output_video}"'
    )
    res = os.system(cmd)
    if res == 0:
        print(f"Trade Reel compiled successfully: {output_video}")
        return output_video
    else:
        raise RuntimeError("FFmpeg compilation failed")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to TradingView screenshot")
    parser.add_argument("--mode", choices=["morning", "evening"], default="evening")
    parser.add_argument("--index", default="BANK NIFTY")
    parser.add_argument("--entry", default="55,080")
    parser.add_argument("--exit", default="55,194")
    parser.add_argument("--points", default="107.3")
    parser.add_argument("--profit", default="1,610")
    parser.add_argument("--out", default="evening_profit_reel.mp4")
    args = parser.parse_args()

    trade_info = {
        "mode": args.mode,
        "index": args.index,
        "entry": args.entry,
        "exit": args.exit,
        "points": args.points,
        "profit": args.profit
    }

    poster = render_trade_reel_poster(args.image, trade_info, output_poster="trade_result_poster.png")
    audio = "trade_result_voiceover.mp3"
    asyncio.run(generate_trade_voiceover(trade_info, output_audio=audio))
    compile_trade_video(poster, audio, output_video=args.out)
    print(f"TRADE REEL READY: {args.out}")

if __name__ == "__main__":
    main()
