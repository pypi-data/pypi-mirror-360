"""
Copyright 2020 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
import datetime as dt
from enum import Enum
from typing import Optional, Union, List

import pandas as pd
import numpy as np
import math
from pandas.tseries.offsets import BDay
from pydash import decapitalize

from gs_quant.api.gs.data import QueryType, GsDataApi, DataQuery
from gs_quant.data.core import DataContext
from gs_quant.entities.entity import EntityType
from gs_quant.errors import MqValueError
from gs_quant.markets.portfolio_manager import PortfolioManager
from gs_quant.markets.report import FactorRiskReport, PerformanceReport, ThematicReport, ReturnFormat, \
    format_aum_for_return_calculation, get_pnl_percent, get_factor_pnl_percent_for_single_factor
from gs_quant.models.risk_model import FactorRiskModel
from gs_quant.target.reports import PositionSourceType
from gs_quant.timeseries import plot_measure_entity
from gs_quant.timeseries.algebra import geometrically_aggregate
from gs_quant.timeseries.measures import _extract_series_from_df, SecurityMaster, AssetIdentifier


class Unit(Enum):
    NOTIONAL = 'Notional'
    PERCENT = 'Percent'


@plot_measure_entity(EntityType.REPORT, [QueryType.FACTOR_EXPOSURE])
def factor_exposure(report_id: str, factor_name: str, unit: str = 'Notional', *, source: str = None,
                    real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Factor exposure data associated with a factor in a factor risk report

    :param report_id: factor risk report id
    :param factor_name: factor name
    :param unit: unit in which the timeseries is returned (Notional or Percent)
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of factor exposure for requested factor
    """
    return _get_factor_data(report_id, factor_name, QueryType.FACTOR_EXPOSURE, Unit(unit))


@plot_measure_entity(EntityType.REPORT, [QueryType.FACTOR_PNL])
def factor_pnl(report_id: str, factor_name: str, unit: str = 'Notional', *, source: str = None,
               real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Factor PnL data associated with a factor in a factor risk report

    :param report_id: factor risk report id
    :param factor_name: factor name
    :param unit: unit in which the timeseries is returned (Notional or Percent)
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of factor pnl for requested factor
    """
    return _get_factor_data(report_id, factor_name, QueryType.FACTOR_PNL, Unit(unit))


@plot_measure_entity(EntityType.REPORT, [QueryType.FACTOR_PROPORTION_OF_RISK])
def factor_proportion_of_risk(report_id: str, factor_name: str, *, source: str = None,
                              real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Factor proportion of risk data associated with a factor in a factor risk report

    :param report_id: factor risk report id
    :param factor_name: factor name
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of factor proportion of risk for requested factor
    """
    return _get_factor_data(report_id, factor_name, QueryType.FACTOR_PROPORTION_OF_RISK)


@plot_measure_entity(EntityType.REPORT, [QueryType.DAILY_RISK])
def daily_risk(report_id: str, factor_name: str = 'Total', *, source: str = None,
               real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Daily risk data associated with a factor in a factor risk report

    :param report_id: factor risk report id
    :param factor_name: factor name (must be "Factor", "Specific", or "Total")
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of daily risk for requested factor
    """
    return _get_factor_data(report_id, factor_name, QueryType.DAILY_RISK)


@plot_measure_entity(EntityType.REPORT, [QueryType.ANNUAL_RISK])
def annual_risk(report_id: str, factor_name: str = 'Total', *, source: str = None,
                real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Annual risk data associated with a factor in a factor risk report

    :param report_id: factor risk report id
    :param factor_name: factor name (must be "Factor", "Specific", or "Total")
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of daily risk for requested factor
    """
    return _get_factor_data(report_id, factor_name, QueryType.ANNUAL_RISK)


@plot_measure_entity(EntityType.REPORT, [QueryType.PNL])
def normalized_performance(report_id: str, leg: str = None, *, source: str = None,
                           real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Returns the Normalized Performance of a performance report based on AUM source
    :param report_id: id of performance report
    :param leg: short or long
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio normalized performance

    **Usage**

    Returns the normalized performance of the portfolio.

    :math:`NP(L/S)_{t} = SUM( PNL(L/S)_{t}/ ( EXP(L/S)_{t} ) - cPNL(L/S)_{t-1) )
        if ( EXP(L/S)_{t} ) > 0
        else:
            1/ SUM( PNL(L/S)_{t}/ ( EXP(L/S)_{t} ) - cPNL(L/S)_{t-1) )`
    For each leg, short and long, then:
    :math:`NP_{t} = NP(L)_{t} * SUM(EXP(L)) / SUM(GROSS_EXP) + NP(S)_{t} * SUM(EXP(S)) / SUM(GROSS_EXP) + 1`

    If leg is short, set SUM(EXP(L)) to 0, if leg is long, set SUM(EXP(S)) to 0

    where :math:`cPNL(L/S)_{t-1}` is your performance reports cumulative long or short PNL at date t-1
    where :math:`PNL(L/S)_{t}` is your performance reports long or short pnl at date t
    where :math:`GROSS_EXP_{t}` is portfolio gross exposure on date t
    where :math:`EXP(L/S)_{t}` is the long or short exposure on date t

    """
    start_date = DataContext.current.start_time
    end_date = DataContext.current.end_time

    start_date = (start_date - BDay(1)).date()
    end_date = end_date.date()

    performance_report = PerformanceReport.get(report_id)

    constituent_data = performance_report.get_portfolio_constituents(
        fields=['assetId', 'pnl', 'quantity', 'netExposure'], start_date=start_date, end_date=end_date).set_index(
        'date')

    if leg:
        if leg.lower() == "long":
            constituent_data = constituent_data[constituent_data['quantity'] > 0]
        if leg.lower() == "short":
            constituent_data = constituent_data[constituent_data['quantity'] < 0]

    # Split into long and short and aggregate across dates
    long_side = _return_metrics(constituent_data[constituent_data['quantity'] > 0],
                                list(constituent_data.index.unique()), "long")
    short_side = _return_metrics(constituent_data[constituent_data['quantity'] < 0],
                                 list(constituent_data.index.unique()), "short")

    short_exposure = sum(abs(short_side['exposure']))
    long_exposure = sum(long_side['exposure'])
    gross_exposure = short_exposure + long_exposure

    long_side['longRetWeighted'] = (long_side['longMetrics'] - 1) * (long_exposure / gross_exposure)
    short_side['shortRetWeighted'] = (short_side['shortMetrics'] - 1) * (short_exposure / gross_exposure)

    combined = long_side[['longRetWeighted']].join(short_side[['shortRetWeighted']], how='inner')
    combined['normalizedPerformance'] = combined['longRetWeighted'] + combined['shortRetWeighted'] + 1
    return pd.Series(combined['normalizedPerformance'], name="normalizedPerformance").dropna()


@plot_measure_entity(EntityType.REPORT, [QueryType.PNL])
def long_pnl(report_id: str, *, source: str = None,
             real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    PNL from long holdings

    :param report_id: id of performance report
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio long pnl
    """
    start_date = DataContext.current.start_time.date()
    end_date = DataContext.current.end_time.date()
    performance_report = PerformanceReport.get(report_id)

    constituent_data = performance_report.get_portfolio_constituents(
        fields=['pnl', 'quantity'], start_date=start_date, end_date=end_date).set_index('date')
    long_leg = constituent_data[constituent_data['quantity'] > 0]['pnl']
    long_leg = long_leg.groupby(level=0).sum()
    return pd.Series(long_leg, name="longPnl")


@plot_measure_entity(EntityType.REPORT, [QueryType.PNL])
def short_pnl(report_id: str, *, source: str = None,
              real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """

    PNL from short holdings
    :param report_id: id of performance report
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio short pnl
    """
    start_date = DataContext.current.start_time.date()
    end_date = DataContext.current.end_time.date()
    performance_report = PerformanceReport.get(report_id)

    constituent_data = performance_report.get_portfolio_constituents(
        fields=['pnl', 'quantity'], start_date=start_date, end_date=end_date).set_index('date')
    short_leg = constituent_data[constituent_data['quantity'] < 0]['pnl']
    short_leg = short_leg.groupby(level=0).sum()
    return pd.Series(short_leg, name="shortPnl")


@plot_measure_entity(EntityType.REPORT, [QueryType.THEMATIC_EXPOSURE])
def thematic_exposure(report_id: str, basket_ticker: str, *, source: str = None,
                      real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Thematic exposure of a portfolio to a requested GS thematic flagship basket

    :param report_id: portfolio thematic analytics report id
    :param basket_ticker: ticker for thematic basket
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of daily thematic beta of portfolio to requested flagship basket
    """
    thematic_report = ThematicReport.get(report_id)
    asset = SecurityMaster.get_asset(basket_ticker, AssetIdentifier.TICKER)
    df = thematic_report.get_thematic_exposure(start_date=DataContext.current.start_date,
                                               end_date=DataContext.current.end_date,
                                               basket_ids=[asset.get_marquee_id()])
    if not df.empty:
        df = df.set_index('date')
        df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, QueryType.THEMATIC_EXPOSURE)


@plot_measure_entity(EntityType.REPORT, [QueryType.THEMATIC_EXPOSURE])
def thematic_beta(report_id: str, basket_ticker: str, *, source: str = None,
                  real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Thematic beta values of a portfolio to a requested GS thematic flagship basket

    :param report_id: portfolio thematic analytics report id
    :param basket_ticker: ticker for thematic basket
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of daily thematic beta of portfolio to requested flagship basket
    """
    thematic_report = ThematicReport.get(report_id)
    asset = SecurityMaster.get_asset(basket_ticker, AssetIdentifier.TICKER)
    df = thematic_report.get_thematic_betas(start_date=DataContext.current.start_date,
                                            end_date=DataContext.current.end_date,
                                            basket_ids=[asset.get_marquee_id()])
    if not df.empty:
        df = df.set_index('date')
        df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, QueryType.THEMATIC_BETA)


@plot_measure_entity(EntityType.REPORT, [QueryType.AUM])
def aum(report_id: str, *, source: str = None,
        real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    AUM of the portfolio

    :param report_id: id of performance report
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio long pnl
    """
    start_date = DataContext.current.start_time.date()
    end_date = DataContext.current.end_time.date()
    performance_report = PerformanceReport.get(report_id)
    aum_curve = performance_report.get_aum(start_date=start_date, end_date=end_date)
    aum_dict = [{'date': key, 'aum': aum_curve[key]} for key in aum_curve]

    # Create and return timeseries
    df = pd.DataFrame(aum_dict)
    if not df.empty:
        df = df.set_index('date')
        df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, QueryType.AUM)


@plot_measure_entity(EntityType.REPORT, [QueryType.PNL])
def pnl(report_id: str, unit: str = 'Notional', *, source: str = None,
        real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    PNL from all holdings, if unit is Percent, geometrically aggregate over time frame

    :param report_id: id of performance report
    :param unit: by default uses mode as Notional, but can also be set to Percent
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio pnl
    """
    start_date = DataContext.current.start_time.date()
    end_date = DataContext.current.end_time.date()
    performance_report = PerformanceReport.get(report_id)
    pnl_df = performance_report.get_pnl(start_date, end_date)

    if unit == Unit.PERCENT.value:
        return get_pnl_percent(performance_report, pnl_df, 'pnl', start_date, end_date)
    else:
        pnl_df = pnl_df.set_index('date')
        return pd.Series(pnl_df['pnl'], name="pnl")


@plot_measure_entity(EntityType.REPORT)
def historical_simulation_estimated_pnl(report_id: str, *, source: str = None,
                                        real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Estimated Pnl from replaying a historical simulation scenario on your latest positions
    :param report_id: id of performance report
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio estimated pnl
    """

    factor_attributed_pnl = _replay_historical_factor_moves_on_latest_positions(report_id, [])
    total_factor_attributed_pnl = factor_attributed_pnl.apply(np.sum, axis=1).to_frame("estimatedPnl")

    total_factor_attributed_pnl.index = pd.to_datetime(total_factor_attributed_pnl.index)
    return total_factor_attributed_pnl.squeeze()


@plot_measure_entity(EntityType.REPORT)
def historical_simulation_estimated_factor_attribution(report_id: str, factor_name: str, *, source: str = None,
                                                       real_time: bool = False,
                                                       request_id: Optional[str] = None) -> pd.Series:
    """
    Estimated Pnl attributed to the factor after replaying a historical simulation scenario on a portfolio's latest
    positions
    :param report_id: id of performance report
    :param factor_name: name of the factor
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: portfolio estimated pnl
    """

    factor_attributed_pnl = _replay_historical_factor_moves_on_latest_positions(report_id, [factor_name])
    factor_attributed_pnl.index = pd.to_datetime(factor_attributed_pnl.index)

    return factor_attributed_pnl.squeeze()


def _replay_historical_factor_moves_on_latest_positions(report_id: str, factors: List[str]) -> \
        Union[pd.Series, pd.DataFrame]:
    start_date = DataContext.current.start_time.date()
    end_date = DataContext.current.end_time.date()
    risk_report = FactorRiskReport.get(report_id)
    risk_model_id = risk_report.get_risk_model_id()

    # Get data in batches of 365 days
    date_range = pd.bdate_range(start_date, end_date)
    batches = np.array_split([d.date() for d in date_range.tolist()], math.ceil(len(date_range.tolist()) / 365))
    data_query_results = []
    query = {"riskModel": risk_model_id}
    if factors:
        query.update({"factor": factors})
    for batch in batches:
        data_query_results += GsDataApi.execute_query(
            'RISK_MODEL_FACTOR',
            DataQuery(
                where=query,
                start_date=batch[0],
                end_date=batch[-1]
            )
        ).get('data', [])

    return_data = pd.DataFrame(data_query_results).pivot(columns="factor", index="date", values="return").sort_index()
    return_data_aggregated = (return_data / 100).apply(geometrically_aggregate)

    latest_report_date = risk_report.latest_end_date
    factor_exposures = risk_report.get_results(
        start_date=latest_report_date,
        end_date=latest_report_date,
        return_format=ReturnFormat.JSON
    )
    factor_exposure_df = pd.DataFrame(factor_exposures).pivot(columns="factor",
                                                              index="date",
                                                              values="exposure").sort_index()

    factor_exposure_df = factor_exposure_df.reindex(columns=return_data_aggregated.columns)
    factor_attributed_pnl_values = return_data_aggregated.values * factor_exposure_df.values
    factor_attributed_pnl = pd.DataFrame(factor_attributed_pnl_values, index=return_data_aggregated.index,
                                         columns=return_data_aggregated.columns)

    return factor_attributed_pnl


def _get_factor_data(report_id: str, factor_name: str, query_type: QueryType, unit: Unit = Unit.NOTIONAL) -> pd.Series:
    # Check params
    report = FactorRiskReport.get(report_id)
    if factor_name not in ['Factor', 'Specific', 'Total']:
        if query_type in [QueryType.DAILY_RISK, QueryType.ANNUAL_RISK]:
            raise MqValueError('Please pick a factor name from the following: ["Total", "Factor", "Specific"]')
        model = FactorRiskModel.get(report.get_risk_model_id())
        factor = model.get_factor(factor_name)
        factor_name = factor.name

    # Extract relevant data for each date
    col_name = query_type.value.replace(' ', '')
    col_name = decapitalize(col_name)
    data_type = decapitalize(col_name[6:]) if col_name.startswith('factor') else col_name
    include_total_factor = factor_name != 'Total' and unit == Unit.PERCENT and query_type == QueryType.FACTOR_PNL
    factors_to_query = [factor_name, 'Total'] if include_total_factor else [factor_name]
    factor_data = report.get_results(
        factors=factors_to_query,
        start_date=DataContext.current.start_date,
        end_date=DataContext.current.end_date,
        return_format=ReturnFormat.JSON
    )
    total_data = [d for d in factor_data if d.get(data_type) is not None and d.get('factor') == 'Total']
    factor_data = [d for d in factor_data if d.get(data_type) is not None and d.get('factor') == factor_name]
    if unit == Unit.PERCENT:
        if report.position_source_type != PositionSourceType.Portfolio:
            raise MqValueError('Unit can only be set to percent for portfolio reports')
        pm = PortfolioManager(report.position_source_id)
        tags = dict((tag.name, tag.value) for tag in report.parameters.tags) if report.parameters.tags else None
        performance_report = pm.get_performance_report(tags=tags)
        start_date = dt.datetime.strptime(min([d['date'] for d in factor_data]), '%Y-%m-%d').date()
        end_date = dt.datetime.strptime(max([d['date'] for d in factor_data]), '%Y-%m-%d').date()
        if query_type == QueryType.FACTOR_PNL:
            # Factor Pnl needs to be geometrically aggregated if unit is %
            aum_df = format_aum_for_return_calculation(performance_report, start_date, end_date)
            return get_factor_pnl_percent_for_single_factor(factor_data, total_data, aum_df, start_date)
        else:
            aum = performance_report.get_aum(start_date=start_date, end_date=end_date)
            for data in factor_data:
                if aum.get(data['date']) is None:
                    raise MqValueError('Cannot convert to percent: Missing AUM on some dates in the date range')
            factor_exposures = [{
                'date': d['date'],
                col_name: d[data_type] / aum.get(d['date']) * 100
            } for d in factor_data]
    else:
        factor_exposures = [{'date': d['date'], col_name: d[data_type]} for d in factor_data]

    # Create and return timeseries
    df = pd.DataFrame(factor_exposures)
    if not df.empty:
        df = df.set_index('date')
        df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, query_type)


def _return_metrics(one_leg: pd.DataFrame, dates: list, name: str):
    if one_leg.empty:
        return pd.DataFrame(index=dates, data={f'{name}Metrics': [0 for d in dates], "exposure": [0 for d in dates]})
    one_leg = one_leg.groupby(one_leg.index).agg(pnl=('pnl', 'sum'), exposure=('netExposure', 'sum'))

    one_leg['cumulativePnl'] = one_leg['pnl'].cumsum(axis=0)

    one_leg['normalizedExposure'] = (one_leg['exposure'] - one_leg['cumulativePnl'])
    one_leg.iloc[0, one_leg.columns.get_loc('cumulativePnl')] = 0
    one_leg[f'{name}Metrics'] = one_leg['cumulativePnl'] / one_leg['normalizedExposure'] + 1

    one_leg[f'{name}Metrics'] = 1 / one_leg[f'{name}Metrics'] if one_leg['exposure'].iloc[-1] < 0 else one_leg[
        f'{name}Metrics']
    return one_leg
