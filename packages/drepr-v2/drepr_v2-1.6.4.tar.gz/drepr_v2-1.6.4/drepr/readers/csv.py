from __future__ import annotations

from io import StringIO
from pathlib import Path

import serde.csv

from drepr.models.resource import ResourceDataObject, ResourceDataString


def read_source_csv(infile: Path | str | ResourceDataString | ResourceDataObject):
    if isinstance(infile, ResourceDataString):
        return serde.csv.deser(StringIO(infile.as_str()))
    elif isinstance(infile, ResourceDataObject):
        return infile.value
    return serde.csv.deser(infile)
