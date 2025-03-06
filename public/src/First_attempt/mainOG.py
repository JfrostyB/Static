from textnode import TextNode, TextType
import shutil
import os
from htmlnode import markdown_to_html_node
from textnode import extract_title
from page_generator import generate_page, generate_pages_recursive

def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(src_dir)

    public_dir = os.path.join(workspace_dir, "public")
    static_dir = workspace_dir
    content_dir = os.path.join(static_dir, "content")
    template_path = os.path.join(src_dir, "template.html")

    print(f"src_dir: {src_dir}")
    print(f"workspace_dir: {workspace_dir}")
    print(f"public_dir: {public_dir}")
    print(f"static_dir: {static_dir}")
    print(f"content_dir: {content_dir}")
    print(f"template_path: {template_path}")

    if os.path.exists(public_dir):
        shutil.rmtree(public_dir)
    os.mkdir(public_dir)

    images_dir = os.path.join(workspace_dir, "images")
    public_images_dir = os.path.join(public_dir, "images")
    os.makedirs(public_images_dir, exist_ok=True)

    for image in os.listdir(images_dir):
        source = os.path.join(images_dir, image)
        destination = os.path.join(public_images_dir, image)
        shutil.copy(source, destination)

    css_source = os.path.join(workspace_dir, "index.css")
    css_dest = os.path.join(public_dir, "index.css")
    shutil.copy(css_source, css_dest)

    
    try:
        print(f"Generating site content recursively from {content_dir} to {public_dir} using {template_path}")
        generate_pages_recursive(content_dir, template_path, public_dir)
    except Exception as e:
        print(f"An error occurred while generating pages: {e}")

def copy_static(source, destination):
    if not os.path.exists(source):
        print(f"Warning: Source directory '{source}' does not exist.")
        return

    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        dest_path = os.path.join(destination, item)

        print(f"Processing: {source_path}")

        if os.path.isfile(source_path):
            print(f"Copying file: {source_path} to {dest_path}")
            shutil.copy(source_path, dest_path)
        elif os.path.isdir(source_path):
            print(f"Copying directory: {source_path} to {dest_path}")
            os.makedirs(dest_path, exist_ok=True)
            copy_static(source_path, dest_path)
            


if __name__ == "__main__":
    main()