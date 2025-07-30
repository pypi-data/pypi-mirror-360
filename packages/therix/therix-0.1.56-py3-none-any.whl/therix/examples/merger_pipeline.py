from therix.core.agent import Agent

#Add  two agents to merge with agent 
        
merger_agent = Agent.merge(['c1600014-bca1-4436-96e9-975cf333fa54' , 'f202d57b-7ede-456b-8aa5-975052a275a8'])    

# set agent_id
# merger_agent.set_primary('f202d57b-7ede-456b-8aa5-975052a275a8')

ans = merger_agent.invoke("Give me summary of both the documents")
    
print(ans)