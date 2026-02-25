import re
from enum import Enum
from htmlnode import HTMLNode, ParentNode, LeafNode, text_node_to_html_node, text_to_textnodes 
from textnode import TextNode, TextType, split_nodes_delimiter

class BlockType(Enum):
    PARAGRAPH = 'p'
    HEADING = 'h1'
    HEADING2 = 'h2'
    HEADING3 = 'h3'
    HEADING4 = 'h4'
    HEADING5 = 'h5'
    HEADING6 = 'h6'
    CODE = 'code'
    QUOTE = 'blockquote'
    UNORDERED_LIST = 'ul'
    ORDERED_LIST = 'ol'
    
def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in blocks if block.strip() != ""]
    return blocks

def block_to_block_type(block):
    if re.match(r'^(#{1}) .+$', block):
        return BlockType.HEADING
    elif re.match(r'^(#{2}) .+$', block):
        return BlockType.HEADING2
    elif re.match(r'^(#{3}) .+$', block):
        return BlockType.HEADING3
    elif re.match(r'^(#{4}) .+$', block):
        return BlockType.HEADING4
    elif re.match(r'^(#{5}) .+$', block):
        return BlockType.HEADING5
    elif re.match(r'^(#{6}) .+$', block):
        return BlockType.HEADING6
    elif re.match(r"^```[\s\S]*?```$", block):
        return BlockType.CODE
    elif re.match(r'^(?:> ?.*(?:\n|$))+$', block):
        return BlockType.QUOTE
    elif re.match(r"^(?:- .+(?:\n|$))+$", block):
        return BlockType.UNORDERED_LIST
    elif re.match(r'^(?:\d+\. .+(?:\n|$))+$', block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def  markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    block_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)

        # stripping block type markers from the block text
        block_text = clean_block_text(block, block_type)

        children = text_to_children(block_text)
        block_node = ParentNode(tag=block_type.value, children=children)
        block_nodes.append(block_node)
    return ParentNode(tag="div", children=block_nodes)

def clean_block_text(block, block_type):
    if block_type in (
        BlockType.HEADING,
        BlockType.HEADING2,
        BlockType.HEADING3,
        BlockType.HEADING4,
        BlockType.HEADING5,
        BlockType.HEADING6,
    ):
        return re.sub(r'^(#{1,6}) ', '', block)

    elif block_type == BlockType.CODE:
        return re.sub(r'^```|```$', '', block)

    elif block_type == BlockType.QUOTE:
        return re.sub(r'^> ?', '', block, flags=re.MULTILINE)

    elif block_type == BlockType.UNORDERED_LIST:
        lines = block.split('\n')
        items = [
            f"<li>{re.sub(r'^- ', '', line)}</li>"
            for line in lines if line.strip()
        ]
        return "  " + "\n  ".join(items)

    elif block_type == BlockType.ORDERED_LIST:
        lines = block.split('\n')
        items = []
        for line in lines:
            if line.strip():
                cleaned = re.sub(r'^\d+\. ', '', line)
                items.append(f"<li>{cleaned}</li>")
        return "  " + "\n  ".join(items)

    else:
        return block


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = [text_node_to_html_node(node) for node in text_nodes]
    return html_nodes


def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.startswith("# "):
            return block[2:].strip()
    raise ValueError("No title found in markdown")

import os

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using template {template_path}")
    
    with open(from_path, 'r') as f:
        markdown = f.read()

    html_node = markdown_to_html_node(markdown)
    html = html_node.to_html()
    title = extract_title(markdown)
    
    with open(template_path, 'r') as f:
        template = f.read()

    html = template.replace("{{ Title }}", title).replace("{{ Content }}", html)

    # ✅ Ensure destination directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, 'w') as f:
        f.write(html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for item in os.listdir(dir_path_content):
        content_path = os.path.join(dir_path_content, item)
        dest_path = os.path.join(dest_dir_path, item.replace('.md', '.html'))

        if os.path.isdir(content_path):
            generate_pages_recursive(content_path, template_path, dest_path)
        elif content_path.endswith('.md'):
            generate_page(content_path, template_path, dest_path)


if __name__ == "__main__":
    md = "this is a paragraph.\n\nthis is another **bold** paragraph\n\n# Heading 1\n\n## Heading 2\n\n" \
         "> this is a quote.\n> second _line_ of quote.\n\nthis is an image: ![alt text yall](https://example.com/image.jpg)\n\n" \
         "this is a link: [link text up in here](https://example.com)" 
    blocks = markdown_to_blocks(md)

    print("blocks\n", blocks)
    for block in blocks:
        print(f"block: {block}\nblock type: {block_to_block_type(block)}\n")
    html_node = markdown_to_html_node(md)
    print(html_node.to_html(), "\n\n")

    md = "```python\nprint('hello world')\nprint('yo mamma so fat')```"
    html_node = markdown_to_html_node(md)
    print(html_node.to_html(), "\n\n")

    md = "- item 1\n- item 2\n- item 3"
    html_node = markdown_to_html_node(md)
    print(html_node.to_html(), "\n\n")

    md = "1. item 1\n2. item 2\n3. item 3"
    html_node = markdown_to_html_node(md)
    print(html_node.to_html())