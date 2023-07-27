from docx import Document
import PyPDF2

def extract_text(file):
    if file.content_type == "application/pdf":
        pdf_reader = PyPDF2.PdfFileReader(file.file)
        text = " ".join(page.extractText() for page in pdf_reader.pages)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file.file)
        text = " ".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {file.content_type}")
    return text
