# utils/decoding.py

def decode_bytes(b: bytes) -> str:
    """
    Robustly decodes bytes into a string using common encodings.
    Tries utf-8, then gbk, and falls back to utf-8 with error replacement.
    """
    if not b:
        return ""
    for enc in ("utf-8", "gbk"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    # Fallback with error replacement
    return b.decode("utf-8", errors="replace")
