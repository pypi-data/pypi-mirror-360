"""This module stores document vectors into the AstraDB vector store."""

import os
from os import getenv
import click
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_astradb import AstraDBVectorStore
from langchain_cohere import CohereEmbeddings

from main.helper.pdf import save_online_pdf
from main.helper.web_crawl import crawler
from main.helper.creditionals import read_db_config
from main.helper.spinner import spinner

COHERE_API_KEY = getenv("COHERE_API_KEY")

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def store_vectors(pdf_or_web, url, collection_name, namespace):
    """Store document vectors into the AstraDB vector store."""
    db_config = read_db_config()
    pdf_path = ""

    if pdf_or_web == "pdf":
        pdf_path = save_online_pdf(url)
    elif pdf_or_web == "web":
        pdf_path = crawler(url)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    pdf_loader = PyPDFLoader(pdf_path)
    documents = pdf_loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    embeddings = CohereEmbeddings(
        model="embed-english-v3.0",  # This returns 1024-dimensional vectors
        cohere_api_key=COHERE_API_KEY
    )

    # Check embedding dimensions
    sample_text = docs[0].page_content if docs else "test"
    sample_vector = embeddings.embed_query(sample_text)
    vector_dim = len(sample_vector)

    logger.info(f"Sample embedding dimension: {vector_dim}")
    if vector_dim != 1024:
        raise ValueError(f"Embedding dimension mismatch: expected 1024, got {vector_dim}")

    spinner()

    vectorstore = AstraDBVectorStore(
        collection_name=collection_name,
        embedding=embeddings,
        api_endpoint=db_config.api_endpoint,
        token=db_config.token,
        namespace=namespace,
    )

    vectorstore.add_documents(documents=docs)
    os.remove(pdf_path)

    click.echo(click.style("Stored vector embeddings ✅", fg="green"))
