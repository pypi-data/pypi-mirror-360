from typing import Protocol, runtime_checkable

import pandas as pd
import flwr

@runtime_checkable
class LLProtocol(Protocol):
    """
    Protocol for defining a local learner in a federated learning setup.
    """

    def prepare_data(self, data: pd.DataFrame) -> None:
        """
        Prepares input data for training or evaluation.
        Args:
            data: Input data as a pandas DataFrame.
        """
        ...

    def train_round(self) -> flwr.common.MetricsRecord:
        """
        Trains the model and returns metrics.
        Returns:
            flwr.common.MetricsRecord: Performance metrics after training.
        """
        ...

    def get_parameters(self) -> flwr.common.ParametersRecord:
        """
        Retrieves the current model parameters.
        Returns:
            flwr.common.ParametersRecord: Current model parameters.
        """
        ...

    def set_parameters(self, parameters: flwr.common.ParametersRecord) -> None:
        """
        Sets the model parameters.
        Args:
            parameters: A flwr.common.ParametersRecord containing the parameters to set.
        """
        ...

    def evaluate(self) -> flwr.common.MetricsRecord:
        """
        Evaluates the model and returns performance metrics.
        Returns:
            flwr.common.MetricsRecord: Evaluation metrics.
        """
        ...

@runtime_checkable
class LLFactoryProtocol(Protocol):
    '''
    Protocol for the function creating the local learner instance
    '''
    def __call__(self) -> LLProtocol:
            """
            Creates and returns an instance of a class conforming to LLProtocol.
            """
            ...