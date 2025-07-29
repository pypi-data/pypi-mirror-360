import datetime
import enum
import inspect
import ssl
import zoneinfo
from typing import Annotated

import fastmcp.prompts
import fastmcp.resources
import fastmcp.tools
import httpx
import mcp
import pydantic

from bir_mcp.grafana.prompts import get_prompts
from bir_mcp.grafana.resources import get_mcp_resouce_uri_functions
from bir_mcp.grafana.utils import to_grafana_time_format
from bir_mcp.utils import (
    araise_for_status,
    build_mcp_server,
    filter_dict_by_keys,
    to_fastmcp_tool,
    to_maybe_ssl_context,
)


class DatasourceType(enum.StrEnum):
    alertmanager = "Alertmanager"
    clickhouse = "ClickHouse"
    grafana_pyroscope = "Grafana Pyroscope"
    influxdb = "InfluxDB"
    json_api = "JSON API"
    loki = "Loki"
    microsoft_sql_server = "Microsoft SQL Server"
    oracle_enterprise_manager_data_source = "Oracle Enterprise Manager Data Source"
    postgresql = "PostgreSQL"
    prometheus = "Prometheus"
    tempo = "Tempo"
    zabbix = "Zabbix"


class InfluxDbQueryType(enum.StrEnum):
    flux = enum.auto()
    influxql = enum.auto()


class Grafana:
    def __init__(
        self,
        url: str,
        auth: tuple[str, str],
        http_timeout_seconds: int = 30,
        timezone: str = "UTC",
        ssl_verify: bool | str = True,
        tag: str | None = "grafana",
    ):
        self.client = httpx.AsyncClient(
            auth=auth,
            base_url=url,
            event_hooks={"response": [araise_for_status]},
            timeout=http_timeout_seconds,
            verify=to_maybe_ssl_context(ssl_verify),
        )
        self.timezone = zoneinfo.ZoneInfo(timezone)
        self.tag = tag
        self.tags = {tag} if tag else set()

    def get_tools(self, max_output_length: int | None = None) -> list[fastmcp.tools.FunctionTool]:
        functions = [
            self.list_all_datasources,
            self.query_influxdb_datasource,
            self.query_datasource,
        ]
        tools = [
            to_fastmcp_tool(
                function,
                tags=self.tags,
                annotations=mcp.types.ToolAnnotations(readOnlyHint=True, destructiveHint=False),
                max_output_length=max_output_length,
            )
            for function in functions
        ]
        return tools

    def get_resources(self) -> list[fastmcp.resources.Resource]:
        resources = [
            fastmcp.resources.Resource.from_function(function, uri=uri, tags=self.tags)
            for uri, function in get_mcp_resouce_uri_functions().items()
        ]
        return resources

    def get_prompts(self) -> list[fastmcp.prompts.Prompt]:
        prompts = get_prompts()
        prompts = [
            fastmcp.prompts.Prompt.from_function(function, tags=self.tags) for function in prompts
        ]
        return prompts

    def build_mcp_server(self, max_output_length: int | None = None) -> fastmcp.FastMCP:
        server = build_mcp_server(
            name="Bir Grafana MCP server",
            instructions=inspect.cleandoc("""
                Use this server for tasks related to Grafana and its datasources.
                Note that in context of the bank, Grafana may be referred to as "Yuno",
                this is due to the fact that the domain name for the on-prem Grafana instance is "yuno.kapitalbank.az".
            """),
            tools=self.get_tools(max_output_length=max_output_length),
            resources=self.get_resources(),
            prompts=self.get_prompts(),
        )
        return server

    async def list_all_datasources(self) -> dict:
        """Lists all datasources in the Grafana instance."""
        response = await self.client.get("/api/datasources")
        datasources = {
            "datasources": [
                filter_dict_by_keys(d, ["uid", "name", "typeName"]) for d in response.json()
            ]
        }
        return datasources

    async def query_influxdb_datasource(
        self,
        datasource_uid: Annotated[
            str,
            pydantic.Field(description="The uid of an InfluxDB Grafana datasource."),
        ],
        query: Annotated[
            str,
            pydantic.Field(description="The query to execute."),
        ],
        start_time: Annotated[
            str,
            pydantic.Field(
                description=inspect.cleandoc("""
                    The start time for the query in relative Grafana time units like "now", "now-5m", 
                    "now-1h", "now-7d", or in ISO 8601 format "YYYY-MM-DDTHH:MM:SS+HH:MM".
                    Can be refered to as "v.timeRangeStart" in queries.
                    Should not be older than one month for query efficiency and because data is probably 
                    not retained longer than that anyway.
                """)
            ),
        ] = "now-1h",
        end_time: Annotated[
            str,
            pydantic.Field(
                description=inspect.cleandoc("""
                    The end time for the query, in same format as start_time. 
                    Can be refered to as "v.timeRangeStop" in queries.
                """)
            ),
        ] = "now",
        query_language: Annotated[
            InfluxDbQueryType,
            pydantic.Field(
                description=inspect.cleandoc(f"""
                The language of query to execute, {InfluxDbQueryType.influxql} for SQL-like Influx query language, 
                and {InfluxDbQueryType.flux} for Flux functional data scripting language.
            """)
            ),
        ] = InfluxDbQueryType.flux,
    ) -> dict:
        """
        Executes a query against an InfluxDB datasource in the Grafana instance.
        Note that InfluxQL may not be supported by the InfluxDB datasource.
        Refer to Flux instruction in the MCP resources for details about the Flux language.
        This function delegates the call to the query_datasource function,
        so refer to its documentation for additional details.
        """
        tables = await self.query_datasource(
            datasource_uid=datasource_uid,
            query=query,
            additional_datasource_params={"queryType": query_language.value},
            start_time=start_time,
            end_time=end_time,
        )
        return tables

    async def query_datasource(
        self,
        datasource_uid: Annotated[
            str,
            pydantic.Field(description="The uid of a Grafana datasource."),
        ],
        query: Annotated[
            str,
            pydantic.Field(description="The query to execute."),
        ],
        additional_datasource_params: Annotated[
            dict[str, str] | None,
            pydantic.Field(
                description="Additional datasource parameters, for example queryType for InfluxDB queries."
            ),
        ] = None,
        start_time: Annotated[
            str,
            pydantic.Field(
                description=inspect.cleandoc("""
                    The start time for the query in relative Grafana time units like "now", "now-5m", 
                    "now-1h", "now-7d", or in ISO 8601 format "YYYY-MM-DDTHH:MM:SS+HH:MM".
                    Should not be older than one month for query efficiency and because data is probably 
                    not retained longer than that anyway.
                """)
            ),
        ] = "now-1h",
        end_time: Annotated[
            str,
            pydantic.Field(description="The end time for the query, in same format as start_time."),
        ] = "now",
    ) -> dict:
        """
        Executes a query against a datasource in the Grafana instance.
        If query returns too much data, it will lead to HTTP timeouts.
        To avoid this, the start to end time range should be as small as possible,
        and the query should aggregate data by time windows.
        Refer to [Grafana endpoint docs](https://grafana.com/docs/grafana/latest/developers/http_api/data_source/#query-a-data-source)
        for details about the used endpoint.
        """
        ref_id = "A"
        datasource_query = additional_datasource_params | {
            "datasource": {"uid": datasource_uid},
            "refId": ref_id,
            "format": "table",
            "maxDataPoints": 100,
            "intervalMs": 1000,
        }
        datasources = await self.list_all_datasources()
        datasource_types = {d["uid"]: d["typeName"] for d in datasources["datasources"]}
        datasource_type = datasource_types.get(datasource_uid)
        match datasource_type:
            case "PostgreSQL":
                datasource_query["rawSql"] = query
            case _:
                datasource_query["query"] = query

        payload = {
            "queries": [datasource_query],
            "from": to_grafana_time_format(start_time),
            "to": to_grafana_time_format(end_time),
        }
        response = await self.client.post("/api/ds/query", json=payload)
        tables = []
        result = response.json()["results"].get(ref_id)
        frames = result["frames"] if result else []
        for frame in frames:
            table = filter_dict_by_keys(frame["schema"], ["name", "fields"])
            table["data"] = frame["data"]["values"]
            tables.append(table)

        tables = {"tables": tables}
        return tables


# def build_prometheus_from_grafana_datasource_proxy(
#     grafana_url: str, datasource: str, auth: tuple[str, str], **kwargs
# ):
#     """https://grafana.com/docs/grafana/v11.2/developers/http_api/data_source/#data-source-proxy-calls-by-id"""
#     data_sources = fetch_grafana_datasources(grafana_url, auth)
#     data_source = data_sources.filter(pl.col("name") == datasource)
#     if len(data_source) != 1:
#         raise ValueError(f"Couldn't find a singular id for data source {data_source}.")

#     data_source_id = data_source["id"].item()
#     prometheus_url = join_url_components(grafana_url, "api", "datasources", "proxy", data_source_id)
#     prometheus = Prometheus(prometheus_url, auth=auth, **kwargs)
#     return prometheus


# class Prometheus:
#     """https://prometheus.io/docs/prometheus/latest/querying/api"""

#     def __init__(
#         self,
#         url: str,
#         api_version: str = "v1",
#         default_start=datetime.timedelta(days=-1),
#         default_end=None,
#         time_zone: str = "Asia/Baku",
#         auth=None,
#     ):
#         self.url = url
#         self.api_version = api_version
#         self.default_date_keys = {
#             "start": default_start,
#             "end": default_end,
#             "time": default_end,
#         }
#         self.time_zone = time_zone
#         self.auth = auth

#     def request_as_dict(self, *url_components, **params) -> dict:
#         params = {k: v for k, v in params.items() if v}
#         match url_components:
#             case (
#                 ["query"]
#                 | ["query_range"]
#                 | ["series"]
#                 | ["labels"]
#                 | ["label", _, "values"]
#                 | ["query_exemplars"]
#             ):
#                 for key, default in self.default_date_keys.items():
#                     value = params.get(key, default)
#                     params[key] = to_datetime(value).isoformat()

#         url = join_url_components(self.url, "api", self.api_version, *url_components)
#         response_dict = request_as_dict(url, params=params, auth=self.auth)
#         if response_dict["status"] == "error":
#             raise RuntimeError(
#                 f'Prometheus API request for "{join_url_components(*url_components)}" endpoint '
#                 f"with parameters {params} returned an error:\n"
#                 f"{response_dict}"
#             )

#         data = response_dict["data"]
#         return data

#     def response_metric_data_to_dataframe(self, data: dict) -> pl.DataFrame | None:
#         if not (result := data["result"]):
#             return

#         rows = []
#         for series in result:
#             match data["resultType"]:
#                 case "matrix":
#                     values = series["values"]
#                 case "vector":
#                     values = [series["value"]]

#             for timestamp, value in values:
#                 row = series["metric"] | {"timestamp": timestamp, "value": value}
#                 rows.append(row)

#         if not rows:
#             return

#         df = pl.DataFrame(rows)
#         df = df.cast({"value": pl.Float64})
#         df = df.with_columns(pl.from_epoch("timestamp").dt.convert_time_zone(self.time_zone))
#         return df

#     def query(self, query, time=None, timeout: str | None = None) -> pl.DataFrame | None:
#         """https://prometheus.io/docs/prometheus/latest/querying/api/#instant-queries"""
#         query = re.sub(r"\s+", " ", query)
#         data = self.request_as_dict("query", query=query, time=time, timeout=timeout)
#         df = self.response_metric_data_to_dataframe(data)
#         return df

#     def query_range(
#         self,
#         query: str,
#         start=None,
#         end=None,
#         step: str | float = "1m",
#         timeout: str | None = None,
#     ) -> pl.DataFrame | None:
#         """https://prometheus.io/docs/prometheus/latest/querying/api/#range-queries"""
#         data = self.request_as_dict(
#             "query_range",
#             query=re.sub(r"\s+", " ", query),
#             start=start,
#             end=end,
#             step=step,
#             timeout=timeout,
#         )
#         df = self.response_metric_data_to_dataframe(data)
#         return df

#     def get_all_metric_names(self, **kwargs) -> list[str]:
#         """https://prometheus.io/docs/prometheus/latest/querying/api/#querying-label-values"""
#         data = self.request_as_dict("label", "__name__", "values", **kwargs)
#         return data

#     def get_time_series(self, series_selector: str, start=None, end=None) -> pl.DataFrame | None:
#         """https://prometheus.io/docs/prometheus/latest/querying/api/#finding-series-by-label-matchers"""
#         data = self.request_as_dict(
#             "series", **{"match[]": series_selector, "start": start, "end": end}
#         )
#         if not data:
#             return

#         df = pl.DataFrame(data)
#         return df
