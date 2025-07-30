import os, logging, traceback
from typing import Any, Iterator, AsyncIterator, Optional, Union
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_core.runnables import run_in_executor
from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption, ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions, TableFormerMode, TesseractCliOcrOptions
from langchain_community.document_loaders import UnstructuredFileLoader

class DoclingLoader(BaseLoader):
  def __init__(self, file_path: str | list[str], **kwargs: Any) -> None:
      self._file_paths = file_path if isinstance(file_path, list) else [file_path]
      self._converter = DocumentConverter(format_options={
            InputFormat.PDF: PdfFormatOption(
              pipeline_options=PdfPipelineOptions(
                table_structure_options=TableStructureOptions(mode=TableFormerMode.ACCURATE)
            )),
            InputFormat.IMAGE: ImageFormatOption(
              pipeline_options=PdfPipelineOptions(
                ocr_options=TesseractCliOcrOptions(lang=["auto"]),
                table_structure_options=TableStructureOptions(mode=TableFormerMode.ACCURATE)
            ))
        })
      self._kwargs = kwargs
  def load(self) -> list[Document]:
      """Load data into Document objects."""
      return list(self.lazy_load())
  async def aload(self) -> list[Document]:
      """Load data into Document objects."""
      return [document async for document in self.alazy_load()]
  async def alazy_load(self) -> AsyncIterator[Document]:
      """A lazy loader for Documents."""
      iterator = await run_in_executor(None, self.lazy_load)
      done = object()
      while True:
          doc = await run_in_executor(None, next, iterator, done)  # type: ignore[call-arg, arg-type]
          if doc is done:
              break
          yield doc  # type: ignore[misc]
  def lazy_load(self) -> Iterator[Document]:
      for source in self._file_paths:
          try:
            _result = self._converter.convert(
               os.path.abspath(source),
               raises_on_error=True)
            doc = _result.document
            text = doc.export_to_markdown(image_placeholder="")
            yield Document(page_content=text, metadata={"source": source})
          except Exception as e:
            if 'fallback' in self._kwargs:
                if issubclass(self._kwargs['fallback'], (BaseLoader, UnstructuredFileLoader)):
                  logging.info(f"Using fallback loader {self._kwargs['fallback']} for {source}")
                  try:
                    loader: Union[BaseLoader, UnstructuredFileLoader] = self._kwargs['fallback'](
                       source,
                       **{k: v for k, v in self._kwargs.items() if k != 'fallback'}
                       )
                    yield from loader.lazy_load()
                  except Exception as e:
                    logging.warning(f"Failed to load document from {source}: {e} | {traceback.format_exc()}")
                else:
                   logging.warning(f"Invalid fallback loader {self._kwargs['fallback']}[{type(self._kwargs['fallback'])}] for {source}")
            else:
              logging.warning(f"Failed to load document from {source}: {e} | {traceback.format_exc()}")
