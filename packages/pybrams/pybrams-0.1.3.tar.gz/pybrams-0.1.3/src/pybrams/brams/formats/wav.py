"""
WAV file reader and writer for BRAMS formatted scientific signal data.

This module provides tools to:
- Parse BRAMS-specific `.wav` files containing binary chunks for metadata (BRA1), signal data (data), and PPS timing (BRA2).
- Convert binary data into structured Python objects (`Metadata`, `Series`, `PPS`).
- Reconstruct `.wav` files from the structured data.
- Fetch and decode remote `.wav` files via the BRAMS downloader API.

Chunk Structure:
- BRA1: Metadata
- data: Signal
- BRA2: PPS (Pulse Per Second) timing data
"""

import struct
from typing import Union, Dict
import autograd.numpy as np
import io
import datetime
from dataclasses import dataclass
from pybrams.brams import system as systems
from pybrams.brams.fetch import downloader
from pybrams.processing.pps import PPS
import logging

from pybrams.processing.series import Series

logger = logging.getLogger(__name__)


@dataclass
class Metadata:
    """Holds BRAMS metadata from BRA1 chunk."""

    version: int
    samplerate: float
    lo_freq: float
    start_us: int
    pps_count: int
    beacon_lat: int
    beacon_long: int
    beacon_alt: int
    beacon_freq: int
    beacon_power: int
    beacon_polar: int
    ant_id: int
    ant_lat: int
    ant_long: int
    ant_alt: int
    ant_az: int
    ant_el: int
    beacon_code: str
    observer_code: str
    station_code: str
    description: str

    def __str__(self):
        return (
            f"Version : {self.version}\n"
            f"Samplerate : {self.samplerate} Hz\n"
            f"LO frequency : {self.lo_freq} Hz\n"
            f"Start (us) : {self.start_us}\n"
            f"PPS count : {self.pps_count}\n"
            f"Beacon latitude : {self.beacon_lat}\n"
            f"Beacon longitude : {self.beacon_long}\n"
            f"Beacon altitude : {self.beacon_alt} m\n"
            f"Beacon frequency : {self.beacon_freq} Hz\n"
            f"Beacon power : {self.beacon_power}\n"
            f"Beacon polarization : {self.beacon_polar}\n"
            f"Antenna ID : {self.ant_id}\n"
            f"Antenna latitude : {self.ant_lat}\n"
            f"Antenna longitude : {self.ant_long}\n"
            f"Antenna altitude : {self.ant_alt}\n"
            f"Antenna azimuth : {self.ant_az}\n"
            f"Antenna elevation : {self.ant_el}\n"
            f"Beacon code : {self.beacon_code}\n"
            f"Observer code : {self.observer_code}\n"
            f"Station code : {self.station_code}\n"
            f"Description : {self.description}"
        )


class HeaderChunk:
    """Parses and serializes the BRA1 chunk (metadata)."""

    fmt_main = "<H 2d 2Q 5d 2H 5d 6s 6s 6s 234s"
    fmt_reserve = " 256s"
    fmt = fmt_main + fmt_reserve

    def __init__(self, buffer):
        (
            self.version,
            self.samplerate,
            self.lo_freq,
            self.start_us,
            self.pps_count,
            self.beacon_lat,
            self.beacon_long,
            self.beacon_alt,
            self.beacon_freq,
            self.beacon_power,
            self.beacon_polar,
            self.ant_id,
            self.ant_lat,
            self.ant_long,
            self.ant_alt,
            self.ant_az,
            self.ant_el,
            self.beacon_code,
            self.observer_code,
            self.station_code,
            self.description,
        ) = struct.unpack(self.fmt_main, buffer[0 : struct.calcsize(self.fmt_main)])

    def pack(self):
        """Packs the header into a binary buffer."""
        packed_data = struct.pack(
            self.fmt_main,
            self.version,
            self.samplerate,
            self.lo_freq,
            self.start_us,
            self.pps_count,
            self.beacon_lat,
            self.beacon_long,
            self.beacon_alt,
            self.beacon_freq,
            self.beacon_power,
            self.beacon_polar,
            self.ant_id,
            self.ant_lat,
            self.ant_long,
            self.ant_alt,
            self.ant_az,
            self.ant_el,
            self.beacon_code,
            self.observer_code,
            self.station_code,
            self.description,
        )

        return packed_data + bytes(256)

    @classmethod
    def from_metadata(cls, metadata: Metadata):
        """Builds a HeaderChunk from Metadata."""
        obj = cls.__new__(cls)
        for key, value in vars(metadata).items():
            setattr(obj, key, value)
        return obj


class PPSChunk:
    """Handles the BRA2 PPS chunk: index and timestamp pairs."""

    fmt = "Q Q"

    def __init__(self, buffer):
        self.pps = struct.unpack(
            self.fmt * int(len(buffer) / struct.calcsize(self.fmt)), buffer
        )

        self.index = np.array(self.pps[0::2])
        self.time = np.array(self.pps[1::2])

    def pack(self):
        return struct.pack(
            self.fmt * int(len(self.pps) / (struct.calcsize(self.fmt) / 8)), *self.pps
        )

    def __str__(self):
        return "\nPPS\n\n" + "\n".join(
            [f"({index}, {time})" for (index, time) in zip(self.index, self.time)]
        )

    @classmethod
    def from_pps(cls, pps: PPS):
        """Creates PPSChunk from a PPS object."""
        obj = cls.__new__(cls)
        obj.pps = np.empty((pps.index.size + pps.time.size,), dtype=pps.index.dtype)
        obj.pps[0::2] = pps.index
        obj.pps[1::2] = pps.time
        return obj


class DataChunk:
    """Handles the 'data' chunk containing the signal."""

    def __init__(self, buffer, dtype: Union[np.int16, np.float64]):
        self.dtype = dtype
        fmt = "h" if self.dtype == np.int16 else "d"
        self.npoints = int(len(buffer) / struct.calcsize(fmt))
        self.signal = np.array(struct.unpack("<" + fmt * self.npoints, buffer))

    def set(self, data):
        """Replaces the internal signal."""
        self.dtype = data.dtype
        self.signal = data
        self.npoints = len(self.signal)

    def pack(self):
        fmt = "h" if self.dtype == np.int16 else "d"
        return struct.pack(fmt * len(self.signal), *self.signal)

    @classmethod
    def from_series(cls, series: Series):
        obj = cls.__new__(cls)
        obj.dtype = series.data.dtype
        obj.npoints = series.data.size
        obj.signal = series.data
        return obj


class Wav:
    """
    Represents a BRAMS `.wav` file with custom metadata (BRA1), signal data (data), and PPS timing (BRA2).
    """

    _header_chunk: HeaderChunk
    _pps_chunk: PPSChunk
    _data_chunk: DataChunk

    @classmethod
    def _read_file(cls, file_path: str) -> bytes:
        try:
            with open(file_path, "rb") as wav_file:
                return wav_file.read()

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise

        except PermissionError:
            logger.error(f"Permission denied: {file_path}")
            raise

    @classmethod
    def read(cls, data: Union[bytes, str]) -> tuple[Metadata, Series, PPS]:
        """Parses a BRAMS `.wav` file (from path or bytes) into structured metadata, signal, and PPS."""
        buffer: bytes
        if isinstance(data, str):
            buffer = cls._read_file(data)

        elif isinstance(data, bytes):
            buffer = data

        stream = io.BytesIO(buffer)
        riff, size, fformat = struct.unpack("<4sI4s", stream.read(12))

        chunk_header = stream.read(8)
        subchunkid, subchunksize = struct.unpack("<4sI", chunk_header)

        cls.aformat: int = int()
        cls.channels: int
        cls.samplerate: int
        cls.byterate: int
        cls.blockalign: int
        cls.bps: int

        if subchunkid == b"fmt ":
            (
                cls.aformat,
                cls.channels,
                cls.samplerate,
                cls.byterate,
                cls.blockalign,
                cls.bps,
            ) = struct.unpack("HHIIHH", stream.read(16))
            stream.read(2) if cls.aformat == 3 else None

        chunkOffset = stream.tell()

        while chunkOffset < size:
            stream.seek(chunkOffset)
            subchunkid, subchunksize = struct.unpack("<4sI", stream.read(8))

            if subchunkid == b"BRA1":
                if not (subchunksize == struct.calcsize(HeaderChunk.fmt)):
                    break

                cls._header_chunk = HeaderChunk(
                    stream.read(struct.calcsize(HeaderChunk.fmt_main))
                )

            elif subchunkid == b"data":
                cls._data_chunk = DataChunk(
                    stream.read(subchunksize),
                    np.int16 if cls.aformat == 1 else np.float64,
                )

            elif subchunkid == b"BRA2":
                cls._pps_chunk = PPSChunk(stream.read(subchunksize))
            else:
                pass
            chunkOffset += subchunksize + 8

        cls._header_chunk.beacon_code = cls._header_chunk.beacon_code.decode()
        cls._header_chunk.observer_code = cls._header_chunk.observer_code.decode()
        cls._header_chunk.station_code = cls._header_chunk.station_code.decode()
        cls._header_chunk.description = cls._header_chunk.description.decode()

        metadata = Metadata(**vars(cls._header_chunk))
        series = Series(cls._data_chunk.signal)
        pps = PPS(cls._pps_chunk.index, cls._pps_chunk.time)
        return (metadata, series, pps)

    @classmethod
    def write(cls, metadata: Metadata, series: Series, pps: PPS):
        """Serializes metadata, signal, and PPS into a BRAMS `.wav` byte buffer."""
        cls._header_chunk = HeaderChunk.from_metadata(metadata)
        cls._data_chunk = DataChunk.from_series(series)
        cls._pps_chunk = PPSChunk.from_pps(pps)
        cls._header_chunk.beacon_code = cls._header_chunk.beacon_code.encode()
        cls._header_chunk.observer_code = cls._header_chunk.observer_code.encode()
        cls._header_chunk.station_code = cls._header_chunk.station_code.encode()
        cls._header_chunk.description = cls._header_chunk.description.encode()

        packed_header = cls._header_chunk.pack()
        packed_pps = cls._pps_chunk.pack()
        packed_data = cls._data_chunk.pack()

        stream = io.BytesIO()

        stream.write(b"RIFF")
        fmt_size = 16 if cls._data_chunk.dtype == np.int16 else 18
        size = 36 + fmt_size + len(packed_header) + len(packed_data) + len(packed_pps)
        stream.write(struct.pack("<I", size))
        stream.write(b"WAVE")

        cls.aformat = 1 if cls._data_chunk.dtype == np.int16 else 3
        cls.blockalign = 2 if cls._data_chunk.dtype == np.int16 else 8
        cls.bps = 16 if cls._data_chunk.dtype == np.int16 else 64
        cls.byterate = cls.blockalign * cls.channels * cls.samplerate

        stream.write(b"fmt ")
        stream.write(struct.pack("<I", 16 if cls._data_chunk.dtype == np.int16 else 18))
        stream.write(
            struct.pack(
                "HHIIHH",
                cls.aformat,
                cls.channels,
                cls.samplerate,
                cls.byterate,
                cls.blockalign,
                cls.bps,
            )
        )
        (
            stream.write(struct.pack("H", 0))
            if cls._data_chunk.dtype == np.float64
            else None
        )

        stream.write(b"BRA1")
        stream.write(struct.pack("<I", len(packed_header)))
        stream.write(packed_header)

        stream.write(b"data")
        stream.write(struct.pack("<I", len(packed_data)))
        stream.write(packed_data)

        stream.write(b"BRA2")
        stream.write(struct.pack("<I", len(packed_pps)))
        stream.write(packed_pps)

        wav_data = stream.getvalue()

        return wav_data


def get(
    interval: datetime.datetime,
    system: Union[
        str,
        systems.System,
    ],
    *,
    load: bool = False,
    save: bool = False,
    process: bool = False,
    clean: bool = False,
) -> Dict[str, Wav]:
    """
    Fetches BRAMS `.wav` files from the API for the specified system and date.

    Args:
        interval (datetime.datetime): Date for which data is requested.
        system (str | System): BRAMS system code or object.
        load (bool): Unused flag placeholder.
        save (bool): Unused flag placeholder.
        process (bool): Unused flag placeholder.
        clean (bool): Unused flag placeholder.

    Returns:
        Dict[str, Wav]: Dictionary of filename → Wav object.
    """
    files: Dict[str, Wav] = {}
    payload = {
        "system": system,
        "type": "wav",
        "year": interval.year,
        "month": interval.month,
        "day": interval.day,
    }

    response = downloader.request(payload)
    if not response:
        print("No response from API")
        return {}

    from pybrams.brams.formats.zip import ZipExtractor

    files = {
        name: Wav(data)
        for name, data in ZipExtractor(getattr(response, "content"))
        .extract_all()
        .items()
    }

    return files
