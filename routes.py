from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, abort, flash


# Blueprint Configuration
home_bp = Blueprint('home', __name__, url_prefix='/', template_folder='templates',static_folder='static') # first argument is the blueprints name,second argument is very important it’s the import_name,The third argument is the url prefix of the blueprint

@home_bp.route('/')
#@login_required
def index():
    #login = current_user
    #if load_user(login) != None:
        #login = True
    login = False
    return render_template(
        'index.html',
        data = login,
        title='ScribblScan',
        subtitle='ScribblScan'
    )


@home_bp.route("/demo", methods=["GET", "POST"])
def demo():
    if request.method == "POST":
        return "Not implemented yet"
        # if "demo-img" in request.files:
        #     img = request.files["demo-img"]
            
    return render_template("demo.html")


@home_bp.route("/about")
def about():
    return render_template("about.html")
