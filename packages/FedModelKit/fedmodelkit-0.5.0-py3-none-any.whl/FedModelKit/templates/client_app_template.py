
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from flwr.client import ClientApp
from flwr.common import Message, Context
from flwr.common.record import RecordSet, MetricsRecord, ConfigsRecord
from sklearn.preprocessing import OneHotEncoder
import FedModelKit as msi

from model_example import create_local_learner #type: ignore[import]
from load_data import load_data #type: ignore[import]


# Initialize the Flower ClientApp
app = ClientApp()

@app.query()
def query(msg: Message, ctx: Context) -> Message:
    """
    Query function to be executed by the Flower client. This function handles the
    initial configuration sent by the server.
    """

    # Retrieve the configuration sent by the server
    fancy_config = msg.content.configs_records['fancy_config']

    # Load the client split data using the load_data function
    data = load_data(fancy_config['num_clients'], fancy_config['client_id'])

    # Instantiate the federated model
    federated_model = msi.FederatedModel(create_local_learner=create_local_learner, model_name='simple_lr')

    # Store the local learner and the data split in the context
    # To store in context other objects, you can use ctx.state.<object_name> = <object>
    ctx.state.local_learner = federated_model.create_local_learner()
    ctx.state.data = data
    ctx.state.undestand = "che succede"

    return msg.create_reply(RecordSet())

@app.train()
def train(msg: Message, ctx: Context):
    """
    Train function to be executed by the Flower client.
    This function handles the training of the local model using the data provided.
    """

    # Retrieve the local learner and the client split from the context
    local_learner = ctx.state.local_learner
    data = ctx.state.data

    # Retrieve configuration sent by the server - example
    #fancy_config = msg.content.configs_records['fancy_config']
    #local_epochs = fancy_config['local_epochs']

    # Retrieve the model parameters sent by the server
    fancy_parameters = msg.content.parameters_records['fancy_model']
    local_learner.set_parameters(fancy_parameters)    

    # Prepare the data using the local learner
    local_learner.prepare_data(data)

    # Perform local training and obtain training metrics
    train_metrics = local_learner.train_round()

    # Retrieve the trained model parameters
    new_parameters_records = local_learner.get_parameters()
    assert ctx.state.undestand.startswith("che"), "The context state is not being stored correctly"

    # Construct a reply message carrying updated model parameters and generated metrics
    reply_content = RecordSet()
    reply_content.parameters_records['fancy_model_returned'] = new_parameters_records
    reply_content.metrics_records['train_metrics'] = train_metrics

    # Store the metrics and the local learner in the context for future reference
    ctx.state.metrics_records['prev'] = train_metrics
    ctx.state.local_learner =  local_learner

    # Return the reply message to the server
    return msg.create_reply(reply_content)

@app.evaluate()
def eval(msg: Message, ctx: Context):
    """
    Evaluate function to be executed by the Flower client.
    This function handles the evaluation of the local model using the data provided.
    """

    # Retrieve the local learner and the client split from the context
    local_learner = ctx.state.local_learner
    data = ctx.state.data

    # Retrieve configuration sent by the server - example
    #fancy_config = msg.content.configs_records['fancy_config']
    #local_epochs = fancy_config['local_epochs']

    # Retrieve the model parameters sent by the server
    fancy_parameters = msg.content.parameters_records['fancy_model']
    local_learner.set_parameters(fancy_parameters)

    # Prepare the data using the local learner
    local_learner.prepare_data(data)

    # Evaluate the model and obtain evaluation metrics
    eval_metrics = local_learner.evaluate()

    # Construct a reply message with evaluation metrics
    reply_content = RecordSet()
    reply_content.metrics_records['eval_metrics'] = eval_metrics

    # Store the metrics and the local learner in the context for future reference
    ctx.state.metrics_records['prev'] = eval_metrics
    ctx.state.local_learner =  local_learner

    # Return the reply message to the server
    return msg.create_reply(reply_content)
