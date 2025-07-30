# Create your custom function defining a PyTorch-based model and returning its instance
def default_create_local_learner():
    import pandas as pd
    from torch import nn, optim
    from torch.utils.data import DataLoader, Dataset
    import torch
    import flwr

    from .src.utils import Utils # Dependency script stored inside the src directory
    
    class DefaultLocalLearner(nn.Module):
            def __init__(self, input_size: int) -> None:
                super(DefaultLocalLearner, self).__init__()
                self.linear = nn.Linear(input_size, 3)
                self.softmax = nn.Softmax(dim=1)
                self.loss_fn = nn.CrossEntropyLoss()
                self.optimizer = optim.Adam(self.parameters(), lr=0.001)

            def _forward(self, x):
                x = self.linear(x)
                return self.softmax(x)

            def get_parameters(self) -> flwr.common.ParametersRecord:
                return Utils.pytorch_to_parameter_record(self.state_dict())

            def set_parameters(self, parameters: flwr.common.ParametersRecord) -> None:
                self.load_state_dict(Utils.parameters_to_pytorch_state_dict(parameters))

            def prepare_data(self, data: pd.DataFrame) -> None:
                class IrisDataset(Dataset):
                    def __init__(self, dataframe: pd.DataFrame) -> None:
                        self.dataframe = dataframe
                        self.dataframe.loc[:, "class"] = dataframe.loc[:, "class"].replace(
                            {"Iris-setosa": 0, "Iris-versicolor": 1, "Iris-virginica": 2}
                        )

                    def __getitem__(self, idx: int):
                        x = self.dataframe.iloc[idx, :-1].to_numpy("float32")
                        y = torch.tensor(self.dataframe.iloc[idx, -1], dtype=torch.long)
                        return x, y

                    def __len__(self) -> int:
                        return len(self.dataframe)

                dataset = IrisDataset(data)
                dataloader = DataLoader(dataset, batch_size=32)
                self.dataloader = dataloader

            def train_round(self) -> flwr.common.MetricsRecord: # type: ignore
                for batch in self.dataloader:
                    x, y = batch
                    self.optimizer.zero_grad()
                    y_hat = self._forward(x)
                    loss = self.loss_fn(y_hat, y)
                    loss.backward()
                    self.optimizer.step()

                return flwr.common.MetricsRecord({"loss": loss.item()}) # type: ignore

            def evaluate(self) -> flwr.common.MetricsRecord:
                correct = 0
                total = 0
                with torch.no_grad():
                    for batch in self.dataloader:
                        x, y = batch
                        y_hat = self._forward(x)
                        _, predicted = torch.max(y_hat, 1)
                        total += y.size(0)
                        correct += (predicted == y).sum().item()
                return flwr.common.MetricsRecord({"accuracy": correct / total})
    
    return DefaultLocalLearner(4)


# Create your custom function defining an aggregation strategy and returning its instance
def default_create_aggregator():
    from collections import OrderedDict
    import numpy as np
    import flwr
    from typing import Optional

    from .src.utils import Utils # Dependency script stored inside the src directory

    class DefaultAggregator:

        def aggregate_parameters(self, results: list[flwr.common.ParametersRecord], config: Optional[flwr.common.ConfigsRecord]=None
            ) -> flwr.common.ParametersRecord:
                parameters = [Utils.parameters_to_dict(param) for param in results]
                keys = parameters[0].keys()
                result = OrderedDict()
                for key in keys:
                    # Init array
                    this_array: np.ndarray = np.zeros_like(parameters[0][key])
                    for p in parameters:
                        this_array += p[key]
                    result[key] = this_array / len(results)
                return Utils.dict_to_parameter_record(result)

        def aggregate_metrics(self, results: list[flwr.common.MetricsRecord], config: Optional[flwr.common.ConfigsRecord]=None) -> flwr.common.MetricsRecord:
                keys = results[0].keys()
                result = OrderedDict()
                for key in keys:
                    # Init array
                    cumsum = 0.0
                    for m in results:
                        if not isinstance(m[key], (int, float)):
                            raise ValueError(
                                f"flwr.common.MetricsRecord value type not supported: {type(m[key])}"
                            )
                        cumsum += m[key]  # type: ignore
                    result[key] = cumsum / len(results)
                return flwr.common.MetricsRecord(result)  # type: ignore
    
    return DefaultAggregator()