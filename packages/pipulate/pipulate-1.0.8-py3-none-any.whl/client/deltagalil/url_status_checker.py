import asyncio
import aiohttp
import sqlite3
import pandas as pd
from typing import Dict, Set
from urllib.parse import urlparse
import time
from datetime import datetime
import os
from tqdm import tqdm
import signal

class URLStatusChecker:
    def __init__(self, db_path: str = "url_status.db"):
        self.db_path = db_path
        self._init_db()
        self.visited_urls: Dict[str, int] = {}
        self.session = None
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent connections
        self.total_processed = 0
        self.total_cached = 0
        self.should_stop = False
        self.rate_limited = False
        self.previous_429s = self._get_previous_429s()
        
    def _init_db(self):
        """Initialize SQLite database for storing URL statuses"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS url_status (
                url TEXT PRIMARY KEY,
                status_code INTEGER,
                checked_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        
    def _get_previous_429s(self) -> Set[str]:
        """Get set of URLs that previously returned 429"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT url FROM url_status WHERE status_code = 429")
        results = c.fetchall()
        conn.close()
        return {url for (url,) in results}
        
    async def __aenter__(self):
        """Async context manager setup"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager cleanup"""
        if self.session:
            await self.session.close()
            
    async def get_status_code(self, url: str) -> int:
        """Get status code for a URL, using cache if available"""
        if self.should_stop or self.rate_limited:
            raise asyncio.CancelledError()
            
        # Check local cache first (but not for previous 429s)
        if url in self.visited_urls and url not in self.previous_429s:
            self.total_cached += 1
            return self.visited_urls[url]
            
        # Check database (but not for previous 429s)
        if url not in self.previous_429s:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT status_code FROM url_status WHERE url = ?", (url,))
            result = c.fetchone()
            conn.close()
            
            if result:
                status_code = result[0]
                self.visited_urls[url] = status_code
                self.total_cached += 1
                return status_code
            
        # If not found or was a 429, make the request
        async with self.semaphore:  # Rate limiting
            try:
                async with self.session.get(url, timeout=30) as response:
                    status_code = response.status
                    if status_code == 429:
                        print("\nReceived 429 (Too Many Requests) status code. Stopping...")
                        self.rate_limited = True
                        raise asyncio.CancelledError()
            except Exception as e:
                print(f"\nError checking {url}: {str(e)}")
                status_code = 0  # Use 0 to indicate error
                
        # Store result
        self.visited_urls[url] = status_code
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO url_status (url, status_code, checked_at) VALUES (?, ?, ?)",
            (url, status_code, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        self.total_processed += 1
        return status_code

def signal_handler(signum, frame):
    print("\nReceived interrupt signal. Saving progress and exiting gracefully...")
    raise KeyboardInterrupt()

async def process_urls(csv_path: str, output_path: str):
    """Process URLs from CSV and save results"""
    print("Reading CSV file...")
    df = pd.read_csv(csv_path)
    
    # Get unique URLs
    urls = df['Full URL'].unique().tolist()
    print(f"Found {len(urls)} unique URLs to process")
    
    # Initialize results list
    all_status_codes = []
    
    # Process URLs
    async with URLStatusChecker() as checker:
        # Create progress bar
        pbar = tqdm(total=len(urls), desc="Processing URLs")
        
        try:
            # Process in chunks to update progress
            chunk_size = 100
            for i in range(0, len(urls), chunk_size):
                if checker.should_stop or checker.rate_limited:
                    break
                    
                chunk = urls[i:i + chunk_size]
                tasks = [checker.get_status_code(url) for url in chunk]
                status_codes = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Convert exceptions to 0 status code
                status_codes = [0 if isinstance(code, Exception) else code for code in status_codes]
                all_status_codes.extend(status_codes)
                
                pbar.update(len(chunk))
                
                # Print progress every chunk
                print(f"\nProcessed: {checker.total_processed}, Cached: {checker.total_cached}")
                
                # Save intermediate results
                intermediate_df = pd.DataFrame({
                    'Full URL': urls[:i + len(chunk)],
                    'Status Code': all_status_codes
                })
                intermediate_df.to_csv(output_path, index=False)
                
        except (KeyboardInterrupt, asyncio.CancelledError):
            checker.should_stop = True
            if checker.rate_limited:
                print("\nStopped due to rate limiting (429 status code)")
            else:
                print("\nGracefully stopping...")
        finally:
            pbar.close()
            
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the checker with correct paths
    asyncio.run(process_urls(
        os.path.join(script_dir, "pre-migration.csv"),
        os.path.join(script_dir, "url_status_results.csv")
    )) 