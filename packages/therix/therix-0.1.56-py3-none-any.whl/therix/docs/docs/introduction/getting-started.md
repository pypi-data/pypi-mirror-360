---
slug: /introduction/getting-started
sidebar_position: 5
---

# Getting Started

You can get started with therix.ai and build your first AI Agent in **less than 5 minutes**. 

## Install Therix

Therix is available as a python package and can be installed using popular python package managers.
See more details on installation on the [installation page](/introduction/insatallation)

To add therix to your python project, just run 

```shell
pip install therix-ai
```

This will add therix and all the required dependencies to add AI to your project.

## Set necessary ENV VARS

In order to get therix working, you will need to provide the details for a Postgres SQL instance with the `pgvector` plugin enabled. 

```env
export THERIX_DB_HOST = 
export THERIX_DB_USERNAME = 

```


## Build your first AI Agent

To build a simple data extractor agent, create a `extractor.py` file within your code. 

### Add the necessary imports 

```python
from therix.core import Agent, AgentConfiguration

# TODO

```
### Create a summarizer agent

```python 

agent = Agent(name="Awesome AI Summarizer")

# TODO

```

### Execute it

```python
# TODO
```

## What next?
Explore the type of Agent Configurations Available to use in your AI Agents.