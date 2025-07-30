'''import mlflow
from mlflow import MlflowClient
from mlflow.pyfunc.model import PythonModel
from mlflow.pyfunc import log_model'''

from .local_learner import LLFactoryProtocol, LLProtocol
from .aggregator import AggFactoryProtocol, AggProtocol
from .default_create_functions import default_create_local_learner, default_create_aggregator

from typing import Literal
import os
import warnings


class FederatedModel():
    """
    A class for creating a federated learning model and its aggregator. If no aggregator is provided
    the PlainAVGAggregator is passed as default

    This class encapsulates the local learner, the aggregation strategy, and their respective names.
    It is designed to facilitate the integration of these components into the MLflow tracking system.

    Attributes:
        aggregator (AggFactoryProtocol): The aggregation strategy for federated learning.
        aggregator_name (str): The name of the aggregation strategy (default is "PlainAVG").
        local_learner (LLFactoryProtocol): The local learner factory for creating model instances.
        model_name (str): The name of the model to be registered in MLflow.
    """
    def __init__(self, create_local_learner: LLFactoryProtocol = default_create_local_learner,
                  model_name: str = "Default_iris_model", 
                  create_aggregator: AggFactoryProtocol = default_create_aggregator,
                  aggregator_name: str = "PlainAVG"
                  ) -> None:
        self.create_aggregator = create_aggregator
        self.aggregator_name = aggregator_name
        self.create_local_learner = create_local_learner
        self.model_name = model_name



'''def submit_fl_model(model: FederatedModel,
                    platform_url: str,
                    username: str,
                    password: str,
                    experiment_name: str,
                    disease: Literal["AML", "SCD"],
                    trained: bool) -> dict:
    """
    Submit the model and aggregation strategy to MLflow.

    This function logs the model and aggregator as artifacts, registers the model in MLflow,
    and ensures a new run is created in the specified experiment.

    Args:
        model (FederatedModel): The federated learning model to be submitted.
        platform_url (str): The URL of the MLflow tracking server.
        username (str): The username for authenticating with the MLflow tracking server.
        password (str): The password for authenticating with the MLflow tracking server.
        experiment_name (str): The name of the MLflow experiment to use or create.
        disease (Literal["AML", "SCD"]): The use case for the model.
        trained (bool): Indicates whether the model is already trained.

    Raises:
        RuntimeError: If the username or password is not provided.
    """
    # Ignore warnings about input example
    warnings.filterwarnings("ignore")

    # Check if username and password are provided
    if not username or not password:
        raise RuntimeError("Username and password must be provided.")
    # Check if the use case is valid
    assert disease in ["AML", "SCD"], "Disease must be either 'AML' or 'SCD'"

    os.environ['MLFLOW_TRACKING_USERNAME'] = username
    os.environ['MLFLOW_TRACKING_PASSWORD'] = password
    os.environ["MLFLOW_TRACKING_INSECURE_TLS"] = "true"

    MLFLOW_URL = platform_url
    mlflow.set_tracking_uri(MLFLOW_URL)

    # Test model and aggregator protocol
    model_instance = model.create_local_learner()
    aggregator_instance = model.create_aggregator()
    assert isinstance(model.create_aggregator, AggFactoryProtocol), "create_aggregator function does not conform to AggFactoryProtocol"
    assert isinstance(model.create_local_learner, LLFactoryProtocol), "create_local_learner function does not conform to LLFactoryProtocol"
    assert isinstance(model_instance, LLProtocol), "Local learner does not conform to LLProtocol" 
    assert isinstance(aggregator_instance, AggProtocol), "Aggregator instance does not conform to AggProtocol"
    
    # Ensure the experiment exists or create it
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = experiment.experiment_id


    # Start a new run
    with mlflow.start_run(experiment_id=experiment_id) as run:
        mlflow.set_tag("use_case", disease)
        mlflow.set_tag("trained", str(trained))
        if os.path.isdir("./src"):
            model_info = log_model(
                artifact_path="model",
                python_model=model,
                registered_model_name=model.model_name,
                code_paths=["src"],
            )
        else:
            model_info = log_model(
                artifact_path="model",
                python_model=model,
                registered_model_name=model.model_name,
            )
    mlflow_client = MlflowClient(tracking_uri=MLFLOW_URL)
    model_meta = mlflow_client.get_latest_versions(model.model_name, stages=["None"])
    version = model_meta[0].version
    # mlflow_client.update_model_version(model.model_name, version, description)
    tags = {"use_case": disease, "trained": str(trained)}
    for key, value in tags.items():
        mlflow_client.set_model_version_tag(model.model_name, version, key, value)
    # mlflow_client.set_experiment_tag(experiment_id, "use_case", disease)
    # mlflow_client.set_experiment_tag(experiment_id, "Trained", str(trained))
    return {
        "detail": f"Model '{model.model_name}' registered.",
        "model_uuid": model_info.model_uuid,
        "run_id": model_info.run_id,
        "model_uri": model_info.model_uri,
        }'''

