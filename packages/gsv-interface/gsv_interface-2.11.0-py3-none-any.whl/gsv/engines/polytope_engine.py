from pathlib import Path
from typing import Dict, BinaryIO
import uuid

from gsv.engines.engine import Engine


class PolytopeEngine(Engine):

    NAME = "polytope"

    def __init__(self):
        from polytope.api import Client
        self.polytope_client = Client(address="polytope.lumi.apps.dte.destination-earth.eu")
        self.temp_path = Path(str(uuid.uuid4())).with_suffix(".grb")

    def __str__(self):
        return "<engine 'polytope'>"

    def retrieve(self, request: Dict) -> BinaryIO:
        self.polytope_client.retrieve(
            "destination-earth", request, self.temp_path
        )

        self.f = open(self.temp_path, 'rb')
        return self.f

    def close(self):
        self.f.close()
        self.temp_path.unlink()

    def grib_dump(self, grib_filename):
        self.f.close()
        self.temp_path.rename(grib_filename)
