from dataclasses import dataclass


@dataclass(frozen=True)
class StandardUnit:
    # All length units
    LENGTH_KILOMETRE: str = "Kilometre"
    LENGTH_METRE: str = "Metre"
    LENGTH_CENTIMETRE: str = "Centimetre"
    LENGTH_MILLIMETRE: str = "Millimetre"
    LENGTH_MICROMETRE: str = "Micrometre"
    LENGTH_INCH: str = "Inch"
    LENGTH_FOOT: str = "Foot"
    LENGTH_YARD: str = "Yard"
    LENGTH_MILE: str = "Mile"

    # All Area corresponding units
    AREA_HECTARE: str = "Hectare"

    # All Mass corresponding units
    MASS_MICROGRAM: str = "Microgram"
    MASS_GRAM: str = "Gram"
    MASS_KILOGRAM: str = "Kilogram"
    MASS_TONNE: str = "Tonne"
    MASS_OUNCE: str = "Ounce"
    MASS_POUNDS: str = "Pound"

    # All Volume corresponding units
    VOLUME_MILLILITRE: str = "Millilitre"
    VOLUME_LITRE: str = "Litre"
    VOLUME_GALLON: str = "Gallon"
    VOLUME_BARREL: str = "Barrel"
    VOLUME_QUINTAL: str = "Quintal"

    # All Metric representation units
    METRIC_ABSOLUTE_NUMBER: str = "Absolute Number"
    METRIC_THOUSAND: str = "Thousand"
    METRIC_MILLION: str = "Million"
    METRIC_BILLION: str = "Billion"
    METRIC_CRORE: str = "Crore"
    METRIC_LAKH: str = "Lakh"
    METRIC_DOZEN: str = "Dozen"
    METRIC_PERCENTAGE: str = "Percentage"
    METRIC_RATIO: str = "Ratio"
    METRIC_NOS: str = "Absolute Number"

    # All Time corresponding units
    TIME_SECOND: str = "Second"
    TIME_MINUTE: str = "Minute"
    TIME_HOUR: str = "Hour"
    TIME_DAY: str = "Day"
    TIME_WEEK: str = "Week"
    TIME_MONTH: str = "Month"
    TIME_YEAR: str = "Year"
    TIME_DECADE: str = "Decade"
    TIME_CENTURY: str = "Century"

    # All Commerce Project unit
    # COMMERCE_NOS: str = "Absolute Number"

    # All DGCA Project unit
