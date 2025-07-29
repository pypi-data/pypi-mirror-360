import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, List

import google.genai.types as types
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from google.adk.tools import ToolContext
from google.cloud import bigquery, storage

from ai_fashion_house.utils.gcp_utils import get_authenticated_genai_client
from ai_fashion_house.utils.image_utils import pil_image_to_png_bytes, create_moodboard

logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
load_dotenv(find_dotenv())

FONTS_FOLDER = Path(__file__).resolve().parents[2] / "assets/fonts"
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

BIGQUERY_DATASET_ID = os.getenv("BIGQUERY_DATASET_ID")
BIGQUERY_EMBEDDINGS_MODEL_ID = os.getenv("BIGQUERY_EMBEDDINGS_MODEL_ID")
BIGQUERY_REGION= os.getenv("BIGQUERY_REGION", "US")
BIGQUERY_VECTOR_INDEX_ID = os.getenv("BIGQUERY_VECTOR_INDEX_ID")
BIGQUERY_TABLE_ID = os.getenv("BIGQUERY_TABLE_ID")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Initialize Clients ---
bq_client = bigquery.Client(project=GOOGLE_PROJECT_ID, location=BIGQUERY_REGION)
gcs_client = storage.Client(project=GOOGLE_PROJECT_ID)
genai_client = get_authenticated_genai_client()


def execute_sql_bigquery(sql: str) -> pd.DataFrame:
    """
    Executes a BigQuery SQL query and returns the results as a DataFrame.

    Args:
        sql (str): SQL query to execute.

    Returns:
        pd.DataFrame: Results from the executed query.

    Raises:
        RuntimeError: If the query execution fails.
    """
    try:
        job = bq_client.query(sql)
        result = job.result()
        logger.info(f"[✅] Query succeeded: Job ID {job.job_id}")
        return result.to_dataframe()
    except Exception as e:
        logger.exception(f"[❌] Query failed: {e}")
        raise


def enhance_query(query: str) -> str:
    """
    Enhances the user query by appending additional context for fashion-related searches,
    using a Gemini model to reformulate the query for better alignment with a RAG system.

    Args:
        query (str): Original user query.

    Returns:
        str: Reformulated query suited for structured image caption retrieval.
    """
    rag_query_prompt = f"""
        Given the user query: 
        
        {query}
        
        Reformulate this query to better align with a Retrieval-Augmented Generation (RAG) system that indexes image captions generated using the following structure:
        
        Caption Format:
        - Overall Impression
        - Fabric and Print
        - Color Palette
        - Bodice
        - Sleeves
        - Skirt
        
        Metadata Included When Available:
        - Culture
        - Period
        - Artist
        - Medium
        - Date (start - end)
        
        Description Style:
        - Full sentences written in a fluent, fashion-specific tone
        - No bullet points or introductory phrases
        - If metadata is missing, Culture and Period are emphasized
        
        Instructions:
        1. Rephrase the user query into a fashion-aware, semantically rich prompt to match the structured caption content.
        2. Expand references to styles, eras, or design inspirations into concrete visual or historical elements (e.g., “New Look” → “cinched waist, full skirt, post-war elegance”), **but only if such references are explicitly or clearly implied by the user query**.
        3. Use vocabulary aligned with how dress descriptions are written (materials, silhouettes, fashion movements, cultural references).
        4. **Do not guess or fabricate metadata or dress features not present in the original query.** Focus only on enhancing what's provided.
        5. Ensure the reformulated query supports retrieval even if only partial metadata is available in the captions.

        Example:
        - User Query: “Help me design a dress inspired by 1950s New Look”
        - Reformulated: “Describe dresses from the 1950s with cinched waists, voluminous skirts, and elegant post-war silhouettes characteristic of the New Look style, focusing on fabric, bodice structure, and color palette.”
    """

    # Run prompt through Gemini model
    response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Part.from_text(text=rag_query_prompt)]
    )

    # Safely extract text
    return response.text.strip() if response.text else query




def search_fashion_embeddings(query: str, top_k: int = 6, search_fraction: float = 0.01) -> pd.DataFrame:
    """
    Performs a vector similarity search using a fashion-related query on a BigQuery embedding table.

    Args:
        query (str): Text to embed and search against the vector database.
        top_k (int, optional): Number of top results to return. Defaults to 6.
        search_fraction (float, optional): Fraction of the vector index to search. Defaults to 0.01.

    Returns:
        pd.DataFrame: A DataFrame with matching content, distances, and image URLs.
    """
    query = enhance_query(query)
    sql = f"""
    SELECT 
    base.object_id,
    base.object_name,
    base.object_begin_date,
    base.object_end_date,
    base.content, 
    base.gcs_url, 
    query.query, 
    distance
    FROM VECTOR_SEARCH(
        TABLE `{GOOGLE_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{BIGQUERY_TABLE_ID}_embeddings`,
        'text_embedding',
        (
            SELECT text_embedding, content AS query
            FROM ML.GENERATE_TEXT_EMBEDDING(
                MODEL `{GOOGLE_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{BIGQUERY_EMBEDDINGS_MODEL_ID}`,
                (SELECT "{query}" AS content)
            )
        ),
        top_k => {top_k},
        OPTIONS => '{{"fraction_lists_to_search": {search_fraction}}}'
    )
    """
    return execute_sql_bigquery(sql)

async def retrieve_met_images(user_query: str, top_k: int = 6, search_fraction: float = 0.01, tool_context: ToolContext = None) -> dict:
    """
    Orchestrates the full RAG pipeline: refines the user query, retrieves similar embeddings,
    and returns a list of matching GCS image URLs.

    Also generates a moodboard of the top results.

    Args:
        user_query (str): Initial query string describing the desired fashion style.
        top_k (int, optional): Number of top image results to return. Defaults to 6.
        search_fraction (float, optional): Search scope for approximate vector match. Defaults to 0.01.
        tool_context (ToolContext, optional): Context for tool execution, if needed.

    Returns:
        Optional[List[str]]: A list of GCS URLs to matching images, or None if no matches found.
    """
    try:
        results = search_fashion_embeddings(user_query , top_k=top_k, search_fraction=search_fraction)
        if results.empty:
            logger.warning("[⚠️] No matches found.")
            return {
                "status": "no_results",
                "message": "No matching images found for the given query."
            }

        logger.info(f"[✅] Retrieved {len(results)} matching results.")

        image_urls = results['gcs_url'].dropna().tolist()
        moodboard_image = create_moodboard(
            image_urls,
            gcs_client=gcs_client,
            watermark_position="center",
            moodboard_watermark_text="Fashion Moodboard — Inspired by The Met Collection",
            moodboard_watermark_font_ratio=0.06,
            moodboard_watermark_font_path=str(FONTS_FOLDER / "GreatVibes-Regular.ttf"),
        )
        if tool_context:
            # Save moodboard to GCS if tool context is provided
            moodboard_artifact_part = types.Part.from_bytes(mime_type="image/png",data=pil_image_to_png_bytes(moodboard_image))
            await tool_context.save_artifact("moodboard.png", moodboard_artifact_part)
            met_rag_results = types.Part.from_bytes(
                mime_type="text/csv",
                data=results.to_csv(index=False).encode('utf-8')
            )
            await tool_context.save_artifact("met_rag_results.csv", met_rag_results)

        # Save moodboard locally if no tool context is provided
        output_folder = Path(os.getenv("OUTPUT_FOLDER", "outputs"))
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file = output_folder / "moodboard.png"
        moodboard_image.save(output_file)
        logger.info(f"[🖼️] Moodboard saved @ {output_file}")
        return {
            "status": "success",
            "result": image_urls,
        }
    except Exception as e:
        logger.error(f"[❌] Error during retrieval: {e}")
        return {
            "status": "error",
            "message": str(e),
        }


def run_retrieve_met_images_sync(
    user_query: str,
    top_k: int = 6,
    search_fraction: float = 0.01,
    tool_context: Optional[ToolContext] = None
) -> dict:
    """
    Synchronous wrapper for the fashion image retrieval function.

    Args:
        user_query (str): User's fashion-related query.
        top_k (int): Number of top results to return.
        search_fraction (float): Fraction of the vector index to search.
        tool_context (Optional[ToolContext]): Context for tool execution, if needed.

    Returns:
        Optional[List[str]]: List of GCS URLs to retrieved images, or None if no matches found.
    """
    return asyncio.run(
        retrieve_met_images(
            user_query=user_query,
            top_k=top_k,
            search_fraction=search_fraction,
            tool_context=tool_context
        )
    )

# --- Entry Point ---
if __name__ == '__main__':

    logger.info("[📂] Listing tables in MET dataset...")
    tables = bq_client.list_tables("bigquery-public-data.the_met")
    for table in tables:
        logger.info(f"• {table.project}.{table.table_id}")

    query = ("I’m looking for inspiration for a bohemian-style maxi dress with floral prints and "
             "flowing sleeves, perfect for a summer festival.")
    # query = "Help me design a dress inspired by 1950's New Look."
    image_results = run_retrieve_met_images_sync(
        user_query=query,
        top_k=8,
        search_fraction=0.01
    )
    if image_results:
        logger.info(f"[📸] Retrieved image URLs:\n{image_results}")
