# AsyncFlowExperiment

## The idea

AsyncFlowExperiment explores asynchronous programming by building and managing function chains and publish-subscribe mechanisms in a distributed environment. It aims to create a framework for chaining functions and handling asynchronous events across multiple workers to enhance scalability and performance. The project simplifies the creation and management of distributed asynchronous workflows by using named functions and a publish-subscribe system. This approach facilitates the development of complex, non-blocking workflows that efficiently distribute tasks across multiple workers. The goal is to develop a library supporting multiple languages, including Go, C++, and JavaScript, enabling seamless integration and interaction between different software ecosystems.

## Project Status

Currently in the experimental phase, the project has no implemented features and is focused on exploring concepts and laying the groundwork for future development.

## Use Case

### Scenario 1: Extending Existing Python Backend

- **Context**: You have a Python backend that requires new features.
- **Requirement**: Integrate the new features seamlessly without significant modifications to the existing system.
- **Solution**: `AsyncFlowExperiment` enables you to extend your backend with asynchronous tasks, improving scalability and performance while maintaining code integrity.

### Scenario 2: Reusing Open Source Libraries

- **Context**: You find open-source libraries in Go and C++ that fit your requirements perfectly.
- **Challenge**: These libraries have their own dependencies and containers, complicating direct integration.
- **Solution**: `AsyncFlowExperiment` allows you to incorporate these libraries without modifying their core code, facilitating smooth integration and leveraging their full potential.

### Scenario 3: Maintaining Integrity of Existing Examples

- **Context**: Open-source libraries come with well-established examples that solve specific tasks effectively.
- **Requirement**: Use these examples without significant alterations to ensure their reliability.
- **Solution**: With `AsyncFlowExperiment`, you can integrate these examples into your workflow, preserving their functionality and ensuring consistent performance.

### Scenario 4: Handling Complex Pipelines

- **Context**: Your project involves complex tasks that span multiple libraries.
- **Challenge**: Ensuring smooth data flow and coordination across different libraries.
- **Solution**: `AsyncFlowExperiment` provides a framework for managing complex pipelines, ensuring efficient task execution and data handling.

### Scenario 5: Seamless Integration with Minimal Changes

- **Context**: You need to integrate diverse libraries into your backend with minimal changes.
- **Solution**: `AsyncFlowExperiment` facilitates the seamless integration of various libraries, allowing for efficient task handling and maintaining the integrity of your existing pipeline.
- **Benefit**: Achieve efficient task execution and results handling with minimal modifications, preserving the integrity of your backend and its workflows.

## Comparison with Similar Libraries/Frameworks/Projects

| Library             | Python Support | Go Support | C++ Support | JS/TS Support | Effort to integrate to existing code | Effort to integrate to existing infrastructure | Async Code support | Focus on Flow Management |
| ------------------- | -------------- | ---------- | ----------- | ------------- | ------------------------------------ | ---------------------------------------------- | ------------------ | ------------------------ |
| **Current project** | Yes            | Planned    | Planned     | Planned       | TBD                                  | Integrates in your ecosystem                   | Yes                | Yes                      |
| **Prefect**         | Yes            | No         | No          | No            | Medium                               | Medium                                         | Yes                | Yes                      |
| **Celery**          | Yes            | No         | No          | No            | Medium                               | High                                           | Yes                | No                       |
| **Dask**            | Yes            | No         | No          | No            | Medium                               | Medium                                         | Yes                | No                       |
| **Apache Airflow**  | Yes            | No         | No          | No            | High                                 | High                                           | Limited            | Yes                      |
| **Ray**             | Yes            | No         | No          | No            | Medium                               | Medium                                         | Yes                | Yes                      |
| **Taskiq**          | Yes            | No         | No          | No            | Medium                               | Medium                                         | Yes                | No                       |

## Contributions

While I am not actively seeking maintainers at the moment, any help with development, testing, and documentation is greatly appreciated. If you have experience with asynchronous programming in Python and are interested in contributing, please reach out through GitHub.

## How to Setup the Project

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/AsyncFlowExperiment.git
   cd AsyncFlowExperiment
   ```

2. Create a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## How to Run It

1. Run the tests:

   ```sh
   pytest
   ```

2. Use the `ptw` library to watch for test changes and automatically run tests:

   ```sh
   ptw
   ```

3. To explore the functionality, you can modify and run the `lib_test.py` file. Note that the main script is designed to be run with pytest and is not meant to be executed directly. You can add your own tests or modify existing ones to see how the asynchronous chains and publish-subscribe system work.

## License

This project is licensed under the MIT License.
