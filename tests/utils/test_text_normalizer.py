"""Unit tests for Persian text normalizer utility module."""

from __future__ import annotations

import pytest

from src.utils.text_normalizer import normalize_persian_text


class TestBoundaryCases:
    """Test boundary and falsy input handling."""

    def test_none_returns_empty_string(self) -> None:
        assert normalize_persian_text(None) == ""

    def test_empty_string_returns_empty_string(self) -> None:
        assert normalize_persian_text("") == ""

    def test_only_spaces_returns_empty_string(self) -> None:
        assert normalize_persian_text("   ") == ""

    def test_only_newlines_and_tabs_returns_empty_string(self) -> None:
        assert normalize_persian_text("\t\n\r  \n\t") == ""

    def test_only_zwnj_and_spaces_returns_empty_string(self) -> None:
        assert normalize_persian_text("  \u200c  \u200c  ") == ""
        assert normalize_persian_text("\u200c") == ""

    def test_non_string_input_converted(self) -> None:
        assert normalize_persian_text(12345) == "12345"


class TestArabicCharacterUnification:
    """Test unification of Arabic characters (Yeh, Kaf, Teh Marbuta)."""

    def test_arabic_yeh_converted_to_persian_yeh(self) -> None:
        # Arabic letter Yeh: \u064A ('ي') -> Persian Yeh: \u06CC ('ی')
        raw = "علي و پيام به كلاس مى روند."
        expected = "علی و پیام به کلاس می‌روند."
        assert normalize_persian_text(raw) == expected

    def test_arabic_alef_maksura_converted_to_persian_yeh(self) -> None:
        # Arabic letter Alef Maksura: \u0649 ('ى') -> Persian Yeh: \u06CC ('ی')
        assert normalize_persian_text("موسى و عيسى") == "موسی و عیسی"
        assert normalize_persian_text("حتى اگر اينطور باشد") == "حتی اگر اینطور باشد"

    def test_arabic_kaf_converted_to_persian_keheh(self) -> None:
        # Arabic letter Kaf: \u0643 ('ك') -> Persian Keheh: \u06A9 ('ک')
        assert normalize_persian_text("كتاب و دفتر") == "کتاب و دفتر"
        assert normalize_persian_text("كارشناس كودك") == "کارشناس کودک"

    def test_arabic_teh_marbuta_converted_to_heh(self) -> None:
        # Arabic letter Teh Marbuta: \u0629 ('ة') -> Persian Heh: \u0647 ('ه')
        assert normalize_persian_text("دقيقة نود") == "دقیقه نود"
        assert normalize_persian_text("منطقة آزاد") == "منطقه آزاد"


class TestTatweelRemoval:
    """Test removal of Arabic Tatweel / Kashida."""

    def test_tatweel_removed(self) -> None:
        assert normalize_persian_text("ســــــلام") == "سلام"
        assert normalize_persian_text("پـــــروژه دانـــــیار") == "پروژه دانیار"
        assert normalize_persian_text("تـسـت") == "تست"


class TestDigitNormalization:
    """Test Arabic, Persian, and English digit unification."""

    def test_arabic_digits_unified_to_persian_by_default(self) -> None:
        raw = "شماره تماس: ٠٩١٢٣٤٥٦٧٨٩"
        expected = "شماره تماس: ۰۹۱۲۳۴۵۶۷۸۹"
        assert normalize_persian_text(raw) == expected

    def test_english_digits_kept_by_default(self) -> None:
        raw = "مدل GPT-4 و Python 3.12"
        expected = "مدل GPT-4 و Python 3.12"
        assert normalize_persian_text(raw) == expected

    def test_to_persian_digits_flag(self) -> None:
        raw = "کد 123 و ٤٥٦"
        expected = "کد ۱۲۳ و ۴۵۶"
        assert normalize_persian_text(raw, to_persian_digits=True) == expected
        assert normalize_persian_text(raw, persian_digits=True) == expected

    def test_to_english_digits_flag(self) -> None:
        raw = "کد ۱۲۳ و ٤٥٦"
        expected = "کد 123 و 456"
        assert normalize_persian_text(raw, to_english_digits=True) == expected
        assert normalize_persian_text(raw, english_digits=True) == expected

    def test_unify_digits_false_leaves_all_digits(self) -> None:
        raw = "کد 123 و ٤٥٦ و ۷۸۹"
        expected = "کد 123 و ٤٥٦ و ۷۸۹"
        assert normalize_persian_text(raw, unify_digits=False) == expected


class TestZwnjPrefixesAndSuffixes:
    """Test correction of Zero-Width Non-Joiner for prefixes and suffixes."""

    def test_continuous_prefix_mi(self) -> None:
        assert normalize_persian_text("او می رود") == "او می‌رود"
        assert normalize_persian_text("می دانم چه می گویی") == "می‌دانم چه می‌گویی"
        assert normalize_persian_text("او می   آید") == "او می‌آید"
        assert normalize_persian_text("باران می بارد") == "باران می‌بارد"

    def test_continuous_prefix_nemi(self) -> None:
        assert normalize_persian_text("این کار انجام نمی شود") == "این کار انجام نمی‌شود"
        assert normalize_persian_text("او نمی   خواهد بیاید") == "او نمی‌خواهد بیاید"
        assert normalize_persian_text("نمی دانم") == "نمی‌دانم"

    def test_prefix_word_boundary_safety(self) -> None:
        # Words ending in mi should not be corrupted
        assert normalize_persian_text("صمیمی است") == "صمیمی است"
        assert normalize_persian_text("شیمی دان") == "شیمی دان"
        assert normalize_persian_text("کرمی در خاک") == "کرمی در خاک"

    def test_plural_suffix_ha(self) -> None:
        assert normalize_persian_text("کتاب ها") == "کتاب‌ها"
        assert normalize_persian_text("خانه ها و پنجره ها") == "خانه‌ها و پنجره‌ها"
        assert normalize_persian_text("دانش آموزان ها") == "دانش آموزان‌ها"
        assert normalize_persian_text("راه ها") == "راه‌ها"

    def test_plural_suffix_inflections(self) -> None:
        assert normalize_persian_text("کتاب های من") == "کتاب‌های من"
        assert normalize_persian_text("ایده هایم") == "ایده‌هایم"
        assert normalize_persian_text("کتاب هایی که خواندم") == "کتاب‌هایی که خواندم"
        assert normalize_persian_text("دوستان تان و همکاران شان") == "دوستان تان و همکاران شان"

    def test_pronoun_plural_forms(self) -> None:
        assert normalize_persian_text("آن ها") == "آن‌ها"
        assert normalize_persian_text("این ها") == "این‌ها"

    def test_suffix_boundary_safety(self) -> None:
        # Standalone 'ها' or after conjunction 'و' must not be attached
        assert normalize_persian_text("ها؟ چی گفتی؟") == "ها؟ چی گفتی؟"
        assert normalize_persian_text("کتاب و ها") == "کتاب و ها"
        assert normalize_persian_text("هاهاها خندیدم") == "هاهاها خندیدم"


class TestZwnjCleanup:
    """Test cleanup of redundant or malformed ZWNJs."""

    def test_multiple_consecutive_zwnjs_collapsed(self) -> None:
        raw = "سلام\u200c\u200c\u200cجهان"
        expected = "سلام‌جهان"
        assert normalize_persian_text(raw) == expected

    def test_zwnj_next_to_whitespace_removed(self) -> None:
        assert normalize_persian_text("سلام \u200c جهان") == "سلام جهان"
        assert normalize_persian_text("سلام\u200c جهان") == "سلام جهان"
        assert normalize_persian_text("سلام \u200cجهان") == "سلام جهان"

    def test_zwnj_at_boundaries_removed(self) -> None:
        assert normalize_persian_text("\u200cسلام دنیا\u200c") == "سلام دنیا"
        assert normalize_persian_text("\u200c\u200cآغاز\u200c\u200c") == "آغاز"

    def test_zwnj_next_to_punctuation_removed(self) -> None:
        assert normalize_persian_text("سلام،\u200c خوبی؟") == "سلام، خوبی؟"
        assert normalize_persian_text("«\u200cمتن\u200c»") == "«متن»"

    def test_existing_valid_zwnj_preserved(self) -> None:
        assert normalize_persian_text("می‌رود") == "می‌رود"
        assert normalize_persian_text("خانه‌ها") == "خانه‌ها"
        assert normalize_persian_text("دانش‌آموز") == "دانش‌آموز"


class TestWhitespaceAndNewlines:
    """Test collapsing multiple consecutive spaces and newlines."""

    def test_multiple_spaces_collapsed(self) -> None:
        raw = "سلام     جهان   من،    چطوری؟"
        expected = "سلام جهان من، چطوری؟"
        assert normalize_persian_text(raw) == expected

    def test_multiple_newlines_collapsed_by_default(self) -> None:
        raw = "خط اول\n\n\n\n\nخط دوم\n\n\nخط سوم"
        expected = "خط اول\nخط دوم\nخط سوم"
        assert normalize_persian_text(raw) == expected

    def test_newlines_with_spaces_and_tabs(self) -> None:
        raw = "خط اول    \n\t   \n   خط دوم"
        expected = "خط اول\nخط دوم"
        assert normalize_persian_text(raw) == expected

    def test_collapse_newlines_false_preserves_paragraphs(self) -> None:
        raw = "خط اول\n\n\n\nخط دوم"
        expected = "خط اول\n\nخط دوم"
        assert normalize_persian_text(raw, collapse_newlines=False) == expected


class TestEdgeCasesAndMixedContent:
    """Test mixed languages, technical terms, emojis, and punctuation."""

    def test_mixed_persian_and_english(self) -> None:
        raw = "سیستم عامل Windows 11 و پردازنده Core i7 بسیار روان كار می كنند."
        expected = "سیستم عامل Windows 11 و پردازنده Core i7 بسیار روان کار می‌کنند."
        assert normalize_persian_text(raw) == expected

    def test_emojis_preserved(self) -> None:
        raw = "سلام به دانیار! 🤖✨🚀 كارها عالی پیش می رود! 👍"
        expected = "سلام به دانیار! 🤖✨🚀 کارها عالی پیش می‌رود! 👍"
        assert normalize_persian_text(raw) == expected

    def test_punctuation_preserved(self) -> None:
        raw = "«آیا این پروژه (دانیار) تكميل شده است؟ بله، صد در صد!»"
        expected = "«آیا این پروژه (دانیار) تکمیل شده است؟ بله، صد در صد!»"
        assert normalize_persian_text(raw) == expected

    def test_urls_preserved(self) -> None:
        raw = "به لینک https://github.com/Armin-MA/danyar-engine مراجعه كنيد."
        expected = "به لینک https://github.com/Armin-MA/danyar-engine مراجعه کنید."
        assert normalize_persian_text(raw) == expected


class TestDiacriticsRemoval:
    """Test optional diacritics removal."""

    def test_diacritics_removed_when_flag_enabled(self) -> None:
        raw = "کِتابِ مُهِمّ"
        expected = "کتاب مهم"
        assert normalize_persian_text(raw, remove_diacritics=True) == expected

    def test_diacritics_preserved_by_default(self) -> None:
        raw = "مُهِمّ"
        assert normalize_persian_text(raw) == "مُهِمّ"
