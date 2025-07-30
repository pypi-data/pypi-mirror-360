---
slug: /components/agent-config/caching
sidebar_position: 15
---

# Caching

Therix provides an optional caching layer for Language Model (LM) requests. This caching layer offers two primary benefits:

- **Cost Reduction**: By caching LM responses, Therix reduces the number of API calls made to the LM provider, saving you money, especially when frequently requesting the same completions.
  
- **Improved Application Performance**: The caching layer also enhances application speed by minimizing the number of API calls made to the LM provider, resulting in faster response times and reduced latency.

Therix supports two types of Caching :- 


## Exact Match Caching

- Exact Match Caching involves storing and retrieving data based on exact key-value pairs. 
- In Therix - Exact Match Caching helps optimize performance by quickly retrieving frequently accessed completions without the need for repeated API calls to the LM provider.

## Semantic Caching


- Semantic Caching extends caching beyond exact matches and considers the meaning or context of the data being cached.
- In Therix, Semantic Caching intelligently caches data based on its semantic relevance, enhancing the efficiency of LM requests and reducing overall resource utilization.



## Adding Caching to Your Agent

- Add Summarizer Configuration to Agent: Use the .add() method to add the SummarizerConfig to your Therix agent.

```python
.add(CacheConfig(config={}))
```


The following example covers how to cache results of individual LLM calls using Therix Cache.


```python 
agent = Agent(name="Summarizer Agent")
    (agent
    .add(PDFDataSource(config={'files': ['../../test-data/rat.pdf']}))
    .add(// Any other configuration you want to add)
    .add(CacheConfig(config={}))
    .save())
```
    

```python
    # The first time, it is not yet in cache, so it should take longer
    answer = agent.invoke("What are some use cases of RAT?")
```

```python
    Output: {'answer':" Here are some examples of use cases for a RAT:
    1. Remote Administration: A RAT can be used to remotely control and manage a compromised system, allowing the attacker to execute commands, install additional malware, or steal sensitive data.
    2. Data Theft: A RAT can be used to steal sensitive data from a compromised system, such as passwords, financial information, or proprietary data.
    3. Surveillance: A RAT can be used to monitor the activities of a compromised system, allowing the attacker to capture screenshots, log keystrokes, or activate webcams or microphones.", 
    'session_id': UUID('0790b696-bb1a-4fa7-b387-d01adcffc4ed')}
    
    CPU time 4.796875
```


```python
#  The second time it is, so it goes faster
agent.invoke("What are some use cases of RAT?")
```

```python
    Output:  {'answer':" Here are some examples of use cases for a RAT:
    1. Remote Administration: A RAT can be used to remotely control and manage a compromised system, allowing the attacker to execute commands, install additional malware, or steal sensitive data.
    2. Data Theft: A RAT can be used to steal sensitive data from a compromised system, such as passwords, financial information, or proprietary data.
    3. Surveillance: A RAT can be used to monitor the activities of a compromised system, allowing the attacker to capture screenshots, log keystrokes, or activate webcams or microphones.", 
    'session_id':UUID('84474906-9800-4ab2-90fc-b29fb3d08769')}

    CPU time 0.0625
```    








