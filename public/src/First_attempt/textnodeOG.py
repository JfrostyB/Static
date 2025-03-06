from enum import Enum
from nodes import HTMLNode, LeafNode
import re

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        return (self.text == other.text and
                self.text_type == other.text_type and
                self.url == other.url)

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt" :text_node.text})
    else:
        raise Exception("TextType missing")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            text = node.text
            first_index = text.find(delimiter)
            if first_index != -1:
                second_index = text.find(delimiter, first_index + len(delimiter))
                if second_index == -1:
                    raise ValueError("Closing delimiter not found")

                before = text[:first_index]
                middle = text[first_index + len(delimiter):second_index]
                after = text[second_index + len(delimiter):]

                if before:
                    new_nodes.append(TextNode(before, TextType.TEXT))
                if middle:
                    new_nodes.append(TextNode(middle, text_type))
                if after:
                    new_nodes.append(TextNode(after, TextType.TEXT))
            else:
                new_nodes.append(node)

    return new_nodes

def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        text = node.text


        while True:
            first_bracket = text.find("[")
            second_bracket = text.find("](")
            closing_parenthesis = text.find(")", second_bracket)

            if first_bracket == -1 or second_bracket == -1 or closing_parenthesis == -1:
                if text:
                    new_nodes.append(TextNode(text, TextType.TEXT))
                break

            before = text[:first_bracket]
            middle = text[first_bracket + 1 : second_bracket]
            url = text[second_bracket + 2 : closing_parenthesis]
            after = text[closing_parenthesis + 1 :]

            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))

            new_nodes.append(TextNode(middle, TextType.LINK, url))

            text = after

    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        text = node.text
        while True:
            first_bracket = text.find("![")
            second_bracket = text.find("](")
            closing_parenthesis = text.find(")")

            if first_bracket == -1 or second_bracket == -1 or closing_parenthesis == -1:
                if text:
                    new_nodes.append(TextNode(text, TextType.TEXT))
                break
        
            before = text[:first_bracket]
            alt_text = text[first_bracket + 2 : second_bracket]
            image_link = text[second_bracket + 2 : closing_parenthesis]
            after = text[closing_parenthesis + 1 :]

            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))

            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url=image_link))

            text = after

    return new_nodes

def text_to_textnodes(text):
    if not text:
        return []

    nodes = [TextNode(text, TextType.TEXT)]

    try:
        nodes = split_nodes_image(nodes)
    except ValueError:
        pass

    try:
        new_nodes = []
        for node in nodes:
            if node.text_type == TextType.TEXT:
                new_nodes.extend(split_nodes_link([node]))
            else:
                new_nodes.append(node)
        nodes = new_nodes
    except ValueError:
        pass

    try:
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    except ValueError:
        pass

    try:    
        nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    except ValueError:
        pass

    try:
        nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    except ValueError:
        pass

    if not nodes:
        return [TextNode(text, TextType.TEXT)]

    return nodes

def markdown_to_blocks(markdown):
    markdown_block = []
    blocks = markdown.split('\n\n')
    for block in blocks:
        true_block = block.strip()
        if true_block != "":
            markdown_block.append(true_block)
    return markdown_block

class BlockType(Enum):
    Paragraph = "paragraph"
    Heading = "heading"
    Code = "code"
    Quote = "quote"
    Unordered_List = "unordered_list"
    Ordered_List = "ordered_list"

def block_to_block_type(block: str) -> BlockType:
    lines = block.split('\n')
    if block.startswith('#'):
        count = 0
        for char in block:
            if char == '#':
                count += 1
            else:
                break        
        if 1 <= count <= 6 and block[count] == ' ':
            return BlockType.Heading
        else:
            return BlockType.Paragraph

    elif block.startswith('```') and block.endswith('```'):
        return BlockType.Code
    elif all(line.startswith('>') for line in lines):
        return BlockType.Quote

    elif all(line.startswith(('* ', '- ')) for line in lines):
        return BlockType.Unordered_List

    elif all(line.startswith(f"{i+1}. ") for i, line in enumerate(lines)):
        return BlockType.Ordered_List
    
    else:
        return BlockType.Paragraph

def extract_title(markdown):
    lines = markdown.splitlines()
    for line in lines:
        print("Inspecting line:", line)
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No H1 header found")

        



    




            

