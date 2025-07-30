from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import requests
from generation_models import SolarResource, SolarResourceTimeSeries
from requests.exceptions import HTTPError
import typing as t
from io import StringIO
from warnings import warn


warn("""tyba_client.solar_resource is deprecated in favor of using generation_models.utils.psm_readers. Tyba will
cease to support tyba_client.solar_resource on 6/1/2025. See https://docs.tybaenergy.com/api/index.html or reach out
to us for help migrating.""", FutureWarning)


@dataclass
class PSMClient:
    api_key: str
    email: str

    def _get_solar_resource(
        self,
        source: str,
        latitude: float,
        longitude: float,
        year: t.Union[str, int],
        utc: bool,
    ):
        resp = requests.get(
            url=f"https://developer.nrel.gov/api/nsrdb/v2/solar/{source}.csv",
            params={
                "api_key": self.api_key,
                "email": self.email,
                "wkt": f"POINT({longitude} {latitude})",
                "names": year,
                "utc": "true" if utc else "false",
            },
        )
        if resp.status_code == 400:
            raise HTTPError(resp.json()["errors"])
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def _process_csv(raw: str) -> SolarResource:
        with StringIO(raw) as f:
            _meta = [f.readline().split(",") for _ in range(2)]
            _data = pd.read_csv(f)
        meta = {k: v for k, v in zip(*_meta)}
        data = _data.rename(columns=psm_column_map)
        return SolarResource(
            latitude=float(meta["Latitude"]),
            longitude=float(meta["Longitude"]),
            elevation=float(meta["Elevation"]),
            time_zone_offset=float(meta["Time Zone"]),
            data=SolarResourceTimeSeries(**data.to_dict(orient="list")),
        )

    def get_historical(
        self,
        latitude: float,
        longitude: float,
        year: int,
        utc: bool = False,
    ) -> SolarResource:
        raw = self._get_solar_resource(source="psm3-2-2-download", latitude=latitude, longitude=longitude, year=year, utc=utc)
        return self._process_csv(raw)

    def get_typical(
        self,
        latitude: float,
        longitude: float,
        year: str = "tgy-2022",
        utc: bool = False,
    ) -> SolarResource:
        raw = self._get_solar_resource(source="psm3-2-2-tmy-download", latitude=latitude, longitude=longitude, year=year, utc=utc)
        return self._process_csv(raw)


def solar_resource_from_psm_csv(
    filename: str,
    monthly_albedo: t.Optional[t.List[float]] = None,
) -> SolarResource:
    """_"""
    with open(filename) as f:
        _meta = [f.readline().split(",") for _ in range(2)]
        _data = pd.read_csv(f)
    meta = {k: v for k, v in zip(*_meta)}
    data = _data.rename(columns=psm_column_map)
    return SolarResource(
        latitude=float(meta["Latitude"]),
        longitude=float(meta["Longitude"]),
        elevation=float(meta["Elevation"]),
        time_zone_offset=float(meta["Time Zone"]),
        data=SolarResourceTimeSeries(**data.to_dict(orient="list")),
        monthly_albedo=monthly_albedo,
    )


psm_column_map = {
    "Year": "year",
    "Month": "month",
    "Day": "day",
    "Hour": "hour",
    "Minute": "minute",
    "GHI": "gh",
    "DNI": "dn",
    "DHI": "df",
    "POA": "poa",
    "Temperature": "tdry",
    # twet
    "Dew Point": "tdew",
    "Relative Humidity": "rhum",
    "Pressure": "pres",
    # Snow
    "Surface Albedo": "alb",
    # aod
    "Wind Speed": "wspd",
    "Wind Direction": "wdir",
}
