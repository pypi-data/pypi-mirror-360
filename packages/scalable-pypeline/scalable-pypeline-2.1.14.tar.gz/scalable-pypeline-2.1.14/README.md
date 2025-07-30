```
______ __   ________  _____  _     _____  _   _  _____ 
| ___ \\ \ / /| ___ \|  ___|| |   |_   _|| \ | ||  ___|
| |_/ / \ V / | |_/ /| |__  | |     | |  |  \| || |__  
|  __/   \ /  |  __/ |  __| | |     | |  | . ` ||  __| 
| |      | |  | |    | |___ | |_____| |_ | |\  || |___ 
\_|      \_/  \_|    \____/ \_____/\___/ \_| \_/\____/                                 
```

## Overview

PypeLine is a versatile open-source library designed to streamline the management of data workflows and APIs. With PypeLine, you can efficiently schedule cron jobs, execute complex Directed Acyclical Graph (DAG) pipelines, and set up a Flask API complete with OpenAPI documentation.

#### Key Features
- Cron Job Scheduling: Easily schedule recurring tasks with flexible cron job functionality, ensuring that your processes run reliably at specified intervals.
- DAG Pipelines: Define and execute DAGs to manage complex data workflows with dependencies. PypeLine handles the execution order and parallelism, ensuring that each task runs in the correct sequence.
- Flask API with OpenAPI: Quickly configure a RESTful API using Flask, with built-in support for OpenAPI documentation, allowing for clear, standardized documentation of your endpoints.

## Requirements

- RabbitMQ
- Redis
- Docker (optional for dev)

## Getting Started

Install PypeLines:

```commandline
pip install scalable-pypeline[flask,web,workers]>=1.2.3
```

Configure your Flask project (app.py)

```python
from flask import Flask
from pypeline.flask import FlaskPypeline
from pypeline_demo.api import bp
from pypeline_demo.config import Config
from pypeline_demo.extensions import dramatiq



def create_app():
    app = Flask(__name__)

    dramatiq.init_app(app)

    # Initialize your app with a configuration
    app.config.from_object(Config)

    pypeline = FlaskPypeline()
    pypeline.init_app(app, init_api=True)

    # Register API blueprints you wish 
    app.extensions["pypeline_core_api"].register_blueprint(bp)
    # Register application blueprints to application
    app.register_blueprint(bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5001)
```

Configure Dramatiq extension (extensions.py)

```python
from pypeline.dramatiq import Dramatiq


dramatiq = Dramatiq()
```

Setup your yaml configuration for pypelines (pypeline.yaml)

```yaml
serviceConfig:
    - name: pipeline-worker
      registeredTasks:
          - handler: pypeline_demo.pipeline.a
          - handler: pypeline_demo.pipeline.b
          - handler: pypeline_demo.pipeline.c
          - handler: pypeline_demo.scheduled_tasks.cron_task

pipelines:
    demo_pipeline:
        name: Demo Pipeline
        description: Pipeline to show examples of DAG Adjacency
        schemaVersion: 1
        config:
            dagAdjacency:
                a:
                    - b
                    - c
            metadata:
                maxRetry: 1
                retryBackoff: 180
                retryBackoffMax: 300
                retryJitter: true
                maxTtl: 10800
                queue: new-queue
            taskDefinitions:
                a:
                    handler: pypeline_demo.pipeline.a
                b:
                    handler:  pypeline_demo.pipeline.b
                c:
                    handler:  pypeline_demo.pipeline.c
scheduledTasks:
    cron-task:
        name: Example cron task
        enabled: true
        config:
            task: pypeline_demo.scheduled_tasks.cron_task
            queue: new-queue
            schedule:
                minute: '*'
                hour: '*'
                dayOfWeek: '*'
                dayOfMonth: '*'
                monthOfYear: '*'
        schemaVersion: 1
```

Setup your modules to be executed by yaml (pipeline.py && scheduled_tasks.py)

```python
import time


def a(event):
    print("A")


def b(event):
    print("B")
    time.sleep(10)


def c(event):
    print("C")
```

```python
def cron_task():
    print("HI")
```

Configure your environment variables (demo.env)

```env
SERMOS_BASE_URL=local
PYPELINE_CLIENT_PKG_NAME=pypeline_demo
REDIS_URL=redis://:password@localhost:6379/0
RABBITMQ_URL=amqp://admin:password@localhost:5672
```

Start Rabbit & Redis as your message broker and backend results storage.  We use `docker compose` for this.

## DEMO PROJECT COMING SOON!


## Testing

If you are developing pypeline and want to test this package,
install the test dependencies:

    $ pip install -e .[test]

Now, run the tests:

    $ tox
