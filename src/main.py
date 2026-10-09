from pathlib import Path

from ai_extractor import extract_invoice_with_ai
from ocr_reader import extract_text_from_image
from pdf_reader import extract_text_from_pdf
from output_writer import save_result
from schemas import Invoice


def read_document(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".txt":
        with open(file_path, "r") as file:
            return file.read()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(file_path)

    raise ValueError(f"Unsupported file type: {extension}")


def main():
    input_file = "data/samples/invoice_006.png"

    text = read_document(input_file)

    data = extract_invoice_with_ai(text)

    invoice = Invoice(
        invoice_number=data["invoice_number"],
        invoice_date=data["invoice_date"],
        vendor_name=data["vendor_name"],
        subtotal=float(data["subtotal"]),
        tax=float(data["tax"]),
        total=float(data["total"]),
        currency=data["currency"]
    )

    output_file = "output/extracted/invoice_006_result.json"

    save_result(invoice, output_file)

    print("Extraction completed successfully.")
    print(invoice)
    print(f"Result saved to: {output_file}")


if __name__ == "__main__":
    main()
