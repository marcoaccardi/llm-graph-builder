"""Main module for LLM Graph Builder.

This module provides the core functionality for extracting knowledge graphs from various
document sources including local files, cloud storage, web pages, and media platforms.
"""

import datetime
import json
import logging
import os
import re
import shutil
import sys
import time
import urllib.parse
import warnings

from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader, WikipediaLoader
from langchain_neo4j import Neo4jGraph

from src.create_chunks import CreateChunksofDocument
from src.document_sources.gcs_bucket import *
from src.document_sources.local_file import get_documents_from_file_by_path
from src.document_sources.s3_bucket import *
from src.document_sources.web_pages import *
from src.document_sources.wikipedia import *
from src.document_sources.youtube import *
from src.entities.source_node import sourceNode
from src.graphDB_dataAccess import graphDBdataAccess
from src.graph_query import get_graphDB_driver
from src.llm import get_graph_from_llm
from src.make_relationships import *
from src.shared.common_fn import *
from src.shared.constants import (
    BUCKET_FAILED_FILE, BUCKET_UPLOAD, DELETE_ENTITIES_AND_START_FROM_BEGINNING,
    PROJECT_ID, QUERY_TO_DELETE_EXISTING_ENTITIES,
    QUERY_TO_GET_LAST_PROCESSED_CHUNK_POSITION,
    QUERY_TO_GET_LAST_PROCESSED_CHUNK_WITHOUT_ENTITY,
    QUERY_TO_GET_NODES_AND_RELATIONS_OF_A_DOCUMENT, QUERY_TO_GET_CHUNKS,
    START_FROM_BEGINNING, START_FROM_LAST_PROCESSED_POSITION
)
from src.shared.llm_graph_builder_exception import LLMGraphBuilderException
from src.shared.schema_extraction import schema_extraction_from_text
from langchain.docstore.document import Document

warnings.filterwarnings("ignore")
load_dotenv()
logging.basicConfig(format='%(asctime)s - %(message)s',level='INFO')

def create_source_node_graph_url_s3(graph, model, source_url, aws_access_key_id, aws_secret_access_key, source_type):
    """
    Create source nodes for S3 bucket files in the graph database.

    Args:
        graph: Neo4j graph connection object
        model: AI model to use for processing
        source_url: S3 bucket URL
        aws_access_key_id: AWS access key for authentication
        aws_secret_access_key: AWS secret key for authentication
        source_type: Type of source (e.g., 's3')

    Returns:
        tuple: (file_list, success_count, failed_count)

    Raises:
        LLMGraphBuilderException: When no PDF files are found in the S3 bucket
    """
    file_list = []
    files_info = get_s3_files_info(source_url, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    if len(files_info) == 0:
        raise LLMGraphBuilderException('No pdf files found.')

    logging.info(f'files info : {files_info}')
    success_count = 0
    failed_count = 0

    for file_info in files_info:
        file_name = file_info['file_key']
        source_node = sourceNode()
        source_node.file_name = file_name.split('/')[-1].strip() if isinstance(file_name.split('/')[-1], str) else file_name.split('/')[-1]
        source_node.file_type = 'pdf'
        source_node.file_size = file_info['file_size_bytes']
        source_node.file_source = source_type
        source_node.model = model
        source_node.url = str(source_url + file_name)
        source_node.awsAccessKeyId = aws_access_key_id
        source_node.created_at = datetime.datetime.now()
        source_node.chunkNodeCount = 0
        source_node.chunkRelCount = 0
        source_node.entityNodeCount = 0
        source_node.entityEntityRelCount = 0
        source_node.communityNodeCount = 0
        source_node.communityRelCount = 0

        try:
            graph_db_access = graphDBdataAccess(graph)
            graph_db_access.create_source_node(source_node)
            success_count += 1
            file_list.append({
                'fileName': source_node.file_name,
                'fileSize': source_node.file_size,
                'url': source_node.url,
                'status': 'Success'
            })

        except Exception as e:
            failed_count += 1
            file_list.append({
                'fileName': source_node.file_name,
                'fileSize': source_node.file_size,
                'url': source_node.url,
                'status': 'Failed'
            })

    return file_list, success_count, failed_count

def create_source_node_graph_url_gcs(graph, model, gcs_project_id, gcs_bucket_name, gcs_bucket_folder, source_type, credentials):
    """
    Create source nodes for GCS bucket files in the graph database.

    Args:
        graph: Neo4j graph connection object
        model: AI model to use for processing
        gcs_project_id: Google Cloud project ID
        gcs_bucket_name: GCS bucket name
        gcs_bucket_folder: GCS bucket folder
        source_type: Type of source (e.g., 'gcs')
        credentials: Authentication credentials for GCS

    Returns:
        tuple: (file_list, success_count, failed_count)
    """
    success_count = 0
    failed_count = 0
    file_list = []

    file_metadata_list = get_gcs_bucket_files_info(gcs_project_id, gcs_bucket_name, gcs_bucket_folder, credentials)

    for file_metadata in file_metadata_list:
        source_node = sourceNode()
        source_node.file_name = file_metadata['fileName'].strip() if isinstance(file_metadata['fileName'], str) else file_metadata['fileName']
        source_node.file_size = file_metadata['fileSize']
        source_node.url = file_metadata['url']
        source_node.file_source = source_type
        source_node.model = model
        source_node.file_type = 'pdf'
        source_node.gcsBucket = gcs_bucket_name
        source_node.gcsBucketFolder = file_metadata['gcsBucketFolder']
        source_node.gcsProjectId = file_metadata['gcsProjectId']
        source_node.created_at = datetime.datetime.now()
        source_node.access_token = credentials.token
        source_node.chunkNodeCount = 0
        source_node.chunkRelCount = 0
        source_node.entityNodeCount = 0
        source_node.entityEntityRelCount = 0
        source_node.communityNodeCount = 0
        source_node.communityRelCount = 0

        try:
            graph_db_access = graphDBdataAccess(graph)
            graph_db_access.create_source_node(source_node)
            success_count += 1
            file_list.append({
                'fileName': source_node.file_name,
                'fileSize': source_node.file_size,
                'url': source_node.url,
                'status': 'Success',
                'gcsBucketName': gcs_bucket_name,
                'gcsBucketFolder': source_node.gcsBucketFolder,
                'gcsProjectId': source_node.gcsProjectId
            })
        except Exception as e:
            failed_count += 1
            file_list.append({
                'fileName': source_node.file_name,
                'fileSize': source_node.file_size,
                'url': source_node.url,
                'status': 'Failed',
                'gcsBucketName': gcs_bucket_name,
                'gcsBucketFolder': source_node.gcsBucketFolder,
                'gcsProjectId': source_node.gcsProjectId
            })

    return file_list, success_count, failed_count

def create_source_node_graph_web_url(graph, model, source_url, source_type):
    """
    Create source nodes for web page URLs in the graph database.

    Args:
        graph: Neo4j graph connection object
        model: AI model to use for processing
        source_url: Web page URL to process
        source_type: Type of source (e.g., 'web')

    Returns:
        tuple: (file_list, success_count, failed_count)

    Raises:
        LLMGraphBuilderException: When unable to load web page content
    """
    success_count = 0
    failed_count = 0
    file_list = []

    pages = WebBaseLoader(source_url, verify_ssl=False).load()

    if pages is None or len(pages) == 0:
        failed_count += 1
        message = f"Unable to read data for given url : {source_url}"
        raise LLMGraphBuilderException(message)

    try:
        title = pages[0].metadata['title'].strip()
        if title:
            graph_db_access = graphDBdataAccess(graph)
            existing_url = graph_db_access.get_websource_url(title)
            if existing_url != source_url:
                title = str(title) + "-" + str(last_url_segment(source_url)).strip()
        else:
            title = last_url_segment(source_url)
        language = pages[0].metadata['language']
    except:
        title = last_url_segment(source_url)
        language = "N/A"

    source_node = sourceNode()
    source_node.file_type = 'text'
    source_node.file_source = source_type
    source_node.model = model
    source_node.url = urllib.parse.unquote(source_url)
    source_node.created_at = datetime.datetime.now()
    source_node.file_name = title.strip() if isinstance(title, str) else title
    source_node.language = language
    source_node.file_size = sys.getsizeof(pages[0].page_content)
    source_node.chunkNodeCount = 0
    source_node.chunkRelCount = 0
    source_node.entityNodeCount = 0
    source_node.entityEntityRelCount = 0
    source_node.communityNodeCount = 0
    source_node.communityRelCount = 0

    graph_db_access = graphDBdataAccess(graph)
    graph_db_access.create_source_node(source_node)
    file_list.append({
        'fileName': source_node.file_name,
        'fileSize': source_node.file_size,
        'url': source_node.url,
        'status': 'Success'
    })
    success_count += 1

    return file_list, success_count, failed_count
  
def _update_source_node_and_get_chunks(graph_db_access, source_node, file_name, chunkId_chunkDoc_list, update_graph_chunk_processed):
    """
    Update source node status and prepare chunks for processing.

    Args:
        graph_db_access: Graph database access object
        source_node: Source node to update
        file_name: Name of the file being processed
        chunkId_chunkDoc_list: List of chunks to process
        update_graph_chunk_processed: Number of chunks to process at once

    Returns:
        None: This function updates the database but doesn't return chunks for processing
    """
    start_update = time.time()
    graph_db_access.update_source_node(source_node)
    graph_db_access.update_node_relationship_count(file_name)
    end_update = time.time()
    elapsed_update = end_update - start_update

    logging.info(f'Time taken to update the document source node: {elapsed_update:.2f} seconds')


def _create_basic_source_node(file_name, file_type, file_source, model, url, language="N/A"):
    """
    Create a basic source node with common properties.

    Args:
        file_name: Name of the file/document
        file_type: Type of file (e.g., 'text', 'pdf')
        file_source: Source type (e.g., 'youtube', 'wikipedia')
        model: AI model to use for processing
        url: URL of the source
        language: Language of the content

    Returns:
        sourceNode: Configured source node object
    """
    source_node = sourceNode()
    source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
    source_node.file_type = file_type
    source_node.file_source = file_source
    source_node.model = model
    source_node.url = url
    source_node.created_at = datetime.datetime.now()
    source_node.language = language
    source_node.chunkNodeCount = 0
    source_node.chunkRelCount = 0
    source_node.entityNodeCount = 0
    source_node.entityEntityRelCount = 0
    source_node.communityNodeCount = 0
    source_node.communityRelCount = 0
    return source_node


def _add_source_node_to_graph(graph, source_node, file_list, status):
    """
    Add a source node to the graph database and update the file list.

    Args:
        graph: Neo4j graph connection object
        source_node: Source node to add to graph
        file_list: List to append file information to
        status: Status ('Success' or 'Failed')

    Returns:
        int: 1 if successful, 0 if failed
    """
    try:
        graph_db_access = graphDBdataAccess(graph)
        graph_db_access.create_source_node(source_node)
        file_list.append({
            'fileName': source_node.file_name,
            'fileSize': source_node.file_size,
            'url': source_node.url,
            'status': status
        })
        return 1
    except Exception:
        file_list.append({
            'fileName': source_node.file_name,
            'fileSize': source_node.file_size,
            'url': source_node.url,
            'status': 'Failed'
        })
        return 0


def create_source_node_graph_url_youtube(graph, model, source_url, source_type):
    """
    Create source nodes for YouTube videos in the graph database.

    Args:
        graph: Neo4j graph connection object
        model: AI model to use for processing
        source_url: YouTube video URL
        source_type: Type of source (e.g., 'youtube')

    Returns:
        tuple: (file_list, success_count, failed_count)

    Raises:
        LLMGraphBuilderException: When YouTube transcript is not available
    """
    youtube_url, language = check_url_source(source_type=source_type, yt_url=source_url)
    success_count = 0
    failed_count = 0
    file_list = []

    source_node = _create_basic_source_node(
        file_name="",  # Will be set after extracting video ID
        file_type='text',
        file_source=source_type,
        model=model,
        url=youtube_url,
        language=language
    )

    match = re.search(r'(?:v=)([0-9A-Za-z_-]{11})\s*', source_node.url)
    logging.info(f"match value: {match}")

    if match:
        video_id = match.group(1)
        source_node.file_name = video_id
        transcript = get_youtube_combined_transcript(video_id)
        logging.info(f"YouTube transcript : {transcript}")

        if transcript is None or len(transcript) == 0:
            message = f"YouTube transcript is not available for : {video_id}"
            raise LLMGraphBuilderException(message)
        else:
            source_node.file_size = sys.getsizeof(transcript)

        success_count += _add_source_node_to_graph(graph, source_node, file_list, 'Success')
    else:
        failed_count += 1
        file_list.append({
            'fileName': 'Unknown',
            'fileSize': 0,
            'url': source_node.url,
            'status': 'Failed'
        })

    return file_list, success_count, failed_count

def create_source_node_graph_url_wikipedia(graph, model, wiki_query, source_type):
    """
    Create source nodes for Wikipedia articles in the graph database.

    Args:
        graph: Neo4j graph connection object
        model: AI model to use for processing
        wiki_query: Wikipedia query or article title
        source_type: Type of source (e.g., 'wikipedia')

    Returns:
        tuple: (file_list, success_count, failed_count)

    Raises:
        LLMGraphBuilderException: When unable to load Wikipedia article
    """
    success_count = 0
    failed_count = 0
    file_list = []

    wiki_query_id, language = check_url_source(source_type=source_type, wiki_query=wiki_query)
    logging.info(f"Creating source node for {wiki_query_id.strip()}, {language}")

    pages = WikipediaLoader(query=wiki_query_id.strip(), lang=language, load_max_docs=1, load_all_available_meta=True).load()

    if pages is None or len(pages) == 0:
        failed_count += 1
        message = f"Unable to read data for given Wikipedia url : {wiki_query}"
        raise LLMGraphBuilderException(message)
    else:
        source_node = _create_basic_source_node(
            file_name=wiki_query_id.strip(),
            file_type='text',
            file_source=source_type,
            model=model,
            url=urllib.parse.unquote(pages[0].metadata['source']),
            language=language
        )
        source_node.file_size = sys.getsizeof(pages[0].page_content)

        success_count += _add_source_node_to_graph(graph, source_node, file_list, 'Success')
        file_list[-1]['language'] = language

    return file_list, success_count, failed_count
    
async def extract_graph_from_file_local_file(uri, userName, password, database, model, merged_file_path, fileName, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):

  logging.info(f'Process file name :{fileName}')
  if not retry_condition:
    gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
    if gcs_file_cache == 'True':
      folder_name = create_gcs_bucket_folder_name_hashed(uri, fileName)
      file_name, pages = get_documents_from_gcs( PROJECT_ID, BUCKET_UPLOAD, folder_name, fileName)
    else:
      file_name, pages, file_extension = get_documents_from_file_by_path(merged_file_path,fileName)
    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'File content is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, True, merged_file_path, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, fileName, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, True, merged_file_path, retry_condition, additional_instructions=additional_instructions)
  
async def extract_graph_from_file_s3(uri, userName, password, database, model, source_url, aws_access_key_id, aws_secret_access_key, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    if(aws_access_key_id==None or aws_secret_access_key==None):
      raise LLMGraphBuilderException('Please provide AWS access and secret keys')
    else:
      logging.info("Insert in S3 Block")
      file_name, pages = get_documents_from_s3(source_url, aws_access_key_id, aws_secret_access_key)

    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'File content is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, file_name, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)
  
async def extract_graph_from_web_page(uri, userName, password, database, model, source_url, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    pages = get_documents_from_web_page(source_url)
    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'Content is not available for given URL : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, file_name, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)
  
async def extract_graph_from_file_youtube(uri, userName, password, database, model, source_url, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    file_name, pages = get_documents_from_youtube(source_url)

    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'Youtube transcript is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
     return await processing_source(uri, userName, password, database, model, file_name, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)
    
async def extract_graph_from_file_Wikipedia(uri, userName, password, database, model, wiki_query, language, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    file_name, pages = get_documents_from_Wikipedia(wiki_query, language)
    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'Wikipedia page is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, file_name,[], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)

async def extract_graph_from_file_gcs(uri, userName, password, database, model, gcs_project_id, gcs_bucket_name, gcs_bucket_folder, gcs_blob_filename, access_token, file_name, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition, additional_instructions):
  if not retry_condition:
    file_name, pages = get_documents_from_gcs(gcs_project_id, gcs_bucket_name, gcs_bucket_folder, gcs_blob_filename, access_token)
    if pages==None or len(pages)==0:
      raise LLMGraphBuilderException(f'File content is not available for file : {file_name}')
    return await processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, additional_instructions=additional_instructions)
  else:
    return await processing_source(uri, userName, password, database, model, file_name, [], allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, retry_condition=retry_condition, additional_instructions=additional_instructions)
  
def _initialize_processing(uri, userName, password, database):
    """
    Initialize the processing by creating database connection and setting up logging.

    Args:
        uri: Database connection URI
        userName: Username for authentication
        password: Password for authentication
        database: Database name

    Returns:
        tuple: (graph, graph_db_access, start_time, processing_start_time, uri_latency)
    """
    start_time = datetime.datetime.now()
    processing_start_time = time.time()
    start_create_connection = time.time()

    graph = create_graph_database_connection(uri, userName, password, database)
    end_create_connection = time.time()
    elapsed_create_connection = end_create_connection - start_create_connection

    logging.info(f'Time taken database connection: {elapsed_create_connection:.2f} seconds')

    uri_latency = {
        "create_connection": f'{elapsed_create_connection:.2f}'
    }

    graph_db_access = graphDBdataAccess(graph)
    create_chunk_vector_index(graph)

    return graph, graph_db_access, start_time, processing_start_time, uri_latency


def _get_chunks_and_initialize_processing(graph, file_name, pages, token_chunk_size, chunk_overlap, retry_condition):
    """
    Get chunks from documents and initialize processing timing.

    Args:
        graph: Neo4j graph connection object
        file_name: Name of the file being processed
        pages: Document pages
        token_chunk_size: Size of chunks in tokens
        chunk_overlap: Overlap between chunks
        retry_condition: Retry condition flag

    Returns:
        tuple: (total_chunks, chunkId_chunkDoc_list, uri_latency_info)
    """
    start_get_chunk_list = time.time()
    total_chunks, chunkId_chunkDoc_list = get_chunkId_chunkDoc_list(graph, file_name, pages, token_chunk_size, chunk_overlap, retry_condition)
    end_get_chunk_list = time.time()
    elapsed_get_chunk_list = end_get_chunk_list - start_get_chunk_list

    logging.info(f'Time taken to create list chunkids with chunk document: {elapsed_get_chunk_list:.2f} seconds')

    uri_latency_info = {
        "create_list_chunk_and_document": f'{elapsed_get_chunk_list:.2f}',
        "total_chunks": total_chunks
    }

    return total_chunks, chunkId_chunkDoc_list, uri_latency_info


def _get_document_status(graph_db_access, file_name):
    """
    Get the current status of the document node.

    Args:
        graph_db_access: Graph database access object
        file_name: Name of the file to check

    Returns:
        tuple: (result, elapsed_time)
    """
    start_status = time.time()
    result = graph_db_access.get_current_status_document_node(file_name)
    end_status = time.time()
    elapsed_status = end_status - start_status

    logging.info(f'Time taken to get the current status of document node: {elapsed_status:.2f} seconds')

    return result, elapsed_status


def _create_processing_source_node(file_name, total_chunks, model, retry_condition, result):
    """
    Create a source node for processing with appropriate initial values.

    Args:
        file_name: Name of the file being processed
        total_chunks: Total number of chunks
        model: AI model to use
        retry_condition: Retry condition flag
        result: Existing document status result

    Returns:
        tuple: (source_node, node_count, rel_count, select_chunks_with_retry)
    """
    source_node = sourceNode()
    source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
    source_node.status = "Processing"
    source_node.total_chunks = total_chunks
    source_node.model = model

    node_count = 0
    rel_count = 0
    select_chunks_with_retry = 0

    if retry_condition == START_FROM_LAST_PROCESSED_POSITION:
        node_count = result[0]['nodeCount']
        rel_count = result[0]['relationshipCount']
        select_chunks_with_retry = result[0]['processed_chunk']

    source_node.processed_chunk = 0 + select_chunks_with_retry

    return source_node, node_count, rel_count, select_chunks_with_retry


async def processing_source(uri, userName, password, database, model, file_name, pages, allowedNodes, allowedRelationship, token_chunk_size, chunk_overlap, chunks_to_combine, is_uploaded_from_local=None, merged_file_path=None, retry_condition=None, additional_instructions=None):
    """
    Extracts a Neo4jGraph from a PDF file based on the model.

    Args:
        uri: URI of the graph to extract
        userName: Username to use for graph creation (if None will use username from config file)
        password: Password to use for graph creation (if None will use password from config file)
        database: Database name
        model: Type of model to use ('Ollama LLM')
        file_name: Name of the file to process
        pages: Document pages to process
        allowedNodes: Allowed node types
        allowedRelationship: Allowed relationship types
        token_chunk_size: Size of chunks in tokens
        chunk_overlap: Overlap between chunks
        chunks_to_combine: Number of chunks to combine
        is_uploaded_from_local: Whether file was uploaded from local storage
        merged_file_path: Path to merged file (if local upload)
        retry_condition: Retry condition flag
        additional_instructions: Additional instructions for processing

    Returns:
        tuple: (uri_latency, response) with processing metrics and results
    """
    # Initialize processing
    graph, graph_db_access, start_time, processing_start_time, uri_latency = _initialize_processing(uri, userName, password, database)

    # Get chunks and initialize processing
    total_chunks, chunkId_chunkDoc_list, chunk_latency_info = _get_chunks_and_initialize_processing(
        graph, file_name, pages, token_chunk_size, chunk_overlap, retry_condition
    )
    uri_latency.update(chunk_latency_info)

    # Get document status
    result, status_elapsed_time = _get_document_status(graph_db_access, file_name)
    uri_latency["get_status_document_node"] = f'{status_elapsed_time:.2f}'

    # Check if document can be processed
    if len(result) == 0:
        error_message = "Unable to get the status of document node."
        logging.error(error_message)
        raise LLMGraphBuilderException(error_message)

    if result[0]['Status'] == 'Processing':
        logging.info("File does not process because its already in Processing status")
        return uri_latency, {}

    # Create and update source node
    source_node, node_count, rel_count, select_chunks_with_retry = _create_processing_source_node(
        file_name, total_chunks, model, retry_condition, result
    )

    # Update source node status
    _update_source_node_and_get_chunks(
        graph_db_access, source_node, file_name, chunkId_chunkDoc_list,
        int(os.environ.get('UPDATE_GRAPH_CHUNKS_PROCESSED', 10))
    )

    # Process chunks
    job_status = "Completed"
    for i in range(0, len(chunkId_chunkDoc_list), int(os.environ.get('UPDATE_GRAPH_CHUNKS_PROCESSED', 10))):
        select_chunks_upto = min(i + int(os.environ.get('UPDATE_GRAPH_CHUNKS_PROCESSED', 10)), len(chunkId_chunkDoc_list))
        selected_chunks = chunkId_chunkDoc_list[i:select_chunks_upto]

        # Check if processing was cancelled
        result = graph_db_access.get_current_status_document_node(file_name)
        is_cancelled_status = result[0]['is_cancelled']
        if bool(is_cancelled_status):
            job_status = "Cancelled"
            break

        # Process the selected chunks
        processing_chunks_start_time = time.time()
        node_count, rel_count, latency_processed_chunk = await processing_chunks(
            selected_chunks, graph, uri, userName, password, database, file_name, model,
            allowedNodes, allowedRelationship, chunks_to_combine, node_count, rel_count, additional_instructions
        )
        processing_chunks_end_time = time.time()
        processing_chunks_elapsed_time = processing_chunks_end_time - processing_chunks_start_time

        uri_latency[f'processed_combine_chunk_{i}-{select_chunks_upto}'] = f'{processing_chunks_elapsed_time:.2f}'
        uri_latency[f'processed_chunk_detail_{i}-{select_chunks_upto}'] = latency_processed_chunk

    # Finalize processing
    end_time = datetime.datetime.now()
    processed_time = end_time - start_time

    # Update final source node status
    final_source_node = sourceNode()
    final_source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
    final_source_node.status = job_status
    final_source_node.processing_time = processed_time
    final_source_node.node_count = node_count
    final_source_node.relationship_count = rel_count

    graph_db_access.update_source_node(final_source_node)
    graph_db_access.update_node_relationship_count(file_name)

    # Clean up temporary files if needed
    if is_uploaded_from_local:
        gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
        if gcs_file_cache == 'True':
            folder_name = create_gcs_bucket_folder_name_hashed(uri, file_name)
            delete_file_from_gcs(BUCKET_UPLOAD, folder_name, file_name)
        else:
            delete_uploaded_local_file(merged_file_path, file_name)

    # Calculate final metrics
    processing_source_func = time.time() - processing_start_time
    uri_latency["Processed_source"] = f'{processing_source_func:.2f}'
    uri_latency["Per_entity_latency"] = 'N/A' if node_count == 0 else f'{int(processing_source_func)/node_count}/s'

    # Create response
    response = {
        "fileName": file_name,
        "nodeCount": node_count,
        "relationshipCount": rel_count,
        "total_processing_time": round(processed_time.total_seconds(), 2),
        "status": job_status,
        "model": model,
        "success_count": 1
    }

    return uri_latency, response

async def processing_chunks(chunkId_chunkDoc_list, graph, uri, userName, password, database, file_name, model, allowedNodes, allowedRelationship, chunks_to_combine, node_count, rel_count, additional_instructions=None):
    """
    Process document chunks to extract knowledge graphs and update the database.

    Args:
        chunkId_chunkDoc_list: List of chunk IDs and documents
        graph: Neo4j graph connection object
        uri: Database connection URI
        userName: Username for authentication
        password: Password for authentication
        database: Database name
        file_name: Name of the file being processed
        model: AI model to use for extraction
        allowedNodes: Allowed node types
        allowedRelationship: Allowed relationship types
        chunks_to_combine: Number of chunks to combine
        node_count: Current node count
        rel_count: Current relationship count
        additional_instructions: Additional instructions for processing

    Returns:
        tuple: (node_count, rel_count, latency_processing_chunk)
    """
    latency_processing_chunk = {}

    # Ensure graph connection is active
    if graph is None or (hasattr(graph, '_driver') and graph._driver._closed):
        graph = create_graph_database_connection(uri, userName, password, database)

    # Update chunk embeddings
    start_update_embedding = time.time()
    create_chunk_embeddings(graph, chunkId_chunkDoc_list, file_name)
    end_update_embedding = time.time()
    elapsed_update_embedding = end_update_embedding - start_update_embedding

    logging.info(f'Time taken to update embedding in chunk node: {elapsed_update_embedding:.2f} seconds')
    latency_processing_chunk["update_embedding"] = f'{elapsed_update_embedding:.2f}'

    # Extract entities using LLM
    start_entity_extraction = time.time()
    graph_documents = await get_graph_from_llm(model, chunkId_chunkDoc_list, allowedNodes, allowedRelationship, chunks_to_combine, additional_instructions)
    end_entity_extraction = time.time()
    elapsed_entity_extraction = end_entity_extraction - start_entity_extraction

    logging.info(f'Time taken to extract entities from LLM Graph Builder: {elapsed_entity_extraction:.2f} seconds')
    latency_processing_chunk["entity_extraction"] = f'{elapsed_entity_extraction:.2f}'

    # Clean and save graph documents
    cleaned_graph_documents = handle_backticks_nodes_relationship_id_type(graph_documents)

    start_save_graph_documents = time.time()
    save_graphDocuments_in_neo4j(graph, cleaned_graph_documents)
    end_save_graph_documents = time.time()
    elapsed_save_graph_documents = end_save_graph_documents - start_save_graph_documents

    logging.info(f'Time taken to save graph document in neo4j: {elapsed_save_graph_documents:.2f} seconds')
    latency_processing_chunk["save_graphDocuments"] = f'{elapsed_save_graph_documents:.2f}'

    # Create relationships between chunks and entities
    chunks_and_graph_documents_list = get_chunk_and_graphDocument(cleaned_graph_documents, chunkId_chunkDoc_list)

    start_relationship = time.time()
    merge_relationship_between_chunk_and_entites(graph, chunks_and_graph_documents_list)
    end_relationship = time.time()
    elapsed_relationship = end_relationship - start_relationship

    logging.info(f'Time taken to create relationship between chunk and entities: {elapsed_relationship:.2f} seconds')
    latency_processing_chunk["relationship_between_chunk_entity"] = f'{elapsed_relationship:.2f}'

    # Update node and relationship counts
    graph_db_access = graphDBdataAccess(graph)
    count_response = graph_db_access.update_node_relationship_count(file_name)
    node_count = count_response[file_name].get('nodeCount', "0")
    rel_count = count_response[file_name].get('relationshipCount', "0")

    return node_count, rel_count, latency_processing_chunk

def get_chunkId_chunkDoc_list(graph, file_name, pages, token_chunk_size, chunk_overlap, retry_condition):
  if not retry_condition:
    logging.info("Break down file into chunks")
    bad_chars = ['"', "\n", "'"]
    for i in range(0,len(pages)):
      text = pages[i].page_content
      for j in bad_chars:
        if j == '\n':
          text = text.replace(j, ' ')
        else:
          text = text.replace(j, '')
      pages[i]=Document(page_content=str(text), metadata=pages[i].metadata)
    create_chunks_obj = CreateChunksofDocument(pages, graph)
    chunks = create_chunks_obj.split_file_into_chunks(token_chunk_size, chunk_overlap)
    chunkId_chunkDoc_list = create_relation_between_chunks(graph,file_name,chunks)
    return len(chunks), chunkId_chunkDoc_list
  
  else:  
    chunkId_chunkDoc_list=[]
    chunks =  execute_graph_query(graph,QUERY_TO_GET_CHUNKS, params={"filename":file_name})
    
    if chunks[0]['text'] is None or chunks[0]['text']=="" or not chunks :
      raise LLMGraphBuilderException(f"Chunks are not created for {file_name}. Please re-upload file and try again.")    
    else:
      for chunk in chunks:
        chunk_doc = Document(page_content=chunk['text'], metadata={'id':chunk['id'], 'position':chunk['position']})
        chunkId_chunkDoc_list.append({'chunk_id': chunk['id'], 'chunk_doc': chunk_doc})
      
      if retry_condition ==  START_FROM_LAST_PROCESSED_POSITION:
        logging.info(f"Retry : start_from_last_processed_position")
        starting_chunk = execute_graph_query(graph,QUERY_TO_GET_LAST_PROCESSED_CHUNK_POSITION, params={"filename":file_name})
        
        if starting_chunk and starting_chunk[0]["position"] < len(chunkId_chunkDoc_list):
          return len(chunks), chunkId_chunkDoc_list[starting_chunk[0]["position"] - 1:]
        
        elif starting_chunk and starting_chunk[0]["position"] == len(chunkId_chunkDoc_list):
          starting_chunk =  execute_graph_query(graph,QUERY_TO_GET_LAST_PROCESSED_CHUNK_WITHOUT_ENTITY, params={"filename":file_name})
          return len(chunks), chunkId_chunkDoc_list[starting_chunk[0]["position"] - 1:]
        
        else:
          raise LLMGraphBuilderException(f"All chunks of file {file_name} are already processed. If you want to re-process, Please start from begnning")    
      
      else:
        logging.info(f"Retry : start_from_beginning with chunks {len(chunkId_chunkDoc_list)}")    
        return len(chunks), chunkId_chunkDoc_list
  
def get_source_list_from_graph(uri,userName,password,db_name=None):
  """
  Args:
    uri: URI of the graph to extract
    db_name: db_name is database name to connect to graph db
    userName: Username to use for graph creation ( if None will use username from config file )
    password: Password to use for graph creation ( if None will use password from config file )
    file: File object containing the PDF file to be used
    model: Type of model to use ('Ollama LLM')
  Returns:
   Returns a list of sources that are in the database by querying the graph and
   sorting the list by the last updated date. 
 """
  logging.info("Get existing files list from graph")
  graph = Neo4jGraph(url=uri, database=db_name, username=userName, password=password)
  graph_DB_dataAccess = graphDBdataAccess(graph)
  if not graph._driver._closed:
      logging.info(f"closing connection for sources_list api")
      graph._driver.close()
  return graph_DB_dataAccess.get_source_list()

def update_graph(graph):
  """
  Update the graph node with SIMILAR relationship where embedding scrore match
  """
  graph_DB_dataAccess = graphDBdataAccess(graph)
  graph_DB_dataAccess.update_KNN_graph()

  
def connection_check_and_get_vector_dimensions(graph,database):
  """
  Args:
    uri: URI of the graph to extract
    userName: Username to use for graph creation ( if None will use username from config file )
    password: Password to use for graph creation ( if None will use password from config file )
    db_name: db_name is database name to connect to graph db
  Returns:
   Returns a status of connection from NEO4j is success or failure
 """
  graph_DB_dataAccess = graphDBdataAccess(graph)
  return graph_DB_dataAccess.connection_check_and_get_vector_dimensions(database)

def merge_chunks_local(file_name, total_chunks, chunk_dir, merged_dir):

  if not os.path.exists(merged_dir):
      os.mkdir(merged_dir)
  logging.info(f'Merged File Path: {merged_dir}')
  merged_file_path = os.path.join(merged_dir, file_name)
  with open(merged_file_path, "wb") as write_stream:
      for i in range(1,total_chunks+1):
          chunk_file_path = os.path.join(chunk_dir, f"{file_name}_part_{i}")
          logging.info(f'Chunk File Path While Merging Parts:{chunk_file_path}')
          with open(chunk_file_path, "rb") as chunk_file:
              shutil.copyfileobj(chunk_file, write_stream)
          os.unlink(chunk_file_path)  # Delete the individual chunk file after merging
  logging.info("Chunks merged successfully and return file size")
  
  file_size = os.path.getsize(merged_file_path)
  return file_size
  


def upload_file(graph, model, chunk, chunk_number:int, total_chunks:int, originalname, uri, chunk_dir, merged_dir):
  
  gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
  logging.info(f'gcs file cache: {gcs_file_cache}')
  
  if gcs_file_cache == 'True':
    folder_name = create_gcs_bucket_folder_name_hashed(uri,originalname)
    upload_file_to_gcs(chunk, chunk_number, originalname, BUCKET_UPLOAD, folder_name)
  else:
    if not os.path.exists(chunk_dir):
      os.mkdir(chunk_dir)
    
    chunk_file_path = os.path.join(chunk_dir, f"{originalname}_part_{chunk_number}")
    logging.info(f'Chunk File Path: {chunk_file_path}')
    
    with open(chunk_file_path, "wb") as chunk_file:
      chunk_file.write(chunk.file.read())

  if int(chunk_number) == int(total_chunks):
      # If this is the last chunk, merge all chunks into a single file
      if gcs_file_cache == 'True':
        file_size = merge_file_gcs(BUCKET_UPLOAD, originalname, folder_name, int(total_chunks))
      else:
        file_size = merge_chunks_local(originalname, int(total_chunks), chunk_dir, merged_dir)
      
      logging.info("File merged successfully")
      file_extension = originalname.split('.')[-1]
      obj_source_node = sourceNode()
      obj_source_node.file_name = originalname.strip() if isinstance(originalname, str) else originalname
      obj_source_node.file_type = file_extension
      obj_source_node.file_size = file_size
      obj_source_node.file_source = 'local file'
      obj_source_node.model = model
      obj_source_node.created_at = datetime.datetime.now()
      obj_source_node.chunkNodeCount=0
      obj_source_node.chunkRelCount=0
      obj_source_node.entityNodeCount=0
      obj_source_node.entityEntityRelCount=0
      obj_source_node.communityNodeCount=0
      obj_source_node.communityRelCount=0
      graphDb_data_Access = graphDBdataAccess(graph)
        
      graphDb_data_Access.create_source_node(obj_source_node)
      return {'file_size': file_size, 'file_name': originalname, 'file_extension':file_extension, 'message':f"Chunk {chunk_number}/{total_chunks} saved"}
  return f"Chunk {chunk_number}/{total_chunks} saved"

def get_labels_and_relationtypes(uri, userName, password, database):
  excluded_labels = {'Document', 'Chunk', '_Bloom_Perspective_', '__Community__', '__Entity__', 'Session', 'Message'}
  excluded_relationships = {
       'NEXT_CHUNK', '_Bloom_Perspective_', 'FIRST_CHUNK',
       'SIMILAR', 'IN_COMMUNITY', 'PARENT_COMMUNITY', 'NEXT', 'LAST_MESSAGE'
   }
  driver = get_graphDB_driver(uri, userName, password,database) 
  triples = set()
  with driver.session(database=database) as session:
    result = session.run("""
           MATCH (n)-[r]->(m)
           RETURN DISTINCT labels(n) AS fromLabels, type(r) AS relType, labels(m) AS toLabels
       """)
    for record in result:
      from_labels = record["fromLabels"]
      to_labels = record["toLabels"]
      rel_type = record["relType"]
      from_label = next((lbl for lbl in from_labels if lbl not in excluded_labels), None)
      to_label = next((lbl for lbl in to_labels if lbl not in excluded_labels), None)
      if not from_label or not to_label:
          continue
      if rel_type == 'PART_OF':
          if from_label == 'Chunk' and to_label == 'Document':
              continue 
      elif rel_type == 'HAS_ENTITY':
          if from_label == 'Chunk':
              continue 
      elif (
          from_label in excluded_labels or
          to_label in excluded_labels or
          rel_type in excluded_relationships
      ):
          continue
      triples.add(f"{from_label}-{rel_type}->{to_label}")
  return {"triplets": list(triples)}

def manually_cancelled_job(graph, filenames, source_types, merged_dir, uri):
  
  filename_list= list(map(str.strip, json.loads(filenames)))
  source_types_list= list(map(str.strip, json.loads(source_types)))
  gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
  
  for (file_name,source_type) in zip(filename_list, source_types_list):
      obj_source_node = sourceNode()
      obj_source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
      obj_source_node.is_cancelled = True
      obj_source_node.status = 'Cancelled'
      obj_source_node.updated_at = datetime.datetime.now()
      graphDb_data_Access = graphDBdataAccess(graph)
      graphDb_data_Access.update_source_node(obj_source_node)
      count_response = graphDb_data_Access.update_node_relationship_count(file_name)
      obj_source_node = None
      merged_file_path = os.path.join(merged_dir, file_name)
      if source_type == 'local file' and gcs_file_cache == 'True':
          folder_name = create_gcs_bucket_folder_name_hashed(uri, file_name)
          delete_file_from_gcs(BUCKET_UPLOAD,folder_name,file_name)
      else:
        logging.info(f'Deleted File Path: {merged_file_path} and Deleted File Name : {file_name}')
        delete_uploaded_local_file(merged_file_path,file_name)
  return "Cancelled the processing job successfully"

def populate_graph_schema_from_text(text, model, is_schema_description_checked, is_local_storage):
  """_summary_

  Args:
      graph (Neo4Graph): Neo4jGraph connection object
      input_text (str): rendom text from PDF or user input.
      model (str): AI model to use extraction from text

  Returns:
      data (list): list of lebels and relationTypes
  """
  result = schema_extraction_from_text(text, model, is_schema_description_checked, is_local_storage)
  return result

def set_status_retry(graph, file_name, retry_condition):
    graphDb_data_Access = graphDBdataAccess(graph)
    obj_source_node = sourceNode()
    status = "Ready to Reprocess"
    obj_source_node.file_name = file_name.strip() if isinstance(file_name, str) else file_name
    obj_source_node.status = status
    obj_source_node.retry_condition = retry_condition
    obj_source_node.is_cancelled = False
    if retry_condition == DELETE_ENTITIES_AND_START_FROM_BEGINNING or retry_condition == START_FROM_BEGINNING:
        obj_source_node.processed_chunk=0
    if retry_condition == DELETE_ENTITIES_AND_START_FROM_BEGINNING:
        execute_graph_query(graph,QUERY_TO_DELETE_EXISTING_ENTITIES, params={"filename":file_name})
        obj_source_node.node_count=0
        obj_source_node.relationship_count=0
    logging.info(obj_source_node)
    graphDb_data_Access.update_source_node(obj_source_node)

def failed_file_process(uri,file_name, merged_file_path):
  gcs_file_cache = os.environ.get('GCS_FILE_CACHE')
  if gcs_file_cache == 'True':
      folder_name = create_gcs_bucket_folder_name_hashed(uri,file_name)
      copy_failed_file(BUCKET_UPLOAD, BUCKET_FAILED_FILE, folder_name, file_name)
      time.sleep(5)
      delete_file_from_gcs(BUCKET_UPLOAD,folder_name,file_name)
  else:
      logging.info(f'Deleted File Path: {merged_file_path} and Deleted File Name : {file_name}')
      delete_uploaded_local_file(merged_file_path,file_name)