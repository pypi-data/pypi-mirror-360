"""This module contains the postprocessing functions for the partner invoice."""


def postprocessing_partner_invoice(partner_invoice):
    """Apply postprocessing to the partner invoice data."""
    # Flatten the invoice amount
    for amount in partner_invoice.get("invoiceAmount", {}):
        if isinstance(amount, list):
            amount = amount[0]
        if isinstance(amount, dict):
            partner_invoice.update(amount)
            break

    # Remove invoiceAmount - comes from DocAI
    if partner_invoice.get("invoiceAmount") is not None:
        partner_invoice.pop("invoiceAmount")

    # Remove containers - comes from DocAI
    # TODO: we can distribute containers to line items based on location proximity
    if partner_invoice.get("containers") is not None:
        partner_invoice.pop("containers")

    # Ensure only one item for optional multiple fields
    optional_multiple_list = [
        "dueDate",
        "eta",
        "etd",
        "fortoEntity",
        "hblNumber",
        "reverseChargeSentence",
    ]
    for k, v in partner_invoice.items():
        if (k in optional_multiple_list) and isinstance(v, list):
            partner_invoice[k] = v[0]

    # Update keys
    key_updates = {
        "pod": "portOfDischarge",
        "pol": "portOfLoading",
        "name": "lineItemDescription",
        "unit": "quantity",
    }

    def update_keys(d, key_updates):
        """
        Recursively updates keys in a dictionary according to a mapping provided in key_updates.

        d: The original dictionary
        key_updates: A dictionary mapping old key names to new key names

        return A new dictionary with updated key names
        """
        if isinstance(d, dict):
            return {
                key_updates.get(k, k): update_keys(v, key_updates) for k, v in d.items()
            }
        elif isinstance(d, list):
            return [update_keys(item, key_updates) for item in d]
        else:
            return d

    updated_data = update_keys(partner_invoice, key_updates)
    return updated_data
