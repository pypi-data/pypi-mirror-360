import logging
import time
from typing import Any, Dict, Optional

import requests
from kumoapi.online_serving import (
    OnlinePredictionOptions,
    OnlineServingEndpointRequest,
    OnlineServingStatusCode,
)

from kumoai import global_state
from kumoai.experimental.rfm.local_graph import LocalGraph
from kumoai.trainer.online_serving import (
    OnlineServingEndpoint,
    OnlineServingEndpointFuture,
)

logger = logging.getLogger(__name__)

DEFAULT_GRAPH_NAME = "rfm_byoc_graph"


class KumoRFM:
    r"""The :class:`KumoRFM` class is an interface to the Kumo Relational
    Foundation model (RFM), see
    `KumoRFM <https://kumo.ai/research/kumo_relational_foundation_model.pdf>`_.

    KumoRFM is a relational foundation model, which can make generate
    predicitons in context for any relational dataset. The model is pretrained
    and the class provides an interface to query the model.

    The class is constructed from a :class:`LocalGraph` object.

    Example:
        .. code-block:: python

            # raw data
            df_users = pd.DataFrame(...)
            df_items = pd.DataFrame(...)
            df_transactions = pd.DataFrame(...)

            # construct LocalGraph from raw data
            graph = LocalGraph.from_data(
                {
                    'users': df_users,
                    'items': df_items,
                    'transactions': df_transactions,
                }
            )

            # start KumoRFM with this graph
            rfm = KumoRFM(graph)

            # query the model
            query_str = ("PREDICT COUNT(transactions.*, 0, 30, days) > 0 "
                         "FOR users.user_id=1")
            result = rfm.query(query_str)
            # Result is a pandas DataFrame with prediction probabilities
            print(result)  # user_id  COUNT(transactions.*, 0, 30, days) > 0
                           # 1        0.85

    """  # noqa: E501

    def __init__(self, graph: LocalGraph,
                 endpoint: Optional[OnlineServingEndpoint] = None) -> None:
        self.graph = graph
        self._endpoint: Optional[OnlineServingEndpoint] = endpoint
        self._endpoint_future: Optional[OnlineServingEndpointFuture] = None

        if self._endpoint is None:
            self._start()

    def query(
        self,
        query: str,
        wait_result_timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """Query the RFM model with a query string

        Args:
            query: The RFM query string
            (e.g., "PREDICT COUNT(orders.*, 0, 30, days) > 0 "
            "FOR users.user_id=1")
            wait_result_timeout: Timeout in seconds to wait for the result

        Returns:
            Dictionary containing the prediction result
        """  # noqa: E501
        # Ensure endpoint is ready
        if not self._endpoint:
            try:
                if self._endpoint_future:
                    logger.info("Waiting for endpoint to be ready...")
                    self._endpoint = self._endpoint_future.result()
                else:
                    raise RuntimeError("Endpoint not initialized")
            except Exception as e:
                raise RuntimeError("Failed to get endpoint result") from e

        # Execute query via direct HTTP request to predict endpoint
        payload = {"query": query, 'wait_result_timeout': wait_result_timeout}

        resp = requests.post(self._endpoint._predict_url,
                             headers=global_state.client._session.headers,
                             json=payload)

        resp.raise_for_status()
        result = resp.json()

        return result

    def shutdown(self) -> None:
        r"""Clean up resources by destroying the RFM endpoint.

        This method attempts to destroy the RFM endpoint if one exists.

        Example:
            .. code-block:: python

                rfm = KumoRFM(graph)
                rfm.wait_until_ready()
                # ... use RFM ...
                rfm.shutdown()  # Clean up endpoint when done
        """  # noqa: E501
        if self._endpoint:
            logger.info("Found endpoint for KumoRFM, destroying...")
            try:
                self._endpoint.destroy()
            except Exception as e:
                logger.error(f"Failed to destroy endpoint: {e}")
        else:
            logger.info("No endpoint found, skipping...")

    def poll_status(self) -> Optional[OnlineServingStatusCode]:
        """Poll the current status of the RFM endpoint.

        Returns:
            The current status code of the endpoint, or None if no endpoint
            exists.

            Possible values:

            - OnlineServingStatusCode.IN_PROGRESS:
              Endpoint is being created/updated
            - OnlineServingStatusCode.READY: Endpoint is ready for queries
            - OnlineServingStatusCode.FAILED: Endpoint creation/update failed
        """
        if not self._endpoint_future:
            logger.info("Endpoint creation not started yet, "
                        "make sure to call _start() first")
            return None

        # Get the endpoint resource to check current status
        endpoint_api = global_state.client.online_serving_endpoint_api
        res = endpoint_api.get_if_exists(self._endpoint_future.id)

        if res is None:
            return None

        return res.status.status_code

    def is_ready(self) -> bool:
        """Check if the RFM endpoint is ready for queries.

        Returns:
            True if the endpoint is ready, False otherwise.
        """
        status = self.poll_status()
        return status == OnlineServingStatusCode.READY

    def wait_until_ready(self, timeout: Optional[float] = None,
                         sleep_interval: float = 10.0) -> None:
        """Wait until the RFM endpoint is ready.

        Args:
            timeout: Maximum time to wait in seconds. If None,
                waits indefinitely.
            sleep_interval: Time to sleep between polls in seconds.

        Raises:
            TimeoutError: If the endpoint is not ready within the
                timeout period.
            RuntimeError: If the endpoint failed to start.
        """
        start_time = time.time()

        if not self._endpoint_future:
            raise RuntimeError("Endpoint creation not started yet, "
                               "make sure to call _start() first")

        while True:
            endpoint_api = global_state.client.online_serving_endpoint_api
            res = endpoint_api.get_if_exists(self._endpoint_future.id)

            if res is None:
                raise RuntimeError("Endpoint resource not found")

            status = res.status.status_code

            if status == OnlineServingStatusCode.READY:
                logger.info(
                    "RFM endpoint is ready. Details:\n"
                    f"ID: {self._endpoint_future.id}\n"
                    f"URL: {res.endpoint_url}\n"
                    f"Launched at: {res.launched_at}\n"
                    f"Config: {res.config}\n"
                    f"Status: {res.status}\n"
                    f"Update status: {res.update if res.update else 'None'}")
                self._endpoint = self._endpoint_future.result()
                return
            elif status == OnlineServingStatusCode.FAILED:
                raise RuntimeError("RFM endpoint failed to start")
            elif timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"RFM endpoint not ready within {timeout} seconds")
            else:
                logger.info(
                    f"RFM endpoint not ready yet. Current status: {status}. ")

            time.sleep(sleep_interval)

    def _start(self) -> None:
        """Initialize KumoRFM by uploading data and creating endpoint"""
        self.graph.validate()
        kumo_graph = self.graph.to_kumo_graph()
        # skip validation as we validate the graph manually
        kumo_graph.save(DEFAULT_GRAPH_NAME, skip_validation=True)
        self._endpoint_future = self._create_endpoint()

    def _create_endpoint(self) -> OnlineServingEndpointFuture:
        """Create online serving endpoint for RFM"""
        endpoint_api = global_state.client.online_serving_endpoint_api

        request = OnlineServingEndpointRequest(
            model_training_job_id='FOUNDATION_MODEL',
            predict_options=OnlinePredictionOptions(),
        )

        # TODO(blaz): fix when we allow multiple graphs
        endpoint_id = endpoint_api.create(
            request,
            graph_name=DEFAULT_GRAPH_NAME,
            use_ge=False,
        )

        return OnlineServingEndpointFuture(endpoint_id)
