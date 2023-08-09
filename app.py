import base64
import io
import json

from flask import Flask, render_template, request
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Load model
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained(
    "microsoft/trocr-base-handwritten"
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/demo", methods=["GET", "POST"])
def demo():
    # OCR API
    if request.method == "POST":
        # Get image
        image_data_url = request.form.get("image")
        image = Image.open(
            io.BytesIO(base64.b64decode(image_data_url.split(",")[1]))
        ).convert("RGB")

        # Get text from image
        pixel_values = processor(image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        # Return text
        return json.dumps({"text": generated_text})

    # Render demo page
    return render_template("demo.html")


@app.route("/about")
def about():
    return render_template("about.html")
