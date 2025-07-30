from collections.abc import Iterable

from mex.common.logging import logger
from mex.common.models import ExtractedOrganizationalUnit, ExtractedPrimarySource
from mex.common.organigram.models import OrganigramUnit
from mex.common.types import Email, MergedOrganizationalUnitIdentifier


def transform_organigram_unit_to_extracted_organizational_unit(
    organigram_unit: OrganigramUnit,
    primary_source: ExtractedPrimarySource,
) -> ExtractedOrganizationalUnit:
    """Transform an organigram unit into an ExtractedOrganizationalUnit.

    Args:
        organigram_unit: Iterable of organigram units coming from the JSON file
        primary_source: Primary source for organigram

    Returns:
        ExtractedOrganizationalUnit
    """
    return ExtractedOrganizationalUnit(
        identifierInPrimarySource=organigram_unit.identifier,
        hadPrimarySource=primary_source.stableTargetId,
        alternativeName=organigram_unit.alternativeName,
        email=[Email(email) for email in organigram_unit.email],
        name=organigram_unit.name,
        shortName=organigram_unit.shortName,
        website=[organigram_unit.website] if organigram_unit.website else [],
    )


def transform_organigram_units_to_organizational_units(
    organigram_units: Iterable[OrganigramUnit],
    primary_source: ExtractedPrimarySource,
) -> list[ExtractedOrganizationalUnit]:
    """Transform organigram units into ExtractedOrganizationalUnits.

    Beware that the order of the output is not necessarily the order of the input.

    Args:
        organigram_units: Iterable of organigram units coming from the JSON file
        primary_source: Primary source for organigram

    Returns:
        List of ExtractedOrganizationalUnit
    """
    extracted_unit_by_id_in_primary_source: dict[str, ExtractedOrganizationalUnit] = {}
    parent_id_in_primary_source_by_id_in_primary_source: dict[str, str] = {}

    for unit in organigram_units:
        extracted_unit = transform_organigram_unit_to_extracted_organizational_unit(
            unit, primary_source
        )
        extracted_unit_by_id_in_primary_source[unit.identifier] = extracted_unit
        if parent_identifier_in_primary_source := unit.parentUnit:
            parent_id_in_primary_source_by_id_in_primary_source[unit.identifier] = (
                parent_identifier_in_primary_source
            )

    for extracted_unit in extracted_unit_by_id_in_primary_source.values():
        identifier_in_primary_source = extracted_unit.identifierInPrimarySource
        if (  # noqa: SIM102
            parent_identifier_in_primary_source
            := parent_id_in_primary_source_by_id_in_primary_source.get(
                identifier_in_primary_source
            )
        ):
            if parent_unit := extracted_unit_by_id_in_primary_source.get(
                parent_identifier_in_primary_source
            ):
                extracted_unit.parentUnit = MergedOrganizationalUnitIdentifier(
                    parent_unit.stableTargetId
                )
    logger.info(
        "transformed %s organizational units",
        len(extracted_unit_by_id_in_primary_source),
    )
    return list(extracted_unit_by_id_in_primary_source.values())
