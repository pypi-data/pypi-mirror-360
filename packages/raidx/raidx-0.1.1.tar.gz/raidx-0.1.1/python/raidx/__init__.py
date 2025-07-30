"""
High-performance FASTA reader - Rust implementation with Python bindings
Drop-in replacement for pyfaidx
"""

from .raidx import Fasta, Faidx, Sequence, FastaRecord

# Version info
__version__ = "0.1.0"


# Exception classes for compatibility with original pyfaidx
class FastaNotFoundError(IOError):
    """Raised if the fasta file cannot be opened."""

    pass


class IndexNotFoundError(IOError):
    """Raised if read_fai cannot open the index file."""

    pass


class FetchError(IndexError):
    """Raised if a request to fetch a FASTA sequence cannot be fulfilled."""

    pass


class FastaIndexingError(Exception):
    """Raised if we encounter malformed FASTA that prevents indexing."""

    pass


class RegionError(Exception):
    """A region error occurred."""

    pass


class UnsupportedCompressionFormat(IOError):
    """Raised when a FASTA file is given with a recognized but unsupported compression extension."""

    pass


class KeyFunctionError(ValueError):
    """Raised if the key_function argument is invalid."""

    pass


class BedError(ValueError):
    """Indicates a malformed BED entry."""

    pass


class VcfIndexNotFoundError(IOError):
    """Raised if vcf cannot find a tbi file."""

    pass


# Utility functions that might be needed for full compatibility
def complement(seq):
    """Returns the complement of seq."""
    complement_map = str.maketrans(
        "ACTGNactgnYRWSKMDVHBXyrwskmdvhbx", "TGACNtgacnRYWSMKHBDVXrywsmkhbdvx"
    )
    return seq.translate(complement_map)


def translate_chr_name(from_name, to_name):
    """Create a translation function for chromosome names."""
    chr_name_map = dict(zip(from_name, to_name))
    return lambda rname: chr_name_map[rname]


def bed_split(bed_entry):
    """Split a BED format entry."""
    if bed_entry[0] == "#":
        return (None, None, None)
    try:
        rname, start, end = bed_entry.rstrip().split()[:3]
    except (IndexError, ValueError):
        raise BedError("Malformed BED entry! {}\n".format(bed_entry.rstrip()))
    start, end = (int(start), int(end))
    return (rname, start, end)


def ucsc_split(region):
    """Split a UCSC format region string."""
    try:
        rname, interval = region.split(":")
    except ValueError:
        rname = region
        interval = None
    try:
        start, end = interval.split("-")
        start, end = (int(start) - 1, int(end))
    except (AttributeError, ValueError):
        start, end = (None, None)
    return (rname, start, end)


# Re-export everything for compatibility
__all__ = [
    "Fasta",
    "Faidx",
    "Sequence",
    "FastaRecord",
    "FastaNotFoundError",
    "IndexNotFoundError",
    "FetchError",
    "FastaIndexingError",
    "RegionError",
    "UnsupportedCompressionFormat",
    "KeyFunctionError",
    "BedError",
    "VcfIndexNotFoundError",
    "complement",
    "translate_chr_name",
    "bed_split",
    "ucsc_split",
]
