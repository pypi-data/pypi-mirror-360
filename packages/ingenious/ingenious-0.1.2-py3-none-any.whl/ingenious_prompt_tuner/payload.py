import csv
import re
from io import StringIO

import markdown
from flask import render_template, render_template_string


async def render_payload(ball_identifier, fs, output_dir, event_type):
    markdown_content = await fs.read_file(
        file_name=f"payload_{event_type}_{ball_identifier}.md", file_path=output_dir
    )

    # Convert embedded CSVs to Markdown tables
    markdown_content = convert_csv_to_md_tables(markdown_content)

    # Convert markdown to HTML
    html_content = markdown.markdown(
        "## Table of Contents \n\n [TOC]\n\n" + markdown_content,
        extensions=["extra", "md_in_html", "toc", "fenced_code", "codehilite"],
    )

    # Render the HTML in a template
    page_content = render_template_string(payload_base_template(html_content))
    return page_content


def convert_csv_to_md_tables(content):
    # Replace sections with CSV data into Markdown table syntax
    def replace_csv_blocks(match):
        csv_data = match.group(1)
        csv_data = csv_to_md(csv_data.strip())
        return csv_data

    # Use regex to find and replace only ``` csv ... ``` blocks
    pattern = r"``` csv\s*(.*?)\s*```"
    print(f"Regex pattern: {pattern}")
    if content is None:
        return ""

    # Find all CSV blocks and their preceding headings
    pattern_with_heading = r"(#+\s[^\n]+)\n+``` csv\s*(.*?)\s*```"
    matches_with_heading = re.findall(pattern_with_heading, content, flags=re.DOTALL)

    i = 0
    processed_content = content
    for heading, csv_data in matches_with_heading:
        print(f"Heading: {heading}")
        processed_content = re.sub(
            pattern, replace_csv_blocks, processed_content, count=1, flags=re.DOTALL
        )
        i += 1

    return processed_content


def csv_to_md(csv_content):
    # Convert raw CSV into Markdown table syntax
    reader = csv.reader(StringIO(csv_content))
    rows = list(reader)

    # Create Markdown table
    header = "| " + " | ".join(rows[0]) + " |"
    separator = "| " + " | ".join(["---"] * len(rows[0])) + " |"
    body = "\n".join(["| " + " | ".join(row) + " |" for row in rows[1:]])

    return f"{header}\n{separator}\n{body}"


def payload_base_template(content):
    ret = render_template("/responses/payload_template.html")
    ret = ret.replace("/@content@/", content)
    return ret
