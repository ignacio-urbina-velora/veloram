import docx

def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

if __name__ == "__main__":
    import sys
    file_path = "maniqui fase.docx"
    try:
        print(read_docx(file_path))
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
