import pandas as pd
import typing as t
from requests import Response

from tyba_client.forecast import Forecast
from generation_models import JobModel, GenerationModel, PVStorageModel, StandaloneStorageModel

from generation_models.v0_output_schema import (
    GenerationModelResults,
    PVStorageModelResults,
    StandaloneStorageModelSimpleResults,
    StandaloneStorageModelWithDownstreamResults
)
import json
import requests
import time
from structlog import get_logger
from typing import Callable

from tyba_client.operations import Operations
from pydantic import BaseModel, Field
from enum import Enum

logger = get_logger()


V0Results = t.Union[
    GenerationModelResults,
    PVStorageModelResults,
    StandaloneStorageModelSimpleResults,
    StandaloneStorageModelWithDownstreamResults
]

class Market(str, Enum):
    """Indicator for which market to pull pricing data for"""
    RT = "realtime"
    """Indicates pricing data for the Real Time (RT) Market is desired"""
    DA = "dayahead"
    """Indicates pricing data for the Day Ahead (DA) Market is desired"""


class AncillaryService(str, Enum):
    """Indicator for which service to pull pricing data for"""
    REGULATION_UP = "Regulation Up"
    """Indicates pricing data for the Regulation Up service is desired"""
    REGULATION_DOWN = "Regulation Down"
    """Indicates pricing data for the Regulation Down service is desired"""
    RESERVES = "Reserves"
    """Indicates pricing data for the Reserves service is desired"""
    ECRS = "ECRS"
    """Indicates pricing data for the ERCOT Contingency Reserve Service is desired"""

class Ancillary(object):
    """Interface for accessing Tyba's historical *ancillary* price data"""
    def __init__(self, services: 'Services'):
        self.services = services

    def get(self, route, params=None):
        return self.services.get(f"ancillary/{route}", params=params)

    def get_pricing_regions(self, *, iso: str, service: AncillaryService, market: Market) -> Response:
        """Get the name and available year ranges for all ancillary service pricing regions that meet the ISO,
        service and market criteria.

        :param iso: ISO name. Possible values can be found by calling :meth:`Services.get_all_isos`
        :param service: specifies which ancillary service to pull prices for
        :param market: specifies whether to pull day ahead or real time prices for the given service
        :return: :class:`~requests.Response` containing an **array** of JSON objects with schema
          :class:`AncillaryRegionData`. For example:

          .. code:: python

             [
                 {
                     'region': 'Pacific Northwest - SP15',
                     'start_year': 2010,
                     'end_year': 2025
                 },
                 {
                     'region': 'WAPA',
                     ...
                 },
                 ...
             ]

        """
        return self.get("regions", {"iso": iso, "service": service, "market": market})

    def get_prices(self, *, iso: str, service: AncillaryService, market: Market, region: str, start_year: int, end_year: int) -> Response:
        """Get price time series data for a single region/service combination

        :param iso: ISO name. Possible values can be found by calling :meth:`Services.get_all_isos`
        :param service: specifies which ancillary service to pull prices for
        :param market: specifies whether to pull day ahead or real time prices for the given service
        :param region: specific region within the ISO to pull prices for. Possible values can be found by calling
          :meth:`get_pricing_regions`
        :param start_year: the year prices should start
        :param end_year: the year prices should end
        :return: :class:`~requests.Response` containing a JSON object with schema :class:`PriceTimeSeries`. For example:

          .. code:: python

              {
                  'prices': [
                      61.7929,
                      58.1359,
                      61.4939,
                      ....
                  ],
                  'datetimes': [
                      '2022-01-01T00:00:00Z',
                      '2022-01-01T01:00:00Z',
                      '2022-01-01T02:00:00Z',
                      ....
                  ],
              }

        """
        return self.get(
            "prices",
            {
                "iso": iso,
                "service": service,
                "market": market,
                "region": region,
                "start_year": start_year,
                "end_year": end_year,
            },
        )


class LMP(object):
    """Interface for accessing Tyba's historical *energy* price data
    """
    def __init__(self, services: 'Services'):
        self.services = services
        self._route_base = "lmp"

    def get(self, route, params=None):
        return self.services.get(f"{self._route_base}/{route}", params=params)

    def post(self, route, json):
        return self.services.post(f"{self._route_base}/{route}", json=json)

    def get_all_nodes(self, *, iso: str) -> requests.Response:
        """Get node names, IDs and other metadata for all nodes within the given ISO territory.

        :param iso: ISO name. Possible values can be found by calling :meth:`Services.get_all_isos`
        :return: :class:`~requests.Response` containing an **array** of JSON objects with schema
          :class:`NodeData`. For example:

          .. code:: python

             [
                 {'da_end_year': 2025,
                  'rt_end_year': 2025,
                  'rt_start_year': 2023,
                  'name': 'CLAP_WWRSR1-APND',
                  'id': '10017280350',
                  'da_start_year': 2023,
                  'zone': 'SDGE',
                  'type': 'GENERATOR'},
                 {'da_start_year': 2015,
                  'rt_end_year': 2025,
                  'zone': '',
                  'name': 'ELCENTRO_2_N001:IVLY2',
                  'type': 'SPTIE',
                  'substation': '',
                  'da_end_year': 2025,
                  'id': '10003899356',
                  'rt_start_year': 2015},
                 ...
             ]

        """
        return self.get("nodes", {"iso": iso})

    def get_prices(self, *, node_ids: list[str], market: Market, start_year: int, end_year: int) -> requests.Response:
        """Get price time series data for a list of node IDs

        :param node_ids: list of IDs for which prices are desired
          - Maximum length is 8 IDS
        :param market: specifies whether to pull day ahead or real time market prices
        :param start_year: the year prices should start
        :param end_year: the year prices should end
        :return: :class:`~requests.Response` containing a JSON object whose keys are node IDs and whose values
          are objects with schema :class:`PriceTimeSeries`. For example:

          .. code:: python

              {
                  '10000802793': {
                      'prices': [
                          61.7929,
                          58.1359,
                          61.4939,
                          ....
                      ],
                      'datetimes': [
                          '2022-01-01T00:00:00',
                          '2022-01-01T01:00:00',
                          '2022-01-01T02:00:00',
                          ....
                      ],
                      ...
                  },
                  '20000004677': {
                      ...
                  },
                  ...
              }

        """
        return self.get(
            "prices",
            {
                "node_ids": json.dumps(node_ids),
                "market": market,
                "start_year": start_year,
                "end_year": end_year,
            },
        )

    def search_nodes(self, location: t.Optional[str] = None, node_name_filter: t.Optional[str] = None,
                     iso_override: t.Optional[str] = None) -> Response:
        """Get a list of matching nodes based on search criteria. Multiple search criteria (e.g. `location`
        and `node_name_filter`) can be applied in a single request.

        :param location: location information. There are 3 possible forms:

          - city/state, e.g. `'dallas, tx'`
          - address, e.g. `'12345 Anywhere Street, Anywhere, TX 12345'`
          - latitude and longitude, e.g. `'29.760427, -95.369804'`

        :param node_name_filter: partial node name with which to perform a pattern-match, e.g. `'HB_'`
        :param iso_override: ISO signifier, used to constrain search to a single ISO. When equal to ``None``, all ISOs
          are searched based on other criteria. Possible values can be found by calling :meth:`Services.get_all_isos`
        :return: :class:`~requests.Response` containing a JSON object. If matching nodes are found, a `'nodes'` item
          will contain an **array** of objects with schema :class:`NodeSearchData`. If no matching nodes are found,
          an error code will be returned. As an example, a successful search result might look like:

          .. code:: python

              {
                  "nodes": [
                      {
                          "node/name": "HB_BUSAVG",
                          "node/id": "10000698380",
                          "node/iso": "ERCOT",
                          "node/lat": 30.850714,
                          "node/lng": -97.877628,
                          "node/distance-meters": 500.67458
                      },
                      {
                          "node/name": ...,
                          ...
                      },
                      ...
                  ]
              }

        """
        return self.get(route="search-nodes",
                        params={"location": location,
                                "node_name_filter": node_name_filter,
                                "iso_override": iso_override})


class Services(object):
    """Interface for accessing Tyba's historical price data
    """
    def __init__(self, client: 'Client'):

        self.client = client
        self.ancillary: Ancillary = Ancillary(self)
        """Interface for accessing Tyba's historical *ancillary* price data"""
        self.lmp: LMP = LMP(self)
        """Interface for accessing Tyba's historical *energy* price data"""
        self._route_base = "services"

    def get(self, route, params=None):
        return self.client.get(f"{self._route_base}/{route}", params=params)

    def post(self, route, json):
        return self.client.post(f"{self._route_base}/{route}", json=json)

    def get_all_isos(self) -> requests.Response:
        """Get of list of all independent system operators and regional transmission operators (generally all referred
        to as ISOs) represented in Tyba's historical price data

        :return: :class:`~requests.Response` containing JSON array of strings of the available ISO names
        """
        return self.get("isos")


class Client(object):
    """High level interface for interacting with Tyba's API.

    :param personal_access_token: required for using the python client/API, contact Tyba to obtain
    """

    DEFAULT_OPTIONS = {"version": "0.1"}

    def __init__(
        self,
        personal_access_token: str,
        host: str = "https://dev.tybaenergy.com",
        request_args: t.Optional[dict] = None,
    ):
        self.personal_access_token = personal_access_token
        self.host = host
        self.services: Services = Services(self)
        """Interface for accessing Tyba's historical price data"""
        self.forecast: Forecast = Forecast(self)
        """Interface for accessing Tyba's historical price data"""
        self.operations = Operations(self)
        self.request_args = {} if request_args is None else request_args

    @property
    def ancillary(self) -> Ancillary:
        """Shortcut to :class:`client.services.ancillary <Ancillary>`"""
        return self.services.ancillary

    @property
    def lmp(self) -> LMP:
        """Shortcut to :class:`client.services.lmp <LMP>`"""
        return self.services.lmp

    def _auth_header(self):
        return self.personal_access_token

    def _base_url(self):
        return self.host + "/public/" + self.DEFAULT_OPTIONS["version"] + "/"

    def get(self, route, params=None):
        return requests.get(
            self._base_url() + route,
            params=params,
            headers={"Authorization": self._auth_header()},
            **self.request_args,
        )

    def post(self, route, json):
        return requests.post(
            self._base_url() + route,
            json=json,
            headers={"Authorization": self._auth_header()},
            **self.request_args,
        )

    def schedule_pv(self, pv_model: GenerationModel) -> Response:
        model_json_dict = pv_model.to_dict()
        return self.post("schedule-pv", json=model_json_dict)

    def schedule_storage(self, storage_model: StandaloneStorageModel) -> Response:
        model_json_dict = storage_model.to_dict()
        return self.post("schedule-storage", json=model_json_dict)

    def schedule_pv_storage(self, pv_storage_model: PVStorageModel) -> Response:
        model_json_dict = pv_storage_model.to_dict()
        return self.post("schedule-pv-storage", json=model_json_dict)

    def schedule(self, model: JobModel) -> Response:
        """Schedule a model simulation based on the given inputs

        :param model: a class instance of one of the model classes, e.g.
          :class:`~generation_models.generation_models.StandaloneStorageModel`. Contains all required inputs for
          running a simulation
        :return: :class:`~requests.Response` whose status code indicates whether the model was successfully scheduled.
          If successful, the response will contain a JSON object with an ``'id'`` for the scheduled model run. This id
          can be used with the :meth:`get_status` and :meth:`wait_on_result` endpoints to retrieve status updates and
          model results. The presence of issues can be easily checked by calling the
          :meth:`~requests.Response.raise_for_status` method of the response object. For example:

          .. code:: python

              resp = client.schedule(pv)
              resp.raise-for_status()  # this will raise an error if the model was not successfully scheduled
              id_ = resp.json()["id"]
              res = client.wait_on_result(id_)

        """
        return self.post("schedule-job", json=model.dict())

    def get_status(self, run_id: str):
        """Check the status and retrieve the results of a scheduled model simulation. If a simulation has not
        completed, this endpoint returns the simulation status/progress. If the simulation has completed, it
        returns the model results.

        :param run_id: ID of the scheduled model simulation
        :return: :class:`~requests.Response` containing a JSON object with schema :class:`ModelStatus`
        """
        url = "get-status/" + run_id
        return self.get(url)

    def get_status_v1(self, run_id: str):
        """`Deprecated, please use` :meth:`get_status`, `which will support additional results schemas in the near
        future`. Identical to :meth:`get_status`, but returns results for completed simulations in the "V1"
        SLD-style schema

        :param run_id: ID of the scheduled model simulation
        :return: :class:`~requests.Response` containing a JSON object with schema :class:`ModelStatus` (except with a
          different schema for :attr:`~ModelStatus.result`)
        """
        return self.get(f"get-status/{run_id}", params={"fmt": "v1"})

    @staticmethod
    def _wait_on_result(
        run_id: str,
        wait_time: int,
        log_progress: bool,
        getter: Callable[[str], Response],
    ) -> dict:
        while True:
            resp = getter(run_id)
            resp.raise_for_status()
            res = resp.json()
            if res["status"] == "complete":
                return res["result"]
            elif res["status"] == "unknown":
                raise UnknownRunId(f"No known model run with run_id '{run_id}'")
            message = {"status": res["status"]}
            if res.get("progress") is not None:
                message["progress"] = f"{float(res['progress']) * 100:3.1f}%"
            if log_progress:
                logger.info("waiting on result", **message)
            time.sleep(wait_time)

    def wait_on_result(
        self, run_id: str, wait_time: int = 5, log_progress: bool = False
    ) -> dict:
        """Poll for simulation status and, once complete, return the model results

        :param run_id: ID of the scheduled model simulation
        :param wait_time: time in seconds to wait between polling/updates
        :param log_progress: indicate whether updates/progress should be logged/displayed. If ``True``, will
          report both :attr:`~ModelStatus.status` and :attr:`~ModelStatus.progress` information
        :return: results dictionary equivalent to :attr:`ModelStatus.result` returned by :meth:`get_status`, with the
          exact schema depending on the model inputs
        """
        return self._wait_on_result(
            run_id, wait_time, log_progress, getter=self.get_status
        )

    def wait_on_result_v1(
        self, run_id: str, wait_time: int = 5, log_progress: bool = False
    ):
        """`Deprecated, please use :meth:`wait_on_result`, which will support additional results schemas in the near
        future`. Identical to :meth:`wait_on_result`, but returns results for completed simulations in the "V1"
        SLD-style schema

        :param run_id: ID of the scheduled model simulation
        :param wait_time: time in seconds to wait between polling/updates
        :param log_progress: indicate whether updates/progress should be logged/displayed. If ``True``, will
          report both :attr:`~ModelStatus.status` and :attr:`~ModelStatus.progress` information
        :return: results dictionary with "V1" SLD-style schema
        """
        res = self._wait_on_result(
            run_id, wait_time, log_progress, getter=self.get_status_v1
        )
        return parse_v1_result(res)


def parse_v1_result(res: dict):
    """:meta private:"""
    return {
        "hourly": pd.concat(
            {k: pd.DataFrame(v) for k, v in res["hourly"].items()}, axis=1
        ),
        "waterfall": res["waterfall"],
    }


class UnknownRunId(ValueError):
    """:meta private:"""
    pass


class NodeType(str, Enum):
    """Indicator of which type of physical infrastructure is associated with a particular market node"""
    GENERATOR = "GENERATOR"
    """Not sure"""
    SPTIE = "SPTIE"
    """Not sure"""
    LOAD = "LOAD"
    """Not sure"""
    INTERTIE = "INTERTIE"
    """Not sure"""
    AGGREGATE = "AGGREGATE"
    """Not sure"""
    HUB = "HUB"
    """Not sure"""
    NA = "N/A"
    """Not sure"""


class NodeData(BaseModel):
    """Schema for node metadata"""
    name: str
    """Name of the node"""
    id: str
    """ID of the node"""
    zone: str
    """Zone where the node is located within the ISO territory"""
    type: NodeType
    """Identifier that indicates physical infrastructure associated with this node"""
    da_start_year: float
    """First year in the Day Ahead (DA) market price dataset for this node"""
    da_end_year: float
    """Final year in the Day Ahead (DA) market price dataset for this node"""
    rt_start_year: int
    """First year in the Real Time (RT) market price dataset for this node"""
    rt_end_year: int
    """Final year in the Real Time (RT) market price dataset for this node"""
    substation: t.Optional[str] = None
    """Indicator of the grid substation associated with this node (not always present)"""

class PriceTimeSeries(BaseModel):
    """Schema for pricing data associated with a particular energy price node or ancillary pricing region"""
    datetimes: list[str]
    """Beginning-of-interval datetimes for the hourly pricing given in local time.
    
    - For energy prices, the datetimes are timezone-naive (no timezone identifier) but given in the local timezone
      (i.e. including Daylight Savings Time or DST). E.g. The start of the year 2022 in ERCOT is given as
      `'2022-01-01T00:00:00'` as opposed to `'2022-01-01T00:00:00-6:00'`. Leap days are represented by a single hour,
      which should be dropped as a post-processing step.
    - For ancillary prices, the datetimes are in local standard time (i.e. not including DST) but appear to be in
      UTC ("Z" timezone identifier). E.g. The start of the year 2022 in ERCOT is given as `'2022-01-01T00:00:00Z'` and
      not `'2022-01-01T00:00:00-6:00'`. Leap days are not included.
      
    """
    prices: list[float]
    """Average hourly settlement prices for hours represented by :attr:`datetimes`.
    """

class NodeSearchData(BaseModel):
    """Schema for search-specific node metadata. The `(name 'xxxx')` to the right of the field names can be ignored"""
    node_name: str = Field(..., alias='node/name')
    """Name of the node"""
    node_id: str = Field(..., alias='node/id')
    """ID of the node"""
    node_iso: str = Field(..., alias='node/iso')
    """ISO that the node belongs to"""
    node_longitude: float = Field(..., alias='node/lng')
    """longitude of the point on the electrical grid associated with the node"""
    node_latitude: float = Field(..., alias='node/lat')
    """latitude of the point on the electrical grid associated with the node"""
    node_distance_meters: t.Optional[float] = Field(default=None, alias='node/distance-meters')
    """Distance from the node to the `location` parameter passed to :meth:`~LMP.search_nodes`. Not present if
    `location` is not given.
    """


class AncillaryRegionData(BaseModel):
    """Schema for ancillary region metadata"""
    region: str
    """Name of the region"""
    start_year: int
    """First year in price dataset for the region and specified service"""
    da_end_year: int
    """Final year in price dataset for the region and specified service"""


class ModelStatus(BaseModel):
    """Schema for model status and results"""
    status: str
    """Status of the scheduled run. Possible values are explained in
    :ref:`Tyba Model Run Status Codes <status_codes>`"""
    progress: t.Optional[str]
    """Percentage value indicating the progress towards completing a model simulation. Only present if :attr:`status`
    is not ``'complete'``.
    
    - Note that in some cases the simulation may involve multiple optimization iterations, and the progress may appear
      to start over as each additional iteration is undertaken
    
    """
    result: t.Optional[V0Results]
    """Model simulation results dictionary with schema defined depending on the model inputs, e.g. scheduling a
    :class:`~generation_models.generation_models.PVGenerationModel` will return a dictionary with
    schema :class:`~generation_models.v0_output_schema.GenerationModelResults`. Only present if
    :attr:`status` is ``'complete'``"""


