#!/usr/bin/env python3
"""
Document Intelligence Integration Example

This example demonstrates how to use Azure Document Intelligence for PDF text extraction
instead of the default pypdf loader in the therix SDK.

Benefits of Document Intelligence:
- Better OCR capabilities for scanned documents
- Superior layout understanding (tables, forms, etc.)
- Higher accuracy text extraction
- Support for complex document formats
"""

import os
from therix.core.data_sources import PDFDIDataSource
from therix.core.pipeline_component import DocumentIntelligence
from therix.core.embedding_models import AzureOpenAIEmbedding3LargeEmbeddingModel
from therix.core.inference_models import AzureOpenAIGPT4OInferenceModel
from therix.core.trace import Trace
from therix.core.agent import Agent

# Azure Document Intelligence Configuration
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = "https://your-document-intelligence.cognitiveservices.azure.com/"
AZURE_DOCUMENT_INTELLIGENCE_KEY = "your_document_intelligence_key"
AZURE_EXTRACTION_MODEL = "prebuilt-document"  # or "prebuilt-layout" for advanced layout

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = "your_azure_openai_api_key"
AZURE_OPENAI_ENDPOINT = "https://your-openai.openai.azure.com"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = "text-embedding-3-large"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"
AZURE_OPENAI_API_VERSION = "2024-02-01"

# Trace Configuration (optional)
TRACE_API_KEY = "your_trace_api_key"

# PDF file paths
pdf_paths = ["path/to/your/document1.pdf", "path/to/your/document2.pdf"]

def create_document_intelligence_pipeline():
    """
    Creates a pipeline that uses Azure Document Intelligence for PDF text extraction
    instead of the default pypdf loader.
    """
    
    pipeline_name = "DocumentIntelligence-RAG-Pipeline"
    
    # Create the agent/pipeline
    embedding_pipeline = Agent(name=pipeline_name)
    
    # Add PDF data source that will use Document Intelligence for text extraction
    embedding_pipeline.add(PDFDIDataSource(config={"files": pdf_paths}))
    
    # Add Document Intelligence configuration
    # This component provides the Azure DI credentials and settings
    embedding_pipeline.add(
        DocumentIntelligence(
            config={
                "azure_document_intelligence_endpoint": AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
                "azure_document_intelligence_key": AZURE_DOCUMENT_INTELLIGENCE_KEY,
                "model": AZURE_EXTRACTION_MODEL,  # Options: prebuilt-document, prebuilt-layout, prebuilt-read
            }
        )
    )
    
    # Add embedding model (same as regular pipeline)
    embedding_pipeline.add(
        AzureOpenAIEmbedding3LargeEmbeddingModel(
            config={
                "azure_api_key": AZURE_OPENAI_API_KEY,
                "azure_endpoint": AZURE_OPENAI_ENDPOINT,
                "azure_deployment": AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
                "openai_api_version": AZURE_OPENAI_API_VERSION,
            }
        )
    )
    
    # Add inference model (same as regular pipeline)
    embedding_pipeline.add(
        AzureOpenAIGPT4OInferenceModel(
            config={
                "azure_api_key": AZURE_OPENAI_API_KEY,
                "azure_endpoint": AZURE_OPENAI_ENDPOINT,
                "azure_deployment": AZURE_OPENAI_DEPLOYMENT_NAME,
                "openai_api_version": AZURE_OPENAI_API_VERSION,
                "temperature": "0",
            }
        )
    )
    
    # Add tracing (optional)
    if TRACE_API_KEY:
        embedding_pipeline.add(
            Trace(
                config={
                    "public_key": TRACE_API_KEY,
                }
            )
        )
    
    # Save the pipeline
    pipeline_data = embedding_pipeline.save()
    print(f"✅ Pipeline created successfully with ID: {pipeline_data.id}")
    
    return embedding_pipeline, pipeline_data.id


def preprocess_and_create_embeddings(pipeline):
    """
    Process the documents using Document Intelligence and create embeddings.
    """
    try:
        print("🔄 Processing documents with Azure Document Intelligence...")
        print("📄 This will extract text using advanced OCR and layout understanding...")
        
        # This will extract text using Azure Document Intelligence instead of pypdf
        result = pipeline.preprocess_data()
        
        print("✅ Document Intelligence extraction and embedding creation completed!")
        print(f"📊 Result: {result}")
        return result
    except Exception as e:
        print(f"❌ Error during preprocessing: {str(e)}")
        return None


def query_pipeline(pipeline, question):
    """
    Query the pipeline with a question.
    """
    try:
        session_id = "document_intelligence_demo_session"
        result = pipeline.invoke(
            question=question,
            session_id=session_id
        )
        print(f"❓ Question: {question}")
        print(f"💡 Answer: {result}")
        print("-" * 80)
        return result
    except Exception as e:
        print(f"❌ Error during query: {str(e)}")
        return None


def demo_regular_vs_di_comparison():
    """
    Demo function to show the difference between regular PDF processing and Document Intelligence.
    """
    print("\n" + "="*80)
    print("📋 DOCUMENT INTELLIGENCE VS REGULAR PDF PROCESSING")
    print("="*80)
    print()
    print("🔸 Regular PDF Processing (pypdf):")
    print("   - Basic text extraction")
    print("   - Limited OCR capabilities")
    print("   - May struggle with complex layouts")
    print("   - Fast but less accurate for scanned documents")
    print()
    print("🔸 Document Intelligence Processing:")
    print("   - Advanced OCR with layout understanding")
    print("   - Handles tables, forms, and complex structures")
    print("   - Better accuracy for scanned/complex documents")
    print("   - Multiple model options for different use cases")
    print()
    print("📊 Available Document Intelligence Models:")
    print("   - prebuilt-document: General document analysis")
    print("   - prebuilt-layout: Advanced layout analysis with tables")
    print("   - prebuilt-read: Optimized for text extraction")
    print("   - Custom models: For specific document types")
    print()


def main():
    """
    Main function demonstrating the Document Intelligence integration.
    """
    print("🚀 Azure Document Intelligence Integration Demo")
    print("=" * 60)
    
    # Show comparison
    demo_regular_vs_di_comparison()
    
    # Set up environment variables (in production, use proper env management)
    if not all([AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, 
                AZURE_DOCUMENT_INTELLIGENCE_KEY,
                AZURE_OPENAI_API_KEY,
                AZURE_OPENAI_ENDPOINT]):
        print("⚠️  Please configure your Azure credentials before running this example:")
        print("   - AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        print("   - AZURE_DOCUMENT_INTELLIGENCE_KEY")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - AZURE_OPENAI_ENDPOINT")
        return
    
    print("\n🏗️  Creating Document Intelligence pipeline...")
    pipeline, pipeline_id = create_document_intelligence_pipeline()
    
    print("\n🔄 Processing documents with Azure Document Intelligence...")
    preprocess_result = preprocess_and_create_embeddings(pipeline)
    
    if preprocess_result:
        print("\n💬 Querying the pipeline...")
        # Example questions that benefit from better text extraction
        questions = [
            "What is the main topic of the document?",
            "Can you summarize the key points?",
            "What are the important dates mentioned?",
            "Are there any tables or structured data in the document?",
            "What specific technical details are provided?"
        ]
        
        for question in questions:
            query_pipeline(pipeline, question)
    
    print("\n🎉 Document Intelligence integration demo completed!")
    print("\n📝 Key Benefits Demonstrated:")
    print("   ✅ Better text extraction quality")
    print("   ✅ Improved handling of complex documents")
    print("   ✅ Enhanced OCR capabilities")
    print("   ✅ Seamless integration with existing pipeline")


if __name__ == "__main__":
    main()


"""
Usage Instructions:

1. Install required dependencies:
   pip install azure-ai-formrecognizer

2. Configure your Azure credentials:
   - Azure Document Intelligence endpoint and key
   - Azure OpenAI API key and endpoint
   - Update the configuration variables at the top of this file

3. Prepare your PDF files:
   - Update the pdf_paths variable with your PDF file paths
   - Ensure the files exist and are accessible

4. Run the example:
   python document_intelligence_example.py

Key Differences from Regular PDF Processing:

1. Data Source: Use PDFDIDataSource instead of PDFDataSource
2. Configuration: Add DocumentIntelligence component with Azure DI credentials
3. Better Results: Azure Document Intelligence provides superior text extraction

Migration Requirements:

If you get an enum error, run this SQL command on your database:
ALTER TYPE configtype ADD VALUE 'DOCUMENT_INTELLIGENCE';

Or use the provided alembic migration:
alembic upgrade head
""" 