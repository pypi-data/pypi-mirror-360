"""This module stores document vectors into the AstraDB vector store."""
import os
import logging

import click
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_astradb import AstraDBVectorStore
from langchain_cohere import CohereEmbeddings

from main.helper.pdf import save_online_pdf
from main.helper.web_crawl import crawler
from main.helper.creditionals import read_db_config
from main.helper.spinner import spinner

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_and_split_document(pdf_path):
    """Load and split the PDF into smaller text chunks."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(documents)


def validate_embedding(embeddings, docs):
    """Ensure the embedding model returns 1024-dim vectors."""
    sample_text = docs[0].page_content if docs else "test"
    sample_vector = embeddings.embed_query(sample_text)
    dim = len(sample_vector)
    logger.info("Sample embedding dimension: %d", dim)
    if dim != 1024:
        raise ValueError(f"Embedding dimension mismatch: expected 1024, got {dim}")


async def store_vectors(pdf_or_web, url, collection_name, namespace, cohere_api_key):
    """Store document vectors into the AstraDB vector store."""
    db_config = read_db_config()

    if pdf_or_web == "pdf":
        pdf_path = save_online_pdf(url)
    elif pdf_or_web == "web":
        pdf_path = crawler(url)
    else:
        raise ValueError("pdf_or_web must be either 'pdf' or 'web'")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    docs = load_and_split_document(pdf_path)

    embeddings = CohereEmbeddings(
        model="embed-english-v3.0",
        cohere_api_key=cohere_api_key
    )

    validate_embedding(embeddings, docs)

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
