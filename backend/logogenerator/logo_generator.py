from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import base64
from datetime import datetime
import uuid

router = APIRouter()

# ================= MODEL =================
class LogoRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

    style: str = Field(
        default="modern",
        pattern="^(modern|minimal|retro|vintage|3d|flat|gradient)$"
    )

    color: str = Field(
        default="#1E40AF",
        pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    )

    shape: str = Field(
        default="circle",
        pattern="^(circle|square|rounded|shield|hexagon)$"
    )

    font: str = Field(
        default="Roboto",
        pattern="^(Roboto|Montserrat|Poppins|Open\\+Sans|Lora)$"
    )

    size: int = Field(default=400, ge=200, le=800)

    background: str = Field(
        default="#ffffff",
        pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    )

    icon: Optional[str] = Field(
        None,
        pattern="^(star|heart|rocket|lightbulb|shield|globe)$"
    )


class LogoResponse(BaseModel):
    logo_url: str
    svg_data: str
    name: str
    request_id: str
    generated_at: datetime


# ================= STORAGE =================
generated_logos = {}

# ================= SVG LOGIC =================
def generate_svg(data: LogoRequest):
    return f"""
<svg width="{data.size}" height="{data.size}" xmlns="http://www.w3.org/2000/svg">
<rect width="100%" height="100%" fill="{data.background}" />
<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
 font-size="40" fill="{data.color}">
 {data.name}
</text>
</svg>
"""


# ================= ROUTES =================
@router.post("/generate", response_model=LogoResponse)
def generate_logo(data: LogoRequest):
    try:
        request_id = str(uuid.uuid4())

        svg = generate_svg(data)
        svg_base64 = base64.b64encode(svg.encode()).decode()

        result = LogoResponse(
            logo_url=f"data:image/svg+xml;base64,{svg_base64}",
            svg_data=svg,
            name=data.name,
            request_id=request_id,
            generated_at=datetime.now()
        )

        generated_logos[request_id] = result.dict()

        return result

    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/history/{request_id}")
def get_logo(request_id: str):
    if request_id in generated_logos:
        return generated_logos[request_id]
    raise HTTPException(404, "Not found")


@router.get("/history")
def get_all():
    return list(generated_logos.values())


# ================= EXTRA FUNCTION (FIXED) =================
def generate_logo_svg(data):
    name = data.get("name", "Logo")
    color = data.get("color", "#000")
    bg = data.get("background", "#fff")
    font = data.get("font", "Arial")
    size = data.get("size", 40)
    template = data.get("template", "modern")

    if template == "gradient":
        bg = "url(#grad)"

    return f"""
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">

<defs>
<linearGradient id="grad">
<stop offset="0%" stop-color="red"/>
<stop offset="100%" stop-color="blue"/>
</linearGradient>
</defs>

<rect width="100%" height="100%" fill="{bg}"/>

<text x="50%" y="50%"
 fill="{color}"
 font-size="{size}"
 font-family="{font}"
 text-anchor="middle"
 dominant-baseline="middle">
{name}
</text>

</svg>
"""