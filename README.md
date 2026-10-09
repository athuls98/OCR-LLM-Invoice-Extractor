# OCR-LLM Invoice Extractor

A Python-based invoice extraction pipeline that processes text files, PDFs, and scanned images, then uses a local large language model to convert semi-structured document content into structured JSON.

The project combines traditional document-processing tools with a locally hosted LLM to handle invoice layouts that may be difficult to parse reliably with fixed rules alone.

## Features
- Supports TXT, PDF, PNG, JPG, and JPEG invoice inputs
- Extracts embedded PDF text with PyMuPDF
- Uses Tesseract OCR for scanned images
- Sends extracted text to a local Gemma 3 12B model through llama.cpp
- Converts semi-structured invoice text into predefined structured fields
- Maps extracted data into a Python `Invoice` dataclass
- Saves extracted invoice data as formatted JSON
- Runs locally without requiring a cloud AI API

## Architecture

```text
                 Input Document
                       |
          +------------+------------+
          |            |            |
         TXT          PDF         Image
          |            |            |
     Direct Read    PyMuPDF     Tesseract OCR
          |            |            |
          +------------+------------+
                       |
                    Raw Text
                       |
                       v
                Gemma 3 12B
                 via llama.cpp
                       |
                       v
               Structured Fields
                       |
                       v
                 Invoice Schema
                       |
                       v
                  JSON Output
```

## Project Structure

```text
ocr-llm-invoice-extractor/
├── data/
│   └── samples/
│       ├── invoice_003.txt
│       ├── invoice_004.pdf
│       └── invoice_006.png
├── output/
│   └── extracted/
│       └── invoice_006_result.json
├── src/
│   ├── ai_extractor.py
│   ├── main.py
│   ├── ocr_reader.py
│   ├── output_writer.py
│   ├── pdf_reader.py
│   └── schemas.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Technologies Used

- Python
- PyMuPDF
- Tesseract OCR
- pytesseract
- Pillow
- requests
- llama.cpp
- Gemma 3 12B
- JSON

## How It Works

The application first determines the document type.

For `.txt` files, Python reads the text directly.

For `.pdf` files, PyMuPDF extracts embedded text from the document.

For `.png`, `.jpg`, and `.jpeg` files, Tesseract OCR converts the image into machine-readable text.

The extracted text is then sent to a locally hosted Gemma 3 12B model through the llama.cpp HTTP API. The model is prompted to return a defined set of invoice fields in JSON format.

The returned data is parsed, converted into an `Invoice` dataclass, and saved as a structured JSON file.

## Example Input

```text
OCR SOLUTIONS LLC
INVOICE # INV-2026-003
Date: October 6, 2026

Bill To:
Tom Riddle

Subtotal ............ $430.00
Tax .................. $36.00
Amount Due .......... $466.00

Payment Currency: USD
```

OCR output may not always preserve the original layout. For example, the same invoice may be returned by OCR as:

```text
subtotal .
Tax .
Amount Due .

$430.00
. $36.00
$466.00
```

Although the individual values are still recognized, their relationship to the labels may no longer be preserved cleanly.

The LLM extraction layer interprets this semi-structured text and returns structured invoice fields.

## Example Output

```json
{
    "invoice": {
        "invoice_number": "INV-2026-003",
        "invoice_date": "October 6, 2026",
        "vendor_name": "OCR SOLUTIONS LLC",
        "subtotal": 430.0,
        "tax": 36.0,
        "total": 466.0,
        "currency": "USD"
    }
}
```

## Installation

### Python Dependencies

The project uses:

```text
PyMuPDF
pytesseract
Pillow
requests
```

On Arch Linux or CachyOS, the dependencies can be installed with packages such as:

```bash
sudo pacman -S python-pymupdf tesseract tesseract-data-eng python-pytesseract python-pillow python-requests
```

The Python dependencies are also listed in `requirements.txt`.

## Local LLM Setup

The project uses a locally hosted Gemma 3 12B model through llama.cpp.

The local API endpoint is:

```text
http://127.0.0.1:8080
```

Example systemd service startup:

```bash
sudo systemctl start llama-gemma3.service
```

Verify that the model server is available:

```bash
curl http://127.0.0.1:8080/v1/models
```

## Running the Project

From the project root:

```bash
python src/main.py
```

The program:

1. Reads the configured input document
2. Selects the appropriate text-extraction method
3. Extracts raw document text
4. Sends the text to the local Gemma model
5. Parses the structured response
6. Creates an `Invoice` object
7. Writes the extracted data to JSON

Example terminal output:

```text
Extraction completed successfully.
Invoice(invoice_number='INV-2026-003', invoice_date='October 6, 2026', vendor_name='OCR SOLUTIONS LLC', subtotal=430.0, tax=36.0, total=466.0, currency='USD')
Result saved to: output/extracted/invoice_006_result.json
```

Generated results are stored under:

```text
output/extracted/
```

## Main Components

### `main.py`

Coordinates the complete workflow. It determines the input type, obtains document text, invokes the AI extractor, creates the invoice object, and saves the result.

### `pdf_reader.py`

Uses PyMuPDF to extract machine-readable text from PDF documents.

### `ocr_reader.py`

Uses Pillow and Tesseract OCR to extract text from scanned invoice images.

### `ai_extractor.py`

Sends extracted document text to the local Gemma model using the llama.cpp HTTP API.

The model is instructed to return:

- invoice number
- invoice date
- vendor name
- subtotal
- tax
- total
- currency

The module also handles model responses wrapped in Markdown code fences before parsing the returned JSON.

### `schemas.py`

Defines the expected invoice structure using a Python dataclass.

```python
from dataclasses import dataclass

@dataclass
class Invoice:
    invoice_number: str
    invoice_date: str
    vendor_name: str
    subtotal: float
    tax: float
    total: float
    currency: str
```

### `output_writer.py`

Converts the `Invoice` dataclass into a dictionary and writes the result to a formatted JSON file.

## Development Notes

The project initially used deterministic parsing and regular expressions to extract invoice fields.

That worked well for predictable layouts, but OCR introduced an important challenge: recognized labels and values were sometimes placed on separate lines even when they appeared next to each other visually.

For example:

```text
Subtotal ............ $430.00
Tax .................. $36.00
Amount Due .......... $466.00
```

could be returned by OCR as:

```text
subtotal .
Tax .
Amount Due .

$430.00
. $36.00
$466.00
```

Instead of continuing to make the regex logic increasingly dependent on layout, the project introduced an LLM-based extraction step. The LLM interprets the semantic relationship between the recognized fields and values and returns a consistent JSON structure.

## Key Learning Outcomes

- Building a modular Python document-processing workflow
- Extracting text from PDF documents
- Performing OCR on scanned images
- Working with inconsistent OCR output
- Using regular expressions for early-stage document parsing
- Understanding the limits of deterministic parsing
- Calling a local LLM through an HTTP API
- Prompting an LLM to produce structured JSON
- Cleaning and parsing model responses
- Using Python dataclasses for structured records
- Converting unstructured documents into machine-readable JSON
- Separating ingestion, extraction, schemas, and output logic into reusable modules

## Project Summary

This project demonstrates a local document-processing workflow that combines PDF parsing, OCR, and LLM-based structured extraction.

PyMuPDF handles text-based PDFs, Tesseract OCR converts scanned invoice images into text, and a locally hosted Gemma 3 12B model interprets the resulting semi-structured content and converts it into predefined invoice fields.

The extracted fields are mapped into a Python dataclass and saved as structured JSON.
