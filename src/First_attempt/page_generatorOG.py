from htmlnode import markdown_to_html_node
from textnode import extract_title
import os
from pathlib import Path

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as file:
        markdown_content = file.read()

    with open(template_path, "r") as file:
        template_content = file.read()

    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    print("Converted HTML Content:", html_content)

    print("HTML Content Before Stripping:", html_content)
    if html_content.startswith("<div>") and html_content.endswith("</div>"):
        html_content = html_content[5:-6]
    print("HTML Content After Stripping:", html_content)

    title = extract_title(markdown_content)
    print("Extracted Title:", title)

    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    print("Final Title for Template:", title)
    print("Final HTML Content for Template:", html_content)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "w") as file:
        file.write(final_html)
    print(f"Page successfully written to {dest_path}")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    print(f"Recursively generating pages in content directory: {dir_path_content}")

    os.makedirs(dest_dir_path, exist_ok=True)

    for entry in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)

        if os.path.isfile(from_path):

            if from_path.endswith(".md"):
                dest_path_html = Path(dest_path).with_suffix(".html")
                print(f"Generating page: {from_path} -> {dest_path_html}")
                generate_page(from_path, template_path, dest_path_html)
        elif os.path.isdir(from_path):
            print(f"Entering subdirectory: {from_path}")
            generate_pages_recursive(from_path, template_path, dest_path)


        

