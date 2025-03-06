from nodes import HTMLNode, LeafNode, ParentNode
from textnode import markdown_to_blocks, block_to_block_type, text_to_textnodes, text_node_to_html_node, BlockType

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    block_type_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.Paragraph:
            node = ParentNode(tag="p", children=text_to_children(block), props={})
            block_type_nodes.append(node)
        elif block_type == BlockType.Heading:
            level = 0
            for char in block:
                if char == "#":
                    level += 1
                else:
                    break
            heading_tag = f"h{level}"
            text = block[level:].strip()
            node = ParentNode(tag=heading_tag, children=text_to_children(text), props={})
            block_type_nodes.append(node)
        elif block_type == BlockType.Code:
            lines = block.split('\n')
            text = '\n'.join(lines[1:-1])
            code_node = ParentNode(tag="code", children=text_to_children(text), props={})
            pre_node = ParentNode(tag="pre", children=[code_node], props={})
            block_type_nodes.append(pre_node)
        elif block_type == BlockType.Quote:
            text = block.lstrip('>').strip()
            node = ParentNode(tag="blockquote", children=text_to_children(text), props={})
            block_type_nodes.append(node)
        elif block_type == BlockType.Unordered_List:
            lines = block.split("\n")
            list_items = []
            for line in lines:
                text = line.lstrip("* ").lstrip("- ").strip()
                li_node = ParentNode(tag="li", children=text_to_children(text), props={})
                list_items.append(li_node)
            node = ParentNode(tag="ul", children=list_items, props={})
            block_type_nodes.append(node)
        elif block_type == BlockType.Ordered_List:
            lines = block.split("\n")
            list_items = []
            for line in lines:
                text = line.split(". ", 1)[1].strip()
                li_node = ParentNode(tag="li", children=text_to_children(text), props={})
                list_items.append(li_node)
            node = ParentNode(tag="ol", children=list_items, props={})
            block_type_nodes.append(node)
        else:
            raise ValueError(f"Unknown block type: {block_type}")
    parent_node = ParentNode(tag="div", children=block_type_nodes, props={})
    return parent_node

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        html_nodes.append(html_node)

    return html_nodes



    


