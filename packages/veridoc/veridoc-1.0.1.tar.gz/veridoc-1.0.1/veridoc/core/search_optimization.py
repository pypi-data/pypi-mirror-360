"""
Search Optimization for VeriDoc
Indexing and caching for high-performance search
"""

import os
import json
import hashlib
import time
import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with metadata."""
    file_path: str
    score: float
    matches: List[Dict[str, Any]]
    file_size: int
    last_modified: float
    file_type: str


@dataclass
class IndexEntry:
    """File index entry."""
    file_path: str
    content_hash: str
    last_modified: float
    file_size: int
    tokens: Set[str]
    content_preview: str  # First 200 chars


class SearchIndex:
    """In-memory search index with persistence."""
    
    def __init__(self, base_path: str, index_file: str = "search_index.json"):
        self.base_path = Path(base_path)
        self.index_file = self.base_path / ".veridoc" / index_file
        self.index: Dict[str, IndexEntry] = {}
        self.word_to_files: Dict[str, Set[str]] = defaultdict(set)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Create index directory
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing index
        self.load_index()
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get file content hash for change detection."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def _tokenize_content(self, content: str) -> Set[str]:
        """Tokenize content for search indexing."""
        # Simple tokenization - can be enhanced with proper NLP
        import re
        
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z0-9_]+\b', content.lower())
        
        # Filter out very short words
        tokens = {word for word in words if len(word) >= 2}
        
        # Add partial matches for file extensions and paths
        for word in list(tokens):
            if len(word) > 3:
                # Add prefixes for partial matching
                for i in range(2, min(len(word), 6)):
                    tokens.add(word[:i])
        
        return tokens
    
    def _should_index_file(self, file_path: Path) -> bool:
        """Check if file should be indexed."""
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return False
        
        # Skip binary files
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:
                    return False
        except Exception:
            return False
        
        # Check file extension
        indexable_extensions = {
            '.md', '.txt', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml',
            '.xml', '.csv', '.rst', '.org', '.tex', '.sh', '.bash', '.zsh',
            '.c', '.cpp', '.h', '.hpp', '.java', '.go', '.rs', '.php', '.rb',
            '.pl', '.r', '.sql', '.dockerfile', '.makefile', '.cmake'
        }
        
        ext = file_path.suffix.lower()
        if ext in indexable_extensions:
            return True
        
        # Check for files without extension that might be text
        if not ext:
            filename_lower = file_path.name.lower()
            text_files = {
                'readme', 'license', 'changelog', 'makefile', 'dockerfile',
                'authors', 'contributors', 'copying', 'install', 'news'
            }
            return filename_lower in text_files
        
        return False
    
    async def index_file(self, file_path: Path) -> bool:
        """Index a single file."""
        if not self._should_index_file(file_path):
            return False
        
        try:
            # Get file stats
            stat = file_path.stat()
            file_hash = self._get_file_hash(file_path)
            relative_path = str(file_path.relative_to(self.base_path))
            
            # Check if file needs reindexing
            if relative_path in self.index:
                existing = self.index[relative_path]
                if (existing.content_hash == file_hash and 
                    existing.last_modified == stat.st_mtime):
                    return False  # No changes, skip
                
                # Remove old tokens
                self._remove_file_tokens(relative_path)
            
            # Read file content
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = await f.read()
            
            # Limit content size for indexing
            if len(content) > 1024 * 1024:  # 1MB limit
                content = content[:1024 * 1024]
            
            # Tokenize content
            tokens = self._tokenize_content(content)
            
            # Create index entry
            entry = IndexEntry(
                file_path=relative_path,
                content_hash=file_hash,
                last_modified=stat.st_mtime,
                file_size=stat.st_size,
                tokens=tokens,
                content_preview=content[:200].replace('\n', ' ')
            )
            
            # Update index
            self.index[relative_path] = entry
            
            # Update word-to-files mapping
            for token in tokens:
                self.word_to_files[token].add(relative_path)
            
            logger.debug(f"Indexed file: {relative_path} ({len(tokens)} tokens)")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to index {file_path}: {e}")
            return False
    
    def _remove_file_tokens(self, file_path: str):
        """Remove file tokens from word-to-files mapping."""
        if file_path in self.index:
            for token in self.index[file_path].tokens:
                self.word_to_files[token].discard(file_path)
                if not self.word_to_files[token]:
                    del self.word_to_files[token]
    
    async def rebuild_index(self, progress_callback: Optional[callable] = None):
        """Rebuild the entire search index."""
        logger.info("Rebuilding search index...")
        start_time = time.time()
        
        # Clear existing index
        self.index.clear()
        self.word_to_files.clear()
        
        # Find all files to index
        files_to_index = []
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file() and self._should_index_file(file_path):
                files_to_index.append(file_path)
        
        # Index files in batches
        indexed_count = 0
        batch_size = 20
        
        for i in range(0, len(files_to_index), batch_size):
            batch = files_to_index[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [self.index_file(file_path) for file_path in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful indexing
            indexed_count += sum(1 for r in results if r is True)
            
            # Progress callback
            if progress_callback:
                progress = (i + len(batch)) / len(files_to_index)
                progress_callback(progress, indexed_count, len(files_to_index))
        
        # Save index
        await self.save_index()
        
        elapsed = time.time() - start_time
        logger.info(f"Index rebuild complete: {indexed_count} files indexed in {elapsed:.2f}s")
    
    async def update_index(self):
        """Update index for changed files."""
        logger.info("Updating search index...")
        start_time = time.time()
        
        updated_count = 0
        
        # Check existing indexed files for changes
        files_to_check = list(self.index.keys())
        for relative_path in files_to_check:
            file_path = self.base_path / relative_path
            
            if not file_path.exists():
                # File was deleted
                self._remove_file_tokens(relative_path)
                del self.index[relative_path]
                updated_count += 1
            else:
                # Check if file changed
                if await self.index_file(file_path):
                    updated_count += 1
        
        # Find new files
        for file_path in self.base_path.rglob('*'):
            if (file_path.is_file() and 
                self._should_index_file(file_path) and
                str(file_path.relative_to(self.base_path)) not in self.index):
                
                if await self.index_file(file_path):
                    updated_count += 1
        
        # Save index if changes were made
        if updated_count > 0:
            await self.save_index()
        
        elapsed = time.time() - start_time
        logger.info(f"Index update complete: {updated_count} files updated in {elapsed:.2f}s")
    
    def search(self, query: str, limit: int = 50) -> List[SearchResult]:
        """Search the index for matching files."""
        if not query or not query.strip():
            return []
        
        # Tokenize query
        query_tokens = self._tokenize_content(query.lower())
        
        # Find candidate files
        candidate_files = set()
        token_matches = {}
        
        for token in query_tokens:
            # Exact matches
            if token in self.word_to_files:
                files = self.word_to_files[token]
                candidate_files.update(files)
                for file_path in files:
                    token_matches[file_path] = token_matches.get(file_path, 0) + 1
            
            # Partial matches for longer tokens
            if len(token) >= 3:
                for indexed_token in self.word_to_files:
                    if indexed_token.startswith(token):
                        files = self.word_to_files[indexed_token]
                        candidate_files.update(files)
                        for file_path in files:
                            token_matches[file_path] = token_matches.get(file_path, 0) + 0.5
        
        # Score and rank results
        results = []
        for file_path in candidate_files:
            if file_path in self.index:
                entry = self.index[file_path]
                
                # Calculate score
                score = token_matches.get(file_path, 0)
                
                # Boost score for exact query matches in filename
                filename = os.path.basename(file_path).lower()
                if query.lower() in filename:
                    score += 2.0
                
                # Boost score for file type preferences
                if file_path.endswith(('.md', '.txt', '.rst')):
                    score += 0.5
                
                # Create search result
                result = SearchResult(
                    file_path=file_path,
                    score=score,
                    matches=[],  # TODO: Extract actual match contexts
                    file_size=entry.file_size,
                    last_modified=entry.last_modified,
                    file_type=Path(file_path).suffix or 'none'
                )
                results.append(result)
        
        # Sort by score and limit results
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    async def save_index(self):
        """Save index to disk."""
        try:
            # Convert index to serializable format
            index_data = {
                'metadata': {
                    'version': '1.0',
                    'created': time.time(),
                    'file_count': len(self.index)
                },
                'files': {}
            }
            
            for file_path, entry in self.index.items():
                index_data['files'][file_path] = {
                    'content_hash': entry.content_hash,
                    'last_modified': entry.last_modified,
                    'file_size': entry.file_size,
                    'tokens': list(entry.tokens),
                    'content_preview': entry.content_preview
                }
            
            # Write to temporary file first
            temp_file = self.index_file.with_suffix('.tmp')
            async with aiofiles.open(temp_file, 'w') as f:
                await f.write(json.dumps(index_data, indent=2))
            
            # Atomic move
            temp_file.replace(self.index_file)
            
            logger.debug(f"Index saved: {len(self.index)} files")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def load_index(self):
        """Load index from disk."""
        if not self.index_file.exists():
            return
        
        try:
            with open(self.index_file, 'r') as f:
                index_data = json.load(f)
            
            # Load files
            for file_path, data in index_data.get('files', {}).items():
                entry = IndexEntry(
                    file_path=file_path,
                    content_hash=data['content_hash'],
                    last_modified=data['last_modified'],
                    file_size=data['file_size'],
                    tokens=set(data['tokens']),
                    content_preview=data['content_preview']
                )
                
                self.index[file_path] = entry
                
                # Rebuild word-to-files mapping
                for token in entry.tokens:
                    self.word_to_files[token].add(file_path)
            
            logger.info(f"Index loaded: {len(self.index)} files")
            
        except Exception as e:
            logger.warning(f"Failed to load index: {e}")
            # Start with empty index
            self.index.clear()
            self.word_to_files.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'total_files': len(self.index),
            'total_tokens': len(self.word_to_files),
            'average_tokens_per_file': sum(len(entry.tokens) for entry in self.index.values()) / max(len(self.index), 1),
            'total_content_size': sum(entry.file_size for entry in self.index.values()),
            'index_file_size': self.index_file.stat().st_size if self.index_file.exists() else 0
        }


class SearchCache:
    """LRU cache for search results."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Tuple[List[SearchResult], float]] = {}
        self.access_order: List[str] = []
    
    def _make_key(self, query: str, limit: int) -> str:
        """Create cache key from search parameters."""
        return f"{query.lower().strip()}:{limit}"
    
    def get(self, query: str, limit: int) -> Optional[List[SearchResult]]:
        """Get cached search results."""
        key = self._make_key(query, limit)
        
        if key in self.cache:
            results, timestamp = self.cache[key]
            
            # Check if cache entry is still valid (5 minutes)
            if time.time() - timestamp < 300:
                # Move to end of access order
                self.access_order.remove(key)
                self.access_order.append(key)
                return results
            else:
                # Expired
                del self.cache[key]
                self.access_order.remove(key)
        
        return None
    
    def put(self, query: str, limit: int, results: List[SearchResult]):
        """Cache search results."""
        key = self._make_key(query, limit)
        
        # Remove if already exists
        if key in self.cache:
            self.access_order.remove(key)
        
        # Add new entry
        self.cache[key] = (results, time.time())
        self.access_order.append(key)
        
        # Evict oldest if over limit
        while len(self.cache) > self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
    
    def clear(self):
        """Clear all cached results."""
        self.cache.clear()
        self.access_order.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'hit_ratio': 0  # TODO: Track hits/misses
        }


class OptimizedSearchEngine:
    """High-performance search engine with indexing and caching."""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.index = SearchIndex(base_path)
        self.cache = SearchCache()
        
        # Background updates will be started when event loop is available
        self._index_update_task = None
    
    async def start_background_updates(self):
        """Start background task for periodic index updates."""
        if self._index_update_task is not None:
            return  # Already started
            
        async def update_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # Update every 5 minutes
                    await self.index.update_index()
                    # Clear cache after index update
                    self.cache.clear()
                except Exception as e:
                    logger.error(f"Background index update failed: {e}")
        
        # Start task
        self._index_update_task = asyncio.create_task(update_loop())
    
    async def search(self, 
                    query: str, 
                    search_type: str = "both",
                    limit: int = 50) -> List[Dict[str, Any]]:
        """Search with caching and indexing."""
        
        # Check cache first
        cached_results = self.cache.get(query, limit)
        if cached_results is not None:
            return [asdict(result) for result in cached_results]
        
        # Perform search
        if search_type in ["content", "both"]:
            results = self.index.search(query, limit)
        else:
            # Filename search only
            results = []
            query_lower = query.lower()
            for file_path in self.index.index:
                if query_lower in os.path.basename(file_path).lower():
                    entry = self.index.index[file_path]
                    result = SearchResult(
                        file_path=file_path,
                        score=1.0,
                        matches=[],
                        file_size=entry.file_size,
                        last_modified=entry.last_modified,
                        file_type=Path(file_path).suffix or 'none'
                    )
                    results.append(result)
            
            results.sort(key=lambda x: x.file_path)
            results = results[:limit]
        
        # Cache results
        self.cache.put(query, limit, results)
        
        return [asdict(result) for result in results]
    
    async def rebuild_index(self, progress_callback: Optional[callable] = None):
        """Rebuild search index."""
        self.cache.clear()
        await self.index.rebuild_index(progress_callback)
    
    async def update_index(self):
        """Update search index."""
        await self.index.update_index()
        self.cache.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        return {
            'index': self.index.get_statistics(),
            'cache': self.cache.get_statistics()
        }
    
    def __del__(self):
        """Cleanup background tasks."""
        if self._index_update_task:
            self._index_update_task.cancel()