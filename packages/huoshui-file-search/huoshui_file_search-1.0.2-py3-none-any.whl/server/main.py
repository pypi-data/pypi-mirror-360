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
    query: str = Field(..., description="mdfind query string (e.g., 'report', 'kind:pdf', 'kMDItemFSName == \"*.py\"')")
    path: Optional[str] = Field(None, description="Directory path to limit search")
    case_sensitive: bool = Field(False, description="Whether to perform case-sensitive search (Note: mdfind is case-insensitive by default)")
    regex: Optional[str] = Field(None, description="Optional regex pattern to filter results by filename")
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
    
    # Add path restriction if specified (must come before query)
    if params.path:
        cmd.extend(["-onlyin", params.path])
    
    # Parse the query to handle complex mdfind syntax
    # Examples:
    # - Simple: "report" -> ["report"]
    # - Complex: "'寻找工程车' kind:movie" -> ["寻找工程车", "kind:movie"]
    # - With quotes: "\"hello world\" kind:pdf" -> ["hello world", "kind:pdf"]
    
    import shlex
    query = params.query
    
    # Try to intelligently split the query
    if " kind:" in query or " date:" in query or " modified:" in query:
        # This looks like a complex query with metadata
        try:
            # Use shlex to handle quoted strings properly
            parts = shlex.split(query)
            cmd.extend(parts)
        except ValueError:
            # If shlex fails, try manual splitting
            # Handle queries like: '寻找工程车' kind:movie
            if query.startswith("'") and "' " in query:
                first_quote_end = query.index("' ", 1)
                first_part = query[1:first_quote_end]
                rest = query[first_quote_end + 2:].strip()
                cmd.append(first_part)
                if rest:
                    cmd.extend(rest.split())
            else:
                cmd.append(query)
    else:
        # Simple query, just append as is
        cmd.append(query)
    
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
- `query`: Search query string using mdfind syntax (required)
- `path`: Directory to limit search (optional)
- `case_sensitive`: Enable case-sensitive search (default: false)
- `regex`: Optional regex pattern to filter results by filename after search
- `sort_by`: Sort results by 'name', 'size', or 'date' (optional)
- `limit`: Maximum results to return (default: 100, max: 1000)

## Query Syntax (mdfind):
- Simple text: `report`
- Exact filename: `kMDItemFSName == "report.pdf"`
- Wildcards: `kMDItemFSName == "*.py"`
- Content search: `kMDItemTextContent == "TODO"`
- File kind: `kind:pdf`, `kind:image`, `kind:movie`
- Date ranges: `date:today`, `date:yesterday`, `modified:this week`
- Combine with AND/OR: `report AND kind:pdf`

## Examples:
1. Basic search: `{"query": "report"}`
2. Search PDF files: `{"query": "kind:pdf"}`
3. Search by filename: `{"query": "kMDItemFSName == '*.py'"}`
4. Search in specific directory: `{"query": "report", "path": "/Users/username/Documents"}`
5. Complex query: `{"query": "invoice AND kind:pdf AND modified:this month"}`
6. Case-sensitive search: `{"query": "README", "case_sensitive": true}`
7. Sorted results: `{"query": "kind:image", "sort_by": "size", "limit": 50}`

## Notes:
- The query uses Spotlight's mdfind syntax
- For simple filename searches, just use the filename
- For advanced searches, use metadata attributes (kMDItem*)
- Recently created files might not appear immediately in Spotlight index
- Regex parameter applies post-filtering on filenames, not the mdfind query itself"""

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
            logger.error(f"mdfind failed with code {result.returncode}: {error_msg}")
            logger.debug(f"Command was: {' '.join(cmd)}")
            return SearchResult(
                success=False,
                files=[],
                count=0,
                error=f"mdfind failed (code {result.returncode}): {error_msg}"
            )
        
        # Parse results
        file_paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        
        # Remove duplicate paths
        file_paths = list(dict.fromkeys(file_paths))
        
        # Apply regex filtering if needed
        if params.regex:
            try:
                pattern = re.compile(params.regex, re.IGNORECASE if not params.case_sensitive else 0)
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