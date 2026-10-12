
from flask import Flask, render_template
from main import read_logs, analyze_logs

app = Flask(__name__)

LOG_FILE = "sample_logs/app.log"


@app.route("/")
def dashboard():
    logs = read_logs(LOG_FILE)
    summary = analyze_logs(logs)

    return render_template(
        "index.html",
        total=len(logs),
        summary=summary,
        logs=logs
    )


if __name__ == "__main__":
    app.run(debug=True)
