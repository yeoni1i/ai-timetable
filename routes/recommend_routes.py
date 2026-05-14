from flask import Blueprint, render_template, request, session
from services.recommend_service import recommend_timetable

recommend_bp = Blueprint("recommend", __name__)


@recommend_bp.route("/priority", methods=["GET", "POST"])
def priority():
    return render_template("priority.html")


@recommend_bp.route("/condition", methods=["GET", "POST"])
def condition():
    if request.method == "GET":
        return render_template("priority.html")

    priorities = {
        "empty_day": int(request.form["empty_day"]),
        "morning": int(request.form["morning"]),
        "difficulty": int(request.form["difficulty"]),
        "graduation": int(request.form["graduation"])
    }

    session["priorities"] = priorities

    return render_template("condition.html", priorities=priorities)


@recommend_bp.route("/result", methods=["POST"])
def result():
    priorities = session.get("priorities")

    if priorities is None:
        return render_template("priority.html")

    conditions = {
        "avoid_first_period": "avoid_first_period" in request.form,
        "max_credit": int(request.form["max_credit"])
    }

    result = recommend_timetable(priorities, conditions)

    session["result"] = result

    return render_template("result.html", result=result)


@recommend_bp.route("/register", methods=["POST"])
def register():
    result = session.get("result")

    if result is None:
        return render_template("home.html", timetable=[])

    return render_template("home.html", timetable=result["timetable"])

