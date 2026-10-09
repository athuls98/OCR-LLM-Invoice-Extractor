import json
from dataclasses import asdict


def save_result(invoice, output_path):
    result = {
        "invoice": asdict(invoice),	
    }

    with open(output_path, "w") as file:
        json.dump(result, file, indent=4)
