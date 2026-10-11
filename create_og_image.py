from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

def create_og_image():
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), (6, 12, 27, 255))
    draw = ImageDraw.Draw(img)

    # 1. Background gradient
    for y in range(H):
        ratio = y / H
        r = int(6 + 8 * math.sin(ratio * math.pi))
        g = int(12 + 12 * math.sin(ratio * math.pi))
        b = int(27 + 25 * math.sin(ratio * math.pi))
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # 2. Ambient Glow (Navy / Electric Blue and Gold)
    glow_blue = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_gb = ImageDraw.Draw(glow_blue)
    draw_gb.ellipse([-100, -100, 500, 500], fill=(59, 130, 246, 40))
    draw_gb.ellipse([100, 300, 600, 750], fill=(30, 64, 175, 30))
    glow_blue = glow_blue.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img, glow_blue)

    # 3. Portrait image on the right
    photo_path = "assets/foto-alan-marinho.jpg"
    try:
        photo = Image.open(photo_path).convert("RGBA")
        # Resize photo to fit height
        target_h = 630
        aspect = photo.width / photo.height
        target_w = int(target_h * aspect)
        photo_resized = photo.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # Create gradient alpha mask for seamless blend on left edge
        mask = Image.new("L", (target_w, target_h), 255)
        fade_width = 220
        for x in range(fade_width):
            alpha = int(255 * (x / fade_width) ** 1.5)
            for y in range(target_h):
                mask.putpixel((x, y), alpha)

        photo_resized.putalpha(mask)

        # Paste on right
        paste_x = W - target_w + 30
        img.paste(photo_resized, (paste_x, 0), photo_resized)
    except Exception as e:
        print(f"Error loading photo: {e}")

    # Re-draw for text
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_bold = "C:/Windows/Fonts/segoeuib.ttf"
    font_reg = "C:/Windows/Fonts/segoeui.ttf"

    font_badge = ImageFont.truetype(font_bold, 18)
    font_title = ImageFont.truetype(font_bold, 64)
    font_subtitle = ImageFont.truetype(font_reg, 28)
    font_pills = ImageFont.truetype(font_bold, 17)
    font_quote = ImageFont.truetype(font_reg, 20)

    # 4. Badge "CONSULTORIA EMPRESARIAL"
    badge_x, badge_y = 70, 75
    badge_text = "CONSULTORIA & GESTÃO ESTRATÉGICA"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0] + 36
    bh = bbox[3] - bbox[1] + 16

    # Badge background
    draw.rounded_rectangle([badge_x, badge_y, badge_x + bw, badge_y + bh], radius=16, fill=(15, 28, 55, 230), outline=(212, 168, 83, 160), width=1)
    # Badge gold dot
    draw.ellipse([badge_x + 14, badge_y + bh//2 - 4, badge_x + 22, badge_y + bh//2 + 4], fill=(212, 168, 83, 255))
    draw.text((badge_x + 30, badge_y + 8), badge_text, font=font_badge, fill=(212, 168, 83, 255))

    # 5. Name Title
    title_y = badge_y + bh + 30
    draw.text((70, title_y), "Alan ", font=font_title, fill=(248, 250, 252, 255))
    alan_w = draw.textbbox((0, 0), "Alan ", font=font_title)[2]
    draw.text((70 + alan_w, title_y), "Marinho", font=font_title, fill=(224, 188, 110, 255))

    # 6. Subtitle
    sub_y = title_y + 85
    draw.text((70, sub_y), "Administrador · Consultor de Resultados", font=font_subtitle, fill=(147, 197, 253, 255))

    # 7. Divider Line with gold gradient accent
    div_y = sub_y + 55
    draw.line([(70, div_y), (250, div_y)], fill=(212, 168, 83, 200), width=3)
    draw.line([(250, div_y), (520, div_y)], fill=(37, 99, 235, 100), width=1)

    # 8. Description / Pillars
    quote_y = div_y + 28
    draw.text((70, quote_y), "Transformando desafios empresariais em", font=font_quote, fill=(203, 213, 225, 240))
    draw.text((70, quote_y + 28), "crescimento sustentável e alta eficiência.", font=font_quote, fill=(203, 213, 225, 240))

    # 9. Feature Tags (Pills)
    pills = ["Gestão de Negócios", "Planejamento Financeiro", "Projetos & RH"]
    pill_x = 70
    pill_y = quote_y + 85
    for p in pills:
        pb = draw.textbbox((0, 0), p, font=font_pills)
        pw = pb[2] - pb[0] + 24
        ph = pb[3] - pb[1] + 14
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pw, pill_y + ph], radius=8, fill=(16, 29, 53, 220), outline=(59, 130, 246, 120), width=1)
        draw.text((pill_x + 12, pill_y + 6), p, font=font_pills, fill=(226, 232, 240, 240))
        pill_x += pw + 12

    # 10. Subtle bottom branding
    draw.text((70, 565), "💼 alanmarinho.com.br", font=font_quote, fill=(100, 116, 139, 200))

    # Convert to RGB and save
    final_img = img.convert("RGB")
    final_img.save("assets/og-image.jpg", quality=90, optimize=True)
    print("Thumbnail gerada com sucesso: assets/og-image.jpg")

if __name__ == "__main__":
    create_og_image()
