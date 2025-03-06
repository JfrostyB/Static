import unittest

from textnode import (
    TextNode, 
    TextType, 
    text_node_to_html_node, 
    split_nodes_delimiter, 
    extract_markdown_images, 
    extract_markdown_links, 
    split_nodes_link, 
    split_nodes_image, 
    text_to_textnodes, 
    markdown_to_blocks,
    BlockType,
    block_to_block_type,
    extract_title
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_different_text(self):
        node3 = TextNode("This is a text node", TextType.BOLD)
        node4 = TextNode("This is a different node", TextType.BOLD)
        self.assertNotEqual(node3, node4)

    def test_different_type(self):
        node5 = TextNode("This is a text node", TextType.TEXT)
        node6 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node5, node6)

    def test_different_text_type(self):
        node7 = TextNode("This is one text node", TextType.TEXT)
        node8 = TextNode("This is another text node", TextType.BOLD)
        self.assertNotEqual(node7, node8)

    def test_same_url(self):
        node9 = TextNode("This is a text node", TextType.BOLD, "https://www.example.com")
        node10 = TextNode("This is a text node", TextType.BOLD, "https://www.example.com")
        self.assertEqual(node9, node10)

    def test_different_url(self):
        node11 = TextNode("This is a text node", TextType.BOLD, "https://www.example1.com")
        node12 = TextNode("This is a text node", TextType.BOLD, "https://www.example2.com")
        self.assertNotEqual(node11, node12)

    def test_one_url(self):
        node13 = TextNode("This is a text node", TextType.BOLD, "https://www.example.com")
        node14 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node13, node14)

    def test_text_type(self):
        node15 = TextNode("This is a text", TextType.TEXT)
        node16 = text_node_to_html_node(node15)
        self.assertIsNone(node16.tag)
        self.assertEqual(node16.value, "This is a text")
    
    def test_bold_type(self):
        node17 = TextNode("Bold text", TextType.BOLD)
        node18 = text_node_to_html_node(node17)
        self.assertEqual(node18.tag, "b")
        self.assertEqual(node18.value, "Bold text")

    def test_italic_type(self):
        node19 = TextNode("Italic text", TextType.ITALIC)
        node20 = text_node_to_html_node(node19)
        self.assertEqual(node20.tag, "i")
        self.assertEqual(node20.value, "Italic text")

    def test_code_type(self):
        node21 = TextNode("Code", TextType.CODE)
        node22 = text_node_to_html_node(node21)
        self.assertEqual(node22.tag, "code")
        self.assertEqual(node22.value, "Code")

    def test_link_type(self):
        node23 = TextNode("Click me", TextType.LINK, "https://www.google.com")
        node24 = text_node_to_html_node(node23)
        self.assertEqual(node24.tag, "a")
        self.assertEqual(node24.value, "Click me")
        self.assertEqual(node24.props["href"], "https://www.google.com")

    def test_image_type(self):
        node25 = TextNode("alt text", TextType.IMAGE, "https://www.google.com/image.png")
        node26 = text_node_to_html_node(node25)
        self.assertEqual(node26.tag, "img")
        self.assertEqual(node26.value, "")
        self.assertEqual(node26.props["src"], "https://www.google.com/image.png")
        self.assertEqual(node26.props["alt"], "alt text")

    def test_invalid_type(self):
        node27 = TextNode("some text", None)
        with self.assertRaises(Exception):
            text_node_to_html_node(node27)

    def test_split_nodes_delimiter_basic(self):
        node28 = TextNode("hello `code` world", TextType.TEXT)
        node29 = split_nodes_delimiter([node28], "`", TextType.CODE)
        self.assertEqual(len(node29), 3)

        self.assertEqual(node29[0].text, "hello ")
        self.assertEqual(node29[0].text_type, TextType.TEXT)

        self.assertEqual(node29[1].text, "code")
        self.assertEqual(node29[1].text_type, TextType.CODE)
        
        self.assertEqual(node29[2].text, " world")
        self.assertEqual(node29[2].text_type, TextType.TEXT)

    def test_split_nodes_delimiter_bold(self):
        node30 = TextNode("hello **bold** world", TextType.TEXT)
        node31 = split_nodes_delimiter([node30], "**", TextType.BOLD)
        self.assertEqual(len(node31), 3)

        self.assertEqual(node31[0].text, "hello ")
        self.assertEqual(node31[0].text_type, TextType.TEXT)

        self.assertEqual(node31[1].text, "bold")
        self.assertEqual(node31[1].text_type, TextType.BOLD)

        self.assertEqual(node31[2].text, " world")
        self.assertEqual(node31[2].text_type, TextType.TEXT)

    def test_split_nodes_delimiter_no_closing(self):
        node32 = TextNode("hello `code without closing", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node32], "`", TextType.CODE)
    
    def test_split_nodes_delimiter_no_delimiters(self):
        node33 = TextNode("hello world plain text", TextType.TEXT)
        node34 = split_nodes_delimiter([node33], "`", TextType.CODE)

        self.assertEqual(len(node34), 1)

        self.assertEqual(node34[0].text, "hello world plain text")
        self.assertEqual(node34[0].text_type, TextType.TEXT)

    def test_extract_markdown_images(self):
        test1 = "![alt text](http://example.com/image.png)"
        self.assertEqual(
            extract_markdown_images(test1),
            [("alt text", "http://example.com/image.png")]
        )

        test2 = "![img1](url1) some text ![img2](url2)"
        self.assertEqual(
            extract_markdown_images(test2),
            [("img1", "url1"), ("img2", "url2")]
        )

        test3 = "plain text without images"
        self.assertEqual(extract_markdown_images(test3), [])

    def test_extract_markdown_links(self):
        test1 = "[link text](https://example.com)"
        self.assertEqual(
            extract_markdown_links(test1),
            [("link text", "https://example.com")]
        )

        test2 = "[link1](url1) some text [link2](url2)"
        self.assertEqual(
            extract_markdown_links(test2),
            [("link1", "url1"), ("link2", "url2")]
        )

        test3 = "plain text without link"
        self.assertEqual(extract_markdown_links(test3), [])

    def test_extract_markdown_images_links(self):
        test1 =  "![image](img.png) and a [link](https://example.com)"

        self.assertEqual(
            extract_markdown_images(test1),
            [("image", "img.png")]
        )

        self.assertEqual(
            extract_markdown_links(test1),
            [("link", "https://example.com")]
        )

    def test_extract_markdown_edge_cases(self):

        self.assertEqual(extract_markdown_images(""), [])
        self.assertEqual(extract_markdown_links(""), [])

        test1 = "![missing closing](http://example.com/image.png"
        test2 = "[missing closing](https://example.com"
        self.assertEqual(extract_markdown_images(test1), [])
        self.assertEqual(extract_markdown_links(test2), [])

    def test_no_images(self):
        node = TextNode("This is a text without images", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "This is a text without images")
        self.assertEqual(result[0].text_type, TextType.TEXT)

    def test_single_image(self):
        node = TextNode("Here is an image ![alt](url) in the text", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "Here is an image ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "alt")
        self.assertEqual(result[1].text_type, TextType.IMAGE)
        self.assertEqual(result[1].url, "url")
        self.assertEqual(result[2].text, " in the text")
        self.assertEqual(result[2].text_type, TextType.TEXT)
        

    def test_multiple_images(self):
        node = TextNode("Text with ![img1](url1) and another ![img2](url2)", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].text, "Text with ")
        self.assertEqual(result[1].text, "img1")
        self.assertEqual(result[1].text_type, TextType.IMAGE)
        self.assertEqual(result[1].url, "url1")
        self.assertEqual(result[2].text, " and another ")
        self.assertEqual(result[3].text, "img2")
        self.assertEqual(result[3].text_type, TextType.IMAGE)
        self.assertEqual(result[3].url, "url2") 

    def test_no_links(self):
        node = TextNode("This text has no links", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "This text has no links")
        self.assertEqual(result[0].text_type, TextType.TEXT)

    def test_single_link(self):
        node = TextNode("This is a [link to Boot.dev](https://www.boot.dev).", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "This is a ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "link to Boot.dev")
        self.assertEqual(result[1].text_type, TextType.LINK)
        self.assertEqual(result[1].url, "https://www.boot.dev")
        self.assertEqual(result[2].text, ".")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_multiple_links(self):
        node = TextNode("This has a [link1](url1) and another [link2](url2).", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].text, "This has a ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "link1")
        self.assertEqual(result[1].text_type, TextType.LINK)
        self.assertEqual(result[1].url, "url1")
        self.assertEqual(result[2].text, " and another ")
        self.assertEqual(result[2].text_type, TextType.TEXT)
        self.assertEqual(result[3].text, "link2")
        self.assertEqual(result[3].text_type, TextType.LINK)
        self.assertEqual(result[3].url, "url2")
        self.assertEqual(result[4].text, ".")
        self.assertEqual(result[4].text_type, TextType.TEXT)

    def test_basic_text(self):
        text = "just text"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "just text")
        self.assertEqual(result[0].text_type, TextType.TEXT)

    def test_text_with_image(self):
        text = "This is an ![image](https://example.com/img.jpg) in text"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "This is an ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "image")
        self.assertEqual(result[1].text_type, TextType.IMAGE)
        self.assertEqual(result[1].url, "https://example.com/img.jpg")
        self.assertEqual(result[2].text, " in text")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_text_with_link(self):
        text = "This is an [link](https://boot.dev) in text"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "This is an ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "link")
        self.assertEqual(result[1].text_type, TextType.LINK)
        self.assertEqual(result[1].url, "https://boot.dev")
        self.assertEqual(result[2].text, " in text")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_no_text(self):
        text = ""
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 0)

    def test_text_with_bold(self):
        text = "this is **bold** text"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "this is ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "bold")
        self.assertEqual(result[1].text_type, TextType.BOLD)
        self.assertEqual(result[2].text, " text")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_text_with_italic(self):
        text = "this is *italic* text"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "this is ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "italic")
        self.assertEqual(result[1].text_type, TextType.ITALIC)
        self.assertEqual(result[2].text, " text")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_text_with_code(self):
        text = "this is `code block` text"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "this is ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "code block")
        self.assertEqual(result[1].text_type, TextType.CODE)
        self.assertEqual(result[2].text, " text")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_text_with_multiple_nodes(self):
        text = "this is **bold** and *italic* and `code` in text"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 7)
        self.assertEqual(result[0].text, "this is ")
        self.assertEqual(result[0].text_type, TextType.TEXT)
        self.assertEqual(result[1].text, "bold")
        self.assertEqual(result[1].text_type, TextType.BOLD)
        self.assertEqual(result[2].text, " and ")
        self.assertEqual(result[2].text_type, TextType.TEXT)
        self.assertEqual(result[3].text, "italic")
        self.assertEqual(result[3].text_type, TextType.ITALIC)
        self.assertEqual(result[4].text, " and ")
        self.assertEqual(result[4].text_type, TextType.TEXT)
        self.assertEqual(result[5].text, "code")
        self.assertEqual(result[5].text_type, TextType.CODE)
        self.assertEqual(result[6].text, " in text")
        self.assertEqual(result[6].text_type, TextType.TEXT)

    def test_mismatched_delimiters(self):
        text = "**bold*"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 1)
        self.assertNotEqual(result[0].text_type, TextType.BOLD)

    def test_empty_delimiters(self):
        text = "****"
        result = text_to_textnodes(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text_type, TextType.TEXT)

    def test_empty_markdown(self):
        self.assertEqual(markdown_to_blocks(""), [])

    def test_single_block(self):
        self.assertEqual(
            markdown_to_blocks("Hello"),
            ["Hello"]
        )
        
    def test_multiple_blocks(self):
        self.assertEqual(
            markdown_to_blocks("Hello\n\nWorld"),
        ["Hello", "World"]
        )

    def test_block_between_newlines(self):
        self.assertEqual(
            markdown_to_blocks("\n\nWorld\n\n"),
        ["World"]
        )

    def test_blocks_with_whitespace(self):
        self.assertEqual(
            markdown_to_blocks("  Hello  \n\n  World  "),
            ["Hello", "World"]
        )

    def test_paragraph(self):
        text = "Thsi is a normal paragraph"
        self.assertEqual(block_to_block_type(text), BlockType.Paragraph)

    def test_heading(self):
        text = "# heading text"
        self.assertEqual(block_to_block_type(text), BlockType.Heading)
        text2 = "###### heading text"
        self.assertEqual(block_to_block_type(text2), BlockType.Heading) 
        text3 = "####### heading text"
        self.assertEqual(block_to_block_type(text3), BlockType.Paragraph)
        text4 = "#heading text"
        self.assertEqual(block_to_block_type(text4), BlockType.Paragraph)

    def test_code(self):
        text = "```\nsome code\n```"
        self.assertEqual(block_to_block_type(text), BlockType.Code)
        text2 = "```\nsome code"
        self.assertEqual(block_to_block_type(text2), BlockType.Paragraph)
        text3 = "some code\n```"
        self.assertEqual(block_to_block_type(text3), BlockType.Paragraph)

    def test_quote(self):
        text = ">this is quote "
        self.assertEqual(block_to_block_type(text), BlockType.Quote)
        text2 = ">First line\n>Second line\n>Third line"
        self.assertEqual(block_to_block_type(text2), BlockType.Quote)
        text3 = ">First line\nSecond line\n>Third line"
        self.assertEqual(block_to_block_type(text3), BlockType.Paragraph)

    def test_unordered_list(self):
        text = "* item one"
        self.assertEqual(block_to_block_type(text), BlockType.Unordered_List)
        text2 = "- item one"
        self.assertEqual(block_to_block_type(text2), BlockType.Unordered_List)
        text3 = "*item one"
        self.assertEqual(block_to_block_type(text3), BlockType.Paragraph)
        text4 = "-item one"
        self.assertEqual(block_to_block_type(text4), BlockType.Paragraph)
        text5 = "* item one\n* item two"
        self.assertEqual(block_to_block_type(text5), BlockType.Unordered_List)
        text6 = "- item one\n- item two"
        self.assertEqual(block_to_block_type(text6), BlockType.Unordered_List)
        text7 = "* item one\n- item two"
        self.assertEqual(block_to_block_type(text7), BlockType.Unordered_List)
        text8 = "- iteam one\n* item two"
        self.assertEqual(block_to_block_type(text8), BlockType.Unordered_List)
        text9 = "*item one\n- item two"
        self.assertEqual(block_to_block_type(text9), BlockType.Paragraph)
        text10 = "* iteam\n-iteam two"
        self.assertEqual(block_to_block_type(text10), BlockType.Paragraph)
        text11 = "* \n* item two"
        self.assertEqual(block_to_block_type(text11), BlockType.Unordered_List)
    
    def test_ordered_list(self):
        text = "1. First item"
        self.assertEqual(block_to_block_type(text), BlockType.Ordered_List)
        text2 = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(text2), BlockType.Ordered_List)
        text3 = "2. First item"
        self.assertEqual(block_to_block_type(text3), BlockType.Paragraph)
        text4 = "1. First item\n3. Second item"
        self.assertEqual(block_to_block_type(text4), BlockType.Paragraph)
        text5 = "1.First item"
        self.assertEqual(block_to_block_type(text5), BlockType.Paragraph)

    def test_extract_title(self):
        # normal case
        text = "# Hello"
        result = extract_title(text)
        self.assertEqual(result, "Hello")

        # No H1
        text = "This is just text\nNo headers here"
        with self.assertRaises(Exception):
            extract_title(text)

        # Whitespace Handling
        text = "# Hello "
        result = extract_title(text)
        self.assertEqual(result, "Hello")

        # Multiple Headers
        text = "# First H1\n## Second Header\n# Third Header"
        result = extract_title(text)
        self.assertEqual(result, "First H1")

        # Blank File
        text = ""
        with self.assertRaises(Exception):
            extract_title(text)
    

if __name__ == "__main__":
    unittest.main()