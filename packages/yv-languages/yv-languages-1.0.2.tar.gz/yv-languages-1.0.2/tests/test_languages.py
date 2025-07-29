"""Test yv-languages module canonical & parsing methods."""

import pytest

import yv_languages


@pytest.mark.parametrize(
    "param",
    [
        ("eng", "en"),
        ("en_US", "en-US"),
        ("en-Latn", "en"),
        ("en-latn", "en"),
        ("nav", "nv"),
        ("es-419", "es-419"),
    ],
)
def test_canonical(param):
    """Test canonical simplification of tag."""
    extra_long_tag, canonical_tag = param
    bcp47 = yv_languages.canonical(extra_long_tag)
    assert canonical_tag == str(bcp47)


@pytest.mark.parametrize(
    "param",
    [
        ("zh-cmn", "cmn"),
        ("zh-yue", "yue"),
    ],
)
def test_extlang_canonical(param):
    """Test canonical rules when using an extlang."""
    language_tag, canonical_tag = param
    bcp47 = yv_languages.canonical(language_tag)
    assert canonical_tag == str(bcp47)


@pytest.mark.parametrize(
    "param",
    [
        ("x-dothraki", "x-dothraki"),
    ],
)
def test_private_locale(param):
    """Test private language tags."""
    extra_long_tag, canonical_tag = param
    bcp47 = yv_languages.canonical(extra_long_tag)
    assert canonical_tag == str(bcp47)


@pytest.mark.parametrize(
    "param",
    [
        ("es-XA", {"language": "es", "region": "XA"}),
        ("az-Qabc", {"language": "az", "script": "Qabc"}),
    ],
)
def test_private_use_region_and_script(param):
    """Test that private use tags region & script tags parse properly."""
    language_tag, expected = param
    bcp_tag = yv_languages.canonical(language_tag)
    assert bcp_tag.language == expected["language"]
    if "region" in expected:
        assert bcp_tag.region == expected["region"]
    if "script" in expected:
        assert bcp_tag.script == expected["script"]


@pytest.mark.parametrize(
    "param",
    [
        ("es-419-419", {"language": "es", "region": "419"}),
        ("az-Arab", {"language": "az", "script": "Arab"}),
    ],
)
def test_redundant(param):
    """Test that redundant tags parse properly."""
    language_tag, expected = param
    bcp_tag = yv_languages.canonical(language_tag)
    assert bcp_tag.language == expected["language"]
    if "region" in expected:
        assert bcp_tag.region == expected["region"]
    if "script" in expected:
        assert bcp_tag.script == expected["script"]


@pytest.mark.parametrize(
    "language_tag",
    [
        "",  # no language subtag
        "zh-tw-hant",  # out of order
        "ja-hepburn-latn",  # out of order
        "asdfasdfasdf",  # tag too long
        "en-asdfasdfasdf",  # tag too long
        "en-GB-asdfasdfasdf",  # tag too long
        "en-cmn",  # invalid primary & extended language subtag combo
        "es-yue",  # invalid primary & extended language subtag combo
    ],
)
def test_validate(language_tag):
    """Test that invalid tags raise an exception."""
    with pytest.raises(yv_languages.LanguagesError):
        yv_languages.validate(language_tag)


@pytest.mark.parametrize(
    "param",
    [
        ("ku_IQ", "ckb"),
        ("my_MM", "my-Qaag"),
        ("spa_es", "es-ES"),
    ],
)
def test_yv_custom(param):
    """Test legacy yv custom language tags."""
    custom_tag, canonical_tag = param
    bcp47 = yv_languages.canonical(custom_tag)
    assert canonical_tag == str(bcp47)
