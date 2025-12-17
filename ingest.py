"""
Data Ingestion Module
Handles automatic loading of PDFs from data/ folder and embedding into ChromaDB
"""

import os
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


class DataIngestor:
    """Handles automatic data ingestion from local folder"""
    
    def __init__(self, data_folder: str = "data", persist_directory: str = "chroma_db"):
        """
        Initialize the data ingestor
        
        Args:
            data_folder: Path to folder containing PDFs
            persist_directory: Path to persist ChromaDB
        """
        self.data_folder = Path(data_folder)
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
    def get_pdf_files(self) -> List[Path]:
        """
        Get all PDF files from the data folder
        
        Returns:
            List of PDF file paths
        """
        if not self.data_folder.exists():
            self.data_folder.mkdir(parents=True, exist_ok=True)
            return []
            
        pdf_files = list(self.data_folder.glob("*.pdf"))
        return pdf_files
    
    def load_documents(self, pdf_files: List[Path]) -> List[Document]:
        """
        Load and extract text from PDF files
        
        Args:
            pdf_files: List of PDF file paths
            
        Returns:
            List of Document objects
        """
        all_documents = []
        
        for pdf_path in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_path))
                documents = loader.load()
                
                # Add source metadata
                for doc in documents:
                    doc.metadata["source"] = pdf_path.name
                    
                all_documents.extend(documents)
                print(f"[OK] Loaded: {pdf_path.name} ({len(documents)} pages)")
            except Exception as e:
                print(f"[ERROR] Loading {pdf_path.name}: {str(e)}")
                
        return all_documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks for better retrieval
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"[OK] Created {len(chunks)} text chunks")
        return chunks
    
    def create_vector_store(self, chunks: List[Document]) -> Chroma:
        """
        Create or load ChromaDB vector store
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Chroma vector store instance
        """
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print(f"[OK] Vector store created/updated at: {self.persist_directory}")
        return vectorstore
    
    def load_existing_vector_store(self) -> Optional[Chroma]:
        """
        Load existing ChromaDB if it exists
        
        Returns:
            Chroma vector store instance or None
        """
        if os.path.exists(self.persist_directory):
            try:
                vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print(f"[OK] Loaded existing vector store from: {self.persist_directory}")
                return vectorstore
            except Exception as e:
                print(f"[ERROR] Loading vector store: {str(e)}")
                return None
        return None
    
    def ingest(self, force_rebuild: bool = False) -> Optional[Chroma]:
        """
        Main ingestion pipeline: Check for PDFs, load, chunk, and embed
        
        Args:
            force_rebuild: If True, rebuild vector store even if it exists
            
        Returns:
            Chroma vector store instance or None if no data
        """
        print("\n" + "="*60)
        print("[INFO] Starting Data Ingestion Process...")
        print("="*60)
        
        # Check for existing vector store
        if not force_rebuild:
            existing_store = self.load_existing_vector_store()
            if existing_store is not None:
                pdf_files = self.get_pdf_files()
                print(f"[OK] Found {len(pdf_files)} PDF files in data/ folder")
                return existing_store
        
        # Get PDF files
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            print("[WARNING] No PDF files found in data/ folder")
            print(f"[INFO] Please add PDF files to: {self.data_folder.absolute()}")
            return None
        
        print(f"[OK] Found {len(pdf_files)} PDF files")
        
        # Load documents
        print("\n[INFO] Loading PDF documents...")
        documents = self.load_documents(pdf_files)
        
        if not documents:
            print("[WARNING] No documents could be loaded")
            return None
        
        # Chunk documents
        print("\n[INFO] Chunking documents...")
        chunks = self.chunk_documents(documents)
        
        # Create vector store
        print("\n[INFO] Creating embeddings and vector store...")
        vectorstore = self.create_vector_store(chunks)
        
        print("\n" + "="*60)
        print("[SUCCESS] Data Ingestion Complete!")
        print("="*60 + "\n")
        
        return vectorstore


def initialize_vector_store(force_rebuild: bool = False) -> Optional[Chroma]:
    """
    Convenience function to initialize the vector store
    
    Args:
        force_rebuild: If True, rebuild vector store even if it exists
        
    Returns:
        Chroma vector store instance or None
    """
    ingestor = DataIngestor()
    return ingestor.ingest(force_rebuild=force_rebuild)
