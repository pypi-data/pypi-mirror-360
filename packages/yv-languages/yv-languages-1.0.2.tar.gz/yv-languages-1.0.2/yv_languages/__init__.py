"""
Languages pip package for YouVersion.
"""

import collections
import dataclasses
import re
import typing

import langcodes

from . import rules

REPLACEMENTS = rules.DATA["replacements"]
SUPPRESSIONS = rules.DATA["suppressions"]
VALIDATIONS = rules.DATA["validations"]


@dataclasses.dataclass
class BCP47LanguageTag:
    """
    Data class for a BCP 47 language tag.

    Parts should be constructed in the following order:
    1. Primary language subtag: Represents the main language (e.g., "en" for English, "fr" for
        French).
    2. Extended language subtag (extlang): Provides additional granularity for certain languages,
        though it is not commonly used.
    3. Script subtag: Specifies the script used for writing (e.g., "Latn" for Latin script, "Cyrl"
        for Cyrillic script).
    4. Region subtag: Indicates the geographical region associated with a language variant (e.g.,
        "US" for United States, "GB" for United Kingdom).
    5. Variant subtag: Specifies a particular variation or dialect of the language (e.g., "scouse"
        for the Scouse dialect of English).
    6. Extension subtags: Additional subtags used for specialized language features.
    """

    language: str
    extended_language: str = ""
    script: str = ""
    region: str = ""
    variants: typing.List[str] = dataclasses.field(default_factory=list)
    extensions: typing.List[tuple[str, str]] = dataclasses.field(default_factory=list)
    private_use: typing.List[str] = dataclasses.field(default_factory=list)

    # Return attributes in BCP47 order when iterating
    _attribute_order: typing.Tuple[str] = (
        "language",
        "extended_language",
        "script",
        "region",
        "variants",
        "extensions",
        "private_use",
    )
    _iter_index: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            attr = self._attribute_order[self._iter_index]
        except IndexError:
            raise StopIteration
        self._iter_index += 1
        return getattr(self, attr)

    def __getitem__(self, key):
        attr = self._attribute_order[key]
        return getattr(self, attr)

    def __str__(self) -> str:
        """Render the tag as a string."""
        subtags = [self.language]
        if self.extended_language:
            subtags.append(self.extended_language)
        if self.script:
            subtags.append(self.script.title())
        if self.region:
            subtags.append(self.region.upper())
        if self.variants:
            subtags += self.variants
        if self.extensions:
            for i, ext in self.extensions:
                subtags += [i, ext]
        if self.private_use:
            subtags.append("x")
            subtags += self.private_use
        return "-".join(subtags)


class LanguagesError(Exception):
    """Custom exception class."""


def canonical(
    language_tag: type[str | BCP47LanguageTag], *, should_validate: bool = False
) -> BCP47LanguageTag:
    """Take in a language tag and return a canonical BCP47LanguageTag data class."""

    # First check the entire tag for YV custom rule replacements
    # This needs to stay the first thing for our custom rules to precede others
    if str(language_tag) in REPLACEMENTS["tags"]:
        language_tag = parse(
            rules.DATA["replacements"]["tags"][str(language_tag)],
            should_validate=should_validate,
        )

    if isinstance(language_tag, str):
        language_tag = parse(language_tag, should_validate=should_validate)

    if language_tag.language in REPLACEMENTS["languages"]:
        language_tag.language = REPLACEMENTS["languages"][str(language_tag)]

    if language_tag.extended_language in REPLACEMENTS["extlangs"]:
        language_tag.extended_language = REPLACEMENTS["extlangs"][language_tag.extended_language]

    if language_tag.script in REPLACEMENTS["scripts"]:
        language_tag.script = REPLACEMENTS["scripts"][language_tag.script]

    if language_tag.script == SUPPRESSIONS["scripts"].get(language_tag.language):
        language_tag.script = ""

    if language_tag.region in REPLACEMENTS["regions"]:
        language_tag.region = REPLACEMENTS["regions"][language_tag.region]

    for idx, variant in enumerate(language_tag.variants):
        if variant in REPLACEMENTS["variants"]:
            language_tag.variants[idx] = REPLACEMENTS["variants"][variant]

    # Validate each attribute in tag is valid from registry lists
    # unless the entire tag is private use
    return language_tag


def distance(*, desired: str, supported: str) -> int:
    """Return a distance measurement between locales."""
    return langcodes.tag_distance(desired, supported)


def match_filter(
    *, priority_list: list[BCP47LanguageTag], language_tags: list[str], extended: bool = False
) -> list[str]:
    """
    Return all matches for a language range given a setup of tags.

    This returns a language priority list consisting of basic or extended (based on param) language
    ranges to sets of language tags.
    """
    matches = []

    if extended:
        for language_range in priority_list:
            if language_range == "*":
                matches = language_tags
                break
            pattern = language_range.replace("-*", ".*")
            regex = re.compile(f"^{pattern}$", re.IGNORECASE)
            matches = matches + [tag for tag in language_tags if regex.match(tag)]

    else:
        for language_range in priority_list:
            if language_range == "*":
                matches = language_tags
                break
            for tag in language_tags:
                if tag.lower()[: len(language_range) + 1].rstrip("-") == language_range.lower():
                    matches.append(tag)

    return matches


def match_lookup(*, priority_list: list[str], language_tags: list[str]) -> str | None:
    """
    Return the best matched language range for the provided language tags.

    This matches a language priority list consisting of basic language ranges to sets of language
    tags to find the one exact language tag that best matches the range. This produces the single
    result that best matches the user's preferences from the list of available tags, so it is
    useful in cases in which a single item is required.
    """
    match = None
    default_language = language_tags[0]
    language_tags = {tag.lower(): tag for tag in language_tags}

    for idx, language_range in enumerate(priority_list):
        if language_range == "*" and idx == len(priority_list) - 1:
            match = default_language.lower()
        if language_range.lower() in language_tags:
            match = language_range.lower()
        else:
            subtags = language_range.lower().split("-")
            for segment_truncation_count in range(1, len(subtags)):
                truncated_language_range = "-".join(subtags[:-segment_truncation_count])
                if truncated_language_range in language_tags:
                    match = truncated_language_range
                    break
        if match:
            break

    if match:
        match = language_tags[match]

    return match


def parse(language_tag: str, *, should_validate: bool = False) -> BCP47LanguageTag:
    """Parse a language tag string to a BCP47LanguageTag data class."""

    language_tag = language_tag.replace("_", "-")
    parts = language_tag.split("-")

    language = parts[0].lower()
    if should_validate and (not language or len(language) > 8):
        raise LanguagesError("Invalid language subtag!")

    extended_language = ""
    script = ""
    region = ""
    variants = []
    extensions = []
    private_use = []

    # once started private use goes to the end of the tag
    private_use_started = False

    # if we see a single char tag the next is an extension
    next_is_ext = ""

    for subtag in parts[1:]:
        # Each subtag is expected to be 8 characters or less according to the RFC
        if should_validate and len(subtag) > 8:
            raise LanguagesError(f"Subtag is too long, max 8 characters {subtag}")

        if subtag.lower() == "x":
            private_use_started = True

        elif next_is_ext != "":
            extensions.append((next_is_ext, subtag.lower()))
            next_is_ext = ""

        elif len(subtag) == 3 and subtag.isalpha() and not private_use_started:
            if should_validate and script or region or variants or extensions:
                raise LanguagesError("Parse error subtags out of order.")

            if subtag not in VALIDATIONS["extlangs"]:
                if should_validate:
                    raise LanguagesError("Invalid extended language subtag.")
                continue  # invalid just skip it

            prefixes = VALIDATIONS["extlangs"][subtag]["prefixes"]
            if language not in prefixes:
                if should_validate:
                    raise LanguagesError(
                        "Invalid primary language & extended language subtag combination."
                    )
                continue  # invalid just skip it

            extended_language = subtag.lower()

        elif len(subtag) == 4 and subtag.isalpha() and not private_use_started:
            if should_validate and (region or variants or extensions):
                raise LanguagesError("Parse error subtags out of order.")
            script = subtag.title()

        elif (
            (len(subtag) == 2 and subtag.isalpha())
            or (len(subtag) == 3 and subtag.isnumeric())
            and not private_use_started
        ):
            if should_validate and (variants or extensions):
                raise LanguagesError("Parse error subtags out of order.")
            region = subtag.upper()

        elif len(subtag) == 4 and subtag.isnumeric() and not private_use_started:
            if should_validate and extensions:
                raise LanguagesError("Parse error subtags out of order.")
            variants.append(subtag.lower())

        elif len(subtag) >= 5 and subtag.isalnum() and not private_use_started:
            if should_validate and extensions:
                raise LanguagesError("Parse error subtags out of order.")
            variants.append(subtag.lower())

        elif len(subtag) == 1 and subtag.isalpha() and subtag.islower() and not private_use_started:
            next_is_ext = subtag.lower()

        elif private_use_started:
            private_use.append(subtag.lower())

        elif should_validate:
            raise LanguagesError(f"Unknown subtag: {subtag}")

    language_tag = BCP47LanguageTag(
        language, extended_language, script, region, variants, extensions, private_use
    )

    if (
        should_validate
        and not str(language_tag).startswith("x")
        and (
            language_tag.language not in VALIDATIONS["languages"]
            or (
                language_tag.extended_language
                and language_tag.extended_language not in VALIDATIONS["extlangs"]
            )
            or (
                language_tag.script
                and (
                    not language_tag.script.startswith("Qa")  # private use
                    and language_tag.script not in VALIDATIONS["scripts"]
                )
            )
            or (language_tag.region and language_tag.region not in VALIDATIONS["regions"])
            or not all(variant in VALIDATIONS["variants"] for variant in language_tag.variants)
        )
    ):
        raise LanguagesError("Invalid language tag.")

    return language_tag


def validate(language_tag: str) -> bool:
    """Validate a language tag string against BCP47LanguageTag."""
    parse(language_tag, should_validate=True)
