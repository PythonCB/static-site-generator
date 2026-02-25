import unittest
from src.htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node, extract_markdown_images, extract_markdown_links, \
                         split_nodes_image, split_nodes_link, text_to_textnodes
from block import markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node, clean_block_text, text_to_children, extract_title
from textnode import TextNode, TextType
import re

class TestHtmlNode(unittest.TestCase):
    def test_leaf_node_to_html(self):
        leaf = LeafNode("p", "This is a paragraph")
        self.assertEqual(leaf.to_html().replace("\n", ""), "<p>This is a paragraph</p>")

    def test_parent_node_to_html(self):
        child1 = LeafNode("p", "This is a paragraph")
        child2 = LeafNode("a", "Click here", props={"href": "https://www.google.com"})
        parent = ParentNode("div", children=[child1, child2])
        self.assertEqual(
            parent.to_html().replace("\n", ""),
            "<div><p>This is a paragraph</p><a href=https://www.google.com>Click here</a></div>"
        )

    def test_md_to_html(self):
        md = "This is a **bold** word and this is an _italic_ word.\n\n" \
             "This is a [link](https://www.example.com) and this is an image: ![alt text](https://www.example.com/image.jpg)"
        html_node = markdown_to_html_node(md)
        expected_html = "<div><p>This is a <b>bold</b> word and this is an <i>italic</i> word.</p>" \
                        "<p>This is a <a href=https://www.example.com>link</a> and " \
                        "this is an image: <img src=https://www.example.com/image.jpg>alt text</img></p></div>"
        self.assertEqual(html_node.to_html().replace("\n", ""), expected_html)

    def test_extract_title(self):
        md = "# My Title\n\nThis is some content.\n\n## Subtitle\n\nMore content."
        title = extract_title(md)
        self.assertEqual(title, "My Title")
