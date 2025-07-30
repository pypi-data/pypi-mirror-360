import asyncio
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List

import jsonpickle
import markdown
from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
    stream_with_context,
)

import ingenious_prompt_tuner.payload as rp1
from ingenious.models.agent import AgentChat, Agents
from ingenious.models.test_data import Event, Events
from ingenious_prompt_tuner.event_processor import functional_tests
from ingenious_prompt_tuner.response_wrapper import AgentChatWrapper
from ingenious_prompt_tuner.utilities import (
    get_selected_revision_direct_call,
    requires_auth,
    requires_selected_revision,
    utils_class,
)

# Authentication Helpers

bp = Blueprint("responses", __name__, url_prefix="/responses")


# Routes
@bp.route("/list")
@requires_auth
@requires_selected_revision
def list():
    utils: utils_class = current_app.utils
    prompt_template_folder = asyncio.run(utils.get_prompt_template_folder())
    base_path = asyncio.run(utils.fs.get_base_path()) / Path(prompt_template_folder)
    data_folder = asyncio.run(utils.get_data_folder())
    data_base_path = asyncio.run(utils.fs_data.get_base_path()) / Path(data_folder)
    return render_template(
        "responses/view_responses.html",
        data_template_folder=data_base_path,
        prompt_template_folder=base_path,
    )


@bp.route("/get_test_data_files", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_test_data_files():
    utils: utils_class = current_app.utils
    output_path = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    files_all = asyncio.run(utils.fs.list_files(file_path=output_path))
    if files_all:
        files = [f for f in files_all if f.endswith(".json") and f.startswith("data_")]
        files.sort(
            key=lambda x: json.loads(
                asyncio.run(utils.fs.read_file(file_name=x, file_path=output_path))
            )["identifier"]
        )
    else:
        files = []

    if files_all:
        files = [f for f in files_all if f.endswith(".json") and f.startswith("data_")]
    else:
        files = []

    return jsonify({"files": files})


@bp.route("/get_payload", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_payload():
    utils: utils_class = current_app.utils
    identifier = request.args.get("identifier", type=str)
    event_type = request.args.get("event_type", type=str)
    output_dir = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    return asyncio.run(rp1.render_payload(identifier, utils.fs, output_dir, event_type))


@bp.route("/rerun_event", methods=["GET"])
@requires_auth
@requires_selected_revision
def rerun_event():
    utils: utils_class = current_app.utils
    agents = current_app.config["agents"]
    prompt_template_folder = asyncio.run(utils.get_prompt_template_folder())
    try:
        identifier = request.args.get("identifier", type=str)
        event_type = request.args.get("event_type", type=str)
        file_name = request.args.get("file_name", type=str)
        identifier_group = request.args.get("identifier_group", type=str)

        # Events are locked in source code and copied to the output folder each time.
        events: Events = asyncio.run(
            utils.get_events(revision_id=get_selected_revision_direct_call())
        )
        event = events.get_event_by_identifier(identifier)

        ft = functional_tests(
            config=utils.get_config(),
            revision_prompt_folder=prompt_template_folder,
            revision_id=get_selected_revision_direct_call(),
            make_llm_calls=True,
        )
        asyncio.run(
            ft.run_event_from_pre_processed_file(
                identifier=identifier,
                identifier_group=identifier_group,
                event_type=event_type,
                file_name=file_name,
                agents=agents,
                conversation_flow=event.conversation_flow,
            )
        )

    except ValueError:
        return "Failed"

    # return success
    return "Succeeded"


@bp.route("/get_agent_response", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_agent_response():
    utils: utils_class = current_app.utils
    identifier = request.args.get("identifier", type=str)
    event_type = request.args.get("event_type", type=str)
    agent_name = request.args.get("agent_name", type=str)
    identifier_group = request.args.get("identifier_group", type=str)

    file_name_parts = [
        identifier_group,
        "agent_response",
        event_type,
        "default",
        agent_name,
        identifier.strip(),
    ]

    file_name = f"{'_'.join(file_name_parts)}.md"
    output_path = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    agent_response_md = asyncio.run(
        utils.fs.read_file(file_name=file_name, file_path=output_path)
    )

    if agent_response_md == "" or agent_response_md is None:
        agent_response_md1 = """
            <div class="markdown-content" markdown='1'><p>No response found - this agent may not be used for this event type</p></div>
        """
    else:
        try:
            # Load the agent chat data with our wrapper to handle the Response object
            agent_chat_data = json.loads(agent_response_md)
            agent_chat_wrapper = AgentChatWrapper.from_dict(agent_chat_data)

            # Access the chat message content via our wrapper
            if agent_chat_wrapper.chat_response_wrapper:
                message_content = (
                    agent_chat_wrapper.chat_response_wrapper.chat_message_content
                )
                inner_messages = agent_chat_wrapper.chat_response_wrapper.inner_messages

                if inner_messages:
                    message_content += "\n\n### Inner Messages \n\n"
                    message_content += (
                        "```json\n"
                        + json.dumps({"inner_messages": inner_messages}, indent=4)
                        + "\n\n```"
                    )
            else:
                message_content = "No message content available"

            html_content = markdown.markdown(
                message_content,
                extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
            )

            agent_response_md1 = render_template(
                "responses/agent_response.html",
                agent_response=html_content,
                prompt_tokens=agent_chat_wrapper.prompt_tokens,
                completion_tokens=agent_chat_wrapper.completion_tokens,
                identifier=identifier,
                event_type=event_type,
                agent_name=agent_chat_wrapper.target_agent_name,
                execution_time=f"{int((agent_chat_wrapper.end_time - agent_chat_wrapper.start_time) // 60)}:{int((agent_chat_wrapper.end_time - agent_chat_wrapper.start_time) % 60):02d}",
                start_time=datetime.fromtimestamp(
                    agent_chat_wrapper.start_time
                ).strftime("%H:%M:%S")
                if agent_chat_wrapper.start_time
                else "",
                identifier_group=identifier_group,
            )
        except Exception as e:
            # If there's an error, display it in the response
            agent_response_md1 = f"""
                <div class="markdown-content" markdown='1'>
                <p>Error loading agent response: {str(e)}</p>
                <pre>{agent_response_md}</pre>
                </div>
            """
    return agent_response_md1


@bp.route("/get_agent_inputs", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_agent_inputs():
    utils: utils_class = current_app.utils
    identifier = request.args.get("identifier", type=str)
    event_type = request.args.get("event_type", type=str)
    agent_name = request.args.get("agent_name", type=str)
    input_type = request.args.get("input_type", type=str)
    identifier_group = request.args.get("identifier_group", type=str)

    file_name_parts = [
        identifier_group,
        "agent_response",
        event_type,
        "default",
        agent_name,
        identifier.strip(),
    ]

    file_name = f"{'_'.join(file_name_parts)}.md"

    output_path = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    agent_response_md = asyncio.run(
        utils.fs.read_file(file_name=file_name, file_path=output_path)
    )

    try:
        # Load the agent chat data with our wrapper to handle the Response object
        agent_chat_data = json.loads(agent_response_md)
        agent_chat_wrapper = AgentChatWrapper.from_dict(agent_chat_data)

        if input_type == "user_input":
            content = agent_chat_wrapper.user_message
        else:
            content = agent_chat_wrapper.system_prompt

        # Convert any csv data to a table
        content_csvs_converted = rp1.convert_csv_to_md_tables(content)

        html_content = markdown.markdown(
            content_csvs_converted,
            extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
        )

        agent_response_md1 = render_template(
            "responses/agent_inputs.html",
            agent_input=html_content,
            input_type=input_type,
            event_type=event_type,
            agent_name=agent_chat_wrapper.target_agent_name,
        )
    except Exception as e:
        # If there's an error, display it in the response
        agent_response_md1 = f"""
            <div class="markdown-content">
            <p>Error loading agent input: {str(e)}</p>
            </div>
        """
    return agent_response_md1


@bp.route("/get_events", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_events():
    utils: utils_class = current_app.utils
    files = asyncio.run(
        utils.get_events(get_selected_revision_direct_call())
    ).get_events()
    return jsonpickle.encode(files, unpicklable=False)


@bp.route("/get_responses", methods=["GET"])
@requires_auth
@requires_selected_revision
def get_responses():
    utils: utils_class = current_app.utils
    agents: Agents = current_app.config["agents"]
    files = asyncio.run(utils.get_events(get_selected_revision_direct_call()))

    # Now loop through the data files and for each get any associated agent chats
    events_html = ""

    # get the agent which has the return_in_response set to True
    # return_agent = None
    for agent in agents.get_agents():
        if agent.return_in_response:
            # return_agent = agent
            break

    events: List[Event] = []
    for file in files.get_events():
        event: Event = file
        events.append(event)
        events_html += render_template(
            "responses/event_template.html",
            identifier=event.identifier,
            event_type=event.event_type,
            file_name=event.file_name,
            agents=agents.get_agents_for_prompt_tuner(),
            identifier_group=event.identifier_group,
        )

    return render_template(
        "responses/events_template.html", files=events, events_html=events_html
    )


@bp.route("/get_agent_response_from_file", methods=["post"])
@requires_auth
@requires_selected_revision
def get_agent_response_from_file():
    utils: utils_class = current_app.utils
    identifier = request.form.get("identifier", type=str).replace("#", "")
    event_type = request.form.get("event_type", type=str)
    identifier_group = request.form.get("identifier_group", type=str, default="default")

    file_name_parts = [
        identifier_group,
        "agent_response",
        event_type,
        "default",
        current_app.config["response_agent_name"],
        identifier.strip(),
    ]
    print(file_name_parts)
    file_name = f"{'_'.join(file_name_parts)}.md"
    output_path = (
        current_app.config["test_output_path"]
        + f"/{get_selected_revision_direct_call()}"
    )
    file_contents = asyncio.run(
        utils.fs.read_file(file_name=file_name, file_path=output_path)
    )

    file_content_placeholder = """
            <div class="markdown-content" markdown='1'><p>No response found</p></div>
    """

    try:
        agent_chat: AgentChat = AgentChat(**json.loads(file_contents))
        html_content = markdown.markdown(
            agent_chat.chat_response.chat_message.content,
            extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
        )
        agent_response_md1 = render_template(
            "responses/agent_response.html",
            agent_response=html_content,
            prompt_tokens=agent_chat.prompt_tokens,
            completion_tokens=agent_chat.completion_tokens,
            agent_name=agent_chat.target_agent_name,
            identifier=identifier,
            event_type=event_type,
            execution_time=agent_chat.get_execution_time_formatted(),
            start_time=agent_chat.get_start_time_formatted(),
            identifier_group=identifier_group,
        )
    # Add exception handling that will print the error message to the console
    except Exception as e:
        print(f"Error: {e}")
        agent_response_md1 = file_content_placeholder

    return agent_response_md1


@bp.route("/run_live_progress", methods=["GET"])
@requires_auth
@requires_selected_revision
def run_live_progress():
    # utils: utils_class = current_app.utils
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
