from textnode import TextNode, TextType
import os
import shutil
from block import generate_page, generate_pages_recursive


def copy_directory(src, dest):
    # 1. If destination exists, remove it completely
    if os.path.exists(dest):
        print(f"Deleting existing destination: {dest}")
        shutil.rmtree(dest)

    # 2. Recreate empty destination directory
    os.makedirs(dest, exist_ok=True)

    # 3. Iterate through items in source directory
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dest_path = os.path.join(dest, item)

        if os.path.isdir(src_path):
            # Recursively copy subdirectory
            copy_directory(src_path, dest_path)
        else:
            # Copy file
            print(f"Copying file: {src_path} -> {dest_path}")
            shutil.copy2(src_path, dest_path)


def main():
    copy_directory("static", "public")
    # generate_page("content/index.md", "template.html", "public/index.html")
    generate_pages_recursive("content", "template.html", "public")

if __name__ == '__main__':
    main()
