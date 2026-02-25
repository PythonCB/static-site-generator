import unittest
from src.htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node, extract_markdown_images, extract_markdown_links, \
                         split_nodes_image, split_nodes_link, text_to_textnodes
from block import markdown_to_blocks, block_to_block_type, BlockType  
from textnode import TextNode, TextType
import re


class TestHtmlNode(unittest.TestCase):
    # def test_eq(self):
    #     node = HTMLNode("div", props={"class": "container"})
    #     node2 = HTMLNode("div", props={"class": "container"})
    #     self.assertEqual(node, node2)

    def test_props_to_html(self):
        node = HTMLNode("a", props={"href": "https://www.google.com"})
        self.assertEqual(node.props_to_html(), ' href=https://www.google.com')

    def test_props_to_html2(self):
        node = HTMLNode("a", props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href=https://www.google.com target=_blank')

    def test_repr(self):
        node = HTMLNode("p", value="This is a paragraph", props={"class": "text"})
        self.assertEqual(
            repr(node),
            'HTMLNode(tag=p, value=This is a paragraph, children=None, props={\'class\': \'text\'})'
        )


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_div(self):
        node = LeafNode("div", "Hello, world!")
        self.assertEqual(node.to_html(), "<div>Hello, world!</div>")

    def test_leaf_to_html_span(self):
        node = LeafNode("span", "Hello, world!")
        self.assertEqual(node.to_html(), "<span>Hello, world!</span>")


class TestParentNode(unittest.TestCase):
    def test_parent_to_html(self):
        child1 = LeafNode("p", "This is a paragraph")
        child2 = LeafNode("a", "Click here", props={"href": "https://www.google.com"})
        parent = ParentNode("div", children=[child1, child2])
        self.assertEqual(
            parent.to_html().replace("\n", ""),
            "<div><p>This is a paragraph</p><a href=https://www.google.com>Click here</a></div>"
        )

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html().replace("\n", ""), 
            "<div><span>child</span></div>"
        )

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html().replace("\n", ""),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold text")

    def test_italic(self):
        node = TextNode("This is italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is italic text")

    def test_code(self):
        node = TextNode("This is code text", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is code text")

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, url="https://www.google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props["href"], "https://www.google.com")

    def test_image(self):
        node = TextNode(None, TextType.IMAGE, url="https://www.google.com/image.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertIsNone(html_node.value)
        self.assertEqual(html_node.props["src"], "https://www.google.com/image.jpg")

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_no_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image] no image url"
        )
        self.assertListEqual([], matches) 

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://www.google.com) and another [link](https://www.yomamma.com)"
        )   
        self.assertListEqual([("link", "https://www.google.com"), ("link", "https://www.yomamma.com")], matches) 

    def test_extract_markdown_no_links(self):
        matches = extract_markdown_links(
            "This is text with an [link] no link url"
        )
        self.assertListEqual([], matches) 

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images2(self):
        node = TextNode(
            "This is text with no images",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with no images", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_images3(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png) yall",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
                TextNode(" yall", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_nodes_link(self):
        node = TextNode(
            "This is text with a [link](https://www.google.com) and another [link](https://www.yomamma.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.google.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.yomamma.com"),
            ],
            new_nodes,
        )

    def test_split_nodes_link2(self):
        node = TextNode(
            "This is text with no links",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with no links", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_nodes_link3(self):
        node = TextNode(
            "[link](https://www.google.com) and another [link](https://www.yomamma.com) yall",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("link", TextType.LINK, "https://www.google.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.yomamma.com"),
                TextNode(" yall", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_text_to_nodes(self):
        text = "This is a text node"
        nodes = text_to_textnodes(text)
        
        self.assertListEqual(
            [TextNode("This is a text node", TextType.TEXT)],
            nodes,
        )

    def test_text_to_nodes2(self):
        text = "This is _italic_ text **and bold** text too `code` also ![image](https://i.imgur.com/zjjcJKZ.png)" \
                " with a [link](https://www.google.com)"
        nodes = text_to_textnodes(text)

        print("nodes", nodes)

        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text ", TextType.TEXT),
                TextNode("and bold", TextType.BOLD),
                TextNode(" text too ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" also ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.google.com"),  
            ],
            nodes,
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type(self):
        self.assertEqual(block_to_block_type("This is a paragraph"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("# This is a heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("```\nprint('hello')\nprint('yo mamma')\n```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("- Item 1\n- Item 2"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("1. Item 1\n2. Item 2"), BlockType.ORDERED_LIST)

    def test_block_to_block_type(self):
        self.assertEqual(block_to_block_type("This is a paragraph. yall.\n straight up"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("# This is a heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("```\nprint('hello')\n```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("> This is a quote\n> multiline"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("- Item 1\n- Item 2"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("1. Item 1\n2. Item 2"), BlockType.ORDERED_LIST)


if __name__ == "__main__":
    unittest.main()
