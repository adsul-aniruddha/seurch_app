def render_logo(data):

    bg = data.get("background", "#fff")
    layers = data.get("layers", [])

    elements = ""

    for l in layers:
        if l["type"] == "text":
            elements += f"""
<text x="{l['x']}" y="{l['y']}" fill="{l['color']}" text-anchor="middle">
{l['value']}
</text>
"""

        elif l["type"] == "icon":
            elements += f"""
<circle cx="{l['x']}" cy="{l['y']}" r="30" fill="{l['color']}" />
"""

    return f"""
<svg width="400" height="400">
<rect width="100%" height="100%" fill="{bg}" />
{elements}
</svg>
"""