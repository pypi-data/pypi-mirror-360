---
slug: /components/agent-config/inference-model
sidebar_position: 10
---

# Inference Model

Inference models are neural network architectures designed for natural language processing tasks. They analyze input text to generate responses, answer questions, make predections, or summarize content. 

In Therix, we make it easy to use many popular inference models. You can choose the best one for your needs, depending on what you're trying to do. Whether you're analyzing data, recognizing patterns, or making predictions, we've got you covered with simple integration and a variety of options to suit your specific use case.



## 1. OpenAI GPT3.5 Turbo

- Import the OpenAIGPT35TurboInferenceModel model from therix.core.inference_models

```python
from therix.core.inference_models import OpenAIGPT35TurboInferenceModel
```

- Add the model to agent configurations using the add method

```python
.add(OpenAIGPT35TurboInferenceModel(config={'api_key': // Your openAi API key here}))
```

## 2. OpenAI GPT4 

- Import the OpenAIGPT4InferenceModel model from therix.core.inference_models

```python
from therix.core.inference_models import OpenAIGPT4InferenceModel
```

- Add the model to agent configurations using the add method.

```python
.add(OpenAIGPT4InferenceModel(config={'api_key': // Your openAi API key here}))
```

## 3. OpenAI GPT4 Turbo Preview

- Import the OpenAIGPT4TurboPreviewInferenceModel model from therix.core.inference_models

```python
from therix.core.inference_models import OpenAIGPT4TurboPreviewInferenceModel
```

- Add the model to agent configurations using the add method.

```python
.add(OpenAIGPT4TurboPreviewInferenceModel(config={'api_key': // Your openAi API key here}))
```

## 4. Azure OpenAI GPT3 Turbo Preview

- Import the AzureOpenAIGPT3TurboPreviewInferenceModel model from therix.core.inference_models

```python
from therix.core.inference_models import AzureOpenAIGPT3TurboPreviewInferenceModel
```

- Add the model to agent configurations using the add method.

```python
.add(AzureOpenAIGPT3TurboPreviewInferenceModel(config={'azure_api_key': // Your azure API key here}))
```

## 5. Azure OpenAI GPT3 Turbo Instructnference Model

- Import the AzureOpenAIGPT3TurboInstructnferenceModel model from therix.core.inference_models

```python
from therix.core.inference_models import AzureOpenAIGPT3TurboInstructnferenceModel
```

- Add the model to agent configurations using the add method.

```python
.add(AzureOpenAIGPT3TurboInstructnferenceModel(config={'azure_api_key': // Your azure API key here}))
```

## 6. Azure OpenAI GPT4 

- Import the AzureOpenAIGPT4InferenceModel model from therix.core.inference_models

```python
from therix.core.inference_models import AzureOpenAIGPT4InferenceModel
```

- Add the model to agent configurations using the add method.

```python
.add(AzureOpenAIGPT4InferenceModel(config={'azure_api_key': // Your azure API key here}))
```

## 7. Azure OpenAI GPT4 Turbo Preview

- Import the AzureOpenAIGPT4TurboPreviewInferenceModel model from therix.core.inference_models

```python
from therix.core.inference_models import AzureOpenAIGPT4TurboPreviewInferenceModel
```

- Add the model to agent configurations using the add method.

```python
.add(AzureOpenAIGPT4TurboPreviewInferenceModel(config={'azure_api_key': // Your azure API key here}))
```

## 8. Groq Mixtral87b

- Import the GroqMixtral87bInferenceModel model from therix.core.inference_models

```python
from therix.core.inference_models import GroqMixtral87bInferenceModel
```

- Add the model to agent configurations using the add method.

```python
.add(GroqMixtral87bInferenceModel(config={'groq_api_key': // Your groq API key here}))
```

## 9. Groq Gemma7B

- Import the GroqGemma7B model from therix.core.inference_models

```python
from therix.core.inference_models import GroqGemma7B
```

- Add the model to agent configurations using the add method.

```python
.add(GroqGemma7B(config={'groq_api_key': // Your groq API key here}))
```

## 10. Groq Llama3x70b

- Import the GroqLlama370b model from therix.core.inference_models

```python
from therix.core.inference_models import GroqLlama370b
```

- Add the model to agent configurations using the add method.

```python
.add(GroqLlama370b(config={'groq_api_key': // Your groq API key here}))
```

## 11. Groq Llama3x8b

- Import the GroqLlama370b model from therix.core.inference_models

```python
from therix.core.inference_models import GroqLlama38b
```

- Add the model to agent configurations using the add method.

```python
.add(GroqLlama38b(config={'groq_api_key': // Your groq API key here}))
```

## 12. Bedrock Text ExpressV1

- Import the BedrockTextExpressV1 model from therix.core.inference_models

```python
from therix.core.inference_models import BedrockTextExpressV1
```

- Add the model to agent configurations using the add method.

```python
.add(BedrockTextExpressV1(config={ "bedrock_aws_access_key_id": // Your bedrock access key,
                                    "bedrock_aws_secret_access_key" : // Your bedrock secret key,
                                    "bedrock_aws_session_token" : // Your bedrock session token,
                                    "bedrock_region_name" : // Your bedrock region
                                    }))
```

## Example

```python
agent = Agent(name="Inference Agent Example")
    (agent
    .add(YourInferenceModel(config = {// Keys according to your selected inference model}))
    .add(// Any other configuration you want to add)
    .save())

     
    ans = agent.invoke(question)
```
In this way you can add your desired inference model to your agent based on your specific use-case.