from flask import Flask, render_template, redirect, request, url_for


app = Flask(__name__)


@app.route("/", methods=["GET"])
def main():
    print("/ get")
    return redirect(url_for('input'))


@app.route("/input", methods=["GET"])
def input():
    print("input get")
    return render_template('input.html')


@app.route("/confirm", methods=["POST"])
def confirm():
    print("confirm post")
    project_name = request.form.get('project_name')
    members      = request.form.get('members')
    if not project_name:
        error_message = "プロジェクト名は必ず入力してください"
        return render_template(
            'input.html',
            project_name=project_name,
            members=members,
            error_message=error_message
        )
    if not members:
        error_message = "アサインメンバーは必ず入力してください"
        return render_template(
            'input.html',
            project_name=project_name,
            members=members,
            error_message=error_message
        )
    return render_template(
        'confirm.html',
        project_name=project_name,
        members=members)


@app.route("/complete", methods=["POST"])
def complete():
    if(request.method == 'POST'):
        print("complete post")
        project_name = request.form.get('project_name')
        members      = request.form.get('members')
        message = f'{project_name}に{members}を追加することに成功しました'
        return render_template('complete.html', message=message)


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5000, debug=True)
