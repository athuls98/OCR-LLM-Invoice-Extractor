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
