"""Test yv-languages module matching methods."""

import pytest

import yv_languages


@pytest.mark.parametrize(
    "params",
    [
        (["en"], ["en"], "en"),
        (["es"], ["en", "es"], "es"),
        (["asdf", "es"], ["en", "es"], "es"),
        (["es"], ["en"], None),
        (["es", "en"], ["en-GB", "es-ES", "es-LA"], None),
        (["*"], ["en", "es", "cho"], "en"),
        (["asdf", "ckb", "ml", "*"], ["en", "es", "cho"], "en"),
        (["de-CH-1996"], ["de-CH", "de"], "de-CH"),
        (["es-ES", "es"], ["es", "es-ES"], "es-ES"),
        (["es-es"], ["es-ES"], "es-ES"),
        (["*", "es"], ["en", "es"], "es"),
    ],
)
def test_match_lookup(params):
    """Test match lookup functionality."""
    priority_list, language_tags, expected = params
    match = yv_languages.match_lookup(priority_list=priority_list, language_tags=language_tags)
    assert match == expected


def test_filter_rfc_example():
    """Test the example given in the RFC of matching."""
    language_range = "de-de"  # German as used in Germany
    should_match = ["de-DE-1996"]  # German as used in Germany, orthography of 1996
    should_not_match = [
        "de-Deva",  # German as written in the Devanagari script
        "de-Latn-DE",  # German, Latin script, as used in Germany
    ]
    assert (
        yv_languages.match_filter(
            priority_list=[language_range], language_tags=should_match + should_not_match
        )
        == should_match
    )


@pytest.mark.parametrize(
    "params",
    [
        (["en"], ["en"], ["en"]),
        (["es"], ["en", "es"], ["es"]),
        (["asdf", "es"], ["en", "es"], ["es"]),
        (["es"], ["en"], []),
        (["es", "en"], ["en-GB", "es-ES", "es-LA"], ["es-ES", "es-LA", "en-GB"]),
        (["*"], ["en", "es", "cho"], ["en", "es", "cho"]),
        (["asdf", "ckb", "ml", "*"], ["en", "es", "cho"], ["en", "es", "cho"]),
        (["en-GB"], ["en"], []),
    ],
)
def test_match_filter(params):
    """Test match basic filter functionality."""
    priority_list, language_tags, expected = params
    match = yv_languages.match_filter(priority_list=priority_list, language_tags=language_tags)
    assert match == expected


@pytest.mark.parametrize(
    "params",
    [
        (["*"], ["en", "en-GB", "en-CA"], ["en", "en-GB", "en-CA"]),
        (["en-*"], ["en", "en-GB"], ["en", "en-GB"]),
    ],
)
def test_match_filter_extended(params):
    """Test match extended filter functionality."""
    priority_list, language_tags, expected = params
    match = yv_languages.match_filter(
        priority_list=priority_list, language_tags=language_tags, extended=True
    )
    assert match == expected
