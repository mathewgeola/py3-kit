from pypdf import PdfWriter


def concat(
        input_pdf_file_paths: list[str],
        output_pdf_file_path: str
) -> bool:
    try:
        writer = PdfWriter()

        for input_pdf_file_path in input_pdf_file_paths:
            writer.append(input_pdf_file_path)

        with open(output_pdf_file_path, "wb") as f:
            writer.write(f)

        return True

    except Exception:  # noqa
        return False
