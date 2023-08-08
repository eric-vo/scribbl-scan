from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/demo", methods=["GET", "POST"])
def demo():
    if request.method == "POST":
        return "Not implemented yet"
        # if "demo-img" in request.files:
        #     img = request.files["demo-img"]
            
    return render_template("demo.html")


@app.route("/about")
def about():
    return render_template("about.html")
