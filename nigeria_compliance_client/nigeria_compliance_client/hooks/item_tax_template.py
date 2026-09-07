def calculate_total_tax_percent(doc):
    total_tax_percent = 0
    for tax in doc.taxes:
        total_tax_percent += tax.tax_rate
    return total_tax_percent

def before_save(doc, method=None):
    doc.custom_total_tax_percent = calculate_total_tax_percent(doc)