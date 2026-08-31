import math
from PIL import Image, ImageDraw, ImageFilter

def create_icon(size):
    # Create 4x supersampled image for ultra-sharp anti-aliasing
    scale = 4
    canvas_size = size * scale
    img = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = canvas_size * 0.06
    r = canvas_size * 0.22

    # Draw rounded squircle background with modern gradient
    for y in range(int(pad), int(canvas_size - pad)):
        progress = (y - pad) / (canvas_size - 2 * pad)
        # Gradient from deep electric blue (#0ea5e9) to vibrant violet/indigo (#6366f1)
        red = int(14 + progress * (99 - 14))
        green = int(165 + progress * (102 - 165))
        blue = int(233 + progress * (241 - 233))
        draw.rounded_rectangle(
            [pad, pad, canvas_size - pad, canvas_size - pad],
            radius=r,
            fill=(red, green, blue, 255)
        )

    # Inner dark contrast plate
    inner_pad = canvas_size * 0.12
    draw.rounded_rectangle(
        [inner_pad, inner_pad, canvas_size - inner_pad, canvas_size - inner_pad],
        radius=r * 0.8,
        fill=(15, 23, 42, 245)
    )

    # Envelope base
    env_left = canvas_size * 0.22
    env_right = canvas_size * 0.78
    env_top = canvas_size * 0.35
    env_bottom = canvas_size * 0.75

    # Draw envelope body
    draw.rounded_rectangle(
        [env_left, env_top, env_right, env_bottom],
        radius=scale * 2,
        fill=(30, 41, 59, 255),
        outline=(56, 189, 248, 255),
        width=int(scale * 1.5)
    )

    # Envelope flap lines (subtle cyan)
    draw.line(
        [(env_left, env_top), (canvas_size * 0.5, env_top + (env_bottom - env_top) * 0.45), (env_right, env_top)],
        fill=(56, 189, 248, 200),
        width=int(scale * 1.2)
    )

    # Rocket / Blast symbol blasting diagonally from bottom-left to top-right
    # Supersonic rocket body (white & electric cyan)
    center_x = canvas_size * 0.52
    center_y = canvas_size * 0.48

    # Blast thruster flames (glowing amber/orange)
    flame_tip = (canvas_size * 0.30, canvas_size * 0.72)
    flame_left = (canvas_size * 0.40, canvas_size * 0.58)
    flame_right = (canvas_size * 0.48, canvas_size * 0.66)
    draw.polygon([flame_tip, flame_left, (canvas_size * 0.42, canvas_size * 0.62), flame_right], fill=(245, 158, 11, 255))
    
    # Inner flame core (yellow hot)
    inner_flame_tip = (canvas_size * 0.34, canvas_size * 0.68)
    draw.polygon([inner_flame_tip, (canvas_size * 0.41, canvas_size * 0.60), (canvas_size * 0.46, canvas_size * 0.64)], fill=(253, 224, 71, 255))

    # Rocket fuselage points
    rocket_nose = (canvas_size * 0.76, canvas_size * 0.24)
    rocket_back_left = (canvas_size * 0.42, canvas_size * 0.56)
    rocket_back_right = (canvas_size * 0.56, canvas_size * 0.70)
    rocket_tail = (canvas_size * 0.46, canvas_size * 0.60)

    # Rocket wings / fins
    fin1 = [(canvas_size * 0.40, canvas_size * 0.52), (canvas_size * 0.32, canvas_size * 0.56), (canvas_size * 0.44, canvas_size * 0.62)]
    fin2 = [(canvas_size * 0.52, canvas_size * 0.40), (canvas_size * 0.56, canvas_size * 0.32), (canvas_size * 0.62, canvas_size * 0.44)]
    draw.polygon(fin1, fill=(239, 68, 68, 255))
    draw.polygon(fin2, fill=(239, 68, 68, 255))

    # Rocket body
    draw.polygon([rocket_nose, (canvas_size * 0.68, canvas_size * 0.46), rocket_back_right, rocket_tail, rocket_back_left, (canvas_size * 0.46, canvas_size * 0.68)], fill=(248, 250, 252, 255))

    # Cockpit window (cyan bubble)
    window_x = canvas_size * 0.62
    window_y = canvas_size * 0.38
    w_r = canvas_size * 0.05
    draw.ellipse([window_x - w_r, window_y - w_r, window_x + w_r, window_y + w_r], fill=(14, 165, 233, 255))

    # Resize down with Lanczos for super clean rendering
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

for s in [16, 32, 48, 128]:
    icon = create_icon(s)
    icon.save(f'public/icons/icon{s}.png')
    print(f'Generated public/icons/icon{s}.png ({s}x{s})')

