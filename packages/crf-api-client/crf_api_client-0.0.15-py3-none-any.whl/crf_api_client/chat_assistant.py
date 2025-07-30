from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, List, Optional, Tuple

import requests
import tiktoken
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

if TYPE_CHECKING:
    from .client import CRFAPIClient

# Configure logging
logger = logging.getLogger(__name__)


def dict_to_markdown(data, depth=0):
    md_lines = []
    indent = "  " * depth
    bullet = "-" if depth == 0 else "*"

    # Add current node's name and description
    name = data.get("name", "Unnamed")
    description = data.get("description", "")
    md_lines.append(f"{indent}{bullet} **{name}**")
    if description:
        md_lines.append(f"{indent}  {description}")

    # Recurse into children if any
    for child in data.get("children", []):
        md_lines.append(dict_to_markdown(child, depth + 1))

    return "\n".join(md_lines)


SYSTEM_PROMPT = """

You are an expert with deep knowledge about {project_brief}.
────────────────────────────────
MISSION  :  WHAT YOU COVER

You are tasked with answering questions in your area of expertise describe above.
You will use the **Knowledge Warehouse** to find relevant information and provide accurate,
citation-backed answers.

All answers must draw on the **Knowledge Warehouse** .
**Query the warehouse exclusively with the provided tool.**

---------------------------------------
ORGANISATION OF KNOWLEDGE WAREHOUSE

You have access to a **Knowledge Warehouse** about {project_brief} that is organised around the
 following dimensions:
{tag_structure}

────────────────────────────────
CITATION RULES – NO EXCEPTIONS
1. Every factual or regulatory statement needs a citation.
2. Format citations exactly as `[Reference <ID>]`.
   • Multiple sources: `[Reference <ID1>][Reference <ID2>]`
3. If the warehouse lacks a direct source, cite `[Model Knowledge]`.
4. Place citations **inline, immediately after the sentence *or list item* they support**.
   • **For bullet/numbered lists, append the citation to *each* item, never as a block at the end.**
   • Example (partial list of mandatory label elements):
     – Name and address of the Responsible Person [Reference 5]
     – Nominal content (weight/volume) [Reference 6]

────────────────────────────────
ANSWERING METHOD
1. **Analyse the query**
   • Break it into parts and detect key topics to adress
    • Identify from the structure the type of dimensions and the associated values that are relevant
     to the query
    • Split the user quesy into sub-questions if needed, to ensure all dimensions - values are c
    overed.

2. **Gather evidence**
   • Reformulate the search if helpful and split it into varuious queries to the Knowledge Warehouse.
   • Use the warehouse tool to pull slightly more data than needed, then filter for relevance.
   • Capture **every** requested dimension (annex, limit, condition, etc.).

3. **Write the answer**
   • Address every sub-question or implicit request.
   • As much as possible, provide a quantitative answer supported by the warehouse.
   • Insert citations inline (see rules above).
   • **Exhaustive-list rule:**
     – If the user's words (e.g. "all", "complete", "exhaustive list") demand exhaustivity, return
     the *entire* list in one response—no truncation, no "let me know if you need more."
     – Provide *only* the fields requested.
       • Example: "List all chemical names that benefit from exemptions for
       hair-care products" → output **just the chemical names**, one per line/bullet, each with its own citation.
  • If the user asks for a list of all the chemicals in the warehouse, return the entire list.
   • For other requests, be precise **and concise**—include only what is relevant.

────────────────────────────────
GOAL
Deliver clear, legally accurate, citation-backed answers that prioritise **exhaustivity** where
demanded and **brevity** everywhere else.
"""


class KnowledgeWarehouseChatAssistant:
    def __init__(
        self,
        llm_model_id: str,
        crf_client: "CRFAPIClient",
        project_id: str,
        included_tags: Optional[List[Tuple[str, str, str]]] = None,
        excluded_tags: Optional[List[Tuple[str, str, str]]] = None,
        reasoning_tree_ids: Optional[List[str]] = None,
        search_indexes: List[str] = ["chunks"],
        default_top_k: int = 10,
    ):
        """
        Initialize the Knowledge Warehouse Assistant.

        Args:
            llm_model_id: The LLM model ID to use
            crf_client: The CRF client instance
            agent_mode: The mode of operation for the agent
            project_id: The project ID
            project_brief: Brief description of the project
            reasoning_tree_ids: List of reasoning tree IDs to include
            included_tags: List of tags to include in filtered searches
            excluded_tags: List of tags to exclude in filtered searches
            default_top_k: Default number of results to return

        """
        logger.info(f"Initializing KnowledgeWarehouseAssistant with model: {llm_model_id}")

        self.token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(llm_model_id).encode
        )
        callback_manager = CallbackManager([self.token_counter])
        self.llm = OpenAI(model=llm_model_id)
        self.crf_client = crf_client
        self.project_id = project_id
        self.warehouse = crf_client.get_warehouse(project_id)
        self.project_brief = self.warehouse.business_brief
        self.default_top_k = default_top_k
        self.reasoning_tree_ids = reasoning_tree_ids or []
        self.included_tags = included_tags or []
        self.excluded_tags = excluded_tags or []
        self.search_indexes = search_indexes or ["chunks"]
        tools = []
        extractor_list = crf_client.list_tag_extractors(project_id=project_id)
        md = ""

        # Build reasoning tree markdown if needed
        if self.reasoning_tree_ids:
            reasoning_trees = [t for t in extractor_list if t["id"] in self.reasoning_tree_ids]
            for tag in reasoning_trees:
                md += dict_to_markdown(tag["tagging_tree"])
                md += "\n\n"

        assistant_prompt = SYSTEM_PROMPT.format(project_brief=self.project_brief, tag_structure=md)

        if len(self.included_tags) > 0 or len(self.excluded_tags) > 0:
            tools.append(
                FunctionTool.from_defaults(
                    fn=self._semantic_search_on_chunks_filter_with_tags,
                    name="semantic_search_on_chunks_with_tags",
                    description="Search inside the chunks collection from Knowledge Warehouse for information that would be relevant to the current question.",
                )
            )
        else:
            tools.append(
                FunctionTool.from_defaults(
                    fn=self._semantic_search_on_knowledge_warehouse,
                    name="semantic_search_on_chunks",
                    description="Search inside the chunks collection from Knowledge Warehouse for information that would be relevant to the current question.",
                )
            )

        logger.info("Creating OpenAI agent with provided tools")

        self.agent = OpenAIAgent.from_tools(
            tools=tools,
            llm=self.llm,
            system_prompt=assistant_prompt,
            verbose=True,
            callback_manager=callback_manager,
        )
        self.tool_call_history = []
        self.cache_kw = []
        logger.info("KnowledgeWarehouseAssistant initialization complete")

    def add_to_cache_update_id_format_for_context(self, results):
        """Add results to cache and update ID format for context."""
        logger.info(f"Updating cache with {len(results)} new results")
        logger.debug(f"Chat history: {self.agent.chat_history}")
        id_start = len(self.cache_kw)
        for i, result in enumerate(results):
            result["id"] = i + id_start
            self.cache_kw.append(result)

        # Filter each result dict to keep only "id", "type", "content"
        return [
            {k: result[k] for k in ["id", "type", "content"] if k in result} for result in results
        ]

    def _semantic_search_on_objects_enriched_with_chunks(
        self, query: str, top_k: Optional[int] = None
    ):
        """Search objects enriched with chunks."""
        if top_k is None:
            top_k = self.default_top_k

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.crf_client.token}",
        }

        payload = {
            "query": query,
            "indexes": ["objects"],
            "n_objects": top_k,
            "enrich_with_chunks": True,
        }

        response = requests.post(
            f"{self.crf_client.base_url}/api/v1/projects/{self.project_id}/retrieve-with-naive/",
            headers=headers,
            json=payload,
        )

        results = response.json()["retrieval_results"]
        self.tool_call_history.append(
            {
                "tool_type": "semantic_search_on_objects_enriched_with_chunks",
                "query": query,
                "top_k": top_k,
                "results": results,
            }
        )

        return self.add_to_cache_update_id_format_for_context(results)

    def _semantic_search_on_chunks_filter_with_tags(self, query: str, top_k: Optional[int] = None):
        """Search chunks with tag filtering."""
        if top_k is None:
            top_k = self.default_top_k

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.crf_client.token}",
        }

        payload = {
            "query": query,
            "indexes": ["chunks"],
            "n_objects": top_k,
            "included_tags": self.included_tags,
            "excluded_tags": self.excluded_tags,
        }

        response = requests.post(
            f"{self.crf_client.base_url}/api/v1/projects/{self.project_id}/retrieve-with-naive-and-filter-with-tags/",
            headers=headers,
            json=payload,
        )

        results = response.json()["retrieval_results"]
        self.tool_call_history.append(
            {
                "tool_type": "semantic_search_on_chunks_filter_with_tags",
                "query": query,
                "included_tags": self.included_tags,
                "excluded_tags": self.excluded_tags,
                "top_k": top_k,
                "results": results,
            }
        )

        return self.add_to_cache_update_id_format_for_context(results)

    def _semantic_search_on_knowledge_warehouse(self, query: str, top_k: int):
        """Perform semantic search on the knowledge warehouse."""
        try:
            results = self.crf_client.retrieve_with_semantic_search(
                self.project_id, query, self.search_indexes, top_k
            )
            logger.info(f"Semantic search completed successfully on indexes: {self.search_indexes}")

            self.tool_call_history.append(
                {
                    "tool_type": "semantic_search",
                    "query": query,
                    "indexes": self.search_indexes,
                    "top_k": top_k,
                    "results": results,
                }
            )
            return self.add_to_cache_update_id_format_for_context(results)
        except Exception as e:
            logger.error(f"Error during semantic search: {e!s}", exc_info=True)
            return f"Error searching for documents: {e!s}"

    def extract_link_for_finding(self, finding_id: str):
        """Extract link for a specific finding ID."""
        try:
            referenced_objects = [obj for obj in self.cache_kw if obj["id"] == int(finding_id)]
            if len(referenced_objects) == 0:
                logger.warning(f"Finding ID {finding_id} not found in cache.")
                return ""
            if len(referenced_objects) > 1:
                logger.warning(
                    f"Multiple objects found for Finding ID {finding_id}. Using the first one."
                )

            referenced_object = referenced_objects[0]
            return referenced_object.get("reference_url", "")
        except (IndexError, ValueError) as e:
            logger.error(f"Error extracting link for finding {finding_id}: {e!s}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error occurred while extracting link for finding: {e}")
            return ""

    def chat(self, query: str):
        """Chat with the assistant."""
        message = self.agent.chat(query)
        return self.replace_findings_with_links(message.response)


    async def achat(self, query: str):
        """Async chat with the assistant."""
        message = await self.agent.achat(query)
        return self.replace_findings_with_links(message.response)


    def replace_findings_with_links(self, text: str):
        """Replace all occurrences of [Reference ####] with links."""

        def replace_match(match):
            findings = match.group(0)
            # Extract all finding numbers from the matched string
            finding_ids = re.findall(r"Reference (\d+)", findings)
            # Replace each finding number with a Link(url) format
            links = [
                rf"[\[Ref {finding_id}\]]({self.extract_link_for_finding(finding_id)})"
                for finding_id in finding_ids
            ]
            return ", ".join(links)

        # Apply the replacement function to each match
        return re.sub(r"\[Reference(?: \d+[,]?)+\]", replace_match, text)
