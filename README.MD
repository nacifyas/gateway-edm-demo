[![CodeQL](https://github.com/nacifyas/gateway-edm-demo/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/nacifyas/gateway-edm-demo/actions/workflows/codeql-analysis.yml)
[![Build](https://github.com/nacifyas/gateway-edm-demo/actions/workflows/flak8-mypy-build.yml/badge.svg)](https://github.com/nacifyas/gateway-edm-demo/actions/workflows/flak8-mypy-build.yml)

Microservice API Gateway.

This MS servers as a API Gateway the following microservices:
- [User Microservice](https://github.com/nacifyas/users-demo)
- [Posts Microservice](https://github.com/nacifyas/posts-demo)
- [Graphs Microservice](https://github.com/nacifyas/followups-ms)

---

The intention behind this project it to create an easy and small example of an *Events Driven Backend* using Redis and FastAPI.

---
To install and use this project, make sure to have Python >3.7 installed as well and the other microservices too, using this same guide.

1. ```git clone https://github.com/nacifyas/gateway-edm-demo/```
2. Create a Python virtual environment (in windows) with ```py -m venv env```
3. Activate tat virtual environment (in windows) with ```& .\env\Scripts\Activate.ps1```
4. Run ```pip install -e .```, or if you want to contribute and do dev related stuff ```pip install .[dev]```
5. Run the src/main.py to start the FastAPI server with ```py src\main.py```
6. Run the PubSub consumer with ```py src\events\consumer.py```
7. A good place to start using the project is at ```127.0.0.1:8000```
