def normalize_priority(label):
    if not isinstance(label, str):
        return None
    return label.strip().upper()
