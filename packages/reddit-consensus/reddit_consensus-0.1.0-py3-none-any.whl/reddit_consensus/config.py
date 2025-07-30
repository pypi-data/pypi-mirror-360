"""
Configuration constants for the Reddit Consensus system.
Centralized configuration for easy maintenance and tuning.
"""

import os

# LLM Model Configuration
DEFAULT_MODEL_NAME = "gpt-4.1-mini"  # Default OpenAI model to use
DEFAULT_MODEL_MAX_TOKENS = 4000  # Maximum tokens for model responses
DEFAULT_SUMMARIZATION_MODEL = "gpt-4.1-mini"  # Model for research data summarization
DEFAULT_SUMMARIZATION_MAX_TOKENS = 1000  # Max tokens for summary responses (increased for better compression)

# Comment tree depth configuration
DEFAULT_MAX_DEPTH = 3  # Maximum depth for comment tree traversal
DEFAULT_MAX_COMMENTS = 5  # Maximum number of comments/posts to fetch by default
DEFAULT_REPLACE_MORE_LIMIT = 3  # Limit for replacing "more comments" objects

# Comment filtering configuration
DEFAULT_SORT_BY_SCORE = True  # Sort comments by score (upvotes) instead of chronological
DEFAULT_ADAPTIVE_PERCENTILE = 80  # Filter bottom X% of comments by score

# Search configuration
DEFAULT_SEARCH_RESULTS = 5  # Default number of search results to return

# UI configuration
DEFAULT_UI_TREE_DISPLAY_DEPTH = 2  # Maximum depth to display in UI tree view
DEFAULT_UI_COMMENT_PREVIEW_LENGTH = 60  # Maximum length for comment preview text
DEFAULT_UI_TITLE_PREVIEW_LENGTH = 40  # Maximum length for title preview text

# Performance configuration
DEFAULT_TIMEOUT_SECONDS = 30  # Default timeout for Reddit API calls
DEFAULT_RETRY_ATTEMPTS = 3  # Number of retry attempts for failed requests

# LLM configuration
DEFAULT_REASONING_STEPS_LIMIT = (
    10  # Maximum reasoning steps before forcing finalization
)
DEFAULT_MINIMUM_SOURCES = 5  # Minimum sources to collect before finalizing
DEFAULT_RECOMMENDATION_COUNT = 3  # Default number of recommendations to generate

# Request pacing configuration (NOT token rate limiting)
DEFAULT_REQUEST_DELAY = 0.1  # Minimum seconds between API requests
DEFAULT_SUMMARIZATION_TRIGGER_TOKENS = 15000  # Start summarization at 15K tokens (more aggressive)
DEFAULT_PROMPT_HARD_LIMIT = 28000  # Maximum prompt size before rejection

# Summarization model configuration
# Summarization configuration uses same request pacing as main model

# Reddit API Configuration
REDDIT_ENV_VARS = {
    "client_id": "REDDIT_CLIENT_ID",
    "client_secret": "REDDIT_CLIENT_SECRET",
    "user_agent": "REDDIT_USER_AGENT",
}

# Reddit API Default Values (for development/testing)
REDDIT_DEFAULTS = {
    "user_agent": "RedditConsensus/1.0 (by /u/your_username)"  # Fallback user agent
}


def get_reddit_credentials() -> dict[str, str]:
    """Get Reddit API credentials from environment variables.

    Centralized credential management with clear error messages.
    All actual secrets remain in environment variables for security.

    Returns:
        Dict containing Reddit API credentials

    Raises:
        ValueError: If required credentials are missing
    """
    credentials = {}
    missing_vars = []

    for key, env_var in REDDIT_ENV_VARS.items():
        value = os.getenv(env_var)
        if not value:
            # Try defaults for non-sensitive fields
            if key in REDDIT_DEFAULTS:
                value = REDDIT_DEFAULTS[key]
            else:
                missing_vars.append(env_var)
        credentials[key] = value

    if missing_vars:
        raise ValueError(
            f"Reddit API credentials not found in environment variables: {', '.join(missing_vars)}.\n"
            f"Please set: {', '.join(missing_vars)}\n"
            f"Example: export REDDIT_CLIENT_ID='your_client_id'"
        )

    return credentials


# Validation functions
def validate_config() -> bool:
    """Validate that all required configuration is available."""
    try:
        get_reddit_credentials()
        return True
    except ValueError as e:
        print(f"Configuration error: {e}")
        return False
