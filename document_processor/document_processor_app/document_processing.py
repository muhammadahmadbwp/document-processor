import pdfplumber

def pdf_to_markdown(file_obj):
    full_text = ""
    basic_info = {
        "title": None,
        "author": None,
        "pages": 0,
        "subject": None,
        "creator": None,
    }

    with pdfplumber.open(file_obj) as pdf:
        basic_info["pages"] = len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text += f"\n\n## Page {i + 1}\n\n{text.strip()}"

    return basic_info, full_text