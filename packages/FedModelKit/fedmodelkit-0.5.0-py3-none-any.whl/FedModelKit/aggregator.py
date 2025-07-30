import flwr
from typing import Protocol, runtime_checkable
from typing import Protocol, Optional


@runtime_checkable
class AggProtocol(Protocol):
    """
    Defines the required structure for aggregation strategies in federated learning.
    """

    def aggregate_parameters(self, results: list[flwr.common.ParametersRecord], config: Optional[flwr.common.ConfigsRecord]=None) -> flwr.common.ParametersRecord: 
        """
        Aggregates model parameters from a list of clients.
        Args:
            results: List of `flwr.common.ParametersRecord` from clients.
        Returns:
            Aggregated `flwr.common.ParametersRecord`.
        """
        ...

    def aggregate_metrics(self, results: list[flwr.common.MetricsRecord], config: Optional[flwr.common.ConfigsRecord]=None) -> flwr.common.MetricsRecord: 
        """
        Aggregates metrics from a list of clients.
        Args:
            results: List of `flwr.common.MetricsRecord` from clients.
        Returns:
            Aggregated `flwr.common.MetricsRecord`.
        """
        ...

@runtime_checkable
class AggFactoryProtocol(Protocol):
    '''
    Protocol for the function creating the aggregator instance
    '''
    def __call__(self) -> AggProtocol:
        """
        Creates and returns an instance of a class conforming to AggProtocol.
        """
        ...
