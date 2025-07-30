# Simulation of Federated Learning Model

## Role of the Simulation

The simulation serves as a testing environment to validate the behavior of a federated learning model before deploying it to a real-world federated learning platform. It allows developers to:

1. **Test Model Compatibility**: Ensure that the local learner and aggregator conform to the required protocols and function as expected.
2. **Validate Training and Evaluation**: Simulate the federated training and evaluation process to verify that the model can handle distributed data and aggregation correctly.
3. **Debug and Optimize**: Identify and resolve issues in the model's implementation or configuration in a controlled environment.
4. **Prepare for Deployment**: Confirm that the model is ready to be uploaded to the model registry and used in production.

By running the simulation, developers can gain confidence in the model's performance and compatibility with the federated learning framework. The simulation generates necessary scripts and files to facilitate this process.

---

## Dataset Used in the Simulation

The simulation uses a preprocessed dataset related to Acute Myeloid Leukemia (AML). This dataset was obtained from a public data repository (Tazi et al., [GitHub Repository](https://github.com/papaemmelab/Tazi_NatureC_AML?tab=readme-ov-file)) and has been reduced and preprocessed for the purpose of federated learning. Key details about the dataset:

This dataset provides a realistic use case for federated learning in the medical domain, where data is often distributed across multiple institutions.

---

## How to Use

1. Open the `simulation_example.ipynb` notebook and follow the steps to set up the environment, define the model, and run the simulation.
2. Once the simulation is successful, upload the model to the model registry using the instructions in the notebook.

This folder provides a complete example of how to simulate, validate, and prepare a federated learning model for deployment.
