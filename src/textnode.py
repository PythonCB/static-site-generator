from enum import Enum

class TextType(Enum):
    BOLD = 'bold text'
    ITALIC = 'italic text'
    CODE = 'code text'
    LINK = 'link'
    IMAGE = 'image'
    TEXT = 'plain text'

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


# def split_nodes_delimiter(old_nodes, delimiter, text_type):
#     new_nodes = []
    
#     for node in old_nodes:
#         special = False
#         if node.text_type == TextType.TEXT:
#             parts = node.text.split(delimiter)
#             for i, part in enumerate(parts):
#                 if special:
#                     new_nodes.append(TextNode(part, text_type))
#                 else:
#                     new_nodes.append(TextNode(part, TextType.TEXT))
#                 special = not special
#         else:
#             new_nodes.append(node)
#     return new_nodes


# def split_nodes_delimiter(old_nodes, delimiter, text_type):
#     new_nodes = []
    
#     for node in old_nodes:
#         if node.text_type == TextType.TEXT:
#             parts = node.text.split(delimiter)
#             if len(parts) % 2 == 0:
#                 raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {node.text}")
#             for i, part in enumerate(parts):
#                 if part == "":
#                     continue
#                 if i % 2 == 0:
#                     new_nodes.append(TextNode(part, TextType.TEXT))
#                 else:
#                     new_nodes.append(TextNode(part, text_type))
#         else:
#             new_nodes.append(node)
#     return new_nodes

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        start = 0
        special = False

        while True:
            index = text.find(delimiter, start)

            if index == -1:
                # No more delimiters
                remaining = text[start:]
                if remaining:
                    new_nodes.append(
                        TextNode(remaining, text_type if special else TextType.TEXT)
                    )
                break

            # Add text before delimiter
            if index > start:
                segment = text[start:index]
                new_nodes.append(
                    TextNode(segment, text_type if special else TextType.TEXT)
                )

            special = not special
            start = index + len(delimiter)

        if special:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {text}")

    return new_nodes



