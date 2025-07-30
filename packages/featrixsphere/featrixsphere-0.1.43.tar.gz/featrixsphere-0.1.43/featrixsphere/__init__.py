"""
Featrix Sphere API Client

Transform any CSV into a production-ready ML model in minutes, not months.

The Featrix Sphere API automatically builds neural embedding spaces from your data 
and trains high-accuracy predictors without requiring any ML expertise. 
Just upload your data, specify what you want to predict, and get a production API endpoint.

Example:
    >>> from featrixsphere import FeatrixSphereClient
    >>> import pandas as pd
    >>> 
    >>> client = FeatrixSphereClient("http://your-server.com")
    >>> 
    >>> # Upload DataFrame directly
    >>> df = pd.read_csv("data.csv")
    >>> session = client.upload_df_and_create_session(df=df)
    >>> 
    >>> # Or upload CSV file directly (with automatic gzip compression)
    >>> session = client.upload_df_and_create_session(file_path="data.csv")
    >>> 
    >>> # Or use the original file upload method
    >>> session = client.upload_file_and_create_session("data.csv")
    >>> 
    >>> client.train_single_predictor(session.session_id, "target_column", "set")
    >>> result = client.predict(session.session_id, {"feature": "value"})
    >>> print(result['prediction'])
"""

__version__ = "0.1.43"
__author__ = "Featrix"
__email__ = "support@featrix.com"
__license__ = "MIT"

from .client import FeatrixSphereClient, SessionInfo

__all__ = [
    "FeatrixSphereClient",
    "SessionInfo",
    "__version__",
] 