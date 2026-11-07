"""Persian text normalizer utility module for Danyar Engine.

Provides deterministic normalization for Persian text including:
- Arabic to Persian character unification (Yeh, Kaf, Teh Marbuta)
- Tatweel (Kashida) removal
- Digit standardization (Arabic to Persian or English)
- Zero-Width Non-Joiner (ZWNJ, \\u200c) correction for prefixes and suffixes
- Redundant ZWNJ cleanup
- Whitespace and newline collapsing
"""

from __future__ import annotations

import re
import unicodedata

__all__ = ["normalize_persian_text"]

# Arabic to Persian character translation table
ARABIC_TO_PERSIAN_CHARS: dict[int, str] = {
    0x064A: "\u06CC",  # Arabic Letter Yeh 'ي' -> Persian Yeh 'ی'
    0x0649: "\u06CC",  # Arabic Letter Alef Maksura 'ى' -> Persian Yeh 'ی'
    0x0643: "\u06A9",  # Arabic Letter Kaf 'ك' -> Persian Keheh 'ک'
    0x0629: "\u0647",  # Arabic Letter Teh Marbuta 'ة' -> Persian Heh 'ه'
}

ARABIC_DIGITS: str = "٠١٢٣٤٥٦٧٨٩"  # U+0660 - U+0669
PERSIAN_DIGITS: str = "۰۱۲۳۴۵۶۷۸۹"  # U+06F0 - U+06F9
ENGLISH_DIGITS: str = "0123456789"

# Pre-compiled regex patterns for performance and correctness
RE_TATWEEL = re.compile(r"[\u0640]")  # Kashida / Tatweel
RE_MULTIPLE_ZWNJS = re.compile(r"\u200c{2,}")

# Verb prefixes: 'می ' and 'نمی ' with verb stems
RE_VERB_PREFIXES = re.compile(r"\b(ن?می)[\s\u200c]+(\w+)")

# Plural suffixes: 'ها' and inflected forms attached to words of length >= 2
RE_PLURAL_SUFFIXES = re.compile(
    r"(?<!\bو)\b(\w{2,})[\s\u200c]+(ها(?:ی|یی|یم|یت|یش|مان|تان|شان)?)\b"
)

# ZWNJ cleanup patterns
RE_ZWNJ_WITH_SPACE = re.compile(r"[ \t]*\u200c+[ \t]+|[ \t]+\u200c+[ \t]*")
RE_ZWNJ_NON_WORD = re.compile(r"([^\w\u200c])\u200c+|\u200c+([^\w\u200c])")
RE_ZWNJ_LINE_BOUNDARIES = re.compile(r"(?:^|(?<=\n))\u200c+|\u200c+(?:(?=\n)|$)")

# Diacritics (Erab / Tashdid / Tanwin / Short vowels)
RE_DIACRITICS = re.compile(r"[\u064B-\u0652]")


def normalize_persian_text(
    raw_text: str | None,
    *,
    unify_digits: bool = True,
    to_persian_digits: bool = False,
    to_english_digits: bool = False,
    collapse_newlines: bool = True,
    remove_diacritics: bool = False,
    persian_digits: bool | None = None,
    english_digits: bool | None = None,
) -> str:
    """Normalize Persian text deterministically.

    Args:
        raw_text: Input text string or None.
        unify_digits: Whether to unify Arabic digits to Persian digits. Defaults to True.
        to_persian_digits: Whether to convert all digits (English & Arabic) to Persian digits.
        to_english_digits: Whether to convert all digits (Persian & Arabic) to English digits.
        collapse_newlines: Whether to collapse multiple consecutive newlines to a single newline. Defaults to True.
        remove_diacritics: Whether to remove short vowel diacritics (Erab/Tashdid). Defaults to False.
        persian_digits: Alias for `to_persian_digits`.
        english_digits: Alias for `to_english_digits`.

    Returns:
        Cleaned, standardized Persian text. Returns "" if input is None or whitespace.
    """
    if raw_text is None:
        return ""

    if not isinstance(raw_text, str):
        raw_text = str(raw_text)

    # Return empty string if input is empty or only whitespace
    if not raw_text.strip():
        return ""

    # Support keyword parameter aliases
    if persian_digits is not None:
        to_persian_digits = persian_digits
    if english_digits is not None:
        to_english_digits = english_digits

    # 1. Unicode NFC normalization and clean invisible artefacts (BOM, zero-width space, NBSP)
    text = unicodedata.normalize("NFC", raw_text)
    text = text.replace("\ufeff", "").replace("\u200b", "").replace("\u00a0", " ")

    # 2. Remove Tatweel / Kashida ('ـ')
    text = RE_TATWEEL.sub("", text)

    # 3. Unify Arabic Yeh ('ي', 'ى'), Kaf ('ك'), and Teh Marbuta ('ة')
    text = text.translate(ARABIC_TO_PERSIAN_CHARS)

    # 4. Optional diacritics removal
    if remove_diacritics:
        text = RE_DIACRITICS.sub("", text)

    # 5. Digits normalization
    if to_persian_digits:
        digit_table = str.maketrans(
            ARABIC_DIGITS + ENGLISH_DIGITS,
            PERSIAN_DIGITS + PERSIAN_DIGITS,
        )
        text = text.translate(digit_table)
    elif to_english_digits:
        digit_table = str.maketrans(
            ARABIC_DIGITS + PERSIAN_DIGITS,
            ENGLISH_DIGITS + ENGLISH_DIGITS,
        )
        text = text.translate(digit_table)
    elif unify_digits:
        # Default: standardize Arabic digits to Persian digits, keep English digits untouched
        digit_table = str.maketrans(ARABIC_DIGITS, PERSIAN_DIGITS)
        text = text.translate(digit_table)

    # 6. Zero-Width Non-Joiner (ZWNJ, \u200c) corrections
    zwnj = "\u200c"
    # Collapse multiple consecutive ZWNJs
    text = RE_MULTIPLE_ZWNJS.sub(zwnj, text)

    # Continuous prefixes: 'می ' and 'نمی ' with verb stems
    text = RE_VERB_PREFIXES.sub(r"\g<1>" + zwnj + r"\g<2>", text)

    # Plural suffix: ' ها' and inflectional variants
    text = RE_PLURAL_SUFFIXES.sub(r"\g<1>" + zwnj + r"\g<2>", text)

    # Clean redundant ZWNJs
    text = RE_ZWNJ_WITH_SPACE.sub(" ", text)
    text = RE_ZWNJ_NON_WORD.sub(r"\1\2", text)
    text = RE_ZWNJ_LINE_BOUNDARIES.sub("", text)
    text = RE_MULTIPLE_ZWNJS.sub(zwnj, text)

    # 7. Whitespace and newline standardization
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)

    if collapse_newlines:
        text = re.sub(r"\n{2,}", "\n", text)
    else:
        text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
