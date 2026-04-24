def sanitize_name(name: str) -> str:
    return "".join(c for c in name.lower() if c.isalnum() or c in ('_', '-'))