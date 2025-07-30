from importlib import metadata
from therix.core.agent import Agent
from therix.core.inference_models import GroqLlama370b
from therix.core.system_prompt_config import SystemPromptConfig
from therix.core.output_parser import OutputParserWrapper


metadata = {
    "name": "Abhishek Dubey",
}

agent = Agent(name="Side Effects Agent")
(
    agent.add(GroqLlama370b(config={"groq_api_key": "key"}))
    .save()
)
print(agent.id)


agent.invoke("Who is sonu nigam?")
