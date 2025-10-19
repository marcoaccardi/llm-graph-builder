import hashlib
import logging
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import os
import re
import time
from langchain_community.graphs.graph_document import GraphDocument
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph
from neo4j.exceptions import TransientError
from src.document_sources.youtube import create_youtube_url


# Constants
DEFAULT_EMBEDDING_DIMENSION = 384
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1
DEFAULT_QUERY_RETRY_DELAY = 2


def validate_and_extract_youtube_url(youtube_url: str) -> str:
    """
    Validate and process a YouTube URL.

    Args:
        youtube_url: The YouTube URL to validate and process

    Returns:
        str: The processed YouTube URL

    Raises:
        ValueError: If the URL is not a valid YouTube URL
    """
    if not youtube_url or not youtube_url.strip():
        raise ValueError("YouTube URL cannot be empty")

    youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?'

    if re.match(youtube_pattern, youtube_url.strip()):
        processed_url = create_youtube_url(youtube_url.strip())
        logging.info(f"Valid YouTube URL processed: {processed_url}")
        return processed_url
    else:
        raise ValueError("Invalid YouTube URL format")


def extract_wikipedia_query_info(wikipedia_url: str) -> tuple[str, str]:
    """
    Extract query ID and language from a Wikipedia URL.

    Args:
        wikipedia_url: The Wikipedia URL to parse

    Returns:
        tuple: (query_id, language) extracted from the URL

    Raises:
        ValueError: If the URL is not a valid Wikipedia URL
    """
    if not wikipedia_url or not wikipedia_url.strip():
        raise ValueError("Wikipedia URL cannot be empty")

    # Pattern to match Wikipedia URLs
    wikipedia_pattern = r'https?:\/\/(www\.)?([a-zA-Z]{2,3})\.wikipedia\.org\/wiki\/(.*)'

    match = re.search(wikipedia_pattern, wikipedia_url.strip())
    if match:
        language = match.group(2)
        query_id = match.group(3)
        logging.info(f"Wikipedia query ID extracted: {query_id}, Language: {language}")
        return query_id, language
    else:
        raise ValueError(f"Invalid Wikipedia URL: {wikipedia_url}")


def check_url_source(source_type: str, yt_url: str = None, wiki_query: str = None) -> tuple[str, str]:
    """
    Validate and parse URLs based on source type.

    Args:
        source_type: Type of source ('youtube' or 'Wikipedia')
        yt_url: YouTube URL (required if source_type is 'youtube')
        wiki_query: Wikipedia URL (required if source_type is 'Wikipedia')

    Returns:
        tuple: (processed_url_or_id, language) - URL for YouTube, query ID for Wikipedia

    Raises:
        ValueError: If validation fails or required parameters are missing
    """
    try:
        if source_type == 'youtube':
            if not yt_url:
                raise ValueError("YouTube URL is required for youtube source type")
            processed_url = validate_and_extract_youtube_url(yt_url)
            return processed_url, ''

        elif source_type == 'Wikipedia':
            if not wiki_query:
                raise ValueError("Wikipedia URL is required for Wikipedia source type")
            return extract_wikipedia_query_info(wiki_query)

        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    except Exception as e:
        logging.error(f"URL validation failed: {e}")
        raise


def get_chunk_and_graphDocument(graph_document_list: List[GraphDocument], chunkId_chunkDoc_list) -> List[dict]:
    """
    Create a mapping between graph documents and their chunks.

    Args:
        graph_document_list: List of graph documents to process

    Returns:
        List[dict]: List of mappings containing graph document and chunk ID pairs
    """
    logging.info("Creating chunk-to-graph document mapping")
    chunk_document_mapping = []

    for graph_document in graph_document_list:
        if hasattr(graph_document.source, 'metadata') and 'combined_chunk_ids' in graph_document.source.metadata:
            for chunk_id in graph_document.source.metadata['combined_chunk_ids']:
                chunk_document_mapping.append({
                    'graph_doc': graph_document,
                    'chunk_id': chunk_id
                })

    return chunk_document_mapping


def create_graph_database_connection(uri: str, userName: str, password: str, database: str) -> Neo4jGraph:
    """
    Create a Neo4j graph database connection with optional user agent configuration.

    Args:
        uri: Database connection URI
        username: Database username
        password: Database password
        database: Database name

    Returns:
        Neo4jGraph: Configured Neo4j graph database connection
    """
    enable_user_agent = os.environ.get("ENABLE_USER_AGENT", "False").lower() in ("true", "1", "yes")

    connection_params = {
        'url': uri,
        'database': database,
        'username': userName,
        'password': password,
        'refresh_schema': False,
        'sanitize': True
    }

    if enable_user_agent:
        user_agent = os.environ.get('NEO4J_USER_AGENT')
        if user_agent:
            connection_params['driver_config'] = {'user_agent': user_agent}

    graph = Neo4jGraph(**connection_params)
    return graph


def load_embedding_model(embedding_model_name: str = None) -> tuple[HuggingFaceEmbeddings, int]:
    """
    Load embedding model based on configuration.

    Supported models:
    - 'all-MiniLM-L6-v2': Default model (384 dimensions)
    - 'mxbai-embed-large': Advanced model (1024 dimensions)

    Set EMBEDDING_MODEL environment variable to choose:
    EMBEDDING_MODEL="all-MiniLM-L6-v2"  # For default model
    EMBEDDING_MODEL="mxbai-embed-large" # For advanced model

    Args:
        embedding_model_name: Name of the embedding model to load.
                           If None, uses EMBEDDING_MODEL environment variable
                           or defaults to 'all-MiniLM-L6-v2'

    Returns:
        tuple: (embeddings, dimension) - configured embeddings and their dimension
    """
    # Determine which model to use
    if embedding_model_name is None:
        embedding_model_name = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    if embedding_model_name == "mxbai-embed-large":
        # MixedBread AI's mxbai-embed-large-v1 (1024 dimensions)
        # Better multilingual support and semantic understanding
        embeddings = HuggingFaceEmbeddings(
            model_name="mixedbread-ai/mxbai-embed-large-v1",
            cache_folder="./embedding_model"
        )
        dimension = 1024
        logging.info(f"Embedding: Using mxbai-embed-large (1024D)")
        return embeddings, dimension
    else:
        # Default: all-MiniLM-L6-v2 (384 dimensions)
        # Lightweight and fast, good for most use cases
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            cache_folder="./embedding_model"
        )
        dimension = 384
        logging.info(f"Embedding: Using all-MiniLM-L6-v2 (384D)")
        return embeddings, dimension


def save_graphDocuments_in_neo4j(
    graph: Neo4jGraph,
    graph_document_list: List[GraphDocument],
    max_retries: int = DEFAULT_MAX_RETRIES,
    delay: int = DEFAULT_RETRY_DELAY
) -> None:
    """
    Save graph documents to Neo4j with retry logic for deadlock handling.

    Args:
        graph: Neo4j graph database connection
        graph_document_list: List of graph documents to save
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Raises:
        RuntimeError: If all retry attempts fail due to persistent deadlocks
    """
    retries = 0
    while retries < max_retries:
        try:
            graph.add_graph_documents(graph_document_list, baseEntityLabel=True)
            return
        except TransientError as e:
            if "DeadlockDetected" in str(e):
                retries += 1
                logging.info(f"Deadlock detected. Retrying {retries}/{max_retries} in {delay} seconds...")
                time.sleep(delay)
            else:
                raise

    logging.error("Failed to save graph documents after maximum retries due to persistent deadlocks.")
    raise RuntimeError("Failed to save graph documents after multiple retries due to deadlock.")


def handle_backticks_nodes_relationship_id_type(graph_document_list: List[GraphDocument]) -> List[GraphDocument]:
    """
    Clean backticks from node and relationship types in graph documents.

    Args:
        graph_document_list: List of graph documents to clean

    Returns:
        List[GraphDocument]: List of cleaned graph documents
    """
    for graph_document in graph_document_list:
        # Clean node types and IDs
        cleaned_nodes = []
        for node in graph_document.nodes:
            if node.type.strip() and node.id.strip():
                node.type = node.type.replace('`', '')
                cleaned_nodes.append(node)

        # Clean relationship types and node references
        cleaned_relationships = []
        for relationship in graph_document.relationships:
            if (relationship.type.strip() and
                relationship.source.id.strip() and
                relationship.source.type.strip() and
                relationship.target.id.strip() and
                relationship.target.type.strip()):

                relationship.type = relationship.type.replace('`', '')
                relationship.source.type = relationship.source.type.replace('`', '')
                relationship.target.type = relationship.target.type.replace('`', '')
                cleaned_relationships.append(relationship)

        graph_document.relationships = cleaned_relationships
        graph_document.nodes = cleaned_nodes

    return graph_document_list


def execute_graph_query(graph: Neo4jGraph, query: str, params: dict = None, max_retries: int = DEFAULT_MAX_RETRIES, delay: int = DEFAULT_QUERY_RETRY_DELAY) -> List[dict]:
    """
    Execute a graph query with retry logic for deadlock handling.

    Args:
        graph: Neo4j graph database connection
        query: Cypher query to execute
        params: Query parameters
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        List[dict]: Query results

    Raises:
        RuntimeError: If all retry attempts fail due to persistent deadlocks
    """
    retries = 0
    while retries < max_retries:
        try:
            return graph.query(query, params)
        except TransientError as e:
            if "DeadlockDetected" in str(e):
                retries += 1
                logging.info(f"Deadlock detected. Retrying {retries}/{max_retries} in {delay} seconds...")
                time.sleep(delay)
            else:
                raise

    logging.error("Failed to execute query after maximum retries due to persistent deadlocks.")
    raise RuntimeError("Query execution failed after multiple retries due to deadlock.")


def delete_uploaded_local_file(merged_file_path: str, file_name: str) -> None:
    """
    Delete an uploaded local file if it exists.

    Args:
        merged_file_path: Full path to the file to delete
        file_name: Name of the file (for logging purposes)
    """
    file_path = Path(merged_file_path)
    if file_path.exists():
        file_path.unlink()
        logging.info(f"File {file_name} deleted successfully")


def close_db_connection(graph: Neo4jGraph, api_name: str) -> None:
    """
    Close a database connection if it's still open.

    Args:
        graph: Neo4j graph database connection to close
        api_name: Name of the API (for logging purposes)
    """
    if not graph._driver._closed:
        logging.info(f"Closing connection for {api_name} API")
        # graph._driver.close()


def create_gcs_bucket_folder_name_hashed(uri: str, file_name: str) -> str:
    """
    Create a SHA1 hash for GCS bucket folder name.

    Args:
        uri: URI component for the folder name
        file_name: File name component for the folder name

    Returns:
        str: SHA1 hash of the combined folder name
    """
    folder_name = uri + file_name
    folder_name_sha1 = hashlib.sha1(folder_name.encode())
    return folder_name_sha1.hexdigest()


def formatted_time(current_time) -> str:
    """
    Format a datetime object to a standardized string format.

    Args:
        current_time: datetime object to format

    Returns:
        str: Formatted time string
    """
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    return str(formatted_time)


def last_url_segment(url: str) -> str:
    """
    Extract the last segment from a URL path.

    Args:
        url: URL to parse

    Returns:
        str: Last segment of the URL path, or domain prefix if no path
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.strip("/")  # Remove leading and trailing slashes
    return path.split("/")[-1] if path else parsed_url.netloc.split(".")[0]