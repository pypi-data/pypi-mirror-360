---
slug: /components/agent-config/data-sources
sidebar_position: 1
---

# Data Sources
Therix is a versatile tool designed to facilitate the integration of various data sources into your projects. Whether you're working with PDFs, CSV files, or even YouTube videos, Therix offers seamless integration, allowing you to harness data from diverse origins effortlessly. This documentation will guide you through the process of adding different data sources using Therix.

## PDF

- Import the PDFDataSource  from therix.core.data_sources
```python
from therix.core.data_sources import PDFDataSource
.add(PDFDataSource(config={"files": [""]}))
```

## Youtube

- Import the YoutubeDataSource  from therix.core.data_sources
```python
from therix.core.data_sources import YoutubeDataSource
.add(YoutubeDataSource(config={"files": [""]}))
```

## Website

- Import the WebsiteDataSource  from therix.core.data_sources
```python
from therix.core.data_sources import WebsiteDataSource
.add(WebsiteDataSource(config={"files": [""]}))
```

## Example 
```python
agent = Agent(name="Summarizer Agent")
    (agent
    .add(DataSource(config = trace_config))
    .add(// Any other configuration you want to add)
    .save())

     
    answer = agent.invoke(text)
```