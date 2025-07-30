from pydantic import BaseModel, Field
from typing import List
from langchain.output_parsers import PydanticOutputParser


class OutputParserWrapper:
    @staticmethod
    def parse_output(pydantic_object):
        pydantic_parser = PydanticOutputParser(pydantic_object=pydantic_object)
        return pydantic_parser
