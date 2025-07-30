---
slug: /components/agent-config/trace
sidebar_position: 20
---

# Trace

Therix provides a tracing feature. Tracing acts like a detective tool for your Language Model (LM), helping understand what's happening, identifying the root cause of problems, and tracking the cost borne by different models based on tokens used. Additionally, it shows you a statistical representation of your Language Model (LM) usage.

## Why Trace
Tracing helps you find problems like:

- **Unexpected Results:** When things don't turn out as expected.
- **Agent Loops:** When your agents keep doing the same thing over and over.
- **Slow Chains:** When things are moving slower than they should.
- **Token Usage:** Keep track of how many tokens are used at each step.

## Getting Started

To add tracing to your Language Model (LM), redirect to [therix-trace-dev](https://analytics.dev.therix.ai/)

After redirecting, you'll see a screen similar to this. ![trace_dashboard](screenshots\trace_dashboard.JPG)
##
Go to settings and create API Keys to add it to your agent ![trace_settings_dashboard](screenshots\trace_settings_dashboard.JPG)



## Integrating Tracing into Your Code
Make sure you have the API Keys avaialable to you from the dashboard.
Here is an example of sample API Keys

```python
trace_config = {
    "secret_key": [TRACE_SECRET_KEY],
    "public_key": [TRACE_PUBLIC_KEY],
    "identifier": [PIPELINE_NAME],
}
```
Now pass the ```trace_config``` to your ```.add``` method in your code. Here is a basic example to demonstrate it.
```python
.add(Trace(config = trace_config))
```

## Example 
```python
agent = Agent(name="Summarizer Agent")
    (agent
    .add(Trace(config = trace_config))
    .add(// Any other configuration you want to add)
    .save())

     
    answer = agent.invoke(text)
```



