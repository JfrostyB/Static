import unittest

from nodes import HTMLNode, LeafNode, ParentNode
from htmlnode import markdown_to_html_node, text_to_children

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_no_props(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_one_props(self):
        node2 = HTMLNode(props={"href": "https://google.com"})
        self.assertEqual(node2.props_to_html(), ' href="https://google.com"')

    def test_props_to_html_multiple_props(self):
        node3 = HTMLNode(props={
            "href": "https://google.com",
            "target": "_blank"
        })
        self.assertEqual(node3.props_to_html(), ' href="https://google.com" target="_blank"')

    def test_parent_node_basic(self):
        node4 = ParentNode(
            "div",
            [LeafNode("span", "Hello")],
        )
        self.assertEqual(node4.to_html(), "<div><span>Hello</span></div>")

    def test_parent_node_with_props(self):
        node5 = ParentNode(
            "div",
            [LeafNode("span", "Hello")],
            {"class": "greeting"}
        )
        self.assertEqual(node5.to_html(), '<div class="greeting"><span>Hello</span></div>')

    def test_parent_node_missing_tag(self):
        node6 = ParentNode(None, [LeafNode("span", "Hello")])
        with self.assertRaises(ValueError):
            node6.to_html()

    def test_parent_node_missing_children(self):
        node7 = ParentNode(
            "div",
            None
        )
        with self.assertRaises(ValueError):
            node7.to_html()

    def test_nested_parent_nodes(self):
        inner_parent = ParentNode(
            "div",
            [LeafNode("span", "Hello")]
        )
        outer_parent = ParentNode(
            "section",
            [       
                inner_parent,
                LeafNode("p", "World")
            ]
        )
        self.assertEqual(outer_parent.to_html(),   "<section><div><span>Hello</span></div><p>World</p></section>")

    def test_parent_node_multiple_children(self):
        node9 = ParentNode(
            "div",
            [
                LeafNode("span", "Hello"),
                LeafNode("p", "World"),
                LeafNode("b", "Bold"),
                LeafNode("i", "Italic")
            ]
        )
        self.assertEqual(node9.to_html(),  "<div><span>Hello</span><p>World</p><b>Bold</b><i>Italic</i></div>")

    def test_parent_node_sporadic_children(self):
        node10 = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text")
            ]
        )
        self.assertEqual(node10.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")

    def test_paragraph_block(self):
        text = "This is a paragraph"
        node = markdown_to_html_node(text)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 1)
        paragraph_node = node.children[0]
        self.assertIsInstance(paragraph_node, ParentNode)
        self.assertEqual(paragraph_node.tag, "p")
        self.assertEqual(len(paragraph_node.children), 1)
        text_node = paragraph_node.children[0]
        self.assertIsInstance(text_node, LeafNode)
        self.assertEqual(text_node.value, "This is a paragraph")

    def test_heading_block(self):
        text = "# This is a heading"
        node = markdown_to_html_node(text)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "div")
        heading_node = node.children[0]
        self.assertIsInstance(heading_node, ParentNode)
        self.assertEqual(heading_node.tag, "h1")
        self.assertEqual(len(heading_node.children), 1)
        text_node = heading_node.children[0]
        self.assertIsInstance(text_node, LeafNode)
        self.assertEqual(text_node.value, "This is a heading")

    def test_multiple_headings(self):
        text = "# Heading 1\n\n## Heading 2"
        node = markdown_to_html_node(text)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 2)
        heading1 = node.children[0]
        self.assertIsInstance(heading1, ParentNode)
        self.assertEqual(heading1.tag, "h1")
        heading2 = node.children[1]
        self.assertIsInstance(heading2, ParentNode)
        self.assertEqual(heading2.tag, "h2")
        text_node1 = heading1.children[0]
        self.assertIsInstance(text_node1, LeafNode)
        self.assertEqual(text_node1.value, "Heading 1")
        text_node2 = heading2.children[0]
        self.assertIsInstance(text_node2, LeafNode)
        self.assertEqual(text_node2.value, "Heading 2")

    def test_code(self):
        text = "```\nthis is a code block\n```"
        node = markdown_to_html_node(text)
        self.assertIsInstance(node.children[0], ParentNode)
        self.assertEqual(node.children[0].tag, "pre")
        pre_node = node.children[0]
        self.assertEqual(pre_node.children[0].tag, "code")
        code_node = pre_node.children[0]
        text_node = code_node.children[0]
        self.assertEqual(text_node.value, "this is a code block")

    def test_quote(self):
        text = "> This is a quote"
        node = markdown_to_html_node(text)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 1)
        quote_node = node.children[0]
        self.assertIsInstance(quote_node, ParentNode)
        self.assertEqual(quote_node.tag, "blockquote")
        self.assertEqual(len(quote_node.children), 1)
        text_node = quote_node.children[0]
        self.assertEqual(text_node.value, "This is a quote")

    def test_unordered_list(self):
        text = "* Item 1\n* Item 2"
        node = markdown_to_html_node(text)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 1)
        ul_node = node.children[0]
        self.assertIsInstance(ul_node, ParentNode)
        self.assertEqual(ul_node.tag, "ul")
        self.assertEqual(len(ul_node.children), 2)
        item1 = ul_node.children[0]
        self.assertIsInstance(item1, ParentNode)
        self.assertEqual(item1.tag, "li")
        item2 = ul_node.children[1]
        self.assertIsInstance(item2, ParentNode)
        self.assertEqual(item2.tag, "li")
        text_node1 = item1.children[0]
        self.assertIsInstance(text_node1, LeafNode)
        self.assertEqual(text_node1.value, "Item 1")
        text_node2 = item2.children[0]
        self.assertIsInstance(text_node2, LeafNode)
        self.assertEqual(text_node2.value, "Item 2")

    def test_ordered_list(self):
        text = "1. First item\n2. Second item"
        node = markdown_to_html_node(text)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 1)
        ol_node = node.children[0]
        self.assertIsInstance(ol_node, ParentNode)
        self.assertEqual(ol_node.tag, "ol")
        self.assertEqual(len(ol_node.children), 2)
        item1 = ol_node.children[0]
        self.assertIsInstance(item1, ParentNode)
        self.assertEqual(item1.tag, "li")
        item2 = ol_node.children[1]
        self.assertIsInstance(item2, ParentNode)
        self.assertEqual(item2.tag, "li")
        text_node1 = item1.children[0]
        self.assertIsInstance(text_node1, LeafNode)
        self.assertEqual(text_node1.value, "First item")
        text_node2 = item2.children[0]
        self.assertIsInstance(text_node2, LeafNode)
        self.assertEqual(text_node2.value, "Second item")

        # finish value error test later

if __name__ == "__main__":
    unittest.main()