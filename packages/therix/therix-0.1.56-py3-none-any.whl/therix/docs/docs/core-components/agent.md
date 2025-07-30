---
slug: /components/agent
sidebar_position: 1
---

# Agent

In therix, everything happens by creating agents of desired structure.

## What is a agent ?

A agent is a sequence of connected steps where a specific input undergoes various processes or transformations to achieve a desired outcome. Each step in the agent is dedicated to performing a specific task that contributes to the final result.

## How to create a agent ?

Import the Agent class and create an instance of a agent, name the agent with the desired name using its constructor.

```python
from therix.core.agent import Agent

# Initialize a new agent
agent = Agent(name="My New Published Agent")
```

Now you can add all the required configuration to your agent using the chaining method. Based on the components added the type of agent is determined implicitly.

## Add components to the agent

The newly created agent object acts as a starting point of adding the agent configurations. On this Instance you can add any required configuration component using the **.add()** method in a chain. So that the entire agent flow is decided.

```python
agent
        .add(AgentConfiguration(config={ // Add required metadata  })) # Chaining add method to add configuration
```

## Save the agent

After you are done adding your desired configuration to your agent object its time to save our agent into the database. You can save your agent by chaining the **.save()** method at the end of the configuration chain.

```python
(agent
        .add(AgentConfiguration(config={ // Add required metadata  }))
        .save() # Save method chained at the end for saving
        )
```

**Note : Once you save your agent, its configurations cannot be altered.**

## Publish your agent

Publishing the agent makes your agent ready to be used. You can simply publish your agent by calling the **.publish()** method on your agent object.

```python
  # Call the publish method
```

## Preprocess the agent Data

Preprocessing the agent data is an optional step. If your agent configuration consists of an embedding model or has embedding creation requirements then only you need to preprocess the data. Otherwise you can skip it.
Preprocessing is done using the **.preprocess_data()** method on your agent object.

```python
agent.preprocess_data() # Add preprocessing method
```

## Invoke agent

The final step is invoking the agent for executing the agent according to the flow that we have configured with the help of agent configurations and its metadata added previously. This returns us the llm response into a dictionary with keys **answer** for the response and the **session_id** for the session.

Invocation is done using the **.invoke()** method on the agent object.

```python
answer = agent.invoke(// Your question) # Invoke the agent

#answer:
{'answer': // LLM response , 'session_id': // Uuid session id}
```

## Example

```python
agent = Agent(name="My New Published Agent")
    (
        agent
        .add(AgentConfiguration(config={ // Add required metadata  })) // Add required configurations
        .save()
    )
    agent.preprocess_data()
    answer = agent.invoke(// Question to the llm)
```
In this way we have sucessfully created the agent, configured it and invoked it based on our requirements.