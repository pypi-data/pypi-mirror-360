---
slug: /introduction/installation
sidebar_position: 10
---

# Installation & Setup

Therix is available to install via [pypi.org](https://pypi.org/) for use in any Python project. If you need a custom solution, get in touch at [enterprise@therix.ai](mailto:enterprise@therix.ai).

## Step 1: Create an Account on Therix Cloud

The first step to get started with Therix is to create an account on Therix Cloud. Follow these steps:

1. Visit [Therix Cloud](https://cloud.dev.therix.ai) and sign up for an account.
2. Complete the registration process.
3. Once logged in, proceed to create a new project.


![Project Creation Dashboard](screenshots\ProjectCreate.PNG)




## Step 2: Generate an API Key

After creating your project on Therix Cloud, generate an API Key to authenticate your application. Here’s how:

1. In your Therix Cloud account, navigate to the API Key section of your project.
2. Generate a new API Key and ensure to securely store it.


![Api Key Creation](screenshots\ApiKey.PNG)

## Installation

To install Therix, use `pip`, Python's package installer. Open your command prompt or terminal and execute:

`pip install therix`


## Setup

After installing Therix, configure your environment:

1. Add the generated API Key to your `.env` file:

`TTHERIX_API_KEY="your_generated_api_key"`





2. Optionally, configure other environment variables based on your setup needs.

### Using the `Agent` Class

Start using `therix` in your Python scripts with the `Agent` class:

```python
from therix.core.agent import Agent

# Initialize a new agent
agent = Agent(name="My New Published Agent")
(agent
 .add(// Add configurations you want to add)
 .save())

answer = agent.invoke(text)
```

### Python Versions Supported

- **3.12**


