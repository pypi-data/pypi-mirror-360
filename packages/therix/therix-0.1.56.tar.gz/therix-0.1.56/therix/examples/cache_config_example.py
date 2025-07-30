import json
import time
from uuid import uuid4
from therix.core.data_sources import PDFDataSource
from therix.core.embedding_models import AzureOpenAIEmbedding3SmallEmbeddingModel, OpenAITextAdaEmbeddingModel
from therix.core.inference_models import AzureOpenAIGPT3TurboPreviewInferenceModel, GroqMixtral87bInferenceModel, OpenAIGPT4TurboPreviewInferenceModel
from therix.core.inference_models import AzureOpenAIGPT3TurboPreviewInferenceModel, OpenAIGPT4TurboPreviewInferenceModel
from therix.core.embedding_models import BedrockTitanEmbedding, OpenAITextAdaEmbeddingModel
from therix.core.inference_models import BedrockTextExpressV1, OpenAIGPT4TurboPreviewInferenceModel
from therix.core.pipeline import Pipeline
from therix.core.cache import CacheConfig
import sys

from therix.core.trace import Trace


start_time = time.process_time()



# TODO: Init therix with DB details, and license key



## Usage:
# python main.py ad11128d-d2ec-4f7c-8d87-15c1a5dfe1a9 "how does it help in reasoning?"

# if args has pipeline_id, then load the pipeline
## else create new pipeline
if len(sys.argv) > 1:
    pipeline = Pipeline.from_id(sys.argv[1])
    question = sys.argv[2]
    session_id = None

    if len(sys.argv) < 4:
        pass
    else:
        session_id = sys.argv[3]

    ans = pipeline.invoke(question, session_id)
    print(ans)

    end_time = time.process_time()


    cpu_time = end_time - start_time

    print("CPU time", cpu_time)

else:
    pipeline = Pipeline(name="My New Published Pipeline")
    (pipeline
    .add(PDFDataSource(config={'files': ['../../test-data/rat.pdf']}))
    .add(BedrockTitanEmbedding(config={"bedrock_aws_access_key_id" : "",
                                "bedrock_aws_secret_access_key" : ""        ,
                                "bedrock_aws_session_token" : "",
                                "bedrock_region_name" : "us-east-1"}))
    .add(GroqMixtral87bInferenceModel(config={'groq_api_key': GROQ_API_KEY}))
    .add(Trace(config={
        'secret_key': 'sk-lf-e62aa7ce-c4c8-4c77-ad7d-9d76dfd96db1',
        'public_key': 'pk-lf-282ad728-c1d6-4247-b6cd-8022198591a9',
        'identifier': 'cache_pipeline'
    }))
    .add(CacheConfig(config={}))
    .save())

    pipeline.preprocess_data()
    print(pipeline.id)
    ans = pipeline.invoke("Explain ablation study?")

    print(ans)


    end_time = time.process_time()


    cpu_time = end_time - start_time

    print("CPU time", cpu_time)
    
    