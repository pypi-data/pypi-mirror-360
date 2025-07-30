import asyncio
import io
import os
import uuid as guid
from pathlib import Path

import yaml
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from ingenious_prompt_tuner.utilities import (
    get_selected_revision_direct_call,
    requires_auth,
    requires_selected_revision,
    set_selected_revision_direct_call,
    utils_class,
)

# Authentication Helpers

bp = Blueprint("index", __name__)


# Routes


@bp.route("/")
@requires_auth
def home():
    class Revision:
        def __init__(self, description):
            self.name = guid.uuid4()
            self.description

    utils: utils_class = current_app.utils
    if asyncio.run(
        utils.fs.check_if_file_exists(
            file_name="revisions.yml",
            file_path=str(current_app.config["revisions_folder"]),
        )
    ):
        revisions_str = asyncio.run(
            utils.fs.read_file(
                file_name="revisions.yml",
                file_path=str(current_app.config["revisions_folder"]),
            )
        )
        revisions = yaml.safe_load(revisions_str)
    else:
        return redirect(url_for("index.create_revision"))
    base_folder = (
        asyncio.run(utils.fs.get_base_path())
        + "/"
        + str(current_app.config["revisions_folder"])
    )
    return render_template("home.html", files=revisions, base_folder=base_folder)


@bp.route("/set_selected_revision", methods=["GET", "POST"])
@requires_auth
def set_selected_revision():
    revision_id = request.args.get("revision_id")
    response = set_selected_revision_direct_call(revision_id)
    return response


@bp.route("/get_selected_revision", methods=["GET", "POST"])
@requires_auth
def get_selected_revision():
    selected_revision = get_selected_revision_direct_call()
    return jsonify({"revision": selected_revision})


@bp.route("/create_revision", methods=["GET", "POST"])
@requires_auth
def create_revision():
    return render_template("revisions/create_revision.html")


@bp.route("/save_revision", methods=["POST"])
@requires_auth
def save_revision():
    utils: utils_class = current_app.utils
    old_guid = request.args.get("old_guid")
    new_guid = request.args.get("new_guid")

    revision_description = request.form["revision_description"]
    new_revision = {"name": new_guid, "description": revision_description}
    file_path_revisions = "revisions"

    if asyncio.run(
        utils.fs.check_if_file_exists(
            file_name="revisions.yml", file_path=file_path_revisions
        )
    ):
        revisions_str = asyncio.run(
            utils.fs.read_file(
                file_name="revisions.yml", file_path=str(file_path_revisions)
            )
        )
        revisions = yaml.safe_load(revisions_str)
    else:
        revisions = []

    revisions.append(new_revision)
    revisions_str = yaml.safe_dump(revisions)
    asyncio.run(
        utils.fs.write_file(
            contents=revisions_str,
            file_name="revisions.yml",
            file_path=str(file_path_revisions),
        )
    )

    # If old_guid is None, then this is a new revision
    if old_guid is None:
        print(f"Creating new revision {new_guid} using source files")
        asyncio.run(
            utils.get_prompt_template_folder(
                revision_id=new_guid, force_copy_from_source=True
            )
        )
        asyncio.run(
            utils.get_functional_tests_folder(
                revision_id=new_guid, force_copy_from_source=True
            )
        )
        return redirect(url_for("index.home"))

    # Make sure that the prompts and sample data files are copied to the new revision folder
    file_path_old_outputs = f"functional_test_outputs/{old_guid}"
    file_path_old_prompts = f"templates/prompts/{old_guid}"
    file_path_new_outputs = f"functional_test_outputs/{new_guid}"
    file_path_new_prompts = f"templates/prompts/{new_guid}"

    for file_path_old, file_path_new in [
        (file_path_old_outputs, file_path_new_outputs),
        (file_path_old_prompts, file_path_new_prompts),
    ]:
        old_files = asyncio.run(utils.fs.list_files(file_path_old))
        if old_files is None or len(old_files) == 0:
            if file_path_old == file_path_old_outputs:
                asyncio.run(
                    utils.get_functional_tests_folder(
                        revision_id=new_guid, force_copy_from_source=True
                    )
                )
            if file_path_old == file_path_old_prompts:
                asyncio.run(
                    utils.get_prompt_template_folder(
                        revision_id=new_guid, force_copy_from_source=True
                    )
                )
        else:
            for file in old_files:
                file_name = Path(file).name
                content = asyncio.run(
                    utils.fs.read_file(file_name=file_name, file_path=file_path_old)
                )
                asyncio.run(
                    utils.fs.write_file(
                        contents=content, file_name=file_name, file_path=file_path_new
                    )
                )

    return redirect(url_for("index.home"))


@bp.route("/sync_prompts")
@requires_auth
def sync_prompts():
    utils: utils_class = current_app.utils
    revision_id = get_selected_revision_direct_call()
    asyncio.run(
        utils.get_prompt_template_folder(revision_id, force_copy_from_source=True)
    )
    # Return ok
    return "OK"


@bp.route("/sync_sample_data")
@requires_auth
def sync_sample_data():
    utils: utils_class = current_app.utils
    revision_id = get_selected_revision_direct_call()
    asyncio.run(
        utils.get_functional_tests_folder(revision_id, force_copy_from_source=True)
    )
    asyncio.run(utils.get_data_folder(revision_id, force_copy_from_source=True))
    # Return ok
    return "OK"


@bp.route("/edit_markdown")
@requires_auth
@requires_selected_revision
def edit_markdown():
    utils: utils_class = current_app.utils
    try:
        prompt_template_folder = asyncio.run(utils.get_prompt_template_folder())
        files_raw = asyncio.run(utils.fs.list_files(file_path=prompt_template_folder))
        files = sorted(
            [Path(f).name for f in files_raw if f.endswith((".md", ".jinja"))]
        )
    except FileNotFoundError:
        files = []
    return render_template("edit_markdown.html", files=files)


@bp.route("/view_responses")
@requires_auth
def view_responses():
    # Simplified version - in real implementation would get more data
    return render_template("responses/view_responses.html")


@bp.route("/download_responses", methods=["GET"])
@requires_auth
def download_responses():
    functional_test_dir = str(current_app.config["test_output_path"])
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
