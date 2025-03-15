from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import boto3
import uuid
import datetime
import logging  # ✅ Logging added
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
import io
from flask_talisman import Talisman  # ✅ Enforces HTTPS in Azure

app = Flask(__name__)
Talisman(app)  # ✅ Force HTTPS on Azure

app.secret_key = 'your_secret_key'

# ✅ Setup Logging for Azure App Service
logging.basicConfig(level=logging.INFO)

# 🔹 Load 3D jersey template
JERSEY_TEMPLATE_PATH = "static/3d_jersey_template.png"  # Ensure this exists in 'static/' folder

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    @classmethod
    def get(cls, user_id):
        return cls(user_id)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.before_request
def before_request():
    """✅ Redirect HTTP to HTTPS (Fixes Azure 301 Redirect Issue)"""
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http://', 'https://', 301))

@app.route('/customize-jersey', methods=['GET'])
@login_required
def customize_jersey():
    """Customize a 3D jersey with team name, color, number, and logo."""
    try:
        logging.info("✅ Customizing jersey request received")

        # Load 3D jersey template
        jersey = Image.open(JERSEY_TEMPLATE_PATH).convert("RGBA")

        # Get customization parameters
        team = request.args.get('team', 'Default Team')
        color = request.args.get('color', '#FFFFFF')  # Default white
        number = request.args.get('number', '10')
        logo_url = request.args.get('logo', None)

        # Apply color overlay
        overlay = Image.new("RGBA", jersey.size, color)
        jersey = Image.blend(jersey, overlay, 0.6)  # Adjust transparency

        # Add team name and number
        draw = ImageDraw.Draw(jersey)
        font = ImageFont.load_default()

        draw.text((150, 60), team, fill="black", font=font)  # Team Name
        draw.text((180, 250), number, fill="black", font=font)  # Jersey Number

        # Add team logo if provided
        if logo_url:
            response = requests.get(logo_url)
            if response.status_code == 200:
                logo = Image.open(io.BytesIO(response.content)).convert("RGBA")
                logo = logo.resize((100, 100))  # Resize logo
                jersey.paste(logo, (150, 100), mask=logo)  # Place logo on chest

        # Save and return the customized jersey
        img_io = io.BytesIO()
        jersey.save(img_io, 'PNG')
        img_io.seek(0)

        logging.info("✅ Jersey customization successful")
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        logging.error(f"❌ Error customizing jersey: {str(e)}")  # ✅ Log Errors
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)  # ✅ Server-Ready for Azure
