import asyncio
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

import httpx
import nest_asyncio
import numpy as np
import pandas as pd
from tqdm.asyncio import tqdm_asyncio

from .api import ForecastRequest, ForecastResponse, OutputSerie

logger = logging.getLogger(__name__)


# Types definiton
class IDForecastResponse(ForecastResponse):
    unique_id: str


ModelAlias = str


class TFCModels(StrEnum):
    """Utils Enum that defines the models available in TFC.
    For each model, it defines the type of covariates it can handle and whether it's a global model or not.
    """

    TimesFM_2 = "timesfm-2"
    TabPFN_TS = "tabpfn-ts"
    TFCGlobal = "tfc-global"
    ChronosBolt = "chronos-bolt"
    Moirai = "moirai"
    MoiraiMoe = "moirai-moe"

    @property
    def accept_future_variables(self) -> bool:
        return self.value in [
            TFCModels.TabPFN_TS,
            TFCModels.TFCGlobal,
            TFCModels.Moirai,
            TFCModels.MoiraiMoe,
            TFCModels.TimesFM_2,
        ]

    @property
    def accept_historical_variables(self) -> bool:
        return self.value in [
            TFCModels.TabPFN_TS,
            TFCModels.TFCGlobal,
            TFCModels.Moirai,
            TFCModels.MoiraiMoe,
        ]

    @property
    def accept_static_variables(self) -> bool:
        return self.value in [
            TFCModels.TabPFN_TS,
            TFCModels.TFCGlobal,
            TFCModels.Moirai,
            TFCModels.MoiraiMoe,
        ]

    @property
    def is_global(self) -> bool:
        return self.value == TFCModels.TFCGlobal


@dataclass
class ModelConfig:
    """
    Represents the configuration of a model for which forecasts are requested.

    Attributes:
        model (TFCModels): string identifier of the model.
        model_alias (str): alias of the model. This will be the name of the column in the result df containing the forecasts.
        future_variables (list[str]): list of future variables to be used by the model.
        with_holidays (bool): whether to include TFC-holidays in the forecast.
        with_events (bool): whether to include TFC-events in the forecast.
        country_isocode (str): ISO code of the country for which the forecast is requested. This is used for fetching the right
        holidays and events.
        historical_variables (list[str]): list of historical variables to be used by the model.
        static_variables (list[str]): list of static variables to be used by the model.
    """

    model: TFCModels
    model_alias: ModelAlias | None = None
    historical_variables: list[str] | None = None
    static_variables: list[str] | None = None
    future_variables: list[str] | None = None
    add_holidays: bool = False
    add_events: bool = False
    country_isocode: str | None = None

    def __post_init__(self) -> None:
        # Validate and possibly convert str to TFCModels
        self.model = TFCModels(self.model)
        if self.future_variables and not self.model.accept_future_variables:
            raise ValueError(f"Model {self.model} does not accept future variables")
        if self.historical_variables and not self.model.accept_historical_variables:
            raise ValueError(f"Model {self.model} does not accept historical variables")
        if self.static_variables and not self.model.accept_static_variables:
            raise ValueError(f"Model {self.model} does not accept static variables")
        if self.model_alias is None:
            self.model_alias = self.model.value

    def get_covariates(self):
        if not (self.add_holidays or self.add_events):
            return None
        if self.country_isocode is None:
            raise ValueError("holidays and events need a countryisocode or `Global` for global events.")

        cov = []
        if self.add_holidays:
            cov += [{"type": "holidays", "config": {"country": self.country_isocode}}]
        if self.add_events:
            # Add by default also Global events.
            cov += [{"type": "events", "config": {"country": self.country_isocode}}]
            cov += [{"type": "events", "config": {"country": "Global"}}]
        return cov


def extract_forecast_df_from_model_idresponse(
    response_dicts: dict[ModelAlias, list[IDForecastResponse]],
    fcds: list[pd.Timestamp] | dict[str,list[pd.Timestamp]],
    id_col: str = "unique_id",
    date_col: str = "ds",
) -> pd.DataFrame:
    """Bild a DataFrame with the Forecasts from each TFCModel.

    response_dicts: For each ModelAlias, a list of IDForecastResponse, one per time series (unique_id) to be forecasted.
    fcds: the forecast creation date
    id_col: the column name for the time series id
    date_col: the column name for the forecast date
    """
    model_dfs = []
    for model_name, response_list in response_dicts.items():
        dfs = []
        for response in response_list:
            unique_id = response.unique_id
            if response.series is None:
                raise ValueError(
                    f"Response series is None: this means the model failed to generate a forecast for serie:{unique_id}"
                )
            series: list[list[OutputSerie]] = response.series
            for serie in series:
                if isinstance(fcds, list):
                    unique_id_fcds = fcds
                elif isinstance(fcds, dict):
                    unique_id_fcds = fcds.get(unique_id, [])
                    if not isinstance(unique_id_fcds, list):
                        unique_id_fcds = [unique_id_fcds]
                else:
                    raise ValueError("fcds must be a list[pd.Timestamp] or a dict[str, list[pd.Timestamp]]")
                assert (len(serie) == len(unique_id_fcds) or (len(serie)==1 and len(unique_id_fcds)==0)), "Wrong number of fcds. Expected %d, got %d" % (len(serie), len(unique_id_fcds))
                for fcd, pred in zip(unique_id_fcds, serie, strict=False):
                    df = pd.DataFrame()
                    df[model_name] = pred.prediction["mean"]
                    df[date_col] = pred.index
                    df[id_col] = unique_id
                    df["fcd"] = fcd
                    # Add quantile predictions
                    df = df.assign(
                        **{
                            f"{model_name}_q{key}": pred.prediction[key]
                            for key in pred.prediction.keys()
                            if key != "mean"
                        }
                    )
                    dfs.append(df)
        model_dfs.append(
            pd.concat(dfs, axis=0)
            .assign(
                **{
                    date_col: lambda df: pd.to_datetime(df[date_col]),
                    "fcd": lambda df: pd.to_datetime(df["fcd"]),
                    id_col: lambda df: df[id_col].astype(str),
                }
            )
            .sort_values([id_col, "fcd", date_col])
        )
    if not all(len(df) == len(model_dfs[0]) for df in model_dfs):
        raise ValueError("All model dfs must have the same number of rows")

    res = pd.concat(model_dfs, axis=1)
    if len(res) != len(model_dfs[0]):
        raise ValueError(
            "Concatenation of model forecasts resulted in more rows than expected. Indexes unique_id, ds, fcd must be the same for all models."
        )

    return res


async def send_request_with_retries(
    payload: dict[str, dict | list],
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    api_key: str,
    url: str,
    max_retries: int = 3,
    retry_delay: int = 2,  # nb seconds before retrying.
) -> tuple[int, list[ForecastResponse]]:
    """
    Send a request to the Retrocast API for a single time series. Return one separate ForecastResponse per OutputSerie
    """
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    ForecastRequest.model_validate(payload)

    def _extract_response(response: ForecastResponse) -> list[ForecastResponse]:
        if response.series is None or len(response.series) == 1:
            return [response]

        return [
            ForecastResponse(
                status=response.status,
                series=[serie],
            )
            for serie in response.series
        ]

    if max_retries < 1:
        raise ValueError("max retries should be >= 1")
    async with semaphore:
        for _ in range(max_retries):
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.status_code, _extract_response(ForecastResponse(**response.json()))
            await asyncio.sleep(retry_delay)  # Wait before retrying
    # No response after max_retries retries
    response.raise_for_status()


async def send_async_requests_multiple_models(
    train_df: pd.DataFrame,
    fcds: list[pd.Timestamp] | dict[str, list[pd.Timestamp]],
    models: list[ModelConfig],
    horizon: int = 13,
    freq: str = "W",
    max_retries: int = 5,
    max_concurrent: int = 10,
    api_key: str | None = None,
    url: str | None = None,
    id_col: str = "unique_id",
    date_col: str = "ds",
    target_col: str = "target",
    new_ids: Iterable[str] | None = None,
) -> dict[ModelAlias, list[IDForecastResponse]]:
    """Given a train_df with columns [id_col, date_col, target_col], sends request for each unique_id (timeseries)
    asynchronously to the Retrocast API. Returns a list of responses."""
    if api_key is None:
        raise ValueError("api_key must be provided")

    if new_ids is None:
        new_ids = set()

    # Try further limiting concurrency, beside setting AsyncClient maximum connections
    semaphore = asyncio.Semaphore(int(max_concurrent * 0.9))
    async with httpx.AsyncClient(
        limits=httpx.Limits(
            max_connections=max_concurrent,
            max_keepalive_connections=max(int(max_concurrent / 10 * 5), 1),
        ),
        timeout=httpx.Timeout(connect=60, read=600, pool=600, write=5),
    ) as client:
        tasks = []
        model_names = []
        payloads = []
        unique_ids = []
        for mymodel in models:
            model_url = url if url else f"https://api.retrocast.com/forecast?model={mymodel.model.value}"
            if mymodel.model not in model_url:
                raise ValueError(f"Wrong url provided: {mymodel.model} not found in url {model_url}")
            payloads = []
            covariates = mymodel.get_covariates()
            static_payload = {
                "horizon": horizon,
                "freq": freq,
                "context": None,
                "quantiles": [0.1, 0.9, 0.4, 0.5],
                "covariates": covariates,
            }
            # Loop over unique_ids (time series) and send one request for each.
            for unique_id in train_df[id_col].unique():
                ts_df = train_df.query(f"{id_col} == @unique_id")
                index = ts_df[date_col].dt.strftime("%Y-%m-%d %H:%M:%S").to_list()
                target = ts_df[target_col].to_list()
                unique_id_fcds = fcds if isinstance(fcds, list) else fcds.get(unique_id, [])
                if not isinstance(unique_id_fcds, list):
                    unique_id_fcds = [unique_id_fcds]
                if unique_id_fcds and not isinstance(unique_id_fcds[0], str):
                    unique_id_fcds = [c.strftime("%Y-%m-%d %H:%M:%S") for c in unique_id_fcds]

                if unique_id in new_ids:
                    # Support only single forecast for a new series. If several FCD needs to be tried, at the moment these need to be separate calls
                    fcds_idxs = [0] 
                else:
                    fcds_idxs = np.nonzero(np.isin(np.array(index), unique_id_fcds))[0].tolist()
                # Test forecast: FCD > max(index) --> fcds = [] passed to the API
                # Backtest forecast: FCD <= max(index) --> fcds = [] will be passed to the API but this is wrong, cause 
                # FCD > max(index) will be used in this case.
                if len(fcds_idxs) != len(fcds) and max(fcds) < max(index):
                    # TODO: I should check for each fcd to be more precise, cause I can have some fcd that re smaller
                    # and some fcds that are bigger than max(index)
                    raise ValueError(
                        f"Not all fcds found in {date_col} for {id_col}={unique_id}"
                    )
                # TODO: Treat future_vars and static_vars separately in the future.
                future_vars = mymodel.future_variables if mymodel.future_variables else []
                if mymodel.static_variables:
                    future_vars += mymodel.static_variables
                if future_vars:
                    future_variables_index = ts_df[date_col].dt.strftime("%Y-%m-%d %H:%M:%S").to_list()
                    future_dict = {col: ts_df[col].to_list() for col in future_vars}
                else:
                    future_variables_index = []
                    future_dict = {}
                if mymodel.historical_variables:
                    hist_variables_dict = {col: ts_df[col].to_list() for col in mymodel.historical_variables}
                else:
                    hist_variables_dict = {}

                if not mymodel.model.is_global:
                    only_as_context = False
                elif isinstance(fcds, list):
                    only_as_context = False
                else:
                    assert isinstance(fcds, dict), "fcds should be either a list or dict"
                    only_as_context = False if unique_id in fcds else True
                    
                payload = {
                    "future_variables": future_dict,
                    "future_variables_index": future_variables_index,
                    "hist_variables": hist_variables_dict,
                    "index": index,
                    "static_variables": {},
                    "target": target,
                    "fcds": fcds_idxs,
                    "only_as_context": only_as_context,
                }
                if not mymodel.model.is_global:
                    tasks.append(
                        asyncio.create_task(
                            send_request_with_retries(
                                {"series": [payload], **static_payload},
                                client=client,
                                semaphore=semaphore,
                                api_key=api_key,
                                url=model_url,
                                max_retries=max_retries,
                            )
                        )
                    )
                else:
                    payloads.append(payload)
                if not only_as_context:
                    # If only as context, they won't be returned as reponses. So I don't need to keep track of the unique_ids
                    model_names.append(mymodel.model_alias)
                    unique_ids.append(unique_id)
            if mymodel.model.is_global:
                tasks.append(
                    asyncio.create_task(
                        send_request_with_retries(
                            {"series": payloads, **static_payload},
                            client=client,
                            semaphore=semaphore,
                            api_key=api_key,
                            url=model_url,
                            max_retries=max_retries,
                        )
                    )
                )

        responses = await tqdm_asyncio.gather(*tasks, desc=f"Sending {len(tasks)} requests")
        failed_status_codes = set(r[0] for r in responses if r[0] != 200)
        if len(failed_status_codes) > 0:
            raise RuntimeError(
                f"Failed to fetch {len(failed_status_codes)} out of {len(responses)} responses. Status codes: {failed_status_codes}"
            )
        responses = [r for _, batched_responses in responses for r in batched_responses]
        responses = [IDForecastResponse(**r.dict(), unique_id=unique_id) for unique_id, r in zip(unique_ids, responses, strict=False)]
        return {
            model_name: [r for name, r in zip(model_names, responses, strict=False) if name == model_name]
            for model_name in set(model_names)
        }


def cross_validate_models(
    train_df: pd.DataFrame,
    fcds: list[pd.Timestamp] | dict[str, pd.Timestamp],
    models: list[ModelConfig],
    horizon: int,
    freq: str,
    max_retries: int = 5,
    max_concurrent: int = 100,
    api_key: str | None = None,
    url: str | None = None,
    id_col: str = "unique_id",
    date_col: str = "ds",
    target_col: str = "target",
    new_ids: Iterable[str] | None = None,
) -> pd.DataFrame:
    async def _run():
        return await send_async_requests_multiple_models(
            train_df,
            fcds,
            models,
            horizon,
            freq,
            max_retries,
            max_concurrent,
            api_key,
            url,
            id_col,
            date_col,
            target_col,
            new_ids,
        )

    try:
        return extract_forecast_df_from_model_idresponse(asyncio.run(_run()), fcds, id_col, date_col)
    except RuntimeError as e:
        if "asyncio.run() cannot be called" in str(e) or "This event loop is already running" in str(e):
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            return extract_forecast_df_from_model_idresponse(loop.run_until_complete(_run()), fcds, id_col, date_col)
        else:
            raise


def cross_validate_single_model(
    train_df: pd.DataFrame,
    fcds: list[pd.Timestamp] | dict[str, pd.Timestamp],
    model: TFCModels,
    horizon: int,
    freq: str,
    add_holidays: bool = False,
    add_events: bool = False,
    country_isocode: str | None = None,
    future_variables: list[str] | None = None,
    historical_variables: list[str] | None = None,
    static_variables: list[str] | None = None,
    max_concurrent: int = 100,
    max_retries: int = 5,
    api_key: str | None = None,
    url: str | None = None,
    id_col: str = "unique_id",
    date_col: str = "ds",
    target_col: str = "target",
    new_ids: Iterable[str] | None = None
) -> pd.DataFrame:
    """Wrapper of cross_validate_models to not expose ModelConfig, TFCModels, etc.

    Args:
        train_df (pd.DataFrame): _description_
        fcds (list[dt.date  |  dt.datetime]): _description_
        model (TFCModels): _description_
        horizon (int): _description_
        freq (str): _description_
        add_holidays (bool, optional): _description_. Defaults to False.
        add_events (bool, optional): _description_. Defaults to False.
        country_isocode (str | None, optional): _description_. Defaults to None.
        future_variables (list[str] | None, optional): _description_. Defaults to None.
        historical_variables (list[str] | None, optional): _description_. Defaults to None.
        static_variables (list[str] | None, optional): _description_. Defaults to None.
        max_concurrent (int, optional): _description_. Defaults to 100.
        max_retries (int, optional): _description_. Defaults to 5.
        api_key (str | None, optional): _description_. Defaults to None.
        url (str | None, optional): _description_. Defaults to None.
        id_col (str, optional): _description_. Defaults to "unique_id".
        date_col (str, optional): _description_. Defaults to "ds".
        target_col (str, optional): _description_. Defaults to "target".

    Returns:
        pd.DataFrame: _description_
    """
    return cross_validate_models(
        train_df,
        fcds,
        models=[
            ModelConfig(
                model=model,
                add_holidays=add_holidays,
                add_events=add_events,
                country_isocode=country_isocode,
                future_variables=future_variables,
                historical_variables=historical_variables,
                static_variables=static_variables,
            )
        ],
        horizon=horizon,
        freq=freq,
        max_concurrent=max_concurrent,
        max_retries=max_retries,
        api_key=api_key,
        url=url,
        id_col=id_col,
        date_col=date_col,
        target_col=target_col,
        new_ids=new_ids,
    )
