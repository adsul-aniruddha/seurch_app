def generate_ai_logo(prompt: str):

    if "food" in prompt.lower():
        return {
            "background": "#fff",
            "layers": [
                {"type": "text", "value": "Food App", "x": 200, "y": 200, "color": "#ff0000"}
            ]
        }

    return {
        "background": "#000",
        "layers": [
            {"type": "text", "value": "My Logo", "x": 200, "y": 200, "color": "#fff"}
        ]
    }