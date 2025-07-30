import os
from typing import List, Iterator
from langchain.docstore.document import Document
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from os.path import splitext, basename


class DocumentIntelligenceExtractor:
    """Azure Document Intelligence extractor for PDF files."""
    
    def __init__(self, key: str, endpoint: str, model: str = "prebuilt-document"):
        self.key = key
        self.endpoint = endpoint
        self.model = model

    def pdf_to_bytes(self, pdf_file_path: str) -> bytes:
        """
        Converts a PDF file to bytes.

        Args:
            pdf_file_path (str): The path to the PDF file.

        Returns:
            pdf_bytes: The contents of the PDF file as bytes.
        """
        # Check if the file exists
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")

        # Read the PDF file into bytes
        with open(pdf_file_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        return pdf_bytes

    def extract_raw_data_from_pdf(self, pdf_path: str) -> tuple:
        """
        Extracts raw data from a single PDF using Azure Document Intelligence.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            tuple: (filename, AnalyzeResult)
        """
        pdf_bytes = self.pdf_to_bytes(pdf_path)
        file_name = splitext(basename(pdf_path))[0]
        
        document_analysis_client = DocumentAnalysisClient(
            endpoint=self.endpoint, 
            credential=AzureKeyCredential(self.key)
        )
        
        poller = document_analysis_client.begin_analyze_document(self.model, pdf_bytes)
        result = poller.result()
        
        return (file_name, result)


class DocumentIntelligenceLoader:
    """
    Loader for PDF documents using Azure Document Intelligence.
    Compatible with LangChain's document loader interface.
    """
    
    def __init__(self, file_path: str, config: dict):
        """
        Initialize the Document Intelligence loader.
        
        Args:
            file_path (str): Path to the PDF file
            config (dict): Configuration containing Azure DI credentials
                - endpoint: Azure Document Intelligence endpoint
                - key: Azure Document Intelligence key  
                - model: Model to use (optional, defaults to 'prebuilt-document')
        """
        self.file_path = file_path
        self.config = config
        
        # Validate required config
        if 'azure_document_intelligence_endpoint' not in config:
            raise ValueError("Azure Document Intelligence endpoint is required in config")
        if 'azure_document_intelligence_key' not in config:
            raise ValueError("Azure Document Intelligence key is required in config")
            
        self.extractor = DocumentIntelligenceExtractor(
            key=config['azure_document_intelligence_key'],
            endpoint=config['azure_document_intelligence_endpoint'],
            model=config.get('model', 'prebuilt-document')
        )

    def load(self) -> List[Document]:
        """Load documents from the PDF file."""
        return list(self.lazy_load())

    def lazy_load(self) -> Iterator[Document]:
        """Lazy load documents from the PDF file."""
        try:
            file_name, result = self.extractor.extract_raw_data_from_pdf(self.file_path)
            
            # Create base metadata
            metadata = {
                "source": self.file_path,
                "filename": file_name,
                "extraction_method": "azure_document_intelligence",
                "model": self.extractor.model
            }
            
            # Add additional metadata from the result if available
            if hasattr(result, 'model_id'):
                metadata["model_id"] = result.model_id
            if hasattr(result, 'pages') and result.pages:
                metadata["page_count"] = len(result.pages)

            # Check if we have pages to create separate documents per page
            if hasattr(result, 'pages') and result.pages:
                # Create separate documents for each page
                for page_num, page in enumerate(result.pages, 1):
                    page_content = ""
                    if hasattr(page, 'lines'):
                        page_content = "\n".join([line.content for line in page.lines if line.content])
                    
                    # Create metadata for this specific page
                    page_metadata = metadata.copy()
                    page_metadata["page"] = page_num
                    
                    yield Document(page_content=page_content, metadata=page_metadata)
            else:
                # Fallback: Extract text content from the entire result
                content = ""
                if hasattr(result, 'content') and result.content:
                    content = result.content
                elif hasattr(result, 'paragraphs'):
                    content = "\n\n".join([para.content for para in result.paragraphs if para.content])
                
                # For single document, set page to 1
                metadata["page"] = 1
                yield Document(page_content=content, metadata=metadata)
            
        except Exception as e:
            raise RuntimeError(f"Error processing PDF with Document Intelligence: {str(e)}")

    def load_and_split(self, text_splitter=None) -> List[Document]:
        """Load and optionally split documents."""
        documents = self.load()
        
        if text_splitter is None:
            return documents
            
        return text_splitter.split_documents(documents) 