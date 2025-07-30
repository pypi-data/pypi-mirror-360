---
slug: /use-cases/asynchronous-methods
sidebar_position: 3
---

# Async Invoke

Therix also includes a feature for invoking the agent asynchronously. This means you can trigger multiple agents at the same time without any one of them slowing down the others.

# Syntax

Keeping it simple, just add `async_` before the `invoke` method, making it `async_invoke`.

# Example

We are using `asyncio` to make asynchronous calls, you can use any other desired library.

```python
import asyncio

agent = Agent(name="My New Published Agent")
    (
        agent
        .add(AgentConfiguration(config={ // Add required metadata  })) // Add required configurations
        .save()
    )

     
    agent.preprocess_data()

     async def call_agent(text):
        ans = await agent.async_invoke(text)
        print(ans)
        return ans

    asyncio.run(call_agent("your question"))
```