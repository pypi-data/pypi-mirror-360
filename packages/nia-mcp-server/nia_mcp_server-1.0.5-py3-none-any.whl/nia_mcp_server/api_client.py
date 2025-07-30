"""
NIA API Client for communicating with production NIA API
"""
import os
import httpx
import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
import json
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API errors with status code."""
    def __init__(self, message: str, status_code: int = None, detail: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail

class NIAApiClient:
    """Client for interacting with NIA's production API."""
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        # Remove trailing slash from base URL to prevent double slashes
        self.base_url = (base_url or os.getenv("NIA_API_URL", "https://api.trynia.ai")).rstrip('/')
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "nia-mcp-server/1.0.0",
                "Content-Type": "application/json"
            },
            timeout=720.0  # 12 minute timeout for deep research operations
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def _handle_api_error(self, e: httpx.HTTPStatusError) -> APIError:
        """Convert HTTP errors to more specific API errors."""
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            error_detail = error_json.get("detail", error_detail)
        except (json.JSONDecodeError, ValueError):
            # Failed to parse JSON response, keep original error_detail
            pass
        
        status_code = e.response.status_code
        
        # Log the full error for debugging
        logger.error(f"API error - Status: {status_code}, Response: {error_detail}")
        
        # Handle specific error cases
        if status_code == 401:
            return APIError(
                "Invalid or missing API key. Please check your API key at https://trynia.ai/api-keys",
                status_code,
                error_detail,
            )
        elif status_code == 403:
            # Check for various forms of usage limit errors
            error_lower = error_detail.lower()
            if any(
                phrase in error_lower
                for phrase in [
                    "lifetime limit",
                    "no chat credits",
                    "free api requests",
                    "25 free",
                    "usage limit",
                ]
            ):
                # Use the exact error message from the API for clarity
                return APIError(error_detail, status_code, error_detail)
            else:
                return APIError(
                    f"Access forbidden: {error_detail}", status_code, error_detail
                )
        elif status_code == 429:
            return APIError(f"Rate limit exceeded: {error_detail}", status_code, error_detail)
        elif status_code == 404:
            return APIError(f"Resource not found: {error_detail}", status_code, error_detail)
        elif status_code == 500:
            # For 500 errors, try to extract more meaningful error details
            if error_detail:
                error_lower = error_detail.lower()
                # Check if it's actually a wrapped error from middleware or API
                if any(
                    phrase in error_lower
                    for phrase in [
                        "lifetime limit",
                        "free api requests",
                        "25 free",
                        "usage limit",
                    ]
                ):
                    return APIError(error_detail, 403, error_detail)
                else:
                    return APIError(f"Server error: {error_detail}", status_code, error_detail)
            else:
                return APIError(
                    "Internal server error. Please try again later.",
                    status_code,
                    error_detail,
                )
        else:
            return APIError(
                f"API error (status {status_code}): {error_detail}",
                status_code,
                error_detail,
            )
    async def validate_api_key(self) -> bool:
        """Validate the API key by making a test request."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/repositories")
            return response.status_code == 200
        except httpx.HTTPStatusError as e:
            # Log the specific error but return False for validation
            error = self._handle_api_error(e)
            logger.error(f"API key validation failed: {error}")
            return False
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    async def list_repositories(self) -> List[Dict[str, Any]]:
        """List all indexed repositories."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/repositories")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Caught HTTPStatusError in list_repositories: status={e.response.status_code}, detail={e.response.text}")
            raise self._handle_api_error(e)
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            raise APIError(f"Failed to list repositories: {str(e)}")
    
    async def index_repository(self, repo_url: str, branch: str = None) -> Dict[str, Any]:
        """Index a GitHub repository."""
        try:
            # Parse repo URL to get owner/repo format
            if "github.com" in repo_url:
                parts = repo_url.rstrip('/').split('/')
                owner_repo = f"{parts[-2]}/{parts[-1]}"
            else:
                owner_repo = repo_url
            
            payload = {
                "repository": owner_repo,
                "branch": branch
            }
            
            response = await self.client.post(
                f"{self.base_url}/v2/repositories",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to index repository: {str(e)}")
    
    async def get_repository_status(self, owner_repo: str) -> Dict[str, Any]:
        """Get the status of a repository."""
        try:
            # Check if this looks like owner/repo format (contains /)
            if '/' in owner_repo:
                # First, list all repositories to find the matching one
                repos = await self.list_repositories()
                
                # Look for a repository matching this owner/repo
                matching_repo = None
                for repo in repos:
                    # Check if repository field matches
                    if repo.get("repository") == owner_repo:
                        matching_repo = repo
                        break
                
                if not matching_repo:
                    logger.warning(f"Repository {owner_repo} not found in list")
                    return None
                
                # Use the repository_id from the matched repo
                repo_id = matching_repo.get("repository_id") or matching_repo.get("id")
                if not repo_id:
                    logger.error(f"No repository ID found for {owner_repo}")
                    return None
                    
                # Now get the status using the ID
                response = await self.client.get(f"{self.base_url}/v2/repositories/{repo_id}")
                response.raise_for_status()
                
                # Merge the response with what we know
                status = response.json()
                # Ensure repository field is included for consistency
                if "repository" not in status:
                    status["repository"] = owner_repo
                return status
            else:
                # Assume it's already a repository ID
                response = await self.client.get(f"{self.base_url}/v2/repositories/{owner_repo}")
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Failed to get repository status: {e}")
            return None
    
    async def query_repositories(
        self,
        messages: List[Dict[str, str]],
        repositories: List[str],
        stream: bool = True,
        include_sources: bool = True
    ) -> AsyncIterator[str]:
        """Query indexed repositories with streaming support."""
        try:
            # Format repositories for the API
            repo_list = []
            for repo in repositories:
                if "/" in repo:
                    repo_list.append({"repository": repo})
                else:
                    # Assume it's a project ID or other identifier
                    repo_list.append({"repository": repo})
            
            payload = {
                "messages": messages,
                "repositories": repo_list,
                "stream": stream,
                "include_sources": include_sources
            }
            
            if stream:
                async with self.client.stream(
                    "POST",
                    f"{self.base_url}/v2/query",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                if data == "[DONE]":
                                    break
                                yield data
            else:
                response = await self.client.post(
                    f"{self.base_url}/v2/query",
                    json=payload
                )
                response.raise_for_status()
                yield json.dumps(response.json())
                
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Query failed: {str(e)}")
    
    async def wait_for_indexing(self, owner_repo: str, timeout: int = 600) -> Dict[str, Any]:
        """Wait for a repository to finish indexing."""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.get_repository_status(owner_repo)
            
            if not status:
                raise Exception(f"Repository {owner_repo} not found")
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"Indexing failed: {status.get('error', 'Unknown error')}")
            
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise Exception(f"Indexing timeout after {timeout} seconds")
            
            # Wait before next check
            await asyncio.sleep(2)
    
    async def delete_repository(self, owner_repo: str) -> bool:
        """Delete an indexed repository."""
        try:
            # Check if this looks like owner/repo format (contains /)
            if '/' in owner_repo:
                # First, get the repository ID
                status = await self.get_repository_status(owner_repo)
                if not status:
                    logger.warning(f"Repository {owner_repo} not found")
                    return False
                
                # Extract the repository ID from status
                repo_id = status.get("repository_id") or status.get("id")
                if not repo_id:
                    # Try to get it from list as fallback
                    repos = await self.list_repositories()
                    for repo in repos:
                        if repo.get("repository") == owner_repo:
                            repo_id = repo.get("repository_id") or repo.get("id")
                            break
                
                if not repo_id:
                    logger.error(f"No repository ID found for {owner_repo}")
                    return False
                    
                # Delete using the ID
                response = await self.client.delete(f"{self.base_url}/v2/repositories/{repo_id}")
                response.raise_for_status()
                return True
            else:
                # Assume it's already a repository ID
                response = await self.client.delete(f"{self.base_url}/v2/repositories/{owner_repo}")
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete repository: {e}")
            return False
    
    # Data Source methods
    
    async def create_data_source(
        self, 
        url: str, 
        url_patterns: List[str] = None,
        max_age: int = None,
        only_main_content: bool = True
    ) -> Dict[str, Any]:
        """Create a new documentation/web data source."""
        try:
            payload = {
                "url": url,
                "url_patterns": url_patterns or []
            }
            
            # Add optional parameters
            if max_age is not None:
                payload["max_age"] = max_age
            # Always use markdown for documentation scraping
            payload["formats"] = ["markdown"]
            if only_main_content is not None:
                payload["only_main_content"] = only_main_content
            
            response = await self.client.post(
                f"{self.base_url}/v2/data-sources",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Failed to create data source: {str(e)}")
    
    async def list_data_sources(self) -> List[Dict[str, Any]]:
        """List all data sources for the authenticated user."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/data-sources")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            logger.error(f"Failed to list data sources: {e}")
            raise APIError(f"Failed to list data sources: {str(e)}")
    
    async def get_data_source_status(self, source_id: str) -> Dict[str, Any]:
        """Get the status of a data source."""
        try:
            response = await self.client.get(f"{self.base_url}/v2/data-sources/{source_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Failed to get data source status: {e}")
            return None
    
    async def delete_data_source(self, source_id: str) -> bool:
        """Delete a data source."""
        try:
            response = await self.client.delete(f"{self.base_url}/v2/data-sources/{source_id}")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete data source: {e}")
            return False
    
    async def query_unified(
        self,
        messages: List[Dict[str, str]],
        repositories: List[str] = None,
        data_sources: List[str] = None,
        search_mode: str = "unified",
        stream: bool = True,
        include_sources: bool = True
    ) -> AsyncIterator[str]:
        """Query across repositories and/or documentation sources."""
        try:
            # Build repository list
            repo_list = []
            if repositories:
                for repo in repositories:
                    repo_list.append({"repository": repo})
            
            # Build data source list  
            source_list = []
            if data_sources:
                for source_id in data_sources:
                    # Handle both list of IDs and list of dicts
                    if isinstance(source_id, dict):
                        source_list.append(source_id)
                    else:
                        source_list.append({"source_id": source_id})
            
            # Validate at least one source
            if not repo_list and not source_list:
                raise Exception("No repositories or data sources specified")
            
            payload = {
                "messages": messages,
                "repositories": repo_list,
                "data_sources": source_list,
                "search_mode": search_mode,
                "stream": stream,
                "include_sources": include_sources
            }
            
            if stream:
                async with self.client.stream(
                    "POST",
                    f"{self.base_url}/v2/query",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                if data == "[DONE]":
                                    break
                                yield data
            else:
                response = await self.client.post(
                    f"{self.base_url}/v2/query",
                    json=payload
                )
                response.raise_for_status()
                yield json.dumps(response.json())
                
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Query failed: {str(e)}")
    
    async def web_search(
        self,
        query: str,
        num_results: int = 5,
        category: Optional[str] = None,
        days_back: Optional[int] = None,
        find_similar_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform AI-powered web search."""
        try:
            payload = {
                "query": query,
                "num_results": min(num_results, 10),
            }
            
            # Add optional parameters
            if category:
                payload["category"] = category
            if days_back:
                payload["days_back"] = days_back
            if find_similar_to:
                payload["find_similar_to"] = find_similar_to
            
            response = await self.client.post(
                f"{self.base_url}/v2/web-search",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Web search failed: {str(e)}")
    
    async def deep_research(
        self,
        query: str,
        output_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform deep research using AI agent."""
        try:
            payload = {
                "query": query,
            }
            
            if output_format:
                payload["output_format"] = output_format
            
            response = await self.client.post(
                f"{self.base_url}/v2/deep-research",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise self._handle_api_error(e)
        except Exception as e:
            raise APIError(f"Deep research failed: {str(e)}")