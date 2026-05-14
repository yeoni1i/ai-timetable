from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html", timetable=[], result=None)

@main_bp.route("/graduation")
def graduation():
    return render_template("graduation.html")