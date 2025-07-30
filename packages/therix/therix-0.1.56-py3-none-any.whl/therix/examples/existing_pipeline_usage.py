import asyncio
from typing import List
import json
from pydantic import BaseModel, Field
from therix.core.agent import Agent
import sys
from therix.core.output_parser import OutputParserWrapper

sys_prompt = """Answer the question like a pirate based only on the following context and reply with your capabilities if something is out of context.
    Context: 
    {context}
    Question: {question}
    
    Give the output as follows : {format_instructions}
"""
    
variables = {
    "name": "Nilesh Sanap",
    }
    

if len(sys.argv) > 1:
    agent = Agent.from_id(sys.argv[1])
    question = sys.argv[2]
    session_id = None
    if len(sys.argv) >= 4:
        session_id = sys.argv[3]  
    ans = agent.invoke(agent, question, session_id)
    print(ans)
else:
    class TestDetails(BaseModel):
        name: str = Field(description="Name of the Topic")
        description: str = Field(description="Short description of the Topic")
        citations: str = Field(description="add source of every topic, from where it is generated")
        page: str = Field(description="page number of the topic")


    class OutputParserJSON(BaseModel):
        tests: List[TestDetails] = Field(description="Topic")
        
    agent_id = "d166ebce-c92b-4c6d-8d7f-3be73307ee66"
    # session_id = 'bb74e7da-9730-4422-82ff-e0b711416c66'
    agent = Agent.from_id(agent_id)
    ans = agent.invoke(question="What are the experiments performed in the study?")
    print(ans)
