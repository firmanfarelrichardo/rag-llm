"""
RAG Chain Module
Implements hybrid RAG logic with ChromaDB + Tavily Search fallback
"""

from typing import Dict, List, Optional, Tuple
import os

from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults


class HybridRAGChain:
    """Hybrid RAG implementation with local vector store and web search fallback"""
    
    def __init__(
        self,
        vectorstore: Optional[Chroma],
        groq_api_key: str,
        tavily_api_key: str,
        model_name: str = "llama-3.3-70b-versatile",
        relevance_threshold: float = 0.5
    ):
        """
        Initialize the hybrid RAG chain
        
        Args:
            vectorstore: ChromaDB vector store instance
            groq_api_key: Groq API key for Llama 3.3
            tavily_api_key: Tavily API key for web search
            model_name: Groq model name (llama-3.1-8b-instant or llama-3.3-70b-versatile)
            relevance_threshold: Minimum relevance score for using local docs
        """
        self.vectorstore = vectorstore
        self.relevance_threshold = relevance_threshold
        
        # Initialize Llama 3 via Groq
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model_name,
            temperature=0.7,
            max_tokens=2048
        )
        
        # Initialize Tavily Search
        self.search_tool = TavilySearchResults(
            tavily_api_key=tavily_api_key,
            max_results=3
        )
        
        # System prompt for Indonesian responses
        self.system_prompt = """Kamu adalah asisten AI yang sangat membantu dan profesional.

ATURAN PENTING:
1. Kamu HARUS SELALU menjawab dalam Bahasa Indonesia yang natural dan profesional
2. Kamu bisa membaca dokumen dalam Bahasa Inggris atau Indonesia
3. Berikan jawaban yang akurat berdasarkan konteks yang diberikan
4. Jika informasi berasal dari PDF lokal, sebutkan nama dokumen sebagai sumber
5. Jika informasi berasal dari pencarian web, sebutkan sumber webnya
6. Jika tidak yakin atau tidak ada informasi yang relevan, katakan dengan jujur
7. Gunakan format yang rapi dan mudah dibaca

Konteks yang tersedia:
{context}

Jawab pertanyaan pengguna dengan bijak dan profesional dalam Bahasa Indonesia."""
    
    def retrieve_from_vectorstore(self, query: str, k: int = 4) -> Tuple[List[Document], bool]:
        """
        Retrieve relevant documents from local vector store
        
        Args:
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            Tuple of (documents, is_relevant)
        """
        if self.vectorstore is None:
            return [], False
        
        try:
            # Retrieve with similarity scores
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            
            if not docs_with_scores:
                return [], False
            
            # Check relevance (lower score = more similar in Chroma)
            best_score = docs_with_scores[0][1]
            is_relevant = best_score < (1 - self.relevance_threshold)
            
            documents = [doc for doc, score in docs_with_scores]
            
            return documents, is_relevant
            
        except Exception as e:
            print(f"Error retrieving from vectorstore: {str(e)}")
            return [], False
    
    def search_web(self, query: str) -> List[Dict]:
        """
        Search the web using Tavily
        
        Args:
            query: User query
            
        Returns:
            List of search results
        """
        try:
            results = self.search_tool.invoke({"query": query})
            return results if results else []
        except Exception as e:
            print(f"Error searching web: {str(e)}")
            return []
    
    def format_context(self, documents: List[Document], web_results: List[Dict]) -> str:
        """
        Format context from documents and web results
        
        Args:
            documents: Retrieved documents from vector store
            web_results: Web search results
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add document context
        if documents:
            context_parts.append("=== INFORMASI DARI DOKUMEN LOKAL ===")
            for i, doc in enumerate(documents, 1):
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "N/A")
                context_parts.append(f"\n[Dokumen {i}: {source}, Halaman {page}]")
                context_parts.append(doc.page_content)
        
        # Add web results context
        if web_results:
            context_parts.append("\n\n=== INFORMASI DARI WEB ===")
            for i, result in enumerate(web_results, 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                content = result.get("content", "")
                context_parts.append(f"\n[Sumber Web {i}: {title}]")
                context_parts.append(f"URL: {url}")
                context_parts.append(content)
        
        return "\n".join(context_parts) if context_parts else "Tidak ada konteks yang tersedia."
    
    def generate_response(self, query: str, context: str) -> str:
        """
        Generate response using Llama 3
        
        Args:
            query: User query
            context: Formatted context
            
        Returns:
            Generated response
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{question}")
        ])
        
        try:
            # Format and invoke
            formatted_prompt = prompt.format_messages(
                context=context,
                question=query
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            return f"Maaf, terjadi kesalahan saat menghasilkan jawaban: {str(e)}"
    
    def ask(self, query: str) -> Dict[str, any]:
        """
        Main method: Hybrid RAG pipeline
        
        Args:
            query: User question
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        # Step 1: Try local retrieval first
        documents, is_relevant = self.retrieve_from_vectorstore(query)
        
        web_results = []
        used_web_search = False
        
        # Step 2: If local docs not relevant, use web search
        if not is_relevant:
            print("[INFO] Local docs not relevant. Triggering web search...")
            web_results = self.search_web(query)
            used_web_search = True
        else:
            print("[INFO] Using local documents...")
        
        # Step 3: Format context
        context = self.format_context(documents, web_results)
        
        # Step 4: Generate response
        response = self.generate_response(query, context)
        
        # Prepare sources
        sources = []
        if documents:
            sources.extend([
                f"{doc.metadata.get('source', 'Unknown')}" 
                for doc in documents
            ])
        if web_results:
            sources.extend([
                f"{result.get('title', 'Web')} - {result.get('url', '')}" 
                for result in web_results
            ])
        
        return {
            "response": response,
            "sources": list(set(sources)),  # Remove duplicates
            "used_web_search": used_web_search,
            "num_local_docs": len(documents),
            "num_web_results": len(web_results)
        }


def create_rag_chain(
    vectorstore: Optional[Chroma],
    groq_api_key: str,
    tavily_api_key: str,
    model_name: str = "llama-3.3-70b-versatile"
) -> HybridRAGChain:
    """
    Factory function to create RAG chain
    
    Args:
        vectorstore: ChromaDB vector store
        groq_api_key: Groq API key
        tavily_api_key: Tavily API key
        model_name: Model name
        
    Returns:
        HybridRAGChain instance
    """
    return HybridRAGChain(
        vectorstore=vectorstore,
        groq_api_key=groq_api_key,
        tavily_api_key=tavily_api_key,
        model_name=model_name
    )
