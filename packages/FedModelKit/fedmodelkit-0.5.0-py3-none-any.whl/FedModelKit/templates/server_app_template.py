
from typing import List
import time

import flwr as fl
from flwr.common import (
    Context,
    NDArrays,
    Message,
    MessageType,
    Metrics,
    RecordSet,
    ConfigsRecord,
    DEFAULT_TTL,
)
from flwr.server import Driver

import FedModelKit as msi

from model_example import create_local_learner #type: ignore[import]


# Run via `flower-server-app server:app`
app = fl.server.ServerApp()




@app.main()
def main(driver: Driver, context: Context) -> None:
    """
    Main function to run the federated learning server.

    Structure:
    - Send a query message to clients for creating the local learner and loading the data
    - Start global epochs loop for training and evaluation
        - Send training messages to clients
        - Aggregate parameters received from clients
        - Send evaluation messages to clients
        - Aggregate evaluation metrics
    """
    print("Starting test run")

    # Get node IDs of connected clients
    node_ids = driver.get_node_ids()

    # Initialize the federated model
    federated_model = msi.FederatedModel(create_local_learner=create_local_learner,
                                        model_name='simple_lr')
    global_model = federated_model.create_local_learner()
    aggregation_strategy = federated_model.create_aggregator()

    # Send a query message to clients for creating the local learner and loading the data
    messages = []
    for idx, node_id in enumerate(node_ids):
        # Create messages to send to clients
        recordset = RecordSet()

        # Add a config with information to send the client for the query
        recordset.configs_records["fancy_config"] = ConfigsRecord({"num_clients": len(node_ids), "client_id": idx})

        # Create a query message for each client
        message = driver.create_message(
            content=recordset,
            message_type=MessageType.QUERY,
            dst_node_id=node_id,
            group_id=str(1),
            ttl=DEFAULT_TTL,
        )
        messages.append(message)

    # Send training messages to clients
    message_ids = driver.push_messages(messages)
    print(f"Pushed {len(list(message_ids))} messages: {message_ids}")

    # Wait for results from clients
    message_ids = [message_id for message_id in message_ids if message_id != ""]
    all_replies: List[Message] = []
    while True:
        replies = driver.pull_messages(message_ids=message_ids)
        print(f"Got {len(list(replies))} results")
        all_replies += replies
        if len(all_replies) == len(message_ids):
            break
        time.sleep(12)

    # Filter out messages with errors
    all_replies = [
        msg
        for msg in all_replies
        if msg.has_content()
    ]
    print(f"Received {len(all_replies)} answers")
    

    # Run federated training and evaluation for a fixed number of rounds
    for server_round in range(3):
        print(f"Commencing server train and evaluation round {server_round + 1}")

        messages = []
        for idx, node_id in enumerate(node_ids):
            # Create messages to send to clients
            recordset = RecordSet()

            # Add model parameters to record
            recordset.parameters_records["fancy_model"] = global_model.get_parameters()
            # Add a config with information to send the client for training
            recordset.configs_records["fancy_config"] = ConfigsRecord({"local_epochs": 3})

            # Create a training message for each client
            message = driver.create_message(
                content=recordset,
                message_type=MessageType.TRAIN,
                dst_node_id=node_id,
                group_id=str(server_round),
                ttl=DEFAULT_TTL,
            )
            messages.append(message)

        # Send training messages to clients
        message_ids = driver.push_messages(messages)
        print(f"Pushed {len(list(message_ids))} messages: {message_ids}")

        # Wait for results from clients
        message_ids = [message_id for message_id in message_ids if message_id != ""]
        all_replies: List[Message] = []
        while True:
            replies = driver.pull_messages(message_ids=message_ids)
            print(f"Got {len(list(replies))} results")
            all_replies += replies
            if len(all_replies) == len(message_ids):
                break
            time.sleep(12)

        # Filter out messages with errors
        all_replies = [
            msg
            for msg in all_replies
            if msg.has_content()
        ]
        print(f"Received {len(all_replies)} results")

        # Print metrics received from clients
        for reply in all_replies:
            print(reply.content.metrics_records)

        # Aggregate parameters received from clients
        parameter_records_list = [reply.content.parameters_records["fancy_model_returned"] for reply in all_replies]
        new_parameter_record = aggregation_strategy.aggregate_parameters(parameter_records_list)
        global_model.set_parameters(new_parameter_record)

        # Evaluate the updated global model
        messages = []
        for idx, node_id in enumerate(node_ids):
            # Create evaluation messages for clients
            recordset = RecordSet()

            # Add updated model parameters to record
            recordset.parameters_records["fancy_model"] = new_parameter_record
            # Add a config with information to send the client for evaluation
            recordset.configs_records["fancy_config"] = ConfigsRecord({"local_epochs": 3})

            # Create an evaluation message for each client
            message = driver.create_message(
                content=recordset,
                message_type=MessageType.EVALUATE,
                dst_node_id=node_id,
                group_id=str(server_round),
                ttl=DEFAULT_TTL,
            )
            messages.append(message)

        # Send evaluation messages to clients
        message_ids = driver.push_messages(messages)
        print(f"Pushed {len(list(message_ids))} messages: {message_ids}")

        # Wait for evaluation results from clients
        message_ids = [message_id for message_id in message_ids if message_id != ""]
        all_replies: List[Message] = []
        while True:
            replies = driver.pull_messages(message_ids=message_ids)
            print(f"Got {len(list(replies))} results")
            all_replies += replies
            if len(all_replies) == len(message_ids):
                break
            time.sleep(3)

        # Filter out messages with errors
        all_replies = [
            msg
            for msg in all_replies
            if msg.has_content()
        ]
        print(f"Received {len(all_replies)} results")

        # Print evaluation metrics received from clients
        metrics_records_list = [reply.content.metrics_records['eval_metrics'] for reply in all_replies]
        for i, reply in enumerate(all_replies):
            print(f"Client {i+1} metrics:   ", reply.content.metrics_records['eval_metrics'])

        # Aggregate evaluation metrics
        print("Aggregated metrics result:   ", aggregation_strategy.aggregate_metrics(metrics_records_list))
    
    print("🎉🎉🎉 Successfully completed federated learning run! 🎉🎉🎉")
