from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter()

# 📦 Request Schema (UPDATED)
class WebsiteRequest(BaseModel):
    name: str
    business: str
    desc: str
    features: dict = {}
    services: list = []
    contact_email: str = ""
    phone: str = ""


# 🔥 DYNAMIC TEMPLATE
def get_template(data):

    # NAVBAR LINKS DYNAMIC
    nav_links = ""
    if data.features.get("about"):
        nav_links += '<a href="#about">About</a>'
    if data.features.get("services"):
        nav_links += '<a href="#services">Services</a>'
    if data.features.get("contact"):
        nav_links += '<a href="#contact">Contact</a>'
    if data.features.get("gallery"):
        nav_links += '<a href="#gallery">Gallery</a>'

    # SERVICES HTML
    services_html = ""
    for s in data.services:
        services_html += f'<div class="card">{s}</div>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{data.business}</title>
        <meta charset="UTF-8">
        <style>
            body {{
                margin: 0;
                font-family: Arial;
                background: #0f2027;
                color: white;
            }}

            nav {{
                display: flex;
                justify-content: space-between;
                padding: 20px;
                background: #000;
            }}

            nav h2 {{ color: #00ffcc; }}

            nav a {{
                color: white;
                margin: 0 10px;
                text-decoration: none;
            }}

            .hero {{
                text-align: center;
                padding: 100px 20px;
                background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
            }}

            .hero h1 {{
                font-size: 40px;
                color: #00ffcc;
            }}

            .section {{
                padding: 60px;
                text-align: center;
            }}

            .services {{
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
            }}

            .card {{
                background: #111;
                padding: 20px;
                border-radius: 10px;
                width: 200px;
            }}

            footer {{
                background: #000;
                padding: 20px;
                text-align: center;
            }}
        </style>
    </head>

    <body>

        <!-- NAVBAR -->
        <nav>
            <h2>{data.business}</h2>
            <div>
                <a href="#">Home</a>
                {nav_links}
            </div>
        </nav>

        <!-- HERO -->
        <div class="hero">
            <h1>Welcome to {data.business}</h1>
            <p>{data.desc}</p>
        </div>
    """

    # ABOUT
    if data.features.get("about"):
        html += f"""
        <div id="about" class="section">
            <h2>About Us</h2>
            <p>Owner: {data.name}</p>
        </div>
        """

    # SERVICES
    if data.features.get("services"):
        html += f"""
        <div id="services" class="section">
            <h2>Our Services</h2>
            <div class="services">
                {services_html}
            </div>
        </div>
        """

    # CONTACT
    if data.features.get("contact"):
        html += f"""
        <div id="contact" class="section">
            <h2>Contact Us</h2>
            <p>Email: {data.contact_email}</p>
            <p>Phone: {data.phone}</p>
        </div>
        """

    # GALLERY
    if data.features.get("gallery"):
        html += """
        <div id="gallery" class="section">
            <h2>Gallery</h2>
            <p>Images coming soon...</p>
        </div>
        """

    html += f"""
        <footer>
            © 2026 {data.business} | All Rights Reserved
        </footer>

    </body>
    </html>
    """

    return html


# 🚀 API
@router.post("/create-website")
def create_website(data: WebsiteRequest):
    safe_name = data.business.replace(" ", "").lower()
    folder = f"generated_sites/{safe_name}"

    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, "index.html")

    html_content = get_template(data)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return {
        "message": "Website created successfully",
        "url": f"http://127.0.0.1:8081/generated_sites/{safe_name}/index.html"
    }