from dataclasses import dataclass, KW_ONLY


@dataclass(frozen=True)
class RadarData:
    # Raw data received from radar, includes position (as bin index), timestamp, and original message
    _: KW_ONLY
    range_bin: int  # Index of the radar's distance bin where detection occurred
    timestamp: int  # Timestamp when the radar captured this data
    raw_message: str  # Original message string received from the radar


@dataclass(frozen=True)
class DistanceMeasurement:
    # Cleaned, high-level measurement extracted from raw radar data
    _: KW_ONLY
    distance: float  # in meters
    time: float  # in seconds
