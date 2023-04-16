from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def main():
    params = {"name": "サンプル１", "age": 20}
    # return render_template("main.html")
    users = [ "Yamada", "サンプル", "２" ]
    return render_template(
        "main.html",
        name=request.args.get("name", "No Name"), age=request.args.get("age", "-"),
        params = params,
        users=users,
    )
