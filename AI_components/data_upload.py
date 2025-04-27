import os
import argparse
import json
from pathlib import Path
import docling
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from data_indexing import openai_index

def extract_text_from_document(file_path):
    """
    Extract text content from various document types using docling.
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        str: Extracted text content
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Create a document converter with support for various formats
    doc_converter = DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.DOCX,
            InputFormat.CSV,
            InputFormat.XLSX,
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=StandardPdfPipeline, 
                backend=PyPdfiumDocumentBackend
            ),
            InputFormat.DOCX: WordFormatOption(
                pipeline_cls=SimplePipeline
            ),
        }
    )
    
    # Convert the document
    conv_results = doc_converter.convert_all([file_path])
    
    # Process the generator results
    for result in conv_results:
        # Extract text content
        text_content = result.document.export_to_text()
        return text_content
    
    # If we get here, no results were processed
    raise ValueError(f"Failed to convert document: {file_path}")

def process_document(file_path, output_path=None):
    """
    Process a document, extract text, and index the data.
    
    Args:
        file_path (str): Path to the document file
        output_path (str, optional): Path to save the indexed data
        
    Returns:
        dict: Indexed data
    """
    # Extract text from document
    extracted_text = extract_text_from_document(file_path)
    
    # Index the extracted text
    indexed_data = openai_index(extracted_text)
    
    # Save to file if output path is provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(indexed_data, f, indent=2)
        print(f"Indexed data saved to: {output_path}")
    
    return indexed_data

def main():
    parser = argparse.ArgumentParser(description='Process and index document data')
    parser.add_argument('file_path', help='Path to the document file')
    parser.add_argument('--output', '-o', help='Path to save the indexed data (optional)')
    
    args = parser.parse_args()
    
    try:
        indexed_data = process_document(args.file_path, args.output)
        print("Document processed successfully!")
        if not args.output:
            print("Indexed data:")
            print(json.dumps(indexed_data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()