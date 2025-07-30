from therix.core.data_sources import PDFDataSource
from therix.core.inference_models import BedrockLiteG1, BedrockTextExpressV1, GroqMixtral87bInferenceModel
from therix.core.embedding_models import BedrockTitanEmbedding
from therix.core.pii_filter_config import PIIFilterConfig
from therix.core.agent import Agent
import sys
from therix.core.trace import Trace

agent = Agent(name="PII Filter Agent")
(agent
    .add(PDFDataSource(config={'files': ['../../test-data/Essay-on-Lata-Mangeshkar-final.pdf']}))
    .add(BedrockTitanEmbedding(config={ "bedrock_aws_access_key_id":"",
                                        "bedrock_aws_secret_access_key" : "",
                                        "bedrock_aws_session_token" : "",
                                        "bedrock_region_name" : "us-east-1"
                                            }))
    .add(BedrockLiteG1(config={ "bedrock_aws_access_key_id":"",
                                "bedrock_aws_secret_access_key" : "",
                                "bedrock_aws_session_token" : "",
                                "bedrock_region_name" : "us-east-1"
                                            }))
    .add(PIIFilterConfig(config={
        'entities': ['PERSON','PHONE_NUMBER','EMAIL_ADDRESS']
    }))
        #   .add(
        #         Trace(
        #         config={
        #             "secret_key": "sk-lf-3207d77e-b681-4d1b-b39a-04d7ee42bca6",
        #             "public_key": "pk-lf-874a92be-a68e-47c2-b129-1fd3f25282d7",
        #             "identifier": "Trying rag with SDK",
        #         }
        #     )
        # )
    .save())

agent.preprocess_data()
print(agent.id)
ans = agent.invoke("Whom is the data about? And what are their personal details?")

print(ans)