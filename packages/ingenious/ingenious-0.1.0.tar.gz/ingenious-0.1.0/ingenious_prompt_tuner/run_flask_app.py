import asyncio
import io
import json
import os
import subprocess
import sys
import uuid as guid
from functools import wraps
from pathlib import Path

import markdown
import yaml
from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    stream_with_context,
    url_for,
)

# Set up parent directory and import dependencies
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(parent_dir)

# import ingenious_extensions.tests.flask_app_render_payload as rp1
# import ingenious_extensions.tests.run_tests as rt
import rich.progress as rp

import ingenious.dependencies as ig_deps
from ingenious.files.files_repository import FileStorage
from ingenious.utils.stage_executor import ProgressConsoleWrapper

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static",
    template_folder="templates",
)
app.secret_key = ig_deps.config.web_configuration.authentication.password

PROMPT_TEMPLATE_FOLDER = os.path.join(
    parent_dir, "ingenious_extensions", "templates", "prompts"
)

output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
functional_test_dir = os.path.join(output_dir, "functional_test_outputs")
os.makedirs(functional_test_dir, exist_ok=True)

USERNAME = ig_deps.config.web_configuration.authentication.username
PASSWORD = ig_deps.config.web_configuration.authentication.password
PORT = ig_deps.config.web_configuration.port
HOST = ig_deps.config.web_configuration.ip_address

fs = FileStorage(config=ig_deps.config)
REVISIONS_FOLDER = Path("revisions")


progress = rp.Progress()
pcw = ProgressConsoleWrapper(progress=progress, log_level="INFO")
# run_tests = rt.RunBatches(progress=pcw, task_id=1)


# Stub class for missing functionality
class MockRunTests:
    def __init__(self, progress, task_id):
        pass

    async def get_output_path(self, session_id):
        return f"./functional_test_outputs/{session_id}"

    async def rerun_single_event(
        self, ball_identifier, event_type, file_name, session_id
    ):
        return "mock_result"


run_tests = MockRunTests(progress=pcw, task_id=1)


def mock_render_dashboard(ball_identifier, fs, output_dir, event_type):
    return (
        f"<h1>Mock Dashboard</h1><p>Ball ID: {ball_identifier}, Event: {event_type}</p>"
    )


# Authentication Helpers
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD


def authenticate():
    return jsonify({"status": "error", "output": "Authentication required"}), 401


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def requires_selected_revision(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        selected_revision = request.cookies.get("selected_revision")
        if not selected_revision:
            return redirect(url_for("home"))
        return f(*args, **kwargs)

    return decorated_function


def get_selected_revision_direct_call():
    selected_revision = request.cookies.get("selected_revision")
    if selected_revision:
        return selected_revision


# Routes
@app.route("/debug")
def debug():
    """Debug route to check config values"""
    return jsonify(
        {
            "username": USERNAME,
            "password": PASSWORD,
            "auth_enabled": ig_deps.config.web_configuration.authentication.enable,
        }
    )


@app.route("/sync_prompts", methods=["POST"])
@requires_auth
def sync_prompts():
    """Stub route for sync prompts functionality"""
    return jsonify(
        {
            "status": "success",
            "message": "Sync prompts functionality not implemented yet",
        }
    )


@app.route("/sync_sample_data", methods=["POST"])
@requires_auth
def sync_sample_data():
    """Stub route for sync sample data functionality"""
    return jsonify(
        {
            "status": "success",
            "message": "Sync sample data functionality not implemented yet",
        }
    )


@app.route("/set_selected_revision", methods=["GET"])
@requires_auth
def set_selected_revision():
    """Set the selected revision using cookies"""
    revision_id = request.args.get("revision_id")
    if revision_id:
        response = jsonify(
            {"status": "success", "message": f"Selected revision: {revision_id}"}
        )
        response.set_cookie("selected_revision", revision_id)
        return response
    else:
        return jsonify({"status": "error", "message": "No revision ID provided"}), 400


@app.route("/health")
def health_check():
    """Simple health check route without any file operations"""
    return jsonify({"status": "healthy", "message": "Flask app is running"})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if check_auth(username, password):
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return "Invalid credentials", 401
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/")
@requires_auth
def home():
    # Simplified home route - avoid slow async operations for now
    try:
        revisions_path = REVISIONS_FOLDER / "revisions.yml"
        if revisions_path.exists():
            with open(revisions_path, "r") as f:
                revisions = yaml.safe_load(f) or []
        else:
            revisions = []
    except Exception:
        # If there are any file issues, just show empty revisions
        revisions = []

    return render_template("home.html", files=revisions)


@app.route("/create_revision", methods=["GET", "POST"])
@requires_auth
def create_revision():
    if request.method == "POST":
        revision_name = str(guid.uuid4())  # Auto-generate revision name
        revision_description = request.form["revision_description"]
        new_revision = {"name": revision_name, "description": revision_description}

        # Simplified file operations
        revisions_file = REVISIONS_FOLDER / "revisions.yml"

        try:
            if revisions_file.exists():
                with open(revisions_file, "r") as f:
                    revisions = yaml.safe_load(f) or []
            else:
                revisions = []

            revisions.append(new_revision)

            # Ensure the directory exists
            REVISIONS_FOLDER.mkdir(parents=True, exist_ok=True)

            with open(revisions_file, "w") as f:
                yaml.safe_dump(revisions, f)

        except Exception as e:
            print(f"Error saving revision: {e}")
            # Continue anyway for now

        return redirect(url_for("home"))
    return render_template("revisions/create_revision.html")


@app.route("/save_revision", methods=["POST"])
@requires_auth
def save_revision():
    revision_name = str(guid.uuid4())
    revision_description = request.form["revision_description"]
    new_revision = {"name": revision_name, "description": revision_description}

    if asyncio.run(
        fs.check_if_file_exists(
            file_name="revisions.yml", file_path=str(REVISIONS_FOLDER)
        )
    ):
        revisions_str = asyncio.run(
            fs.read_file(file_name="revisions.yml", file_path=str(REVISIONS_FOLDER))
        )
        revisions = yaml.safe_load(revisions_str)
    else:
        revisions = []

    revisions.append(new_revision)
    revisions_str = yaml.safe_dump(revisions)
    asyncio.run(
        fs.write_file(
            contents=revisions_str,
            file_name="revisions.yml",
            file_path=str(REVISIONS_FOLDER),
        )
    )
    prompts = asyncio.run(
        fs.list_files(f"prompts/{get_selected_revision_direct_call()}")
    )
    function_test_outputs = asyncio.run(
        fs.list_files(f"functional_test_outputs/{get_selected_revision_direct_call()}")
    )

    for prompt in prompts:
        content = asyncio.run(
            fs.read_file(
                file_name=prompt,
                file_path=f"prompts/{get_selected_revision_direct_call()}",
            )
        )
        asyncio.run(
            fs.write_file(
                file_name=prompt, file_path=f"prompts/{revision_name}", contents=content
            )
        )

    for function_test_output in function_test_outputs:
        content = asyncio.run(
            fs.read_file(
                file_name=function_test_output,
                file_path=f"functional_test_outputs/{get_selected_revision_direct_call()}",
            )
        )
        asyncio.run(
            fs.write_file(
                file_name=function_test_output,
                file_path=f"functional_test_outputs/{revision_name}",
                contents=content,
            )
        )

    return redirect(url_for("home"))


@app.route("/get_selected_revision", methods=["GET"])
@requires_auth
def get_selected_revision():
    selected_revision = request.cookies.get("selected_revision")
    return jsonify({"selected_revision": selected_revision})


@app.route("/edit_markdown")
@requires_auth
@requires_selected_revision
def edit_markdown():
    # Simplified - just return empty files list for now
    # In a real implementation, this would list files in the revision's prompt folder
    files = []
    return render_template("edit_markdown.html", files=files)


@app.route("/view_responses")
@requires_auth
@requires_selected_revision
def view_responses():
    return render_template("responses/view_responses_simple.html")


@app.route("/get_test_data_files", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_test_data_files():
    output_path = str(
        Path(
            asyncio.run(
                run_tests.get_output_path(
                    session_id=get_selected_revision_direct_call()
                )
            )
        ).parent
    )
    files_all = asyncio.run(fs.list_files(file_path=output_path))
    if files_all:
        files = [f for f in files_all if f.endswith(".json") and f.startswith("data_")]
        files.sort(
            key=lambda x: json.loads(
                asyncio.run(fs.read_file(file_name=x, file_path=output_path))
            )["ball_identifier"]
        )
    else:
        files = []

    if files_all:
        files = [f for f in files_all if f.endswith(".json") and f.startswith("data_")]
    else:
        files = []

    return jsonify({"files": files})


@app.route("/get_payload", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_payload():
    ball_identifier = request.args.get("ball_identifier", type=str)
    event_type = request.args.get("event_type", type=str)
    output_dir = str(
        Path(
            asyncio.run(
                run_tests.get_output_path(
                    session_id=get_selected_revision_direct_call()
                )
            )
        ).parent
    )
    return asyncio.run(
        mock_render_dashboard(ball_identifier, fs, output_dir, event_type)
    )


@app.route("/rerun_event", methods=["GET"])
@requires_auth
@requires_selected_revision
def rerun_event():
    try:
        ball_identifier = request.args.get("ball_identifier", type=str)
        event_type = request.args.get("event_type", type=str)
        file_name = request.args.get("file_name", type=str)
        asyncio.run(
            run_tests.rerun_single_event(
                ball_identifier=ball_identifier,
                event_type=event_type,
                file_name=file_name,
                session_id=get_selected_revision_direct_call(),
            )
        )

    except ValueError:
        return "Failed"

    # return success
    return "Succeeded"


@app.route("/get_agent_response", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_agent_response():
    ball_identifier = request.args.get("ball_identifier", type=str)
    event_type = request.args.get("event_type", type=str)
    agent_name = request.args.get("agent_name", type=str)
    # Return mock html page
    file_name = f"agent_response_{event_type}_{agent_name}_{ball_identifier.strip()}.md"
    output_path = str(
        Path(
            asyncio.run(
                run_tests.get_output_path(
                    session_id=get_selected_revision_direct_call()
                )
            )
        ).parent
    )
    agent_response_md = asyncio.run(
        fs.read_file(file_name=file_name, file_path=output_path)
    )
    agent_response_md1 = render_template(
        "agent_response.html", agent_response=agent_response_md
    )
    html_content = markdown.markdown(
        agent_response_md1,
        extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
    )
    return html_content


@app.route("/get_responses", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_responses():
    try:
        output_path = str(
            Path(
                asyncio.run(
                    run_tests.get_output_path(
                        session_id=get_selected_revision_direct_call()
                    )
                )
            ).parent
        )
        if asyncio.run(
            fs.check_if_file_exists(file_name="events.yml", file_path=output_path)
        ):
            files = yaml.safe_load(
                asyncio.run(fs.read_file(file_name="events.yml", file_path=output_path))
            )
        else:
            return "<p>No responses folder found.</p>"

    except ValueError:
        return "<p>No responses folder found.</p>"

    # render the responses2.html file
    return render_template("responses2.html", files=files)


@app.route("/get_agent_response_from_file", methods=["post"])
@requires_auth
@requires_selected_revision
def get_agent_response_from_file():
    ball_identifier = request.form.get("ball_identifier", type=str).replace("#", "")
    event_type = request.form.get("event_type", type=str)

    file_name = f"agent_response_{event_type}_summary_{ball_identifier.strip()}.md"
    output_path = str(
        Path(
            asyncio.run(
                run_tests.get_output_path(
                    session_id=get_selected_revision_direct_call()
                )
            )
        ).parent
    )
    file_contents = asyncio.run(
        fs.read_file(file_name=file_name, file_path=output_path)
    )
    html_content = markdown.markdown(
        file_contents,
        extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
    )
    return html_content


@app.route("/get_responses1", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_responses1():
    try:
        latest_folder = max(
            [
                os.path.join(functional_test_dir, d)
                for d in os.listdir(functional_test_dir)
            ],
            key=os.path.getmtime,
        )
    except ValueError:
        return "<p>No responses folder found.</p>"

    RESPONSES_FILE = os.path.join(latest_folder, "responses.html")

    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, "r", encoding="utf-8") as rf:
            return rf.read()
    return "<p>No responses found or file does not exist.</p>"


@app.route("/download_responses", methods=["GET"])
@requires_auth
@requires_selected_revision
def download_responses():
    try:
        latest_folder = max(
            [
                os.path.join(functional_test_dir, d)
                for d in os.listdir(functional_test_dir)
            ],
            key=os.path.getmtime,
        )
        RESPONSES_FILE = os.path.join(latest_folder, "responses.html")

        if os.path.exists(RESPONSES_FILE):
            with open(RESPONSES_FILE, "r", encoding="utf-8") as rf:
                file_contents = rf.read()
            return send_file(
                io.BytesIO(file_contents.encode("utf-8")),
                as_attachment=True,
                download_name="responses.html",
                mimetype="text/html",
            )
    except ValueError:
        pass
    return jsonify({"status": "error", "output": "Responses file not found"}), 404


@app.route("/run_live_progress", methods=["GET"])
@requires_auth
@requires_selected_revision
def run_live_progress():
    max_processed_events = request.args.get("max_processed_events", default=1, type=int)

    def generate():
        process = subprocess.Popen(
            args=[
                "ingen",
                "run-test-batch",
                "--run-args",
                f"--max_processed_events={max_processed_events} --test_run_session_id={get_selected_revision_direct_call()}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered
        )
        try:
            for line in iter(process.stdout.readline, ""):
                if line:
                    # from ansi2html import Ansi2HTMLConverter
                    # conv = Ansi2HTMLConverter()
                    # ansi = line
                    # html = conv.convert(ansi, full=False)
                    html = line
                    yield f"data: {html}\n\n"
            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                yield "event: complete\ndata: Tests completed successfully.\n\n"
            else:
                yield f"data: Error occurred: MPE{max_processed_events} --- {process.stderr.read().strip()}\n\n"
        except Exception as e:
            yield f"data: Error occurred: MPE{max_processed_events} --- {str(e)}\n\n"
        finally:
            process.terminate()

    return Response(stream_with_context(generate()), content_type="text/event-stream")


@app.route("/run_simple_tests", methods=["POST"])
@requires_auth
@requires_selected_revision
def run_simple_tests():
    try:
        result = subprocess.run(
            ["ingen", "run-test-batch"], capture_output=True, text=True, check=False
        )
        status = "success" if result.returncode == 0 else "error"
        return jsonify({"status": status, "output": result.stdout or result.stderr})
    except Exception as e:
        return jsonify({"status": "error", "output": str(e)})


@app.route("/edit/<filename>", methods=["GET", "POST"])
@requires_auth
@requires_selected_revision
def edit_file(filename):
    # Simplified file editing - create files in a prompts directory per revision
    selected_revision = get_selected_revision_direct_call()
    if not selected_revision:
        return redirect(url_for("home"))

    # Create revision-specific prompts directory
    prompts_dir = Path("prompts") / selected_revision
    prompts_dir.mkdir(parents=True, exist_ok=True)
    file_path = prompts_dir / filename

    if request.method == "POST":
        new_content = request.form.get("file_content", "")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            print(f"Error saving file: {e}")
        return redirect(url_for("home"))
    else:
        # Read existing content or create empty file
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = "# New prompt file\n\n"
        except Exception as e:
            print(f"Error reading file: {e}")
            content = "# New prompt file\n\n"

        return render_template(
            "prompts/edit_prompt.html", filename=filename, content=content
        )


if __name__ == "__main__":
    app.run(debug=True, host=HOST, port=PORT)
