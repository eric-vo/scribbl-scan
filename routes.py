import base64
import io
import torch
import json
import cv2 # Sorry I'm mixing PIL and OpenCV in the same project :(
import numpy as np
import matplotlib.pyplot as plt

from flask import Blueprint, render_template, request
from PIL import Image, ImageOps
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(device)

def show_image_with_horizontal_lines(image, line_heights):
    # Read the image
    # Convert to RGB color format for Matplotlib
    image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    # Show the image
    plt.imshow(image_rgb)

    # Add horizontal lines at specified heights
    for height in line_heights:
        plt.axhline(y=height, color='r', linewidth=2)

    plt.title('Image with Horizontal Lines')
    plt.show()

def std_dev(arr):
    if len(arr) == 0:
        raise ValueError("Input array must not be empty")
    mean = np.mean(arr)
    squared_diff = np.abs(arr - mean)
    variance = np.mean(squared_diff)
    std_dev = variance #np.sqrt(variance)
    return std_dev

LINE_SEGMENTATION_SCALE_FACTOR = 0.1
def line_segmentation(image):
    og_image = image
    image = cv2.resize(image, (int(og_image.shape[1] * LINE_SEGMENTATION_SCALE_FACTOR), int(og_image.shape[0] * LINE_SEGMENTATION_SCALE_FACTOR)), interpolation=cv2.INTER_AREA)
    brightness_array = np.mean(image, axis=1)
    threshold = np.median(brightness_array) * 0.2 + np.average(brightness_array) * 0.8
    binarized_array = np.where(brightness_array >= threshold, 1, 0).tolist()
    changes_indices = []
    for i in range(1, len(binarized_array)): # tried doing a smart numpy thing here and it didn't work for some reason so uhhhh dumb solution ig
        if binarized_array[i] != binarized_array[i - 1]:
            changes_indices.append(i)

    spacings = np.array([changes_indices[i] - (0 if i == 0 else changes_indices[i - 1]) for i in range(0, len(changes_indices)) ])
    new_changes_indices = []
    if len(changes_indices) > 2:
        lastHeight = changes_indices[0]
        i = 0
        while True:
            i += 1
            if i >= len(changes_indices):
                break
            curHeight = changes_indices[i]
            space = curHeight - lastHeight
            section_crop = image[lastHeight:curHeight, :]
            if not space < np.mean(spacings) * 0.4:
                if (std_dev(section_crop) < std_dev(image) * 0.7 and i != 1) :
                    new_changes_indices[-1] = curHeight * 0.35 + lastHeight * 0.65           
                else:
                    new_changes_indices.append(curHeight)
            lastHeight = curHeight

    changes_indices = new_changes_indices
    changes_indices = np.rint(np.array(changes_indices) / LINE_SEGMENTATION_SCALE_FACTOR)
    #show_image_with_horizontal_lines(og_image, changes_indices)
    return changes_indices.tolist()

# Load model
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("ericvo/scribbl-scan-trocr")
model.to(device)

# Blueprint configuration
# First argument is the blueprint's name
# Second argument is very important; it’s the import_name
# The third argument is the url prefix of the blueprint
home_bp = Blueprint(
    "home",
    __name__,
    url_prefix="/",
    template_folder="templates",
    static_folder="static",
)


@home_bp.route("/")
def index():
    login = False
    return render_template(
        "index.html", data=login, title="ScribblScan", subtitle="ScribblScan"
    )

def infer_on_img(image):
    pixel_values = processor(image, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(
        generated_ids, skip_special_tokens=True
    )[0]
    return generated_text

@home_bp.route("/demo", methods=["GET", "POST"])
def demo():
    # OCR API
    if request.method == "POST":
        # Get image
        image_data_url = request.form.get("image")
        image = Image.open(
            io.BytesIO(base64.b64decode(image_data_url.split(",")[1]))
        ).convert("RGB")
        img_arr = np.array(image)
        threshold = np.median(img_arr) * 0.2 + np.average(img_arr) * 0.8
        binarized_array = np.where(img_arr >= threshold, 1, 0)
        if np.mean(binarized_array) < 0.5:
            image = ImageOps.invert(image)
            print("Inverted image")


        # Get line segmentation (ewww I use opencv here ewwww)
        cv2_image = np.array(image.convert("L"))
        split_points = line_segmentation(cv2_image)
        split_points.append(image.height - 1)

        out_text = ""
        last_crop_height = 0
        for i, height in enumerate(split_points):
            cropped_image = image.crop((0, int(last_crop_height), image.width, int(height)));
            out_text += infer_on_img(cropped_image) + "\n"
            last_crop_height = height

        
        # Return text
        return json.dumps({"text": out_text})

    # Render demo page
    return render_template("demo.html")


@home_bp.route("/about")
def about():
    return render_template("about.html")

@home_bp.route("/metrics")
def metrics():
    return render_template("metrics.html")
