from textnode import TextNode, TextType, split_nodes_delimiter
import re

class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        """
        inputs:
        tag - A string representing the HTML tag name (e.g. "p", "a", "h1", etc.)
        value - A string representing the value of the HTML tag (e.g. the text inside a paragraph)
        children - A list of HTMLNode objects representing the children of this node
        props - A dictionary of key-value pairs representing the attributes of the HTML tag. 
                For example, a link (<a> tag) might have {"href": "https://www.google.com"}
        """
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props 

    def to_html(self):
        raise NotImplementedError("to be implemented by child classes")

    def props_to_html(self):
        result = ""
        if isinstance(self.props, dict):
            for k,v in self.props.items():
                result += f' {k}="{v}"'
        return result 

    def __repr__(self):
        result = []
        if self.tag:
            result.append(f"tag={self.tag}")
        else:
            result.append("tag=None")

        if self.value:
            result.append(f"value={self.value}")
        else:
            result.append("value=None")

        if self.children:
            result.append(", ".join(self.children))
        else:
            result.append("children=None")

        if self.props:
            str_props = "props={"
            for k,v in self.props.items():
                str_props += f"'{k}': '{v}', "
            str_props = str_props[:-2] + "}"
            result.append(str_props)
        else:
            result.append("props=None")

        return f"HTMLNode({', '.join(result)})"

    
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag, value=value, children=None, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError(f"Leaf nodes must have a value. tag: {self.tag}, props: {self.props}")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        result = []
        if self.tag:
            result.append(f"tag={self.tag}")
        else:
            result.append("tag=None")

        if self.value:
            result.append(f"value={self.value}")
        else:
            result.append("value=None")

        if self.props:
            str_props = "props={"
            for k,v in self.props.items():
                str_props += f"'{k}': '{v}', "
            str_props = str_props[:-2] + "}"
            result.append(str_props)
        else:
            result.append("props=None")

        return f"LeafNode({', '.join(result)})"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self):
        if self.children is None:
            raise ValueError("Parent nodes must have children")
        if self.tag is None:
            raise ValueError("Parent nodes must have a tag")

        return f"<{self.tag}{self.props_to_html()}>{''.join([child.to_html() for child in self.children])}</{self.tag}>\n"

    def __repr__(self):
        result = []
        if self.tag:
            result.append(f"tag={self.tag}")
        else:
            result.append("tag=None")

        if self.children:
            result.append(", ".join(self.children))
        else:
            result.append("children=None")

        if self.props:
            str_props = "props={"
            for k,v in self.props.items():
                str_props += f"'{k}': '{v}', "
            str_props = str_props[:-2] + "}"
            result.append(str_props)
        else:
            result.append("props=None")

        return f"ParentNode({', '.join(result)})"


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, props={"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", text_node.text, props={"src": text_node.url})
    else:
        raise ValueError(f"Unsupported text type: {text_node.text_type}")


def extract_markdown_images(text):
    # This function extracts markdown image syntax ![alt text](image_url) from the input text
    # and returns a list of tuples (alt_text, image_url)
    
    pattern = r'!\[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    # This function extracts markdown link syntax [link text](url) from the input text
    # and returns a list of tuples (link_text, url)
    
    pattern = r'\[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            matches = extract_markdown_images(node.text)
            if matches:
                # If there are markdown images, we need to split the text node into multiple nodes
                # For example, "This is an image ![alt text](image_url) in the text" would be split into:
                # [TextNode("This is an image ", TextType.TEXT), TextNode(None, TextType.IMAGE, url="image_url"), TextNode(" in the text", TextType.TEXT)]
                last_index = 0
                for alt_text, image_url in matches:
                    start_index = node.text.find(f"![{alt_text}]({image_url})", last_index)
                    if start_index != -1:
                        # Add the text before the image as a separate node
                        if start_index > last_index:
                            new_nodes.append(TextNode(node.text[last_index:start_index], TextType.TEXT))
                        # Add the image as a separate node
                        new_nodes.append(TextNode(alt_text, TextType.IMAGE, url=image_url))
                        last_index = start_index + len(f"![{alt_text}]({image_url})")
                # Add any remaining text after the last image as a separate node
                if last_index < len(node.text):
                    new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))
            else:
                new_nodes.append(node)
        else:
            new_nodes.append(node)
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            matches = extract_markdown_links(node.text)
            if matches:
                last_index = 0
                for link_text, url in matches:
                    start_index = node.text.find(f"[{link_text}]({url})", last_index)
                    if start_index != -1:
                        # Add the text before the link as a separate node
                        if start_index > last_index:
                            new_nodes.append(TextNode(node.text[last_index:start_index], TextType.TEXT))
                        # Add the link as a separate node
                        new_nodes.append(TextNode(link_text, TextType.LINK, url=url))
                        last_index = start_index + len(f"[{link_text}]({url})")
                # Add any remaining text after the last link as a separate node
                if last_index < len(node.text):
                    new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))
            else:
                new_nodes.append(node)
        else:
            new_nodes.append(node)
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


