import docx
import sys
import os

def read_docx(file_path):
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

if __name__ == "__main__":
    file_path = "mejora 2d.docx"
    try:
        content = read_docx(file_path)
        print("---CONTENT START---")
        print(content)
        print("---CONTENT END---")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
