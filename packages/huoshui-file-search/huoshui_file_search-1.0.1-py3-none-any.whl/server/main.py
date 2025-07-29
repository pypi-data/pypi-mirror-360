#!/usr/bin/env python3

import asyncio
import platform
import subprocess
import json
import os
import re
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field, field_validator

# Configure logging
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("huoshui-file-search")

class FileSearchParams(BaseModel):
    """Parameters for file search"""
    query: str = Field(..., description="Search query string")
    path: Optional[str] = Field(None, description="Directory path to limit search")
    case_sensitive: bool = Field(False, description="Whether to perform case-sensitive search")
    regex: bool = Field(False, description="Whether to use regular expression matching")
    sort_by: Optional[Literal["name", "size", "date"]] = Field(None, description="Sort results by name, size, or date")
    limit: int = Field(100, description="Maximum number of results to return", ge=1, le=1000)
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: Optional[str]) -> Optional[str]:
        if v and not os.path.exists(v):
            raise ValueError(f"Path does not exist: {v}")
        return v

class FileInfo(BaseModel):
    """Information about a file"""
    path: str
    name: str
    size: Optional[int] = None
    modified_date: Optional[str] = None

class SearchResult(BaseModel):
    """Search result response"""
    success: bool
    files: List[FileInfo]
    count: int
    error: Optional[str] = None
    platform_warning: Optional[str] = None

def check_platform() -> Optional[str]:
    """Check if running on macOS"""
    if platform.system() != "Darwin":
        return f"This tool requires macOS. Current platform: {platform.system()}"
    return None

def parse_allowed_directories(dirs_string: str) -> List[str]:
    """Parse comma-separated directories string"""
    if not dirs_string:
        return []
    return [d.strip() for d in dirs_string.split(',') if d.strip()]

def check_mdfind() -> bool:
    """Check if mdfind command is available"""
    try:
        subprocess.run(["which", "mdfind"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def build_mdfind_command(params: FileSearchParams) -> List[str]:
    """Build mdfind command with parameters"""
    cmd = ["mdfind"]
    
    # Add case-insensitive flag if needed
    if not params.case_sensitive:
        cmd.append("-i")
    
    # Add path restriction if specified
    if params.path:
        cmd.extend(["-onlyin", params.path])
    
    # Build query
    if params.regex:
        # For regex, we'll need to filter results after mdfind
        cmd.append(params.query)
    else:
        # For regular search, escape special characters
        query = params.query.replace('"', '\\"')
        cmd.append(f'"{query}"')
    
    return cmd

def get_file_info(file_path: str) -> FileInfo:
    """Get detailed information about a file"""
    try:
        path_obj = Path(file_path)
        if path_obj.exists():
            stat = path_obj.stat()
            return FileInfo(
                path=file_path,
                name=path_obj.name,
                size=stat.st_size,
                modified_date=datetime.fromtimestamp(stat.st_mtime).isoformat()
            )
    except Exception as e:
        logger.debug(f"Error getting file info for {file_path}: {e}")
    
    return FileInfo(
        path=file_path,
        name=Path(file_path).name
    )

def sort_files(files: List[FileInfo], sort_by: Optional[str]) -> List[FileInfo]:
    """Sort files based on criteria"""
    if not sort_by:
        return files
    
    if sort_by == "name":
        return sorted(files, key=lambda f: f.name.lower())
    elif sort_by == "size":
        return sorted(files, key=lambda f: f.size or 0, reverse=True)
    elif sort_by == "date":
        return sorted(files, key=lambda f: f.modified_date or "", reverse=True)
    
    return files

@mcp.prompt()
async def file_search_prompt() -> str:
    """Provide guidance on using the file search tool"""
    return """# Huoshui File Search Tool

**⚠️ IMPORTANT: This tool only works on macOS systems using the mdfind command (Spotlight search).**

## Available Commands:
- `search_files`: Search for files with various filtering options

## Parameters:
- `query`: Search query string (required)
- `path`: Directory to limit search (optional)
- `case_sensitive`: Enable case-sensitive search (default: false)
- `regex`: Use regular expression matching (default: false)
- `sort_by`: Sort results by 'name', 'size', or 'date' (optional)
- `limit`: Maximum results to return (default: 100, max: 1000)

## Examples:
1. Basic search: `{"query": "report.pdf"}`
2. Search in specific directory: `{"query": "*.py", "path": "/Users/username/Documents"}`
3. Case-sensitive search: `{"query": "README", "case_sensitive": true}`
4. Regex search: `{"query": "log.*2024", "regex": true}`
5. Sorted results: `{"query": "*.jpg", "sort_by": "size", "limit": 50}`

Note: This tool uses macOS Spotlight index, so recently created files might not appear immediately."""

@mcp.tool()
async def search_files(ctx: Context, params: FileSearchParams) -> SearchResult:
    """Search for files using macOS mdfind with filtering options"""
    
    # Check platform
    platform_warning = check_platform()
    if platform_warning:
        return SearchResult(
            success=False,
            files=[],
            count=0,
            error="Platform not supported",
            platform_warning=platform_warning
        )
    
    # Check mdfind availability
    if not check_mdfind():
        return SearchResult(
            success=False,
            files=[],
            count=0,
            error="mdfind command not found. This tool requires macOS with Spotlight enabled."
        )
    
    try:
        # Build and run mdfind command
        cmd = build_mdfind_command(params)
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() or "mdfind command failed"
            return SearchResult(
                success=False,
                files=[],
                count=0,
                error=error_msg
            )
        
        # Parse results
        file_paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        
        # Apply regex filtering if needed
        if params.regex:
            try:
                pattern = re.compile(params.query, re.IGNORECASE if not params.case_sensitive else 0)
                file_paths = [fp for fp in file_paths if pattern.search(os.path.basename(fp))]
            except re.error as e:
                return SearchResult(
                    success=False,
                    files=[],
                    count=0,
                    error=f"Invalid regex pattern: {e}"
                )
        
        # Get file info for each result
        files = [get_file_info(fp) for fp in file_paths]
        
        # Sort files if requested
        files = sort_files(files, params.sort_by)
        
        # Apply limit
        total_count = len(files)
        files = files[:params.limit]
        
        return SearchResult(
            success=True,
            files=files,
            count=len(files),
            platform_warning=f"Total results: {total_count}" if total_count > params.limit else None
        )
        
    except subprocess.TimeoutExpired:
        return SearchResult(
            success=False,
            files=[],
            count=0,
            error="Search timed out after 30 seconds"
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        return SearchResult(
            success=False,
            files=[],
            count=0,
            error=f"Search failed: {str(e)}"
        )

def main():
    """Main entry point for the MCP server"""
    # Enable logging if configured
    if os.getenv("HUOSHUI_ENABLE_LOGGING", "false").lower() == "true":
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    main()