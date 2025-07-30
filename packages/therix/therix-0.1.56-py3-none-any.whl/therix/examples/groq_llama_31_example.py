from therix.core.inference_models import GroqLlama31405B, GroqLlama3170B, GroqLlama318B
from therix.core.agent import Agent

agent = Agent(name="My New Published Agent")
(
        agent
        # .add(GroqLlama3170B(
        #     config={"groq_api_key":""}
        # ))
        # .add(GroqLlama318B(
        #     config={"groq_api_key":""}
        # ))
        .add(GroqLlama31405B(
            config={"groq_api_key":""}
        ))
        .save()
    )

print(agent.id)
ans = agent.invoke("Who is sonu nigam?")

print(ans)