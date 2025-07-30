#!/usr/bin/env python3
"""
Featrix Sphere API Client

A simple Python client for testing the Featrix Sphere API endpoints,
with a focus on the new single predictor functionality.
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import gzip
import os
import random
import ssl
from urllib3.exceptions import SSLError as Urllib3SSLError


@dataclass
class SessionInfo:
    """Container for session information."""
    session_id: str
    session_type: str
    status: str
    jobs: Dict[str, Any]
    job_queue_positions: Dict[str, Any]


class FeatrixSphereClient:
    """Client for interacting with the Featrix Sphere API."""
    
    def __init__(self, base_url: str = "https://sphere-api.featrix.com", 
                 default_max_retries: int = 3, 
                 default_timeout: int = 30,
                 retry_base_delay: float = 1.0,
                 retry_max_delay: float = 60.0):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server
            default_max_retries: Default number of retries for failed requests
            default_timeout: Default timeout for requests in seconds
            retry_base_delay: Base delay for exponential backoff in seconds
            retry_max_delay: Maximum delay for exponential backoff in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # Set a reasonable timeout
        self.session.timeout = default_timeout
        
        # Retry configuration
        self.default_max_retries = default_max_retries
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        
    def _make_request(self, method: str, endpoint: str, max_retries: int = None, **kwargs) -> requests.Response:
        """
        Make an HTTP request with comprehensive error handling and retry logic.
        
        Retries on:
        - 503 Service Unavailable
        - SSL/TLS errors  
        - Connection errors
        - Timeout errors
        - Other transient network errors
        """
        if max_retries is None:
            max_retries = self.default_max_retries
            
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
                
            except requests.exceptions.HTTPError as e:
                # Retry on 503 Service Unavailable
                if e.response.status_code == 503 and attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    print(f"503 Service Unavailable, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    # Re-raise for other status codes or final attempt
                    print(f"API request failed: {method} {url}")
                    print(f"HTTP Error: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"Response status: {e.response.status_code}")
                        print(f"Response body: {e.response.text[:500]}")
                    raise
                    
            except (requests.exceptions.SSLError, ssl.SSLError, Urllib3SSLError) as e:
                # Retry on SSL/TLS errors (often transient)
                if attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    print(f"SSL/TLS error, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                    print(f"SSL Error details: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API request failed after {max_retries + 1} attempts: {method} {url}")
                    print(f"SSL Error: {e}")
                    raise
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Retry on connection errors and timeouts
                if attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    error_type = "Connection" if isinstance(e, requests.exceptions.ConnectionError) else "Timeout"
                    print(f"{error_type} error, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                    print(f"Error details: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API request failed after {max_retries + 1} attempts: {method} {url}")
                    print(f"Connection/Timeout Error: {e}")
                    raise
                    
            except requests.exceptions.RequestException as e:
                # For other request exceptions, retry if they might be transient
                error_msg = str(e).lower()
                is_transient = any(keyword in error_msg for keyword in [
                    'temporary failure', 'name resolution', 'network', 'reset', 
                    'broken pipe', 'connection aborted', 'bad gateway', 'gateway timeout'
                ])
                
                if is_transient and attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    print(f"Transient network error, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                    print(f"Error details: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API request failed: {method} {url}")
                    print(f"Request Error: {e}")
                    raise
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff with jitter.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay time in seconds with jitter applied
        """
        # Exponential backoff: base_delay * (2 ^ attempt)
        delay = self.retry_base_delay * (2 ** attempt)
        
        # Cap at max_delay
        delay = min(delay, self.retry_max_delay)
        
        # Add jitter (±25% randomization)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        
        return max(0.1, delay + jitter)  # Ensure minimum 0.1s delay
    
    def _get_json(self, endpoint: str, max_retries: int = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request and return JSON response."""
        response = self._make_request("GET", endpoint, max_retries=max_retries, **kwargs)
        return response.json()
    
    def _post_json(self, endpoint: str, data: Dict[str, Any] = None, max_retries: int = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request with JSON data and return JSON response."""
        if data is not None:
            kwargs['json'] = data
        response = self._make_request("POST", endpoint, max_retries=max_retries, **kwargs)
        return response.json()

    # =========================================================================
    # Session Management
    # =========================================================================
    
    def create_session(self, session_type: str = "sphere") -> SessionInfo:
        """
        Create a new session.
        
        Args:
            session_type: Type of session to create ('sphere', 'predictor', etc.)
            
        Returns:
            SessionInfo object with session details
        """
        print(f"Creating {session_type} session...")
        
        # Send empty JSON object to ensure proper content-type
        response_data = self._post_json("/compute/session", {})
        
        session_id = response_data.get('session_id')
        print(f"Created session: {session_id}")
        
        return SessionInfo(
            session_id=session_id,
            session_type=response_data.get('session_type', 'sphere'),
            status=response_data.get('status', 'unknown'),
            jobs={},
            job_queue_positions={}
        )
    
    def get_session_status(self, session_id: str) -> SessionInfo:
        """
        Get detailed session status.
        
        Args:
            session_id: ID of the session
            
        Returns:
            SessionInfo object with current session details
        """
        response_data = self._get_json(f"/compute/session/{session_id}")
        
        session = response_data.get('session', {})
        jobs = response_data.get('jobs', {})
        positions = response_data.get('job_queue_positions', {})
        
        return SessionInfo(
            session_id=session.get('session_id', session_id),
            session_type=session.get('session_type', 'unknown'),
            status=session.get('status', 'unknown'),
            jobs=jobs,
            job_queue_positions=positions
        )
    
    def get_session_models(self, session_id: str) -> Dict[str, Any]:
        """
        Get available models and embedding spaces for a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Dictionary containing available models, their metadata, and summary information
        """
        print(f"Getting available models for session {session_id}")
        
        response_data = self._get_json(f"/compute/session/{session_id}/models")
        
        models = response_data.get('models', {})
        summary = response_data.get('summary', {})
        
        print(f"Available models: {summary.get('available_model_types', [])}")
        print(f"Training complete: {'✅' if summary.get('training_complete') else '❌'}")
        print(f"Prediction ready: {'✅' if summary.get('prediction_ready') else '❌'}")
        print(f"Similarity search ready: {'✅' if summary.get('similarity_search_ready') else '❌'}")
        print(f"Visualization ready: {'✅' if summary.get('visualization_ready') else '❌'}")
        
        return response_data
    
    def wait_for_session_completion(self, session_id: str, max_wait_time: int = 3600, 
                                   check_interval: int = 10) -> SessionInfo:
        """
        Wait for a session to complete, with smart progress display.
        
        Args:
            session_id: ID of the session to monitor
            max_wait_time: Maximum time to wait in seconds
            check_interval: How often to check status in seconds
            
        Returns:
            Final SessionInfo when session completes or times out
        """
        return self._wait_with_smart_display(session_id, max_wait_time, check_interval)
    
    def _is_notebook(self) -> bool:
        """Detect if running in a Jupyter notebook."""
        try:
            from IPython import get_ipython
            ipython = get_ipython()
            return ipython is not None and hasattr(ipython, 'kernel')
        except ImportError:
            return False
    
    def _has_rich(self) -> bool:
        """Check if rich library is available."""
        try:
            import rich
            return True
        except ImportError:
            return False
    
    def _wait_with_smart_display(self, session_id: str, max_wait_time: int, check_interval: int) -> SessionInfo:
        """Smart progress display that adapts to environment."""
        
        if self._is_notebook():
            return self._wait_with_notebook_display(session_id, max_wait_time, check_interval)
        elif self._has_rich():
            return self._wait_with_rich_display(session_id, max_wait_time, check_interval)
        else:
            return self._wait_with_simple_display(session_id, max_wait_time, check_interval)
    
    def _wait_with_notebook_display(self, session_id: str, max_wait_time: int, check_interval: int) -> SessionInfo:
        """Notebook-optimized display with clean updates."""
        try:
            from IPython.display import clear_output, display, HTML
            import time
            
            print(f"🚀 Monitoring session {session_id}")
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                session_info = self.get_session_status(session_id)
                
                # Clear previous output and show updated status
                clear_output(wait=True)
                
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                
                html_content = f"""
                <h3>🚀 Session {session_id}</h3>
                <p><strong>Status:</strong> {session_info.status} | <strong>Elapsed:</strong> {mins:02d}:{secs:02d}</p>
                """
                
                if session_info.jobs:
                    html_content += "<h4>Jobs:</h4><ul>"
                    for job_id, job in session_info.jobs.items():
                        job_status = job.get('status', 'unknown')
                        progress = job.get('progress')
                        job_type = job.get('type', job_id.split('_')[0])
                        
                        if progress is not None:
                            progress_pct = progress * 100
                            progress_bar = "▓" * int(progress_pct / 5) + "░" * (20 - int(progress_pct / 5))
                            html_content += f"<li><strong>{job_type}:</strong> {job_status} [{progress_bar}] {progress_pct:.1f}%</li>"
                        else:
                            status_emoji = "✅" if job_status == "done" else "🔄" if job_status == "running" else "❌"
                            html_content += f"<li>{status_emoji} <strong>{job_type}:</strong> {job_status}</li>"
                    html_content += "</ul>"
                
                display(HTML(html_content))
                
                # Check completion
                if session_info.status in ['done', 'failed', 'cancelled']:
                    print(f"✅ Session completed with status: {session_info.status}")
                    return session_info
                
                if session_info.jobs:
                    terminal_states = {'done', 'failed', 'cancelled'}
                    all_jobs_terminal = all(job.get('status') in terminal_states for job in session_info.jobs.values())
                    if all_jobs_terminal:
                        job_summary = self._analyze_job_completion(session_info.jobs)
                        print(f"✅ All jobs completed. {job_summary}")
                        return session_info
                
                time.sleep(check_interval)
            
            print(f"⏰ Timeout after {max_wait_time} seconds")
            return self.get_session_status(session_id)
            
        except ImportError:
            # Fallback if IPython not available
            return self._wait_with_simple_display(session_id, max_wait_time, check_interval)
    
    def _wait_with_rich_display(self, session_id: str, max_wait_time: int, check_interval: int) -> SessionInfo:
        """Rich progress bars for beautiful terminal display."""
        try:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
            from rich.live import Live
            from rich.table import Table
            from rich.panel import Panel
            from rich.text import Text
            import time
            
            start_time = time.time()
            job_tasks = {}  # Track progress tasks for each job
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                expand=True
            ) as progress:
                
                # Main session task
                session_task = progress.add_task(f"[bold green]Session {session_id}", total=100)
                
                while time.time() - start_time < max_wait_time:
                    session_info = self.get_session_status(session_id)
                    
                    # Update session progress
                    elapsed = time.time() - start_time
                    session_progress = min(elapsed / max_wait_time * 100, 99)
                    progress.update(session_task, completed=session_progress, 
                                  description=f"[bold green]Session {session_id} ({session_info.status})")
                    
                    # Update job progress
                    current_jobs = set(session_info.jobs.keys())
                    
                    # Add new jobs
                    for job_id, job in session_info.jobs.items():
                        if job_id not in job_tasks:
                            job_type = job.get('type', job_id.split('_')[0])
                            job_tasks[job_id] = progress.add_task(f"[cyan]{job_type}", total=100)
                        
                        # Update job progress
                        job_status = job.get('status', 'unknown')
                        raw_progress = job.get('progress', 0)
                        job_progress = 100 if job_status == 'done' else (raw_progress * 100 if raw_progress else 0)
                        
                        progress.update(job_tasks[job_id], completed=job_progress,
                                      description=f"[cyan]{job.get('type', job_id.split('_')[0])} ({job_status})")
                    
                    # Check completion
                    if session_info.status in ['done', 'failed', 'cancelled']:
                        progress.update(session_task, completed=100, 
                                      description=f"[bold green]Session {session_id} ✅ {session_info.status}")
                        break
                    
                    if session_info.jobs:
                        terminal_states = {'done', 'failed', 'cancelled'}
                        all_jobs_terminal = all(job.get('status') in terminal_states for job in session_info.jobs.values())
                        if all_jobs_terminal:
                            progress.update(session_task, completed=100,
                                          description=f"[bold green]Session {session_id} ✅ completed")
                            break
                    
                    time.sleep(check_interval)
                
                # Final summary
                session_info = self.get_session_status(session_id)
                if session_info.jobs:
                    job_summary = self._analyze_job_completion(session_info.jobs)
                    progress.console.print(f"\n[bold green]✅ {job_summary}")
                
                return session_info
                
        except ImportError:
            # Fallback if rich not available
            return self._wait_with_simple_display(session_id, max_wait_time, check_interval)
    
    def _wait_with_simple_display(self, session_id: str, max_wait_time: int, check_interval: int) -> SessionInfo:
        """Simple display with line overwriting for basic terminals."""
        import sys
        import time
        
        print(f"🚀 Waiting for session {session_id} to complete...")
        start_time = time.time()
        last_num_lines = 0
        
        while time.time() - start_time < max_wait_time:
            session_info = self.get_session_status(session_id)
            
            # Clear previous lines if terminal supports it
            if sys.stdout.isatty() and last_num_lines > 0:
                for _ in range(last_num_lines):
                    sys.stdout.write('\033[F')  # Move cursor up
                    sys.stdout.write('\033[2K')  # Clear line
            
            # Build status display
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            
            lines = []
            lines.append(f"📊 Session {session_id} | Status: {session_info.status} | Elapsed: {mins:02d}:{secs:02d}")
            
            if session_info.jobs:
                for job_id, job in session_info.jobs.items():
                    job_status = job.get('status', 'unknown')
                    progress = job.get('progress')
                    job_type = job.get('type', job_id.split('_')[0])
                    
                    if progress is not None:
                        # Fix percentage issue: show 100% when job is done
                        progress_pct = 100.0 if job_status == 'done' else (progress * 100)
                        progress_bar = "█" * int(progress_pct / 5) + "░" * (20 - int(progress_pct / 5))
                        lines.append(f"  {job_type}: {job_status} [{progress_bar}] {progress_pct:.1f}%")
                    else:
                        status_emoji = "✅" if job_status == "done" else "🔄" if job_status == "running" else "❌"
                        lines.append(f"  {status_emoji} {job_type}: {job_status}")
            
            # Print all lines
            for line in lines:
                print(line)
            
            last_num_lines = len(lines)
            
            # Check completion
            if session_info.status in ['done', 'failed', 'cancelled']:
                print(f"\n✅ Session completed with status: {session_info.status}")
                return session_info
            
            if session_info.jobs:
                terminal_states = {'done', 'failed', 'cancelled'}
                all_jobs_terminal = all(job.get('status') in terminal_states for job in session_info.jobs.values())
                if all_jobs_terminal:
                    job_summary = self._analyze_job_completion(session_info.jobs)
                    print(f"\n✅ All jobs completed. {job_summary}")
                    return session_info
            
            time.sleep(check_interval)
        
        print(f"\n⏰ Timeout waiting for session completion after {max_wait_time} seconds")
        return self.get_session_status(session_id)

    def _analyze_job_completion(self, jobs: Dict[str, Any]) -> str:
        """
        Analyze job completion status and provide detailed summary.
        
        Args:
            jobs: Dictionary of job information
            
        Returns:
            Formatted string describing job completion status
        """
        done_jobs = []
        failed_jobs = []
        cancelled_jobs = []
        
        for job_id, job in jobs.items():
            status = job.get('status', 'unknown')
            job_type = job.get('type', 'unknown')
            
            if status == 'done':
                done_jobs.append(f"{job_type} ({job_id})")
            elif status == 'failed':
                error_info = ""
                # Look for error information in various possible fields
                if 'error' in job:
                    error_info = f" - Error: {job['error']}"
                elif 'message' in job:
                    error_info = f" - Message: {job['message']}"
                failed_jobs.append(f"{job_type} ({job_id}){error_info}")
            elif status == 'cancelled':
                cancelled_jobs.append(f"{job_type} ({job_id})")
        
        # Build summary message
        summary_parts = []
        if done_jobs:
            summary_parts.append(f"✅ {len(done_jobs)} succeeded: {', '.join(done_jobs)}")
        if failed_jobs:
            summary_parts.append(f"❌ {len(failed_jobs)} failed: {', '.join(failed_jobs)}")
        if cancelled_jobs:
            summary_parts.append(f"🚫 {len(cancelled_jobs)} cancelled: {', '.join(cancelled_jobs)}")
        
        return " | ".join(summary_parts) if summary_parts else "No jobs found"

    def create_embedding_space(self, name: str, s3_training_dataset: str, s3_validation_dataset: str) -> SessionInfo:
        """
        Create a new embedding space from S3 training and validation datasets.
        
        Args:
            name: Name for the embedding space
            s3_training_dataset: S3 URL for training dataset (must start with 's3://')
            s3_validation_dataset: S3 URL for validation dataset (must start with 's3://')
            
        Returns:
            SessionInfo for the newly created embedding space session
            
        Raises:
            ValueError: If S3 URLs are invalid
        """
        # Validate S3 URLs
        if not s3_training_dataset.startswith('s3://'):
            raise ValueError("s3_training_dataset must be a valid S3 URL (s3://...)")
        if not s3_validation_dataset.startswith('s3://'):
            raise ValueError("s3_validation_dataset must be a valid S3 URL (s3://...)")
        
        print(f"Creating embedding space '{name}' from S3 datasets...")
        print(f"  Training: {s3_training_dataset}")
        print(f"  Validation: {s3_validation_dataset}")
        
        data = {
            "name": name,
            "s3_file_data_set_training": s3_training_dataset,
            "s3_file_data_set_validation": s3_validation_dataset
        }
        
        response_data = self._post_json("/compute/create-embedding-space", data)
        
        session_id = response_data.get('session_id')
        print(f"Embedding space session created: {session_id}")
        
        return SessionInfo(
            session_id=session_id,
            session_type=response_data.get('session_type', 'embedding_space'),
            status=response_data.get('status', 'ready'),
            jobs={},
            job_queue_positions={}
        )

    # =========================================================================
    # File Upload
    # =========================================================================
    
    def upload_file_and_create_session(self, file_path: Path) -> SessionInfo:
        """
        Upload a CSV file and create a new session.
        
        Args:
            file_path: Path to the CSV file to upload
            
        Returns:
            SessionInfo for the newly created session
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"Uploading file: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'text/csv')}
            response = self._make_request("POST", "/compute/upload_with_new_session/", files=files)
        
        response_data = response.json()
        session_id = response_data.get('session_id')
        
        print(f"File uploaded, session created: {session_id}")
        
        # Check for and display warnings
        warnings = response_data.get('warnings', [])
        if warnings:
            print("\n" + "="*60)
            print("⚠️  UPLOAD WARNINGS")
            print("="*60)
            for warning in warnings:
                print(warning)
            print("="*60 + "\n")
        
        return SessionInfo(
            session_id=session_id,
            session_type=response_data.get('session_type', 'sphere'),
            status=response_data.get('status', 'ready'),
            jobs={},
            job_queue_positions={}
        )

    def upload_df_and_create_session(self, df=None, filename: str = "data.csv", file_path: str = None, 
                                    column_overrides: Dict[str, str] = None, string_list_delimiter: str = "|") -> SessionInfo:
        """
        Upload a pandas DataFrame or CSV file and create a new session.
        
        Args:
            df: pandas DataFrame to upload (optional if file_path is provided)
            filename: Name to give the uploaded file (default: "data.csv")
            file_path: Path to CSV file to upload (optional if df is provided)
            column_overrides: Dict mapping column names to types ("scalar", "set", "string", "string_list")
            string_list_delimiter: Delimiter for string_list columns (default: "|")
            
        Returns:
            SessionInfo for the newly created session
        """
        import pandas as pd
        import io
        import gzip
        import os
        
        # Validate inputs
        if df is None and file_path is None:
            raise ValueError("Either df or file_path must be provided")
        if df is not None and file_path is not None:
            raise ValueError("Provide either df or file_path, not both")
        
        # Handle file path input
        if file_path:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check if it's a CSV file
            if not file_path.lower().endswith(('.csv', '.csv.gz')):
                raise ValueError("File must be a CSV file (with .csv or .csv.gz extension)")
            
            print(f"Uploading file: {file_path}")
            
            # Read the file content
            if file_path.endswith('.gz'):
                # Already gzipped
                with gzip.open(file_path, 'rb') as f:
                    file_content = f.read()
                upload_filename = os.path.basename(file_path)
                content_type = 'application/gzip'
            else:
                # Read CSV and compress it
                with open(file_path, 'rb') as f:
                    csv_content = f.read()
                
                # Compress the content
                print("Compressing CSV file...")
                compressed_buffer = io.BytesIO()
                with gzip.GzipFile(fileobj=compressed_buffer, mode='wb') as gz:
                    gz.write(csv_content)
                file_content = compressed_buffer.getvalue()
                upload_filename = os.path.basename(file_path) + '.gz'
                content_type = 'application/gzip'
                
                original_size = len(csv_content)
                compressed_size = len(file_content)
                compression_ratio = (1 - compressed_size / original_size) * 100
                print(f"Compressed from {original_size:,} to {compressed_size:,} bytes ({compression_ratio:.1f}% reduction)")
        
        # Handle DataFrame input
        else:
            if not isinstance(df, pd.DataFrame):
                raise TypeError("df must be a pandas DataFrame")
            
            print(f"Uploading DataFrame ({len(df)} rows, {len(df.columns)} columns)")
            
            # Convert DataFrame to CSV and compress
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue().encode('utf-8')
            
            # Compress the CSV data
            print("Compressing DataFrame...")
            compressed_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=compressed_buffer, mode='wb') as gz:
                gz.write(csv_data)
            file_content = compressed_buffer.getvalue()
            upload_filename = filename if filename.endswith('.gz') else filename + '.gz'
            content_type = 'application/gzip'
            
            original_size = len(csv_data)
            compressed_size = len(file_content)
            compression_ratio = (1 - compressed_size / original_size) * 100
            print(f"Compressed from {original_size:,} to {compressed_size:,} bytes ({compression_ratio:.1f}% reduction)")
        
        # Upload the compressed file with optional column overrides
        files = {'file': (upload_filename, file_content, content_type)}
        
        # Add column overrides and string_list_delimiter as form data if provided
        data = {}
        if column_overrides:
            import json
            data['column_overrides'] = json.dumps(column_overrides)
            print(f"Column overrides: {column_overrides}")
        if string_list_delimiter != "|":  # Only send if non-default
            data['string_list_delimiter'] = string_list_delimiter
            print(f"String list delimiter: '{string_list_delimiter}'")
            
        response = self._make_request("POST", "/compute/upload_with_new_session/", files=files, data=data)
        
        response_data = response.json()
        session_id = response_data.get('session_id')
        
        print(f"Upload complete, session created: {session_id}")
        
        # Check for and display warnings
        warnings = response_data.get('warnings', [])
        if warnings:
            print("\n" + "="*60)
            print("⚠️  UPLOAD WARNINGS")
            print("="*60)
            for warning in warnings:
                print(warning)
            print("="*60 + "\n")
        
        return SessionInfo(
            session_id=session_id,
            session_type=response_data.get('session_type', 'sphere'),
            status=response_data.get('status', 'ready'),
            jobs={},
            job_queue_positions={}
        )
        


    # =========================================================================
    # Single Predictor Functionality
    # =========================================================================
    
    def predict(self, session_id: str, record: Dict[str, Any], max_retries: int = None) -> Dict[str, Any]:
        """
        Make a single prediction for a record.
        
        Args:
            session_id: ID of session with trained predictor
            record: Record dictionary (without target column)
            max_retries: Number of retries for errors (default: uses client default)
            
        Returns:
            Prediction result dictionary
        """
        response_data = self._post_json(f"/compute/session/{session_id}/predict", record, max_retries=max_retries)
        return response_data
    
    def get_training_metrics(self, session_id: str) -> Dict[str, Any]:
        """
        Get training metrics for a session's single predictor.
        
        Args:
            session_id: ID of session with trained single predictor
            
        Returns:
            Training metrics including loss history, validation metrics, etc.
        """
        response_data = self._get_json(f"/compute/session/{session_id}/training_metrics")
        return response_data

    def train_single_predictor(self, session_id: str, target_column: str, target_column_type: str, 
                              epochs: int = 50, batch_size: int = 256, learning_rate: float = 0.001) -> Dict[str, Any]:
        """
        Add single predictor training to an existing session that has a trained embedding space.
        
        Args:
            session_id: ID of session with trained embedding space
            target_column: Name of the target column to predict
            target_column_type: Type of target column ("set" or "scalar")
            epochs: Number of training epochs (default: 50)
            batch_size: Training batch size (default: 256)
            learning_rate: Learning rate for training (default: 0.001)
            
        Returns:
            Response with training start confirmation
        """
        data = {
            "target_column": target_column,
            "target_column_type": target_column_type,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate
        }
        
        response_data = self._post_json(f"/compute/session/{session_id}/train_predictor", data)
        return response_data

    # =========================================================================
    # JSON Tables Batch Prediction
    # =========================================================================
    
    def predict_table(self, session_id: str, table_data: Dict[str, Any], max_retries: int = None) -> Dict[str, Any]:
        """
        Make batch predictions using JSON Tables format.
        
        Args:
            session_id: ID of session with trained predictor
            table_data: Data in JSON Tables format, or list of records, or dict with 'table'/'records'
            max_retries: Number of retries for errors (default: uses client default, recommend higher for batch)
            
        Returns:
            Batch prediction results in JSON Tables format
            
        Raises:
            PredictorNotFoundError: If no single predictor has been trained for this session
        """
        # Use higher default for batch operations if not specified
        if max_retries is None:
            max_retries = max(5, self.default_max_retries)
        
        try:
            response_data = self._post_json(f"/compute/session/{session_id}/predict_table", table_data, max_retries=max_retries)
            return response_data
        except Exception as e:
            # Enhanced error handling for common prediction issues
            if "404" in str(e) and "Single predictor not found" in str(e):
                self._raise_predictor_not_found_error(session_id, "predict_table")
            else:
                raise
    
    def predict_records(self, session_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Make batch predictions on a list of records.
        
        Args:
            session_id: ID of session with trained predictor
            records: List of record dictionaries
            
        Returns:
            Batch prediction results
            
        Raises:
            PredictorNotFoundError: If no single predictor has been trained for this session
        """
        # Clean NaN/Inf values before sending
        cleaned_records = self._clean_numpy_values(records)
        
        # Convert to JSON Tables format
        from jsontables import JSONTablesEncoder
        table_data = JSONTablesEncoder.from_records(cleaned_records)
        
        try:
            return self.predict_table(session_id, table_data)
        except Exception as e:
            # Enhanced error handling for common prediction issues
            if "404" in str(e) and "Single predictor not found" in str(e):
                self._raise_predictor_not_found_error(session_id, "predict_records")
            else:
                raise
    
    def predict_df(self, session_id: str, df) -> Dict[str, Any]:
        """
        Make batch predictions on a pandas DataFrame.
        
        Args:
            session_id: ID of session with trained predictor
            df: Pandas DataFrame
            
        Returns:
            Batch prediction results
            
        Raises:
            PredictorNotFoundError: If no single predictor has been trained for this session
        """
        # Convert DataFrame to records and clean NaN/Inf values
        records = df.to_dict(orient='records')
        try:
            return self.predict_records(session_id, records)
        except Exception as e:
            # Enhanced error handling for common prediction issues
            if "404" in str(e) and "Single predictor not found" in str(e):
                self._raise_predictor_not_found_error(session_id, "predict_df")
            else:
                raise
    
    def _raise_predictor_not_found_error(self, session_id: str, method_name: str):
        """
        Raise a helpful error message when a single predictor is not found.
        
        Args:
            session_id: ID of the session
            method_name: Name of the method that was called
        """
        # Try to get session status to provide better guidance
        try:
            status = self.get_session_status(session_id)
            has_embedding = any('train_es' in job_id or 'embedding' in job.get('type', '') 
                              for job_id, job in status.jobs.items())
            has_predictor = any('train_single_predictor' in job_id or 'single_predictor' in job.get('type', '') 
                               for job_id, job in status.jobs.items())
            
            if not has_embedding:
                error_msg = f"""
❌ No trained model found for session {session_id}

🔍 ISSUE: This session doesn't have a trained embedding space yet.

🛠️  SOLUTION: Wait for training to complete, or start training:
   1. Check session status: client.get_session_status('{session_id}')
   2. Wait for completion: client.wait_for_session_completion('{session_id}')

📊 Current session jobs: {len(status.jobs)} jobs, status: {status.status}
"""
            elif not has_predictor:
                error_msg = f"""
❌ No single predictor found for session {session_id}

🔍 ISSUE: This session has a trained embedding space but no single predictor.

🛠️  SOLUTION: Train a single predictor first:
   client.train_single_predictor('{session_id}', 'target_column_name', 'set')
   
   Replace 'target_column_name' with your actual target column.
   Use 'set' for classification or 'scalar' for regression.

📊 Session has embedding space but needs predictor training.
"""
            else:
                error_msg = f"""
❌ Single predictor not ready for session {session_id}

🔍 ISSUE: Predictor training may still be in progress or failed.

🛠️  SOLUTION: Check training status:
   1. Check status: client.get_session_status('{session_id}')
   2. Check training metrics: client.get_training_metrics('{session_id}')
   3. Wait for completion if still training

📊 Found predictor job but prediction failed - training may be incomplete.
"""
                
        except Exception:
            # Fallback error message if we can't get session info
            error_msg = f"""
❌ Single predictor not found for session {session_id}

🔍 ISSUE: No trained single predictor available for predictions.

🛠️  SOLUTIONS:
   1. Train a single predictor:
      client.train_single_predictor('{session_id}', 'target_column', 'set')
   
   2. Check if training is still in progress:
      client.get_session_status('{session_id}')
   
   3. Create a new session if this one is corrupted:
      session = client.upload_df_and_create_session(df=your_data)
      client.train_single_predictor(session.session_id, 'target_column', 'set')

💡 TIP: Use 'set' for classification, 'scalar' for regression.
"""
        
        # Create a custom exception class for better error handling
        class PredictorNotFoundError(Exception):
            def __init__(self, message):
                super().__init__(message)
                self.session_id = session_id
                self.method_name = method_name
        
        raise PredictorNotFoundError(error_msg.strip())
    
    def predict_csv_file(self, session_id: str, file_path: Path) -> Dict[str, Any]:
        """
        Make batch predictions on a CSV file.
        
        Args:
            session_id: ID of session with trained predictor
            file_path: Path to CSV file
            
        Returns:
            Batch prediction results
        """
        import pandas as pd
        from jsontables import JSONTablesEncoder
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Convert to JSON Tables format
        table_data = JSONTablesEncoder.from_dataframe(df)
        
        return self.predict_table(session_id, table_data)

    def run_predictions(self, session_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run predictions on provided records. Clean and fast for production use.
        
        Args:
            session_id: ID of session with trained predictor
            records: List of record dictionaries
            
        Returns:
            Dictionary with prediction results
        """
        # Make batch predictions
        batch_results = self.predict_records(session_id, records)
        predictions = batch_results['predictions']
        
        # Process predictions into clean format
        results = []
        for pred in predictions:
            if pred['prediction']:
                record_idx = pred['row_index']
                prediction = pred['prediction']
                predicted_class = max(prediction, key=prediction.get)
                confidence = prediction[predicted_class]
                
                results.append({
                    'record_index': record_idx,
                    'predicted_class': predicted_class,
                    'confidence': confidence,
                    'full_prediction': prediction,
                    'error': batch_results.get('error', None),
                    'full_prediction': pred
                })
        
        return {
            'predictions': results,
            'total_records': len(records),
            'successful_predictions': len(results),
            'failed_predictions': len(records) - len(results)
        }

    def update_prediction_label(self, prediction_id: str, user_label: str) -> Dict[str, Any]:
        """
        Update the label for a prediction to enable retraining.
        
        Args:
            prediction_id: UUID of the prediction to update
            user_label: Correct label provided by user
            
        Returns:
            Update confirmation with prediction details
        """
        data = {
            "prediction_id": prediction_id,
            "user_label": user_label
        }
        response_data = self._post_json(f"/compute/prediction/{prediction_id}/update_label", data)
        return response_data
    
    def get_session_predictions(self, session_id: str, corrected_only: bool = False, limit: int = 100) -> Dict[str, Any]:
        """
        Get predictions for a session, optionally filtered for corrected ones.
        
        Args:
            session_id: ID of session
            corrected_only: Only return predictions with user corrections
            limit: Maximum number of predictions to return
            
        Returns:
            List of predictions with metadata
        """
        params = {
            "corrected_only": corrected_only,
            "limit": limit
        }
        response_data = self._get_json(f"/compute/session/{session_id}/predictions", params=params)
        return response_data
    
    def create_retraining_batch(self, session_id: str) -> Dict[str, Any]:
        """
        Create a retraining batch from corrected predictions.
        
        Args:
            session_id: ID of session with corrected predictions
            
        Returns:
            Retraining batch information
        """
        response_data = self._post_json(f"/compute/session/{session_id}/create_retraining_batch", {})
        return response_data

    def evaluate_predictions(self, session_id: str, records: List[Dict[str, Any]], 
                           actual_values: List[str], target_column: str = None) -> Dict[str, Any]:
        """
        Evaluate predictions with accuracy calculation. Use this for testing/validation.
        
        Args:
            session_id: ID of session with trained predictor
            records: List of record dictionaries
            actual_values: List of actual target values for accuracy calculation
            target_column: Name of target column (for display purposes)
            
        Returns:
            Dictionary with prediction results and accuracy metrics
        """
        # Get predictions
        pred_results = self.run_predictions(session_id, records)
        
        # Calculate accuracy
        correct_predictions = 0
        total_predictions = 0
        confidence_scores = []
        
        for pred in pred_results['predictions']:
            record_idx = pred['record_index']
            if record_idx < len(actual_values):
                predicted_class = pred['predicted_class']
                actual = str(actual_values[record_idx])
                confidence = pred['confidence']
                
                confidence_scores.append(confidence)
                total_predictions += 1
                
                if predicted_class == actual:
                    correct_predictions += 1
        
        # Add accuracy metrics
        if total_predictions > 0:
            accuracy = correct_predictions / total_predictions
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            pred_results['accuracy_metrics'] = {
                'accuracy': accuracy,
                'correct_predictions': correct_predictions,
                'total_predictions': total_predictions,
                'average_confidence': avg_confidence,
                'target_column': target_column
            }
        
        return pred_results

    def run_csv_predictions(self, session_id: str, csv_file: str, target_column: str = None,
                           sample_size: int = None, remove_target: bool = True) -> Dict[str, Any]:
        """
        Run predictions on a CSV file with automatic accuracy calculation.
        
        Args:
            session_id: ID of session with trained predictor
            csv_file: Path to CSV file
            target_column: Name of target column (for accuracy calculation)
            sample_size: Number of records to test (None = all records)
            remove_target: Whether to remove target column from prediction input
            
        Returns:
            Dictionary with prediction results and accuracy metrics
        """
        import pandas as pd
        
        # Load CSV
        df = pd.read_csv(csv_file)
        
        # Handle target column
        actual_values = None
        if target_column and target_column in df.columns:
            actual_values = df[target_column].tolist()
            if remove_target:
                prediction_df = df.drop(target_column, axis=1)
            else:
                prediction_df = df
        else:
            prediction_df = df
        
        # Take sample ONLY if explicitly requested
        if sample_size and sample_size < len(prediction_df):
            sample_df = prediction_df.head(sample_size)
            if actual_values:
                actual_values = actual_values[:sample_size]
        else:
            sample_df = prediction_df
        
        # Convert to records
        records = sample_df.to_dict('records')
        
        # Run predictions with accuracy calculation
        return self.evaluate_predictions(
            session_id=session_id,
            records=records,
            actual_values=actual_values,
            target_column=target_column
        )

    def run_comprehensive_test(self, session_id: str, test_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a comprehensive test of the single predictor including individual and batch predictions.
        
        Args:
            session_id: ID of session with trained predictor
            test_data: Optional dict with 'csv_file', 'target_column', 'sample_size', 'test_records'
            
        Returns:
            Comprehensive test results
        """
        print("🧪 " + "="*60)
        print("🧪 COMPREHENSIVE SINGLE PREDICTOR TEST")
        print("🧪 " + "="*60)
        
        results = {
            'session_id': session_id,
            'individual_tests': [],
            'batch_test': None,
            'training_metrics': None,
            'session_models': None
        }
        
        # 1. Check session models
        print("\n1. 📦 Checking available models...")
        try:
            models_info = self.get_session_models(session_id)
            results['session_models'] = models_info
        except Exception as e:
            print(f"Error checking models: {e}")
        
        # 2. Get training metrics
        print("\n2. 📊 Getting training metrics...")
        try:
            metrics = self.get_training_metrics(session_id)
            results['training_metrics'] = metrics
            
            training_metrics = metrics['training_metrics']
            print(f"Target column: {training_metrics.get('target_column')}")
            print(f"Target type: {training_metrics.get('target_column_type')}")
            print(f"Training epochs: {len(training_metrics.get('training_info', []))}")
        except Exception as e:
            print(f"Error getting training metrics: {e}")
        
        # 3. Individual prediction tests
        print("\n3. 🎯 Testing individual predictions...")
        
        # Default test records if none provided
        default_test_records = [
            {"domain": "shell.com", "snippet": "fuel card rewards program", "keyword": "fuel card"},
            {"domain": "exxon.com", "snippet": "gas station locator and fuel cards", "keyword": "gas station"},
            {"domain": "amazon.com", "snippet": "buy books online", "keyword": "books"},
            {"domain": "bp.com", "snippet": "fleet fuel cards for business", "keyword": "fleet cards"},
        ]
        
        test_records = test_data.get('test_records', default_test_records) if test_data else default_test_records
        
        for i, record in enumerate(test_records):
            try:
                result = self.predict(session_id, record)
                prediction = result['prediction']
                
                # Get predicted class and confidence
                predicted_class = max(prediction, key=prediction.get)
                confidence = prediction[predicted_class]
                
                test_result = {
                    'record': record,
                    'prediction': prediction,
                    'predicted_class': predicted_class,
                    'confidence': confidence,
                    'success': True
                }
                
                results['individual_tests'].append(test_result)
                print(f"✅ Record {i+1}: {predicted_class} ({confidence*100:.1f}%)")
                
            except Exception as e:
                test_result = {
                    'record': record,
                    'error': str(e),
                    'success': False
                }
                results['individual_tests'].append(test_result)
                print(f"❌ Record {i+1}: Error - {e}")
        
        # 4. Batch prediction test
        print("\n4. 📊 Testing batch predictions...")
        
        if test_data and test_data.get('csv_file'):
            try:
                batch_results = self.run_csv_predictions(
                    session_id=session_id,
                    csv_file=test_data['csv_file'],
                    target_column=test_data.get('target_column'),
                    sample_size=test_data.get('sample_size', 100)
                )
                results['batch_test'] = batch_results
                
                # Summary
                if batch_results.get('accuracy_metrics'):
                    acc = batch_results['accuracy_metrics']
                    print(f"✅ Batch test completed: {acc['accuracy']*100:.2f}% accuracy")
                else:
                    print(f"✅ Batch test completed: {batch_results['successful_predictions']} predictions")
                    
            except Exception as e:
                print(f"❌ Batch test failed: {e}")
                results['batch_test'] = {'error': str(e)}
        else:
            print("📝 No CSV file provided for batch testing")
        
        # 5. Summary
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        individual_success = sum(1 for t in results['individual_tests'] if t['success'])
        print(f"Individual predictions: {individual_success}/{len(results['individual_tests'])} successful")
        
        if results['batch_test'] and 'accuracy_metrics' in results['batch_test']:
            acc = results['batch_test']['accuracy_metrics']
            print(f"Batch prediction accuracy: {acc['accuracy']*100:.2f}%")
            print(f"Average confidence: {acc['average_confidence']*100:.2f}%")
        
        if results['training_metrics']:
            tm = results['training_metrics']['training_metrics']
            print(f"Model trained on: {tm.get('target_column')} ({tm.get('target_column_type')})")
        
        print("\n🎉 Comprehensive test completed!")
        
        return results

    # =========================================================================
    # Other API Endpoints
    # =========================================================================
    
    def encode_records(self, session_id: str, query_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode records using the embedding space.
        
        Args:
            session_id: ID of session with trained embedding space
            query_record: Record to encode
            
        Returns:
            Encoded vector representation
        """
        data = {"query_record": query_record}
        response_data = self._post_json(f"/compute/session/{session_id}/encode_records", data)
        return response_data
    
    def similarity_search(self, session_id: str, query_record: Dict[str, Any], k: int = 5) -> Dict[str, Any]:
        """
        Find similar records using vector similarity search.
        
        Args:
            session_id: ID of session with trained embedding space and vector DB
            query_record: Record to find similarities for
            k: Number of similar records to return
            
        Returns:
            List of similar records with distances
        """
        data = {"query_record": query_record}
        response_data = self._post_json(f"/compute/session/{session_id}/similarity_search", data)
        return response_data
    
    def get_projections(self, session_id: str) -> Dict[str, Any]:
        """
        Get 2D projections for visualization.
        
        Args:
            session_id: ID of session with generated projections
            
        Returns:
            Projection data for visualization
        """
        response_data = self._get_json(f"/compute/session/{session_id}/projections")
        return response_data


def main():
    """Example usage of the API client."""
    
    # Initialize client
    client = FeatrixSphereClient("https://sphere-api.featrix.com")
    
    print("=== Featrix Sphere API Client Test ===\n")
    
    try:
        # Example 1: Create a session and check status
        print("1. Creating a new session...")
        session_info = client.create_session("sphere")
        print(f"Session created: {session_info.session_id}\n")
        
        # Example 2: Check session status
        print("2. Checking session status...")
        current_status = client.get_session_status(session_info.session_id)
        print(f"Current status: {current_status.status}\n")
        
        # Example 3: Upload a file (if test data exists)
        test_file = Path("featrix_data/test.csv")
        if test_file.exists():
            print("3. Uploading test file...")
            upload_session = client.upload_file_and_create_session(test_file)
            print(f"Upload session: {upload_session.session_id}\n")
        else:
            print("3. Skipping file upload (test.csv not found)\n")
        
        print("API client test completed successfully!")
        
    except Exception as e:
        print(f"Error during API client test: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 