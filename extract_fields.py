import re
from datetime import datetime

def extract_amount(text):
    # Prefer lines with 'Total', 'Amount Due', 'Grand Total', etc.
    amount_labels = [
        r'(total\s*[:\-]?\s*\$?([0-9\,]+\.?[0-9]{0,2}))',
        r'(amount due\s*[:\-]?\s*\$?([0-9\,]+\.?[0-9]{0,2}))',
        r'(grand total\s*[:\-]?\s*\$?([0-9\,]+\.?[0-9]{0,2}))',
    ]
    for label in amount_labels:
        match = re.search(label, text, re.IGNORECASE)
        if match:
            amt = match.group(2).replace(',', '')
            try:
                return float(amt)
            except:
                continue
    # Fallback: largest currency value
    amount_regex = re.compile(r'(?:\$|USD\s?)?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})|[0-9]+\.[0-9]{2})')
    amounts = amount_regex.findall(text)
    if amounts:
        return max([float(a.replace(',', '')) for a in amounts])
    return None

def extract_date(text):
    # Prefer lines with 'Invoice Date', 'Date', 'Due Date', etc.
    date_labels = [
        r'(invoice date\s*[:\-]?\s*([0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}-[0-9]{2}-[0-9]{4}|[0-9]{2}\.[0-9]{2}\.[0-9]{4}))',
        r'(date\s*[:\-]?\s*([0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}-[0-9]{2}-[0-9]{4}|[0-9]{2}\.[0-9]{2}\.[0-9]{4}))',
        r'(due date\s*[:\-]?\s*([0-9]{2}/[0-9]{2}/[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}-[0-9]{2}-[0-9]{4}|[0-9]{2}\.[0-9]{2}\.[0-9]{4}))',
    ]
    for label in date_labels:
        match = re.search(label, text, re.IGNORECASE)
        if match:
            date_str = match.group(2)
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
                try:
                    return datetime.strptime(date_str, fmt).date().isoformat()
                except ValueError:
                    continue
    # Fallback: first date found
    date_patterns = [
        r'(\d{2}/\d{2}/\d{4})',
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{2}-\d{2}-\d{4})',
        r'(\d{2}\.\d{2}\.\d{4})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
                try:
                    return datetime.strptime(match.group(1), fmt).date().isoformat()
                except ValueError:
                    continue
    return None

def extract_vendor(text):
    # Prefer 'From:' or 'Supplier:' lines, ignore common invoice words
    lines = text.splitlines()
    for line in lines[:15]:
        if any(x in line.lower() for x in ['from:', 'supplier:', 'billed by:', 'seller:']):
            return line.split(':', 1)[-1].strip()
    # Ignore lines with 'invoice', 'date', 'number', 'total', etc.
    ignore = ['invoice', 'date', 'number', 'total', 'amount', 'due', 'bill', 'to:', 'for:']
    for line in lines[:10]:
        if line.strip() and not any(x in line.lower() for x in ignore):
            return line.strip()
    # Fallback: first non-empty line
    for line in lines:
        if line.strip():
            return line.strip()
    return None 