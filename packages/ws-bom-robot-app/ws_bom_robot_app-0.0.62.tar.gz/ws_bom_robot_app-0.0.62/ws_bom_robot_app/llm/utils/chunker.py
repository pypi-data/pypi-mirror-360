from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter

class DocumentChunker:
  @staticmethod
  def chunk(documents: list[Document]) -> list[Document]:
      text_splitter = CharacterTextSplitter(chunk_size=10_000, chunk_overlap=500)
      chunked_documents = []
      for doc in documents:
          chunks = text_splitter.split_text(doc.page_content)
          for chunk in chunks:
              chunked_documents.append(
                  Document(page_content=chunk, metadata=doc.metadata)
              )
      return chunked_documents
