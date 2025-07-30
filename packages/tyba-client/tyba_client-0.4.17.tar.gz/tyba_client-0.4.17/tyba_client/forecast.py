from datetime import datetime, time
from typing import List, Optional


class Forecast(object):
    """-"""
    def __init__(self, client):
        self.client = client

    def get(self, route, params=None):
        response = self.client.get(f"forecasts/{route}", params=params)
        response.raise_for_status()
        return response.json()

    def most_recent(
        self,
        object_name: str,
        product: str,
        start_time: datetime,
        end_time: datetime,
        forecast_type=None,
        predictions_per_hour=None,
        prediction_lead_time_mins=None,
        horizon_mins=None,
    ):
        """

        :param object_name:
        :param product:
        :param start_time:
        :param end_time:
        :param forecast_type:
        :param predictions_per_hour:
        :param prediction_lead_time_mins:
        :param horizon_mins:
        :return:
        """
        return self.get(
            "most_recent_forecast",
            params={
                "object_name": object_name,
                "product": product,
                "start_time": start_time,
                "end_time": end_time,
                "forecast_type": forecast_type,
                "predictions_per_hour": predictions_per_hour,
                "prediction_lead_time_mins": prediction_lead_time_mins,
                "horizon_mins": horizon_mins,
            },
        )

    def most_recent_probabilistic(
        self,
        object_name: str,
        product: str,
        start_time: datetime,
        end_time: datetime,
        quantiles: List[float],
        forecast_type=None,
        predictions_per_hour=None,
        prediction_lead_time_mins=None,
        horizon_mins=None,

    ):
        """

        :param object_name:
        :param product:
        :param start_time:
        :param end_time:
        :param quantiles:
        :param forecast_type:
        :param predictions_per_hour:
        :param prediction_lead_time_mins:
        :param horizon_mins:
        :return:
        """
        return self.get(
            "most_recent_probabilistic_forecast",
            params={
                "object_name": object_name,
                "product": product,
                "start_time": start_time,
                "end_time": end_time,
                "quantiles": quantiles,
                "forecast_type": forecast_type,
                "predictions_per_hour": predictions_per_hour,
                "prediction_lead_time_mins": prediction_lead_time_mins,
                "horizon_mins": horizon_mins,
            },
        )

    def vintaged(
        self,
        object_name: str,
        product: str,
        start_time: datetime,
        end_time: datetime,
        days_ago: int,
        before_time: time,
        exact_vintage: bool = False,
        forecast_type=None,
        predictions_per_hour=None,
        prediction_lead_time_mins=None,
        horizon_mins=None,
    ):
        """

        :param object_name:
        :param product:
        :param start_time:
        :param end_time:
        :param days_ago:
        :param before_time:
        :param exact_vintage:
        :param forecast_type:
        :param predictions_per_hour:
        :param prediction_lead_time_mins:
        :param horizon_mins:
        :return:
        """
        return self.get(
            "vintaged_forecast",
            params={
                "object_name": object_name,
                "product": product,
                "start_time": start_time,
                "end_time": end_time,
                "days_ago": days_ago,
                "before_time": before_time,
                "exact_vintage": exact_vintage,
                "forecast_type": forecast_type,
                "predictions_per_hour": predictions_per_hour,
                "prediction_lead_time_mins": prediction_lead_time_mins,
                "horizon_mins": horizon_mins,
            },
        )

    def vintaged_probabilistic(
        self,
        object_name: str,
        product: str,
        start_time: datetime,
        end_time: datetime,
        quantiles: List[float],
        days_ago: int,
        before_time: time,
        exact_vintage: bool = False,
        forecast_type=None,
        predictions_per_hour=None,
        prediction_lead_time_mins=None,
        horizon_mins=None,
    ):
        """

        :param object_name:
        :param product:
        :param start_time:
        :param end_time:
        :param quantiles:
        :param days_ago:
        :param before_time:
        :param exact_vintage:
        :param forecast_type:
        :param predictions_per_hour:
        :param prediction_lead_time_mins:
        :param horizon_mins:
        :return:
        """
        return self.get(
            "vintaged_probabilistic_forecast",
            params={
                "object_name": object_name,
                "product": product,
                "start_time": start_time,
                "end_time": end_time,
                "quantiles": quantiles,
                "days_ago": days_ago,
                "before_time": before_time,
                "exact_vintage": exact_vintage,
                "forecast_type": forecast_type,
                "predictions_per_hour": predictions_per_hour,
                "prediction_lead_time_mins": prediction_lead_time_mins,
                "horizon_mins": horizon_mins,
            },
        )

    def by_vintage(
        self,
        object_name: str,
        product: str,
        vintage_start_time: datetime,
        vintage_end_time: datetime,
        forecast_type=None,
        predictions_per_hour=None,
        prediction_lead_time_mins=None,
        horizon_mins=None,
    ):
        """

        :param object_name:
        :param product:
        :param vintage_start_time:
        :param vintage_end_time:
        :param forecast_type:
        :param predictions_per_hour:
        :param prediction_lead_time_mins:
        :param horizon_mins:
        :return:
        """
        return self.get(
            "forecasts_by_vintage",
            params={
                "object_name": object_name,
                "product": product,
                "start_time": vintage_start_time,
                "end_time": vintage_end_time,
                "forecast_type": forecast_type,
                "predictions_per_hour": predictions_per_hour,
                "prediction_lead_time_mins": prediction_lead_time_mins,
                "horizon_mins": horizon_mins,
            },
        )

    def by_vintage_probabilistic(
        self,
        object_name: str,
        product: str,
        quantiles: List[float],
        vintage_start_time: datetime,
        vintage_end_time: datetime,
        forecast_type=None,
        predictions_per_hour=None,
        prediction_lead_time_mins=None,
        horizon_mins=None,
    ):
        """

        :param object_name:
        :param product:
        :param quantiles:
        :param vintage_start_time:
        :param vintage_end_time:
        :param forecast_type:
        :param predictions_per_hour:
        :param prediction_lead_time_mins:
        :param horizon_mins:
        :return:
        """
        return self.get(
            "probabilistic_forecasts_by_vintage",
            params={
                "object_name": object_name,
                "product": product,
                "quantiles": quantiles,
                "start_time": vintage_start_time,
                "end_time": vintage_end_time,
                "forecast_type": forecast_type,
                "predictions_per_hour": predictions_per_hour,
                "prediction_lead_time_mins": prediction_lead_time_mins,
                "horizon_mins": horizon_mins,
            },
        )

    def actuals(
        self, object_name: str, product: str, start_time: datetime, end_time: datetime,
        predictions_per_hour: Optional[int] = None
    ):
        """

        :param object_name:
        :param product:
        :param start_time:
        :param end_time:
        :return:
        """
        return self.get(
            "actuals",
            params={
                "object_name": object_name,
                "product": product,
                "start_time": start_time,
                "end_time": end_time,
                "predictions_per_hour": predictions_per_hour,
            },
        )
