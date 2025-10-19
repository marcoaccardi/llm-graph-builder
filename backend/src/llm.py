import logging
from langchain.docstore.document import Document
import os
from langchain_community.chat_models import ChatOllama
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs.graph_document import GraphDocument
from langchain_community.graphs.graph_document import (
    Node as Neo4jNode,
    Relationship as Neo4jRelationship,
)
from src.shared.constants import ADDITIONAL_INSTRUCTIONS
from src.shared.llm_graph_builder_exception import LLMGraphBuilderException
import re
from typing import List

def get_llm(model: str):
    """Retrieve the specified language model based on the model name."""
    model = model.lower().strip()
    env_key = f"LLM_MODEL_CONFIG_{model}"
    env_value = os.environ.get(env_key)

    if not env_value:
        err = f"Environment variable '{env_key}' is not defined as per format or missing"
        logging.error(err)
        raise Exception(err)

    logging.info("Model: {}".format(env_key))
    try:
        if "ollama" in model:
            model_name, base_url = env_value.split(",")
            llm = ChatOllama(base_url=base_url, model=model_name)
        else:
            # Default to Ollama if no specific provider matched
            model_name, base_url = env_value.split(",")
            llm = ChatOllama(base_url=base_url, model=model_name)
    except Exception as e:
        err = f"Error while creating LLM '{model}': {str(e)}"
        logging.error(err)
        raise Exception(err)

    logging.info(f"Model created - Model Version: {model}")
    return llm, model_name

def get_llm_model_name(llm):
    """Extract name of llm model from llm object"""
    for attr in ["model_name", "model", "model_id"]:
        model_name = getattr(llm, attr, None)
        if model_name:
            return model_name.lower()
    print("Could not determine model name; defaulting to empty string")
    return ""

def get_combined_chunks(chunkId_chunkDoc_list, chunks_to_combine):
    combined_chunk_document_list = []
    combined_chunks_page_content = [
        "".join(
            document["chunk_doc"].page_content
            for document in chunkId_chunkDoc_list[i : i + chunks_to_combine]
        )
        for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
    ]
    combined_chunks_ids = [
        [
            document["chunk_id"]
            for document in chunkId_chunkDoc_list[i : i + chunks_to_combine]
        ]
        for i in range(0, len(chunkId_chunkDoc_list), chunks_to_combine)
    ]

    for i in range(len(combined_chunks_page_content)):
        combined_chunk_document_list.append(
            Document(
                page_content=combined_chunks_page_content[i],
                metadata={"combined_chunk_ids": combined_chunks_ids[i]},
            )
        )
    return combined_chunk_document_list

def get_chunk_id_as_doc_metadata(chunkId_chunkDoc_list):
    combined_chunk_document_list = [
       Document(
           page_content=document["chunk_doc"].page_content,
           metadata={"chunk_id": [document["chunk_id"]]},
       )
       for document in chunkId_chunkDoc_list
   ]
    return combined_chunk_document_list
      

async def get_graph_document_list(
    llm, combined_chunk_document_list, allowedNodes, allowedRelationship, additional_instructions=None
):
    if additional_instructions:
        additional_instructions = sanitize_additional_instruction(additional_instructions)
    graph_document_list = []

    # For local Ollama models, always use simplified transformer configuration
    node_properties = False
    relationship_properties = False

    TOOL_SUPPORTED_MODELS = {"qwen3", "deepseek"}
    model_name = get_llm_model_name(llm)
    ignore_tool_usage = not any(pattern in model_name for pattern in TOOL_SUPPORTED_MODELS)
    logging.info(f"Keeping ignore tool usage parameter as {ignore_tool_usage}")
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        node_properties=node_properties,
        relationship_properties=relationship_properties,
        allowed_nodes=allowedNodes,
        allowed_relationships=allowedRelationship,
        ignore_tool_usage=ignore_tool_usage,
        additional_instructions=ADDITIONAL_INSTRUCTIONS+ (additional_instructions if additional_instructions else "")
    )

    graph_document_list = await llm_transformer.aconvert_to_graph_documents(combined_chunk_document_list)
    return graph_document_list

async def get_graph_from_llm(model, chunkId_chunkDoc_list, allowedNodes, allowedRelationship, chunks_to_combine, additional_instructions=None):
   try:
       llm, model_name = get_llm(model)
       logging.info(f"Using model: {model_name}")
    
       combined_chunk_document_list = get_combined_chunks(chunkId_chunkDoc_list, chunks_to_combine)
       logging.info(f"Combined {len(combined_chunk_document_list)} chunks")
    
       allowed_nodes = [node.strip() for node in allowedNodes.split(',') if node.strip()]
       logging.info(f"Allowed nodes: {allowed_nodes}")
    
       allowed_relationships = []
       if allowedRelationship:
           items = [item.strip() for item in allowedRelationship.split(',') if item.strip()]
           if len(items) % 3 != 0:
               raise LLMGraphBuilderException("allowedRelationship must be a multiple of 3 (source, relationship, target)")
           for i in range(0, len(items), 3):
               source, relation, target = items[i:i + 3]
               if source not in allowed_nodes or target not in allowed_nodes:
                   raise LLMGraphBuilderException(
                       f"Invalid relationship ({source}, {relation}, {target}): "
                       f"source or target not in allowedNodes"
                   )
               allowed_relationships.append((source, relation, target))
           logging.info(f"Allowed relationships: {allowed_relationships}")
       else:
           logging.info("No allowed relationships provided")

       graph_document_list = await get_graph_document_list(
           llm,
           combined_chunk_document_list,
           allowed_nodes,
           allowed_relationships,
           additional_instructions
       )
       logging.info(f"Generated {len(graph_document_list)} graph documents")
       return graph_document_list
   except Exception as e:
       logging.error(f"Error in get_graph_from_llm: {e}", exc_info=True)
       raise LLMGraphBuilderException(f"Error in getting graph from llm: {e}")

def sanitize_additional_instruction(instruction: str) -> str:
   """
   Sanitizes additional instruction by:
   - Replacing curly braces `{}` with `[]` to prevent variable interpretation.
   - Removing potential injection patterns like `os.getenv()`, `eval()`, `exec()`.
   - Stripping problematic special characters.
   - Normalizing whitespace.
   Args:
       instruction (str): Raw additional instruction input.
   Returns:
       str: Sanitized instruction safe for LLM processing.
   """
   logging.info("Sanitizing additional instructions")
   instruction = instruction.replace("{", "[").replace("}", "]")  # Convert `{}` to `[]` for safety
   # Step 2: Block dangerous function calls
   injection_patterns = [r"os\.getenv\(", r"eval\(", r"exec\(", r"subprocess\.", r"import os", r"import subprocess"]
   for pattern in injection_patterns:
       instruction = re.sub(pattern, "[BLOCKED]", instruction, flags=re.IGNORECASE)
   # Step 4: Normalize spaces
   instruction = re.sub(r'\s+', ' ', instruction).strip()
   return instruction
