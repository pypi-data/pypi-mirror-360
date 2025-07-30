"""MCP server implementation for Semantic Scholar API."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from core.cache import InMemoryCache
from core.config import ApplicationConfig, get_config
from core.exceptions import ValidationError
from core.logging import MCPToolContext, RequestContext, get_logger, initialize_logging

from .api_client_enhanced import SemanticScholarClient
from .domain_models import (
    SearchFilters,
    SearchQuery,
)

# Initialize FastMCP server
mcp = FastMCP(
    name="semantic-scholar-mcp",
    description="MCP server for accessing Semantic Scholar academic database"
)

# Global instances
logger = get_logger(__name__)
config: ApplicationConfig | None = None
api_client: SemanticScholarClient | None = None


async def initialize_server():
    """Initialize server components."""
    global config, api_client

    # Load configuration
    config = get_config()

    # Initialize logging with MCP-safe settings
    import os
    
    # Handle MCP mode logging configuration
    if os.getenv("MCP_MODE", "false").lower() == "true":
        # Standard MCP compatibility mode
        if not config.logging.debug_mcp_mode:
            config.logging.level = "ERROR"
    
    # Override log level for debug mode
    if config.logging.debug_mcp_mode and config.logging.debug_level_override:
        config.logging.level = config.logging.debug_level_override
    elif config.logging.debug_mcp_mode:
        # Enable debug logging when MCP debug mode is active
        config.logging.level = "DEBUG"
    
    initialize_logging(config.logging)

    # Create cache
    cache = InMemoryCache(
        max_size=config.cache.max_size,
        default_ttl=config.cache.ttl_seconds
    ) if config.cache.enabled else None

    # Create API client
    api_client = SemanticScholarClient(
        config=config.semantic_scholar,
        logger=logger,
        cache=cache
    )

    # Log server initialization details
    logger.info(
        "Semantic Scholar MCP server initialized",
        version=config.server.version,
        environment=config.environment.value,
        debug_mcp_mode=config.logging.debug_mcp_mode,
        log_level=config.logging.level.value if hasattr(config.logging.level, 'value') else str(config.logging.level),
        performance_metrics_enabled=config.logging.log_performance_metrics
    )
    
    # Log MCP tools and resources if debug mode is enabled
    if config.logging.debug_mcp_mode:
        logger.debug_mcp(
            "MCP server configuration details",
            mcp_tools=[
                "search_papers", "get_paper", "get_paper_citations", "get_paper_references",
                "get_author", "get_author_papers", "search_authors", "get_recommendations", "batch_get_papers"
            ],
            mcp_resources=[
                "papers/{paper_id}", "authors/{author_id}"
            ],
            mcp_prompts=[
                "literature_review", "citation_analysis", "research_trend_analysis"
            ],
            cache_enabled=config.cache.enabled,
            rate_limit_enabled=config.rate_limit.enabled,
            circuit_breaker_enabled=config.circuit_breaker.enabled
        )


def extract_field_value(value: Any) -> Any:
    """Extract actual value from Pydantic Field objects."""
    if hasattr(value, 'default'):
        return getattr(value, 'default', value)
    return value


# Tool implementations

@mcp.tool()
async def search_papers(
    query: str,
    limit: int = Field(default=10, ge=1, le=100, description="Number of results to return"),
    offset: int = Field(default=0, ge=0, description="Offset for pagination"),
    year: int | None = Field(default=None, description="Filter by publication year"),
    fields_of_study: list[str] | None = Field(default=None, description="Filter by fields of study"),
    sort: str | None = Field(default=None, description="Sort order (relevance, citationCount, year)")
) -> dict[str, Any]:
    """
    Search for academic papers in Semantic Scholar.
    
    Args:
        query: Search query string
        limit: Maximum number of results (1-100)
        offset: Pagination offset
        year: Filter by publication year
        fields_of_study: Filter by fields of study
        sort: Sort order
        
    Returns:
        Dictionary containing search results with papers and metadata
    """
    with RequestContext(), MCPToolContext("search_papers"):
        try:
            logger.debug_mcp(
                "Starting search_papers tool execution",
                query=query,
                limit=limit,
                offset=offset,
                year=year,
                fields_of_study=fields_of_study,
                sort=sort
            )
            
            # Extract actual values from Field objects
            actual_limit = extract_field_value(limit)
            actual_offset = extract_field_value(offset)
            actual_sort = extract_field_value(sort)
            actual_year = extract_field_value(year)
            actual_fields_of_study = extract_field_value(fields_of_study)

            logger.debug_mcp(
                "Extracted field values",
                actual_limit=actual_limit,
                actual_offset=actual_offset,
                actual_sort=actual_sort,
                actual_year=actual_year,
                actual_fields_of_study=actual_fields_of_study
            )

            # Build search query
            search_query = SearchQuery(
                query=query,
                limit=actual_limit,
                offset=actual_offset,
                sort=actual_sort
            )

            # Apply filters if provided
            if actual_year or actual_fields_of_study:
                search_query.filters = SearchFilters(
                    year=actual_year,
                    fields_of_study=actual_fields_of_study
                )
                logger.debug_mcp("Applied search filters", filters=search_query.filters.model_dump() if search_query.filters else None)

            # Execute search
            logger.debug_mcp("Executing API search", search_query=search_query.model_dump())
            async with api_client:
                result = await api_client.search_papers(search_query)

            logger.debug_mcp(
                "Search completed successfully",
                result_count=len(result.items),
                total=result.total,
                has_more=result.has_more
            )

            # Format response
            return {
                "success": True,
                "data": {
                    "papers": [paper.model_dump(exclude_none=True) for paper in result.items],
                    "total": result.total,
                    "offset": result.offset,
                    "limit": result.limit,
                    "has_more": result.has_more
                }
            }

        except ValidationError as e:
            logger.log_with_stack_trace(
                logging.ERROR,
                "Validation error in search_papers",
                exception=e,
                tool_name="search_papers",
                query=query,
                validation_details=e.details
            )
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": str(e),
                    "details": e.details
                }
            }
        except Exception as e:
            logger.log_with_stack_trace(
                logging.ERROR,
                "Error searching papers",
                exception=e,
                tool_name="search_papers",
                query=query,
                exception_type=type(e).__name__
            )
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


@mcp.tool()
async def get_paper(
    paper_id: str,
    include_citations: bool = Field(default=False, description="Include citation details"),
    include_references: bool = Field(default=False, description="Include reference details")
) -> dict[str, Any]:
    """
    Get detailed information about a specific paper.
    
    Args:
        paper_id: Paper ID (Semantic Scholar ID, DOI, or ArXiv ID)
        include_citations: Whether to include citation details
        include_references: Whether to include reference details
        
    Returns:
        Dictionary containing paper details
    """
    with RequestContext():
        try:
            async with api_client:
                paper = await api_client.get_paper(
                    paper_id=paper_id,
                    include_citations=include_citations,
                    include_references=include_references
                )

            return {
                "success": True,
                "data": paper.model_dump(exclude_none=True)
            }

        except ValidationError as e:
            logger.error("Validation error in get_paper", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": str(e),
                    "details": e.details
                }
            }
        except Exception as e:
            logger.error("Error getting paper", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


@mcp.tool()
async def get_paper_citations(
    paper_id: str,
    limit: int = Field(default=100, ge=1, le=1000, description="Number of citations to return"),
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
) -> dict[str, Any]:
    """
    Get citations for a specific paper.
    
    Args:
        paper_id: Paper ID
        limit: Maximum number of citations
        offset: Pagination offset
        
    Returns:
        Dictionary containing citation list
    """
    with RequestContext():
        try:
            async with api_client:
                citations = await api_client.get_paper_citations(
                    paper_id=paper_id,
                    limit=limit,
                    offset=offset
                )

            return {
                "success": True,
                "data": {
                    "citations": [cite.model_dump(exclude_none=True) for cite in citations],
                    "count": len(citations)
                }
            }

        except Exception as e:
            logger.error("Error getting citations", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


@mcp.tool()
async def get_paper_references(
    paper_id: str,
    limit: int = Field(default=100, ge=1, le=1000, description="Number of references to return"),
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
) -> dict[str, Any]:
    """
    Get references for a specific paper.
    
    Args:
        paper_id: Paper ID
        limit: Maximum number of references
        offset: Pagination offset
        
    Returns:
        Dictionary containing reference list
    """
    with RequestContext():
        try:
            async with api_client:
                references = await api_client.get_paper_references(
                    paper_id=paper_id,
                    limit=limit,
                    offset=offset
                )

            return {
                "success": True,
                "data": {
                    "references": [ref.model_dump(exclude_none=True) for ref in references],
                    "count": len(references)
                }
            }

        except Exception as e:
            logger.error("Error getting references", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


@mcp.tool()
async def get_author(
    author_id: str
) -> dict[str, Any]:
    """
    Get detailed information about an author.
    
    Args:
        author_id: Author ID
        
    Returns:
        Dictionary containing author details
    """
    with RequestContext():
        try:
            async with api_client:
                author = await api_client.get_author(author_id=author_id)

            return {
                "success": True,
                "data": author.model_dump(exclude_none=True)
            }

        except Exception as e:
            logger.error("Error getting author", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


@mcp.tool()
async def get_author_papers(
    author_id: str,
    limit: int = Field(default=100, ge=1, le=1000, description="Number of papers to return"),
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
) -> dict[str, Any]:
    """
    Get papers by a specific author.
    
    Args:
        author_id: Author ID
        limit: Maximum number of papers
        offset: Pagination offset
        
    Returns:
        Dictionary containing author's papers
    """
    with RequestContext():
        try:
            async with api_client:
                result = await api_client.get_author_papers(
                    author_id=author_id,
                    limit=limit,
                    offset=offset
                )

            return {
                "success": True,
                "data": {
                    "papers": [paper.model_dump(exclude_none=True) for paper in result.items],
                    "total": result.total,
                    "offset": result.offset,
                    "limit": result.limit,
                    "has_more": result.has_more
                }
            }

        except Exception as e:
            logger.error("Error getting author papers", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


@mcp.tool()
async def search_authors(
    query: str,
    limit: int = Field(default=10, ge=1, le=100, description="Number of results to return"),
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
) -> dict[str, Any]:
    """
    Search for authors by name.
    
    Args:
        query: Author name search query
        limit: Maximum number of results
        offset: Pagination offset
        
    Returns:
        Dictionary containing search results
    """
    with RequestContext():
        try:
            # Extract actual values from Field objects if needed
            actual_offset = extract_field_value(offset)

            async with api_client:
                result = await api_client.search_authors(
                    query=query,
                    limit=limit,
                    offset=actual_offset
                )

            return {
                "success": True,
                "data": {
                    "authors": [author.model_dump(exclude_none=True) for author in result.items],
                    "total": result.total,
                    "offset": result.offset,
                    "limit": result.limit,
                    "has_more": result.has_more
                }
            }

        except Exception as e:
            logger.error("Error searching authors", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


@mcp.tool()
async def get_recommendations(
    paper_id: str,
    limit: int = Field(default=10, ge=1, le=100, description="Number of recommendations")
) -> dict[str, Any]:
    """
    Get paper recommendations based on a given paper.
    
    Args:
        paper_id: Paper ID to base recommendations on
        limit: Maximum number of recommendations
        
    Returns:
        Dictionary containing recommended papers
    """
    with RequestContext():
        try:
            async with api_client:
                papers = await api_client.get_recommendations(
                    paper_id=paper_id,
                    limit=limit
                )

            return {
                "success": True,
                "data": {
                    "recommendations": [paper.model_dump(exclude_none=True) for paper in papers],
                    "count": len(papers)
                }
            }

        except Exception as e:
            logger.error("Error getting recommendations", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


@mcp.tool()
async def batch_get_papers(
    paper_ids: list[str],
    fields: list[str] | None = Field(default=None, description="Fields to include in response")
) -> dict[str, Any]:
    """
    Get multiple papers in a single request.
    
    Args:
        paper_ids: List of paper IDs (max 500)
        fields: Optional list of fields to include
        
    Returns:
        Dictionary containing paper details
    """
    with RequestContext():
        try:
            if len(paper_ids) > 500:
                raise ValidationError(
                    "Too many paper IDs",
                    field="paper_ids",
                    value=len(paper_ids)
                )

            # Extract actual values from Field objects if needed
            actual_fields = None
            if fields is not None:
                actual_fields = extract_field_value(fields)

            async with api_client:
                papers = await api_client.batch_get_papers(
                    paper_ids=paper_ids,
                    fields=actual_fields
                )

            return {
                "success": True,
                "data": {
                    "papers": [paper.model_dump(exclude_none=True) for paper in papers],
                    "count": len(papers)
                }
            }

        except ValidationError as e:
            logger.error("Validation error in batch_get_papers", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": str(e),
                    "details": e.details
                }
            }
        except Exception as e:
            logger.error("Error in batch get papers", exception=e)
            return {
                "success": False,
                "error": {
                    "type": "error",
                    "message": str(e)
                }
            }


# Resource implementations

@mcp.resource("papers/{paper_id}")
async def get_paper_resource(paper_id: str) -> str:
    """
    Get paper information as a resource.
    
    Args:
        paper_id: Paper ID
        
    Returns:
        Formatted paper information
    """
    try:
        async with api_client:
            paper = await api_client.get_paper(paper_id=paper_id)

        # Format paper as markdown
        lines = [
            f"# {paper.title}",
            "",
            f"**Authors**: {', '.join([a.name for a in paper.authors])}",
            f"**Year**: {paper.year}",
            f"**Venue**: {paper.venue or 'N/A'}",
            f"**Citations**: {paper.citation_count}",
            "",
            "## Abstract",
            paper.abstract or "No abstract available.",
            ""
        ]

        if paper.url:
            lines.append(f"**URL**: {paper.url}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Error getting paper resource: {e}")
        return f"Error: Could not retrieve paper {paper_id}"


@mcp.resource("authors/{author_id}")
async def get_author_resource(author_id: str) -> str:
    """
    Get author information as a resource.
    
    Args:
        author_id: Author ID
        
    Returns:
        Formatted author information
    """
    try:
        async with api_client:
            author = await api_client.get_author(author_id=author_id)

        # Format author as markdown
        lines = [
            f"# {author.name}",
            "",
            f"**H-Index**: {author.h_index or 'N/A'}",
            f"**Citation Count**: {author.citation_count or 0}",
            f"**Paper Count**: {author.paper_count or 0}",
            ""
        ]

        if author.affiliations:
            lines.append(f"**Affiliations**: {', '.join(author.affiliations)}")

        if author.homepage:
            lines.append(f"**Homepage**: {author.homepage}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Error getting author resource: {e}")
        return f"Error: Could not retrieve author {author_id}"


# Prompt implementations

@mcp.prompt()
def literature_review(
    topic: str,
    max_papers: int = Field(default=20, ge=5, le=50),
    start_year: int | None = Field(default=None)
) -> str:
    """
    Generate a literature review prompt for a given topic.
    
    Args:
        topic: Research topic
        max_papers: Maximum number of papers to include
        start_year: Starting year for paper search
        
    Returns:
        Prompt text for literature review
    """
    year_filter = f" published after {start_year}" if start_year else ""

    return f"""Please help me create a comprehensive literature review on the topic: "{topic}"

Instructions:
1. Search for the most relevant and highly-cited papers on this topic{year_filter}
2. Retrieve up to {max_papers} papers
3. For each paper, analyze:
   - Main contributions and findings
   - Methodology used
   - Limitations and future work
4. Identify common themes and research gaps
5. Organize the review by subtopics or chronologically
6. Include proper citations for all papers

Please structure the review with:
- Introduction to the topic
- Methodology (how papers were selected)
- Main body organized by themes
- Summary of findings
- Research gaps and future directions
- References list"""


@mcp.prompt()
def citation_analysis(
    paper_id: str,
    depth: int = Field(default=1, ge=1, le=3)
) -> str:
    """
    Generate a citation analysis prompt for a paper.
    
    Args:
        paper_id: Paper ID to analyze
        depth: Depth of citation analysis (1-3)
        
    Returns:
        Prompt text for citation analysis
    """
    return f"""Please perform a comprehensive citation analysis for paper ID: {paper_id}

Analysis depth: {depth} levels

Instructions:
1. Retrieve the main paper and its metadata
2. Analyze citations at depth {depth}:
   - Level 1: Direct citations (papers citing the main paper)
   - Level 2: Citations of citations (if depth >= 2)
   - Level 3: Third-level citations (if depth = 3)

For each level, analyze:
- Most influential citing papers (by citation count)
- Common themes in citing papers
- How the original paper is used/referenced
- Evolution of the research area
- Identify key research groups or authors

Please provide:
- Citation statistics and trends
- Network visualization description
- Key insights about the paper's impact
- Recommendations for related work"""


@mcp.prompt()
def research_trend_analysis(
    field: str,
    years: int = Field(default=5, ge=1, le=20)
) -> str:
    """
    Generate a research trend analysis prompt.
    
    Args:
        field: Research field to analyze
        years: Number of years to analyze
        
    Returns:
        Prompt text for trend analysis
    """
    return f"""Please analyze research trends in the field of "{field}" over the past {years} years.

Instructions:
1. Search for papers in this field from the last {years} years
2. Group papers by year and identify:
   - Publication volume trends
   - Most cited papers per year
   - Emerging topics and keywords
   - Declining research areas
   
3. Analyze:
   - Top contributing authors and institutions
   - International collaboration patterns
   - Funding sources (if available)
   - Industry vs academic contributions
   
4. Identify:
   - Breakthrough papers and why they're significant
   - Methodology shifts
   - Technology adoption
   - Interdisciplinary connections

Please provide:
- Executive summary of trends
- Detailed year-by-year analysis
- Future research predictions
- Recommendations for researchers entering the field"""


# Server lifecycle

async def on_startup():
    """Initialize server on startup."""
    logger.debug_mcp("MCP server startup initiated")
    await initialize_server()
    logger.debug_mcp("MCP server startup completed")


async def on_shutdown():
    """Cleanup on shutdown."""
    logger.debug_mcp("MCP server shutdown initiated")
    logger.info("Semantic Scholar MCP server shutting down")
    logger.debug_mcp("MCP server shutdown completed")


# Main entry point
def main():
    """Main entry point for the server."""
    import os
    
    # Log environment information if debug mode is enabled
    if os.getenv("DEBUG_MCP_MODE", "false").lower() == "true":
        temp_config = get_config()
        temp_logger = get_logger("mcp.main")
        temp_logger.debug_mcp(
            "MCP server main() called",
            environment_vars={
                "DEBUG_MCP_MODE": os.getenv("DEBUG_MCP_MODE"),
                "LOG_MCP_MESSAGES": os.getenv("LOG_MCP_MESSAGES"),
                "LOG_API_PAYLOADS": os.getenv("LOG_API_PAYLOADS"),
                "LOG_PERFORMANCE_METRICS": os.getenv("LOG_PERFORMANCE_METRICS"),
                "MCP_MODE": os.getenv("MCP_MODE"),
                "SEMANTIC_SCHOLAR_API_KEY": "***SET***" if os.getenv("SEMANTIC_SCHOLAR_API_KEY") else "***NOT_SET***"
            },
            python_version=sys.version,
            working_directory=str(Path.cwd())
        )
    
    # Initialize server on startup
    asyncio.run(on_startup())

    # Run the server
    try:
        logger.debug_mcp("Starting FastMCP server with stdio transport")
        # Run the MCP server - this will block and handle stdio communication
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.debug_mcp("MCP server interrupted by user")
    except Exception as e:
        logger.log_with_stack_trace(
            logging.ERROR,
            "Fatal error running MCP server",
            exception=e,
            transport="stdio"
        )
        raise
    finally:
        asyncio.run(on_shutdown())


if __name__ == "__main__":
    main()
