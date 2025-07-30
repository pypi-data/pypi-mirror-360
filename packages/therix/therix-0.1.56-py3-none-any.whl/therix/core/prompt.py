import os
from therix.services.api_service import ApiService
import re

class Prompt:
    @classmethod
    def get_prompt(cls, prompt_name, variables=None):
        api_service = ApiService(therix_api_key=os.getenv("THERIX_API_KEY"))
        if os.getenv("THERIX_API_KEY") is not None:
            response_data = api_service.get(endpoint="prompts/active", params={"prompt_name": prompt_name})
            prompt_template = response_data['data']['prompt']
            
            # Function to replace only provided variables (case-sensitive)
            def replace_placeholders(template, variables):
                if not variables:
                    return template
                
                # Use regex to match and replace placeholders
                def replacer(match):
                    key = match.group(1).strip()
                    return variables.get(key, match.group(0))
                
                return re.sub(r'\{([\w\s]+)\}', replacer, template)
            
            formatted_prompt = replace_placeholders(prompt_template, variables)
            return formatted_prompt
        else:
            raise EnvironmentError("THERIX_API_KEY is not set")