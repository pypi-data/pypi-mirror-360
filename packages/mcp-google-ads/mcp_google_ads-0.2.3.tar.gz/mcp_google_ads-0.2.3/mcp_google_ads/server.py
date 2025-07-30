from typing import Any, Dict, List, Optional, Union
from pydantic import Field
import os
import json
import requests
from datetime import datetime, timedelta
import base64
import mimetypes
from pathlib import Path
import io

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import logging

# MCP
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('google_ads_server')

mcp = FastMCP(
    "google-ads-server",
    dependencies=[
        "google-auth-oauthlib",
        "google-auth",
        "requests",
        "python-dotenv"
    ]
)

# Constants and configuration
SCOPES = ['https://www.googleapis.com/auth/adwords']
API_VERSION = "v19"  # Google Ads API version

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load from .env file if it exists
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except ImportError:
    logger.warning("python-dotenv not installed, skipping .env file loading")

# Environment variables will be loaded at runtime, not import time
def get_env_var(key, default=None):
    """Get environment variable at runtime."""
    return os.environ.get(key, default)

def format_customer_id(customer_id: str) -> str:
    """Format customer ID to ensure it's 10 digits without dashes."""
    # Convert to string if passed as integer or another type
    customer_id = str(customer_id)
    
    # Remove any quotes surrounding the customer_id (both escaped and unescaped)
    customer_id = customer_id.replace('\"', '').replace('"', '')
    
    # Remove any non-digit characters (including dashes, braces, etc.)
    customer_id = ''.join(char for char in customer_id if char.isdigit())
    
    # Ensure it's 10 digits with leading zeros if needed
    return customer_id.zfill(10)

def get_credentials():
    """
    Get and refresh OAuth credentials or service account credentials based on the auth type.
    
    This function supports two authentication methods:
    1. OAuth 2.0 (User Authentication) - For individual users or desktop applications
    2. Service Account (Server-to-Server Authentication) - For automated systems

    Returns:
        Valid credentials object to use with Google Ads API
    """
    auth_type = get_env_var("GOOGLE_ADS_AUTH_TYPE", "oauth").lower()
    logger.info(f"Using authentication type: {auth_type}")
    
    # Service Account authentication
    if auth_type == "service_account":
        try:
            return get_service_account_credentials()
        except Exception as e:
            logger.error(f"Error with service account authentication: {str(e)}")
            raise
    
    # OAuth 2.0 authentication (default)
    return get_oauth_credentials()

def get_service_account_credentials():
    """Get credentials using a service account key file."""
    credentials_path = get_env_var("GOOGLE_ADS_CREDENTIALS_PATH")
    if not credentials_path:
        raise ValueError("GOOGLE_ADS_CREDENTIALS_PATH environment variable not set for service account")
    
    logger.info(f"Loading service account credentials from {credentials_path}")
    
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Service account key file not found at {credentials_path}")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, 
            scopes=SCOPES
        )
        
        # Check if impersonation is required
        impersonation_email = get_env_var("GOOGLE_ADS_IMPERSONATION_EMAIL")
        if impersonation_email:
            logger.info(f"Impersonating user: {impersonation_email}")
            credentials = credentials.with_subject(impersonation_email)
            
        return credentials
        
    except Exception as e:
        logger.error(f"Error loading service account credentials: {str(e)}")
        raise

def get_oauth_credentials():
    """Get and refresh OAuth user credentials."""
    creds = None
    client_config = None
    
    # Check if we have a refresh token in environment variables
    refresh_token = get_env_var("GOOGLE_ADS_REFRESH_TOKEN")
    client_id = get_env_var("GOOGLE_ADS_CLIENT_ID")
    client_secret = get_env_var("GOOGLE_ADS_CLIENT_SECRET")
    
    if refresh_token and client_id and client_secret:
        logger.info("Using refresh token from environment variables")
        creds_info = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "type": "authorized_user"
        }
        try:
            creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
            # Test if credentials work by refreshing them
            if creds.expired or not creds.token:
                creds.refresh(Request())
            logger.info("Successfully created credentials from environment variables")
            return creds
        except Exception as e:
            logger.warning(f"Error using refresh token from environment: {str(e)}, falling back to file-based flow")
    
    # Fallback to file-based credentials if environment variables don't work
    credentials_path = get_env_var("GOOGLE_ADS_CREDENTIALS_PATH")
    if not credentials_path:
        if client_id and client_secret:
            # If we have client credentials but no refresh token, start OAuth flow
            logger.info("No refresh token found, will start OAuth flow")
        else:
            raise ValueError("Either GOOGLE_ADS_REFRESH_TOKEN or GOOGLE_ADS_CREDENTIALS_PATH must be set")
    
    # Path to store the refreshed token
    token_path = credentials_path or "/tmp/google_ads_token.json"
    if credentials_path and os.path.exists(token_path) and not os.path.basename(token_path).endswith('.json'):
        # If it's not explicitly a .json file, append a default name
        token_dir = os.path.dirname(token_path)
        token_path = os.path.join(token_dir, 'google_ads_token.json')
    
    # Check if token file exists and load credentials
    if credentials_path and os.path.exists(token_path):
        try:
            logger.info(f"Loading OAuth credentials from {token_path}")
            with open(token_path, 'r') as f:
                creds_data = json.load(f)
                # Check if this is a client config or saved credentials
                if "installed" in creds_data or "web" in creds_data:
                    client_config = creds_data
                    logger.info("Found OAuth client configuration")
                else:
                    logger.info("Found existing OAuth token")
                    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in token file: {token_path}")
            creds = None
        except Exception as e:
            logger.warning(f"Error loading credentials: {str(e)}")
            creds = None
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired token")
                creds.refresh(Request())
                logger.info("Token successfully refreshed")
            except RefreshError as e:
                logger.warning(f"Error refreshing token: {str(e)}, will try to get new token")
                creds = None
            except Exception as e:
                logger.error(f"Unexpected error refreshing token: {str(e)}")
                raise
        
        # If we need new credentials
        if not creds:
            # If no client_config is defined yet, create one from environment variables
            if not client_config:
                logger.info("Creating OAuth client config from environment variables")
                client_id = get_env_var("GOOGLE_ADS_CLIENT_ID")
                client_secret = get_env_var("GOOGLE_ADS_CLIENT_SECRET")
                
                if not client_id or not client_secret:
                    raise ValueError("GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set if no client config file exists")
                
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                    }
                }
            
            # Run the OAuth flow
            logger.info("Starting OAuth authentication flow")
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("OAuth flow completed successfully")
        
        # Save the refreshed/new credentials
        try:
            logger.info(f"Saving credentials to {token_path}")
            # Ensure directory exists
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        except Exception as e:
            logger.warning(f"Could not save credentials: {str(e)}")
    
    return creds

def get_headers(creds):
    """Get headers for Google Ads API requests."""
    developer_token = get_env_var("GOOGLE_ADS_DEVELOPER_TOKEN")
    if not developer_token:
        raise ValueError("GOOGLE_ADS_DEVELOPER_TOKEN environment variable not set")
    
    # Handle different credential types
    if isinstance(creds, service_account.Credentials):
        # For service account, we need to get a new bearer token
        auth_req = Request()
        creds.refresh(auth_req)
        token = creds.token
    else:
        # For OAuth credentials
        token = creds.token
        
    headers = {
        'Authorization': f'Bearer {token}',
        'developer-token': developer_token,
        'content-type': 'application/json'
    }
    
    login_customer_id = get_env_var("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    if login_customer_id:
        headers['login-customer-id'] = format_customer_id(login_customer_id)
    
    return headers

@mcp.tool()
async def list_accounts() -> str:
    """
    Lists all accessible Google Ads accounts.
    
    This is typically the first command you should run to identify which accounts 
    you have access to. The returned account IDs can be used in subsequent commands.
    
    Returns:
        A formatted list of all Google Ads accounts accessible with your credentials
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers:listAccessibleCustomers"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return f"Error accessing accounts: {response.text}"
        
        customers = response.json()
        if not customers.get('resourceNames'):
            return "No accessible accounts found."
        
        # Format the results
        result_lines = ["Accessible Google Ads Accounts:"]
        result_lines.append("-" * 50)
        
        for resource_name in customers['resourceNames']:
            customer_id = resource_name.split('/')[-1]
            formatted_id = format_customer_id(customer_id)
            result_lines.append(f"Account ID: {formatted_id}")
        
        return "\n".join(result_lines)
    
    except Exception as e:
        return f"Error listing accounts: {str(e)}"

@mcp.tool()
async def execute_gaql_query(
    customer_id: Union[str, int] = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    query: str = Field(description="Valid GAQL query string following Google Ads Query Language syntax")
) -> str:
    """
    Execute a custom GAQL (Google Ads Query Language) query.
    
    This tool allows you to run any valid GAQL query against the Google Ads API.
    Always specify the customer_id as a string (even if it looks like a number).
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        query: The GAQL query to execute (must follow GAQL syntax)
        
    Returns:
        Formatted query results or error message
        
    Example:
        customer_id: "1234567890"
        query: "SELECT campaign.id, campaign.name FROM campaign LIMIT 10"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
        
        payload = {"query": query}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return f"Error executing query: {response.text}"
        
        results = response.json()
        if not results.get('results'):
            return "No results found for the query."
        
        # Format the results as a table
        result_lines = [f"Query Results for Account {formatted_customer_id}:"]
        result_lines.append("-" * 80)
        
        # Get field names from the first result
        fields = []
        first_result = results['results'][0]
        for key in first_result:
            if isinstance(first_result[key], dict):
                for subkey in first_result[key]:
                    fields.append(f"{key}.{subkey}")
            else:
                fields.append(key)
        
        # Add header
        result_lines.append(" | ".join(fields))
        result_lines.append("-" * 80)
        
        # Add data rows
        for result in results['results']:
            row_data = []
            for field in fields:
                if "." in field:
                    parent, child = field.split(".")
                    value = str(result.get(parent, {}).get(child, ""))
                else:
                    value = str(result.get(field, ""))
                row_data.append(value)
            result_lines.append(" | ".join(row_data))
        
        return "\n".join(result_lines)
    
    except Exception as e:
        return f"Error executing GAQL query: {str(e)}"

@mcp.tool()
async def get_campaign_performance(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes) as a string"),
    days: int = Field(default=30, description="Number of days to look back (7, 30, 90, etc.)")
) -> str:
    """
    Get campaign performance metrics for the specified time period.
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Then run get_account_currency() to see what currency the account uses
    3. Finally run this command to get campaign performance
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        days: Number of days to look back (default: 30)
        
    Returns:
        Formatted table of campaign performance data
        
    Note:
        Cost values are in micros (millionths) of the account currency
        (e.g., 1000000 = 1 USD in a USD account)
        
    Example:
        customer_id: "1234567890"
        days: 14
    """
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING LAST_{days}DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 50
    """
    
    return await execute_gaql_query(customer_id, query)

@mcp.tool()
async def get_ad_performance(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes) as a string"),
    days: int = Field(default=30, description="Number of days to look back (7, 30, 90, etc.)")
) -> str:
    """
    Get ad performance metrics for the specified time period.
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Then run get_account_currency() to see what currency the account uses
    3. Finally run this command to get ad performance
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        days: Number of days to look back (default: 30)
        
    Returns:
        Formatted table of ad performance data
        
    Note:
        Cost values are in micros (millionths) of the account currency
        (e.g., 1000000 = 1 USD in a USD account)
        
    Example:
        customer_id: "1234567890"
        days: 14
    """
    query = f"""
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.status,
            campaign.name,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM ad_group_ad
        WHERE segments.date DURING LAST_{days}DAYS
        ORDER BY metrics.impressions DESC
        LIMIT 50
    """
    
    return await execute_gaql_query(customer_id, query)

@mcp.tool()
async def run_gaql(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    query: str = Field(description="Valid GAQL query string following Google Ads Query Language syntax"),
    format: str = Field(default="table", description="Output format: 'table', 'json', or 'csv'")
) -> str:
    """
    Execute any arbitrary GAQL (Google Ads Query Language) query with custom formatting options.
    
    This is the most powerful tool for custom Google Ads data queries. Always format your
    customer_id as a string, even though it looks like a number.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        query: The GAQL query to execute (any valid GAQL query)
        format: Output format ("table", "json", or "csv")
    
    Returns:
        Query results in the requested format
    
    EXAMPLE QUERIES:
    
    1. Basic campaign metrics:
        SELECT 
          campaign.name, 
          metrics.clicks, 
          metrics.impressions,
          metrics.cost_micros
        FROM campaign 
        WHERE segments.date DURING LAST_7DAYS
    
    2. Ad group performance:
        SELECT 
          ad_group.name, 
          metrics.conversions, 
          metrics.cost_micros,
          campaign.name
        FROM ad_group 
        WHERE metrics.clicks > 100
    
    3. Keyword analysis:
        SELECT 
          keyword.text, 
          metrics.average_position, 
          metrics.ctr
        FROM keyword_view 
        ORDER BY metrics.impressions DESC
        
    4. Get conversion data:
        SELECT
          campaign.name,
          metrics.conversions,
          metrics.conversions_value,
          metrics.cost_micros
        FROM campaign
        WHERE segments.date DURING LAST_30DAYS
        
    Note:
        Cost values are in micros (millionths) of the account currency
        (e.g., 1000000 = 1 USD in a USD account)
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
        
        payload = {"query": query}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return f"Error executing query: {response.text}"
        
        results = response.json()
        if not results.get('results'):
            return "No results found for the query."
        
        if format.lower() == "json":
            return json.dumps(results, indent=2)
        
        elif format.lower() == "csv":
            # Get field names from the first result
            fields = []
            first_result = results['results'][0]
            for key, value in first_result.items():
                if isinstance(value, dict):
                    for subkey in value:
                        fields.append(f"{key}.{subkey}")
                else:
                    fields.append(key)
            
            # Create CSV string
            csv_lines = [",".join(fields)]
            for result in results['results']:
                row_data = []
                for field in fields:
                    if "." in field:
                        parent, child = field.split(".")
                        value = str(result.get(parent, {}).get(child, "")).replace(",", ";")
                    else:
                        value = str(result.get(field, "")).replace(",", ";")
                    row_data.append(value)
                csv_lines.append(",".join(row_data))
            
            return "\n".join(csv_lines)
        
        else:  # default table format
            result_lines = [f"Query Results for Account {formatted_customer_id}:"]
            result_lines.append("-" * 100)
            
            # Get field names and maximum widths
            fields = []
            field_widths = {}
            first_result = results['results'][0]
            
            for key, value in first_result.items():
                if isinstance(value, dict):
                    for subkey in value:
                        field = f"{key}.{subkey}"
                        fields.append(field)
                        field_widths[field] = len(field)
                else:
                    fields.append(key)
                    field_widths[key] = len(key)
            
            # Calculate maximum field widths
            for result in results['results']:
                for field in fields:
                    if "." in field:
                        parent, child = field.split(".")
                        value = str(result.get(parent, {}).get(child, ""))
                    else:
                        value = str(result.get(field, ""))
                    field_widths[field] = max(field_widths[field], len(value))
            
            # Create formatted header
            header = " | ".join(f"{field:{field_widths[field]}}" for field in fields)
            result_lines.append(header)
            result_lines.append("-" * len(header))
            
            # Add data rows
            for result in results['results']:
                row_data = []
                for field in fields:
                    if "." in field:
                        parent, child = field.split(".")
                        value = str(result.get(parent, {}).get(child, ""))
                    else:
                        value = str(result.get(field, ""))
                    row_data.append(f"{value:{field_widths[field]}}")
                result_lines.append(" | ".join(row_data))
            
            return "\n".join(result_lines)
    
    except Exception as e:
        return f"Error executing GAQL query: {str(e)}"

@mcp.tool()
async def get_ad_creatives(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes) as a string")
) -> str:
    """
    Get ad creative details including headlines, descriptions, and URLs.
    
    This tool retrieves the actual ad content (headlines, descriptions) 
    for review and analysis. Great for creative audits.
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Then run this command with the desired account ID
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        
    Returns:
        Formatted list of ad creative details
        
    Example:
        customer_id: "1234567890"
    """
    query = """
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.ad.type,
            ad_group_ad.ad.final_urls,
            ad_group_ad.status,
            ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions,
            ad_group.name,
            campaign.name
        FROM ad_group_ad
        WHERE ad_group_ad.status != 'REMOVED'
        ORDER BY campaign.name, ad_group.name
        LIMIT 50
    """
    
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
        
        payload = {"query": query}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return f"Error retrieving ad creatives: {response.text}"
        
        results = response.json()
        if not results.get('results'):
            return "No ad creatives found for this customer ID."
        
        # Format the results in a readable way
        output_lines = [f"Ad Creatives for Customer ID {formatted_customer_id}:"]
        output_lines.append("=" * 80)
        
        for i, result in enumerate(results['results'], 1):
            ad = result.get('adGroupAd', {}).get('ad', {})
            ad_group = result.get('adGroup', {})
            campaign = result.get('campaign', {})
            
            output_lines.append(f"\n{i}. Campaign: {campaign.get('name', 'N/A')}")
            output_lines.append(f"   Ad Group: {ad_group.get('name', 'N/A')}")
            output_lines.append(f"   Ad ID: {ad.get('id', 'N/A')}")
            output_lines.append(f"   Ad Name: {ad.get('name', 'N/A')}")
            output_lines.append(f"   Status: {result.get('adGroupAd', {}).get('status', 'N/A')}")
            output_lines.append(f"   Type: {ad.get('type', 'N/A')}")
            
            # Handle Responsive Search Ads
            rsa = ad.get('responsiveSearchAd', {})
            if rsa:
                if 'headlines' in rsa:
                    output_lines.append("   Headlines:")
                    for headline in rsa['headlines']:
                        output_lines.append(f"     - {headline.get('text', 'N/A')}")
                
                if 'descriptions' in rsa:
                    output_lines.append("   Descriptions:")
                    for desc in rsa['descriptions']:
                        output_lines.append(f"     - {desc.get('text', 'N/A')}")
            
            # Handle Final URLs
            final_urls = ad.get('finalUrls', [])
            if final_urls:
                output_lines.append(f"   Final URLs: {', '.join(final_urls)}")
            
            output_lines.append("-" * 80)
        
        return "\n".join(output_lines)
    
    except Exception as e:
        return f"Error retrieving ad creatives: {str(e)}"

@mcp.tool()
async def get_account_currency(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)")
) -> str:
    """
    Retrieve the default currency code used by the Google Ads account.
    
    IMPORTANT: Run this first before analyzing cost data to understand which currency
    the account uses. Cost values are always displayed in the account's currency.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
    
    Returns:
        The account's default currency code (e.g., 'USD', 'EUR', 'GBP')
        
    Example:
        customer_id: "1234567890"
    """
    query = """
        SELECT
            customer.id,
            customer.currency_code
        FROM customer
        LIMIT 1
    """
    
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
        
        payload = {"query": query}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return f"Error retrieving account currency: {response.text}"
        
        results = response.json()
        if not results.get('results'):
            return "No account information found for this customer ID."
        
        # Extract the currency code from the results
        customer = results['results'][0].get('customer', {})
        currency_code = customer.get('currencyCode', 'Not specified')
        
        return f"Account {formatted_customer_id} uses currency: {currency_code}"
    
    except Exception as e:
        return f"Error retrieving account currency: {str(e)}"

@mcp.resource("gaql://reference")
def gaql_reference() -> str:
    """Google Ads Query Language (GAQL) reference documentation."""
    return """
    # Google Ads Query Language (GAQL) Reference
    
    GAQL is similar to SQL but with specific syntax for Google Ads. Here's a quick reference:
    
    ## Basic Query Structure
    ```
    SELECT field1, field2, ... 
    FROM resource_type
    WHERE condition
    ORDER BY field [ASC|DESC]
    LIMIT n
    ```
    
    ## Common Field Types
    
    ### Resource Fields
    - campaign.id, campaign.name, campaign.status
    - ad_group.id, ad_group.name, ad_group.status
    - ad_group_ad.ad.id, ad_group_ad.ad.final_urls
    - keyword.text, keyword.match_type
    
    ### Metric Fields
    - metrics.impressions
    - metrics.clicks
    - metrics.cost_micros
    - metrics.conversions
    - metrics.ctr
    - metrics.average_cpc
    
    ### Segment Fields
    - segments.date
    - segments.device
    - segments.day_of_week
    
    ## Common WHERE Clauses
    
    ### Date Ranges
    - WHERE segments.date DURING LAST_7DAYS
    - WHERE segments.date DURING LAST_30DAYS
    - WHERE segments.date BETWEEN '2023-01-01' AND '2023-01-31'
    
    ### Filtering
    - WHERE campaign.status = 'ENABLED'
    - WHERE metrics.clicks > 100
    - WHERE campaign.name LIKE '%Brand%'
    
    ## Tips
    - Always check account currency before analyzing cost data
    - Cost values are in micros (millionths): 1000000 = 1 unit of currency
    - Use LIMIT to avoid large result sets
    """

@mcp.prompt("google_ads_workflow")
def google_ads_workflow() -> str:
    """Provides guidance on the recommended workflow for using Google Ads tools."""
    return """
    I'll help you analyze your Google Ads account data. Here's the recommended workflow:
    
    1. First, let's list all the accounts you have access to:
       - Run the `list_accounts()` tool to get available account IDs
    
    2. Before analyzing cost data, let's check which currency the account uses:
       - Run `get_account_currency(customer_id="ACCOUNT_ID")` with your selected account
    
    3. Now we can explore the account data:
       - For campaign performance: `get_campaign_performance(customer_id="ACCOUNT_ID", days=30)`
       - For ad performance: `get_ad_performance(customer_id="ACCOUNT_ID", days=30)`
       - For ad creative review: `get_ad_creatives(customer_id="ACCOUNT_ID")`
    
    4. For custom queries, use the GAQL query tool:
       - `run_gaql(customer_id="ACCOUNT_ID", query="YOUR_QUERY", format="table")`
    
    5. Let me know if you have specific questions about:
       - Campaign performance
       - Ad performance
       - Keywords
       - Budgets
       - Conversions
    
    Important: Always provide the customer_id as a string, even though it looks like a number.
    For example: customer_id="1234567890" (not customer_id=1234567890)
    """

@mcp.prompt("gaql_help")
def gaql_help() -> str:
    """Provides assistance for writing GAQL queries."""
    return """
    I'll help you write a Google Ads Query Language (GAQL) query. Here are some examples to get you started:
    
    ## Get campaign performance last 30 days
    ```
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions
    FROM campaign
    WHERE segments.date DURING LAST_30DAYS
    ORDER BY metrics.cost_micros DESC
    ```
    
    ## Get keyword performance
    ```
    SELECT
      keyword.text,
      keyword.match_type,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions
    FROM keyword_view
    WHERE segments.date DURING LAST_30DAYS
    ORDER BY metrics.clicks DESC
    ```
    
    ## Get ads with poor performance
    ```
    SELECT
      ad_group_ad.ad.id,
      ad_group_ad.ad.name,
      campaign.name,
      ad_group.name,
      metrics.impressions,
      metrics.clicks,
      metrics.conversions
    FROM ad_group_ad
    WHERE 
      segments.date DURING LAST_30DAYS
      AND metrics.impressions > 1000
      AND metrics.ctr < 0.01
    ORDER BY metrics.impressions DESC
    ```
    
    Once you've chosen a query, use it with:
    ```
    run_gaql(customer_id="YOUR_ACCOUNT_ID", query="YOUR_QUERY_HERE")
    ```
    
    Remember:
    - Always provide the customer_id as a string
    - Cost values are in micros (1,000,000 = 1 unit of currency)
    - Use LIMIT to avoid large result sets
    - Check the account currency before analyzing cost data
    """

@mcp.tool()
async def get_image_assets(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes) as a string"),
    limit: int = Field(default=50, description="Maximum number of image assets to return")
) -> str:
    """
    Retrieve all image assets in the account including their full-size URLs.
    
    This tool allows you to get details about image assets used in your Google Ads account,
    including the URLs to download the full-size images for further processing or analysis.
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Then run this command with the desired account ID
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        limit: Maximum number of image assets to return (default: 50)
        
    Returns:
        Formatted list of image assets with their download URLs
        
    Example:
        customer_id: "1234567890"
        limit: 100
    """
    query = f"""
        SELECT
            asset.id,
            asset.name,
            asset.type,
            asset.image_asset.full_size.url,
            asset.image_asset.full_size.height_pixels,
            asset.image_asset.full_size.width_pixels,
            asset.image_asset.file_size
        FROM
            asset
        WHERE
            asset.type = 'IMAGE'
        LIMIT {limit}
    """
    
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
        
        payload = {"query": query}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return f"Error retrieving image assets: {response.text}"
        
        results = response.json()
        if not results.get('results'):
            return "No image assets found for this customer ID."
        
        # Format the results in a readable way
        output_lines = [f"Image Assets for Customer ID {formatted_customer_id}:"]
        output_lines.append("=" * 80)
        
        for i, result in enumerate(results['results'], 1):
            asset = result.get('asset', {})
            image_asset = asset.get('imageAsset', {})
            full_size = image_asset.get('fullSize', {})
            
            output_lines.append(f"\n{i}. Asset ID: {asset.get('id', 'N/A')}")
            output_lines.append(f"   Name: {asset.get('name', 'N/A')}")
            
            if full_size:
                output_lines.append(f"   Image URL: {full_size.get('url', 'N/A')}")
                output_lines.append(f"   Dimensions: {full_size.get('widthPixels', 'N/A')} x {full_size.get('heightPixels', 'N/A')} px")
            
            file_size = image_asset.get('fileSize', 'N/A')
            if file_size != 'N/A':
                # Convert to KB for readability
                file_size_kb = int(file_size) / 1024
                output_lines.append(f"   File Size: {file_size_kb:.2f} KB")
            
            output_lines.append("-" * 80)
        
        return "\n".join(output_lines)
    
    except Exception as e:
        return f"Error retrieving image assets: {str(e)}"

@mcp.tool()
async def download_image_asset(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes) as a string"),
    asset_id: str = Field(description="The ID of the image asset to download"),
    output_dir: str = Field(default="./ad_images", description="Directory to save the downloaded image")
) -> str:
    """
    Download a specific image asset from a Google Ads account.
    
    This tool allows you to download the full-size version of an image asset
    for further processing, analysis, or backup.
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Then run get_image_assets() to get available image asset IDs
    3. Finally use this command to download specific images
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        asset_id: The ID of the image asset to download
        output_dir: Directory where the image should be saved (default: ./ad_images)
        
    Returns:
        Status message indicating success or failure of the download
        
    Example:
        customer_id: "1234567890"
        asset_id: "12345"
        output_dir: "./my_ad_images"
    """
    query = f"""
        SELECT
            asset.id,
            asset.name,
            asset.image_asset.full_size.url
        FROM
            asset
        WHERE
            asset.type = 'IMAGE'
            AND asset.id = {asset_id}
        LIMIT 1
    """
    
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
        
        payload = {"query": query}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return f"Error retrieving image asset: {response.text}"
        
        results = response.json()
        if not results.get('results'):
            return f"No image asset found with ID {asset_id}"
        
        # Extract the image URL
        asset = results['results'][0].get('asset', {})
        image_url = asset.get('imageAsset', {}).get('fullSize', {}).get('url')
        asset_name = asset.get('name', f"image_{asset_id}")
        
        if not image_url:
            return f"No download URL found for image asset ID {asset_id}"
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Download the image
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            return f"Failed to download image: HTTP {image_response.status_code}"
        
        # Clean the filename to be safe for filesystem
        safe_name = ''.join(c for c in asset_name if c.isalnum() or c in ' ._-')
        filename = f"{asset_id}_{safe_name}.jpg"
        file_path = os.path.join(output_dir, filename)
        
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(image_response.content)
        
        return f"Successfully downloaded image asset {asset_id} to {file_path}"
    
    except Exception as e:
        return f"Error downloading image asset: {str(e)}"

@mcp.tool()
async def get_asset_usage(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes) as a string"),
    asset_id: str = Field(default=None, description="Optional: specific asset ID to look up (leave empty to get all image assets)"),
    asset_type: str = Field(default="IMAGE", description="Asset type to search for ('IMAGE', 'TEXT', 'VIDEO', etc.)")
) -> str:
    """
    Find where specific assets are being used in campaigns, ad groups, and ads.
    
    This tool helps you analyze how assets are linked to campaigns and ads across your account,
    which is useful for creative analysis and optimization.
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Run get_image_assets() to see available assets
    3. Use this command to see where specific assets are used
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        asset_id: Optional specific asset ID to look up (leave empty to get all assets of the specified type)
        asset_type: Type of asset to search for (default: 'IMAGE')
        
    Returns:
        Formatted report showing where assets are used in the account
        
    Example:
        customer_id: "1234567890"
        asset_id: "12345"
        asset_type: "IMAGE"
    """
    # Build the query based on whether a specific asset ID was provided
    where_clause = f"asset.type = '{asset_type}'"
    if asset_id:
        where_clause += f" AND asset.id = {asset_id}"
    
    # First get the assets themselves
    assets_query = f"""
        SELECT
            asset.id,
            asset.name,
            asset.type
        FROM
            asset
        WHERE
            {where_clause}
        LIMIT 100
    """
    
    # Then get the associations between assets and campaigns/ad groups
    # Try using campaign_asset instead of asset_link
    associations_query = f"""
        SELECT
            campaign.id,
            campaign.name,
            asset.id,
            asset.name,
            asset.type
        FROM
            campaign_asset
        WHERE
            {where_clause}
        LIMIT 500
    """

    # Also try ad_group_asset for ad group level information
    ad_group_query = f"""
        SELECT
            ad_group.id,
            ad_group.name,
            asset.id,
            asset.name,
            asset.type
        FROM
            ad_group_asset
        WHERE
            {where_clause}
        LIMIT 500
    """
    
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        
        # First get the assets
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
        payload = {"query": assets_query}
        assets_response = requests.post(url, headers=headers, json=payload)
        
        if assets_response.status_code != 200:
            return f"Error retrieving assets: {assets_response.text}"
        
        assets_results = assets_response.json()
        if not assets_results.get('results'):
            return f"No {asset_type} assets found for this customer ID."
        
        # Now get the associations
        payload = {"query": associations_query}
        assoc_response = requests.post(url, headers=headers, json=payload)
        
        if assoc_response.status_code != 200:
            return f"Error retrieving asset associations: {assoc_response.text}"
        
        assoc_results = assoc_response.json()
        
        # Format the results in a readable way
        output_lines = [f"Asset Usage for Customer ID {formatted_customer_id}:"]
        output_lines.append("=" * 80)
        
        # Create a dictionary to organize asset usage by asset ID
        asset_usage = {}
        
        # Initialize the asset usage dictionary with basic asset info
        for result in assets_results.get('results', []):
            asset = result.get('asset', {})
            asset_id = asset.get('id')
            if asset_id:
                asset_usage[asset_id] = {
                    'name': asset.get('name', 'Unnamed asset'),
                    'type': asset.get('type', 'Unknown'),
                    'usage': []
                }
        
        # Add usage information from the associations
        for result in assoc_results.get('results', []):
            asset = result.get('asset', {})
            asset_id = asset.get('id')
            
            if asset_id and asset_id in asset_usage:
                campaign = result.get('campaign', {})
                ad_group = result.get('adGroup', {})
                ad = result.get('adGroupAd', {}).get('ad', {}) if 'adGroupAd' in result else {}
                asset_link = result.get('assetLink', {})
                
                usage_info = {
                    'campaign_id': campaign.get('id', 'N/A'),
                    'campaign_name': campaign.get('name', 'N/A'),
                    'ad_group_id': ad_group.get('id', 'N/A'),
                    'ad_group_name': ad_group.get('name', 'N/A'),
                    'ad_id': ad.get('id', 'N/A') if ad else 'N/A',
                    'ad_name': ad.get('name', 'N/A') if ad else 'N/A'
                }
                
                asset_usage[asset_id]['usage'].append(usage_info)
        
        # Format the output
        for asset_id, info in asset_usage.items():
            output_lines.append(f"\nAsset ID: {asset_id}")
            output_lines.append(f"Name: {info['name']}")
            output_lines.append(f"Type: {info['type']}")
            
            if info['usage']:
                output_lines.append("\nUsed in:")
                output_lines.append("-" * 60)
                output_lines.append(f"{'Campaign':<30} | {'Ad Group':<30}")
                output_lines.append("-" * 60)
                
                for usage in info['usage']:
                    campaign_str = f"{usage['campaign_name']} ({usage['campaign_id']})"
                    ad_group_str = f"{usage['ad_group_name']} ({usage['ad_group_id']})"
                    
                    output_lines.append(f"{campaign_str[:30]:<30} | {ad_group_str[:30]:<30}")
            
            output_lines.append("=" * 80)
        
        return "\n".join(output_lines)
    
    except Exception as e:
        return f"Error retrieving asset usage: {str(e)}"

@mcp.tool()
async def analyze_image_assets(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes) as a string"),
    days: int = Field(default=30, description="Number of days to look back (7, 30, 90, etc.)")
) -> str:
    """
    Analyze image assets with their performance metrics across campaigns.
    
    This comprehensive tool helps you understand which image assets are performing well
    by showing metrics like impressions, clicks, and conversions for each image.
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Then run get_account_currency() to see what currency the account uses
    3. Finally run this command to analyze image asset performance
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        days: Number of days to look back (default: 30)
        
    Returns:
        Detailed report of image assets and their performance metrics
        
    Example:
        customer_id: "1234567890"
        days: 14
    """
    # Make sure to use a valid date range format
    # Valid formats are: LAST_7_DAYS, LAST_14_DAYS, LAST_30_DAYS, etc. (with underscores)
    if days == 7:
        date_range = "LAST_7_DAYS"
    elif days == 14:
        date_range = "LAST_14_DAYS"
    elif days == 30:
        date_range = "LAST_30_DAYS"
    else:
        # Default to 30 days if not a standard range
        date_range = "LAST_30_DAYS"
        
    query = f"""
        SELECT
            asset.id,
            asset.name,
            asset.image_asset.full_size.url,
            asset.image_asset.full_size.width_pixels,
            asset.image_asset.full_size.height_pixels,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM
            campaign_asset
        WHERE
            asset.type = 'IMAGE'
            AND segments.date DURING LAST_30_DAYS
        ORDER BY
            metrics.impressions DESC
        LIMIT 200
    """
    
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/googleAds:search"
        
        payload = {"query": query}
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return f"Error analyzing image assets: {response.text}"
        
        results = response.json()
        if not results.get('results'):
            return "No image asset performance data found for this customer ID and time period."
        
        # Group results by asset ID
        assets_data = {}
        for result in results.get('results', []):
            asset = result.get('asset', {})
            asset_id = asset.get('id')
            
            if asset_id not in assets_data:
                assets_data[asset_id] = {
                    'name': asset.get('name', f"Asset {asset_id}"),
                    'url': asset.get('imageAsset', {}).get('fullSize', {}).get('url', 'N/A'),
                    'dimensions': f"{asset.get('imageAsset', {}).get('fullSize', {}).get('widthPixels', 'N/A')} x {asset.get('imageAsset', {}).get('fullSize', {}).get('heightPixels', 'N/A')}",
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'cost_micros': 0,
                    'campaigns': set(),
                    'ad_groups': set()
                }
            
            # Aggregate metrics
            metrics = result.get('metrics', {})
            assets_data[asset_id]['impressions'] += int(metrics.get('impressions', 0))
            assets_data[asset_id]['clicks'] += int(metrics.get('clicks', 0))
            assets_data[asset_id]['conversions'] += float(metrics.get('conversions', 0))
            assets_data[asset_id]['cost_micros'] += int(metrics.get('costMicros', 0))
            
            # Add campaign and ad group info
            campaign = result.get('campaign', {})
            ad_group = result.get('adGroup', {})
            
            if campaign.get('name'):
                assets_data[asset_id]['campaigns'].add(campaign.get('name'))
            if ad_group.get('name'):
                assets_data[asset_id]['ad_groups'].add(ad_group.get('name'))
        
        # Format the results
        output_lines = [f"Image Asset Performance Analysis for Customer ID {formatted_customer_id} (Last {days} days):"]
        output_lines.append("=" * 100)
        
        # Sort assets by impressions (highest first)
        sorted_assets = sorted(assets_data.items(), key=lambda x: x[1]['impressions'], reverse=True)
        
        for asset_id, data in sorted_assets:
            output_lines.append(f"\nAsset ID: {asset_id}")
            output_lines.append(f"Name: {data['name']}")
            output_lines.append(f"Dimensions: {data['dimensions']}")
            
            # Calculate CTR if there are impressions
            ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
            
            # Format metrics
            output_lines.append(f"\nPerformance Metrics:")
            output_lines.append(f"  Impressions: {data['impressions']:,}")
            output_lines.append(f"  Clicks: {data['clicks']:,}")
            output_lines.append(f"  CTR: {ctr:.2f}%")
            output_lines.append(f"  Conversions: {data['conversions']:.2f}")
            output_lines.append(f"  Cost (micros): {data['cost_micros']:,}")
            
            # Show where it's used
            output_lines.append(f"\nUsed in {len(data['campaigns'])} campaigns:")
            for campaign in list(data['campaigns'])[:5]:  # Show first 5 campaigns
                output_lines.append(f"  - {campaign}")
            if len(data['campaigns']) > 5:
                output_lines.append(f"  - ... and {len(data['campaigns']) - 5} more")
            
            # Add URL
            if data['url'] != 'N/A':
                output_lines.append(f"\nImage URL: {data['url']}")
            
            output_lines.append("-" * 100)
        
        return "\n".join(output_lines)
    
    except Exception as e:
        return f"Error analyzing image assets: {str(e)}"

# ================== MEDIA UPLOAD FUNCTIONS ==================

def validate_image_file(file_path: str) -> Dict[str, Any]:
    """
    Validate image file for Google Ads requirements.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Dict with validation results
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "valid": False,
                "error": f"File not found: {file_path}",
                "file_size": 0,
                "mime_type": None,
                "dimensions": None
            }
        
        # Check file size (5MB limit)
        file_size = os.path.getsize(file_path)
        if file_size > 5 * 1024 * 1024:  # 5MB limit
            return {
                "valid": False,
                "error": f"File size {file_size / (1024*1024):.2f}MB exceeds 5MB limit",
                "file_size": file_size,
                "mime_type": None,
                "dimensions": None
            }
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type not in ['image/jpeg', 'image/png']:
            return {
                "valid": False,
                "error": f"Unsupported file format: {mime_type}. Only JPEG and PNG are supported.",
                "file_size": file_size,
                "mime_type": mime_type,
                "dimensions": None
            }
        
        # Try to get image dimensions using PIL if available
        dimensions = None
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                width, height = img.size
                dimensions = {"width": width, "height": height}
                
                # Check minimum dimensions
                if width < 300 or height < 300:
                    return {
                        "valid": False,
                        "error": f"Image dimensions {width}x{height} are too small. Minimum is 300x300 pixels.",
                        "file_size": file_size,
                        "mime_type": mime_type,
                        "dimensions": dimensions
                    }
        except ImportError:
            # PIL not available, skip dimension check
            pass
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error reading image: {str(e)}",
                "file_size": file_size,
                "mime_type": mime_type,
                "dimensions": None
            }
        
        return {
            "valid": True,
            "error": None,
            "file_size": file_size,
            "mime_type": mime_type,
            "dimensions": dimensions
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
            "file_size": 0,
            "mime_type": None,
            "dimensions": None
        }

def validate_image_url(image_url: str) -> Dict[str, Any]:
    """
    Validate image URL and download for Google Ads requirements.
    
    Args:
        image_url: URL of the image to validate
        
    Returns:
        Dict with validation results and image data
    """
    try:
        # Download the image
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            return {
                "valid": False,
                "error": f"Failed to download image from URL: HTTP {response.status_code}",
                "image_data": None,
                "file_size": 0,
                "mime_type": None,
                "dimensions": None
            }
        
        image_data = response.content
        file_size = len(image_data)
        
        # Check file size (5MB limit)
        if file_size > 5 * 1024 * 1024:
            return {
                "valid": False,
                "error": f"Image size {file_size / (1024*1024):.2f}MB exceeds 5MB limit",
                "image_data": None,
                "file_size": file_size,
                "mime_type": None,
                "dimensions": None
            }
        
        # Detect MIME type from content
        mime_type = None
        if image_data.startswith(b'\xff\xd8\xff'):
            mime_type = 'image/jpeg'
        elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            mime_type = 'image/png'
        else:
            # Try to get from Content-Type header
            content_type = response.headers.get('content-type', '').lower()
            if 'jpeg' in content_type or 'jpg' in content_type:
                mime_type = 'image/jpeg'
            elif 'png' in content_type:
                mime_type = 'image/png'
        
        if mime_type not in ['image/jpeg', 'image/png']:
            return {
                "valid": False,
                "error": f"Unsupported image format. Only JPEG and PNG are supported.",
                "image_data": None,
                "file_size": file_size,
                "mime_type": mime_type,
                "dimensions": None
            }
        
        # Try to get image dimensions using PIL if available
        dimensions = None
        try:
            from PIL import Image
            with Image.open(io.BytesIO(image_data)) as img:
                width, height = img.size
                dimensions = {"width": width, "height": height}
                
                # Check minimum dimensions
                if width < 300 or height < 300:
                    return {
                        "valid": False,
                        "error": f"Image dimensions {width}x{height} are too small. Minimum is 300x300 pixels.",
                        "image_data": None,
                        "file_size": file_size,
                        "mime_type": mime_type,
                        "dimensions": dimensions
                    }
        except ImportError:
            # PIL not available, skip dimension check
            pass
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error reading image: {str(e)}",
                "image_data": None,
                "file_size": file_size,
                "mime_type": mime_type,
                "dimensions": None
            }
        
        return {
            "valid": True,
            "error": None,
            "image_data": image_data,
            "file_size": file_size,
            "mime_type": mime_type,
            "dimensions": dimensions
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Error validating image URL: {str(e)}",
            "image_data": None,
            "file_size": 0,
            "mime_type": None,
            "dimensions": None
        }

@mcp.tool()
async def upload_image_asset_from_file(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    file_path: str = Field(description="Local path to the image file to upload"),
    asset_name: str = Field(default="", description="Name for the asset (auto-generated if not provided)")
) -> str:
    """
    Upload an image asset from a local file to Google Ads account.
    
    This function uploads an image file to your Google Ads account, making it available
    for use in campaigns, ad groups, and ads. The image is validated for size, format,
    and dimensions before upload.
    
    REQUIREMENTS:
    - Maximum file size: 5 MB
    - Supported formats: JPEG (.jpg), PNG (.png)
    - Minimum dimensions: 300x300 pixels
    - Recommended dimensions: 1200x1200 (square), 1200x628 (landscape), 960x1200 (portrait)
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Use this command to upload your image assets
    3. Use the returned asset resource name in campaign/ad group asset linking
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        file_path: Path to the image file to upload
        asset_name: Name for the asset (auto-generated if not provided)
        
    Returns:
        Success message with asset resource name or detailed error message
        
    Example:
        customer_id: "1234567890"
        file_path: "/path/to/image.jpg"
        asset_name: "Holiday Sale Banner"
    """
    try:
        # Validate the image file
        validation = validate_image_file(file_path)
        if not validation["valid"]:
            return f"Upload failed: {validation['error']}"
        
        # Read the image file
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        # Generate asset name if not provided
        if not asset_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            asset_name = f"image_{timestamp}_{filename}"
        
        # Upload the image
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/assets:mutate"
        
        # Create the asset payload
        asset_payload = {
            "operations": [{
                "create": {
                    "name": asset_name,
                    "type": "IMAGE",
                    "imageAsset": {
                        "data": base64.b64encode(image_data).decode('utf-8'),
                        "fileSize": str(validation["file_size"]),
                        "mimeType": validation["mime_type"].upper().replace('IMAGE/', '')
                    }
                }
            }]
        }
        
        # Add dimensions if available
        if validation["dimensions"]:
            asset_payload["operations"][0]["create"]["imageAsset"]["fullSize"] = {
                "widthPixels": str(validation["dimensions"]["width"]),
                "heightPixels": str(validation["dimensions"]["height"])
            }
        
        response = requests.post(url, headers=headers, json=asset_payload)
        
        if response.status_code != 200:
            return f"Upload failed: {response.text}"
        
        result = response.json()
        if not result.get('results'):
            return f"Upload failed: No results returned from API"
        
        asset_resource_name = result['results'][0]['resourceName']
        
        # Format success response
        output_lines = [
            f"Successfully uploaded image asset '{asset_name}'",
            f"Resource name: {asset_resource_name}",
            f"File: {file_path}",
            f"Size: {validation['file_size'] / 1024:.2f} KB",
            f"Format: {validation['mime_type']}"
        ]
        
        if validation["dimensions"]:
            output_lines.append(f"Dimensions: {validation['dimensions']['width']}x{validation['dimensions']['height']} pixels")
        
        output_lines.extend([
            "",
            "Asset is now available for use in:",
            "- Campaign assets",
            "- Ad group assets",
            "- Performance Max campaigns",
            "- Discovery campaigns",
            "",
            "Next steps:",
            "1. Link asset to campaigns using asset linking functions",
            "2. Monitor asset performance in reporting"
        ])
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error uploading image asset: {str(e)}"

@mcp.tool()
async def upload_image_asset_from_url(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    image_url: str = Field(description="URL of the image to download and upload"),
    asset_name: str = Field(default="", description="Name for the asset (auto-generated if not provided)")
) -> str:
    """
    Upload an image asset from a remote URL to Google Ads account.
    
    This function downloads an image from a URL and uploads it to your Google Ads account,
    making it available for use in campaigns, ad groups, and ads. The image is validated
    for size, format, and dimensions before upload.
    
    REQUIREMENTS:
    - Maximum file size: 5 MB
    - Supported formats: JPEG (.jpg), PNG (.png)
    - Minimum dimensions: 300x300 pixels
    - Recommended dimensions: 1200x1200 (square), 1200x628 (landscape), 960x1200 (portrait)
    
    RECOMMENDED WORKFLOW:
    1. First run list_accounts() to get available account IDs
    2. Use this command to upload your image assets from URLs
    3. Use the returned asset resource name in campaign/ad group asset linking
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        image_url: URL of the image to download and upload
        asset_name: Name for the asset (auto-generated if not provided)
        
    Returns:
        Success message with asset resource name or detailed error message
        
    Example:
        customer_id: "1234567890"
        image_url: "https://example.com/banner.jpg"
        asset_name: "Holiday Sale Banner"
    """
    try:
        # Validate and download the image from URL
        validation = validate_image_url(image_url)
        if not validation["valid"]:
            return f"Upload failed: {validation['error']}"
        
        image_data = validation["image_data"]
        
        # Generate asset name if not provided
        if not asset_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            url_filename = image_url.split('/')[-1].split('?')[0]  # Remove query params
            asset_name = f"image_{timestamp}_{url_filename}"
        
        # Upload the image
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/assets:mutate"
        
        # Create the asset payload
        asset_payload = {
            "operations": [{
                "create": {
                    "name": asset_name,
                    "type": "IMAGE",
                    "imageAsset": {
                        "data": base64.b64encode(image_data).decode('utf-8'),
                        "fileSize": str(validation["file_size"]),
                        "mimeType": validation["mime_type"].upper().replace('IMAGE/', '')
                    }
                }
            }]
        }
        
        # Add dimensions if available
        if validation["dimensions"]:
            asset_payload["operations"][0]["create"]["imageAsset"]["fullSize"] = {
                "widthPixels": str(validation["dimensions"]["width"]),
                "heightPixels": str(validation["dimensions"]["height"])
            }
        
        response = requests.post(url, headers=headers, json=asset_payload)
        
        if response.status_code != 200:
            return f"Upload failed: {response.text}"
        
        result = response.json()
        if not result.get('results'):
            return f"Upload failed: No results returned from API"
        
        asset_resource_name = result['results'][0]['resourceName']
        
        # Format success response
        output_lines = [
            f"Successfully uploaded image asset '{asset_name}'",
            f"Resource name: {asset_resource_name}",
            f"Source URL: {image_url}",
            f"Size: {validation['file_size'] / 1024:.2f} KB",
            f"Format: {validation['mime_type']}"
        ]
        
        if validation["dimensions"]:
            output_lines.append(f"Dimensions: {validation['dimensions']['width']}x{validation['dimensions']['height']} pixels")
        
        output_lines.extend([
            "",
            "Asset is now available for use in:",
            "- Campaign assets",
            "- Ad group assets",
            "- Performance Max campaigns",
            "- Discovery campaigns",
            "",
            "Next steps:",
            "1. Link asset to campaigns using asset linking functions",
            "2. Monitor asset performance in reporting"
        ])
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error uploading image asset: {str(e)}"

@mcp.tool()
async def list_resources(customer_id: str) -> str:
    """
    List valid resources that can be used in GAQL FROM clauses.
    
    Args:
        customer_id: The Google Ads customer ID as a string
        
    Returns:
        Formatted list of valid resources
    """
    # Example query that lists some common resources
    # This might need to be adjusted based on what's available in your API version
    query = """
        SELECT
            google_ads_field.name,
            google_ads_field.category,
            google_ads_field.data_type
        FROM
            google_ads_field
        WHERE
            google_ads_field.category = 'RESOURCE'
        ORDER BY
            google_ads_field.name
    """
    
    # Use your existing run_gaql function to execute this query
    return await run_gaql(customer_id, query)

# ================== WRITE/UPDATE OPERATIONS ==================

@mcp.tool()
async def create_campaign_budget(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    budget_name: str = Field(description="Name for the budget"),
    amount_micros: int = Field(description="Daily budget amount in micros (e.g., 50000000 = $50)"),
    delivery_method: str = Field(default="STANDARD", description="Budget delivery method: STANDARD or ACCELERATED")
) -> str:
    """
    Create a new campaign budget that can be used by campaigns.
    
    Campaign budgets define the daily spending limit for campaigns. Multiple campaigns
    can share the same budget, or each campaign can have its own dedicated budget.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        budget_name: A descriptive name for the budget
        amount_micros: Daily budget amount in micros (1,000,000 micros = 1 unit of currency)
        delivery_method: How the budget should be spent (STANDARD or ACCELERATED)
        
    Returns:
        Success message with the new budget resource name or error message
        
    Example:
        customer_id: "1234567890"
        budget_name: "Search Campaign Budget"
        amount_micros: 50000000  # $50 daily budget
        delivery_method: "STANDARD"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/campaignBudgets:mutate"
        
        # Build the budget creation operation
        budget_operation = {
            "operations": [{
                "create": {
                    "name": budget_name,
                    "amountMicros": str(amount_micros),
                    "deliveryMethod": delivery_method,
                    "explicitlyShared": True  # Allow multiple campaigns to use this budget
                }
            }]
        }
        
        response = requests.post(url, headers=headers, json=budget_operation)
        
        if response.status_code != 200:
            return f"Error creating campaign budget: {response.text}"
        
        result = response.json()
        if result.get('results'):
            budget_resource_name = result['results'][0]['resourceName']
            return f"Successfully created campaign budget '{budget_name}'\nResource name: {budget_resource_name}\nDaily budget: {amount_micros / 1000000:.2f} (account currency)"
        else:
            return f"Budget creation completed but no resource name returned: {result}"
    
    except Exception as e:
        return f"Error creating campaign budget: {str(e)}"

@mcp.tool()
async def create_campaign(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    campaign_name: str = Field(description="Name for the new campaign"),
    budget_resource_name: str = Field(description="Budget resource name (from create_campaign_budget)"),
    campaign_type: str = Field(default="SEARCH", description="Campaign type: SEARCH, DISPLAY, SHOPPING, VIDEO, etc."),
    status: str = Field(default="PAUSED", description="Initial campaign status: PAUSED, ENABLED, or REMOVED"),
    bidding_strategy: str = Field(default="TARGET_SPEND", description="Bidding strategy type")
) -> str:
    """
    Create a new Google Ads campaign.
    
    IMPORTANT: Campaigns are created in PAUSED status by default for safety.
    You can enable them later using update_campaign_status().
    
    RECOMMENDED WORKFLOW:
    1. First run create_campaign_budget() to create a budget
    2. Use the returned budget resource name in this function
    3. Create the campaign (starts paused)
    4. Use update_campaign_status() to enable when ready
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        campaign_name: A descriptive name for the campaign
        budget_resource_name: The resource name of an existing budget (from create_campaign_budget)
        campaign_type: Type of campaign (SEARCH, DISPLAY, SHOPPING, VIDEO, etc.)
        status: Initial status (PAUSED recommended for safety)
        bidding_strategy: Bidding strategy (TARGET_SPEND, MANUAL_CPC, TARGET_CPA, MAXIMIZE_CONVERSIONS, etc.)
        
    Returns:
        Success message with campaign resource name or error message
        
    Example:
        customer_id: "1234567890"
        campaign_name: "Brand Search Campaign"
        budget_resource_name: "customers/1234567890/campaignBudgets/12345"
        campaign_type: "SEARCH"
        status: "PAUSED"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/campaigns:mutate"
        
        # Build the campaign creation operation
        campaign_create = {
            "name": campaign_name,
            "advertisingChannelType": campaign_type,
            "status": status,
            "campaignBudget": budget_resource_name,
            "biddingStrategyType": bidding_strategy,
            "networkSettings": {
                "targetGoogleSearch": True,
                "targetSearchNetwork": True,
                "targetContentNetwork": False if campaign_type == "SEARCH" else True,
                "targetPartnerSearchNetwork": False
            }
        }
        
        # Add bidding strategy configuration
        if bidding_strategy == "TARGET_SPEND":
            campaign_create["targetSpend"] = {}
        elif bidding_strategy == "MANUAL_CPC":
            campaign_create["manualCpc"] = {
                "enhancedCpcEnabled": False
            }
        elif bidding_strategy == "TARGET_CPA":
            campaign_create["targetCpa"] = {}
        elif bidding_strategy == "MAXIMIZE_CONVERSIONS":
            campaign_create["maximizeConversions"] = {}
        elif bidding_strategy == "MAXIMIZE_CONVERSION_VALUE":
            campaign_create["maximizeConversionValue"] = {}
        
        # Add campaign-specific settings
        if campaign_type == "DISPLAY":
            # Display campaigns need content network enabled
            campaign_create["networkSettings"]["targetContentNetwork"] = True
            campaign_create["networkSettings"]["targetGoogleSearch"] = False
        elif campaign_type == "PERFORMANCE_MAX":
            # Performance Max campaigns have specific requirements
            campaign_create["networkSettings"] = {
                "targetGoogleSearch": True,
                "targetSearchNetwork": True,
                "targetContentNetwork": True,
                "targetPartnerSearchNetwork": True
            }
        
        campaign_operation = {
            "operations": [{
                "create": campaign_create
            }]
        }
        
        response = requests.post(url, headers=headers, json=campaign_operation)
        
        if response.status_code != 200:
            return f"Error creating campaign: {response.text}"
        
        result = response.json()
        if result.get('results'):
            campaign_resource_name = result['results'][0]['resourceName']
            return f"Successfully created campaign '{campaign_name}'\nResource name: {campaign_resource_name}\nStatus: {status}\nType: {campaign_type}\n\nNext steps:\n1. Create ad groups for this campaign\n2. Add keywords and ads\n3. Enable the campaign when ready"
        else:
            return f"Campaign creation completed but no resource name returned: {result}"
    
    except Exception as e:
        return f"Error creating campaign: {str(e)}"

@mcp.tool()
async def update_campaign_status(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    campaign_resource_name: str = Field(description="Campaign resource name (e.g., customers/123/campaigns/456)"),
    status: str = Field(description="New campaign status: ENABLED, PAUSED, or REMOVED")
) -> str:
    """
    Update the status of an existing campaign (enable, pause, or remove).
    
    This is commonly used to enable campaigns that were created in PAUSED status,
    or to pause campaigns that are underperforming.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        campaign_resource_name: The resource name of the campaign to update
        status: New status (ENABLED, PAUSED, or REMOVED)
        
    Returns:
        Success message or error message
        
    Example:
        customer_id: "1234567890"
        campaign_resource_name: "customers/1234567890/campaigns/12345"
        status: "ENABLED"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/campaigns:mutate"
        
        # Build the campaign update operation
        campaign_operation = {
            "operations": [{
                "update": {
                    "resourceName": campaign_resource_name,
                    "status": status
                },
                "updateMask": "status"
            }]
        }
        
        response = requests.post(url, headers=headers, json=campaign_operation)
        
        if response.status_code != 200:
            return f"Error updating campaign status: {response.text}"
        
        result = response.json()
        if result.get('results'):
            return f"Successfully updated campaign status to {status}\nCampaign: {campaign_resource_name}"
        else:
            return f"Campaign status update completed: {result}"
    
    except Exception as e:
        return f"Error updating campaign status: {str(e)}"

@mcp.tool()
async def update_campaign_budget(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    campaign_resource_name: str = Field(description="Campaign resource name (e.g., customers/123/campaigns/456)"),
    new_budget_resource_name: str = Field(description="New budget resource name to assign to the campaign")
) -> str:
    """
    Update the budget assigned to an existing campaign.
    
    This allows you to change which budget a campaign uses, useful for
    reallocating spending between campaigns or changing budget amounts.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        campaign_resource_name: The resource name of the campaign to update
        new_budget_resource_name: The resource name of the budget to assign
        
    Returns:
        Success message or error message
        
    Example:
        customer_id: "1234567890"
        campaign_resource_name: "customers/1234567890/campaigns/12345"
        new_budget_resource_name: "customers/1234567890/campaignBudgets/67890"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/campaigns:mutate"
        
        # Build the campaign update operation
        campaign_operation = {
            "operations": [{
                "update": {
                    "resourceName": campaign_resource_name,
                    "campaignBudget": new_budget_resource_name
                },
                "updateMask": "campaign_budget"
            }]
        }
        
        response = requests.post(url, headers=headers, json=campaign_operation)
        
        if response.status_code != 200:
            return f"Error updating campaign budget: {response.text}"
        
        result = response.json()
        if result.get('results'):
            return f"Successfully updated campaign budget\nCampaign: {campaign_resource_name}\nNew budget: {new_budget_resource_name}"
        else:
            return f"Campaign budget update completed: {result}"
    
    except Exception as e:
        return f"Error updating campaign budget: {str(e)}"

@mcp.tool()
async def create_ad_group(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    ad_group_name: str = Field(description="Name for the new ad group"),
    campaign_resource_name: str = Field(description="Campaign resource name where the ad group will be created"),
    cpc_bid_micros: int = Field(description="Maximum CPC bid in micros (e.g., 1000000 = $1.00)"),
    status: str = Field(default="PAUSED", description="Initial ad group status: PAUSED, ENABLED, or REMOVED")
) -> str:
    """
    Create a new ad group within an existing campaign.
    
    Ad groups contain keywords and ads that are related to each other.
    Each ad group should focus on a specific theme or set of related keywords.
    
    RECOMMENDED WORKFLOW:
    1. Create a campaign first using create_campaign()
    2. Create ad groups within that campaign
    3. Add keywords and ads to the ad groups
    4. Enable the ad group when ready
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        ad_group_name: A descriptive name for the ad group
        campaign_resource_name: The resource name of the parent campaign
        cpc_bid_micros: Maximum cost-per-click bid in micros (1,000,000 = 1 unit of currency)
        status: Initial status (PAUSED recommended for safety)
        
    Returns:
        Success message with ad group resource name or error message
        
    Example:
        customer_id: "1234567890"
        ad_group_name: "Running Shoes"
        campaign_resource_name: "customers/1234567890/campaigns/12345"
        cpc_bid_micros: 2000000  # $2.00 max CPC
        status: "PAUSED"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/adGroups:mutate"
        
        # Build the ad group creation operation
        ad_group_operation = {
            "operations": [{
                "create": {
                    "name": ad_group_name,
                    "campaign": campaign_resource_name,
                    "status": status,
                    "cpcBidMicros": str(cpc_bid_micros)
                }
            }]
        }
        
        response = requests.post(url, headers=headers, json=ad_group_operation)
        
        if response.status_code != 200:
            return f"Error creating ad group: {response.text}"
        
        result = response.json()
        if result.get('results'):
            ad_group_resource_name = result['results'][0]['resourceName']
            return f"Successfully created ad group '{ad_group_name}'\nResource name: {ad_group_resource_name}\nStatus: {status}\nMax CPC: {cpc_bid_micros / 1000000:.2f} (account currency)\n\nNext steps:\n1. Add keywords to this ad group\n2. Create ads for this ad group\n3. Enable the ad group when ready"
        else:
            return f"Ad group creation completed but no resource name returned: {result}"
    
    except Exception as e:
        return f"Error creating ad group: {str(e)}"

@mcp.tool()
async def add_keywords(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    ad_group_resource_name: str = Field(description="Ad group resource name where keywords will be added"),
    keywords: List[Dict[str, Union[str, int]]] = Field(description="List of keyword objects with 'text', 'match_type', and 'cpc_bid_micros'"),
    status: str = Field(default="PAUSED", description="Initial keyword status: PAUSED, ENABLED, or REMOVED")
) -> str:
    """
    Add keywords to an existing ad group.
    
    Keywords determine when your ads will show. Each keyword should be relevant
    to the ad group theme and have an appropriate match type and bid.
    
    IMPORTANT: Keywords are created in PAUSED status by default for safety.
    Use update_keyword_status() to enable them when ready.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        ad_group_resource_name: The resource name of the target ad group
        keywords: List of keyword dictionaries with:
                 - text: The keyword text (e.g., "running shoes")
                 - match_type: EXACT, PHRASE, or BROAD
                 - cpc_bid_micros: Maximum CPC bid in micros (optional, uses ad group default if not specified)
        status: Initial status for all keywords (PAUSED recommended)
        
    Returns:
        Success message with keyword resource names or error message
        
    Example:
        customer_id: "1234567890"
        ad_group_resource_name: "customers/1234567890/adGroups/67890"
        keywords: [
            {"text": "running shoes", "match_type": "EXACT", "cpc_bid_micros": 2500000},
            {"text": "athletic footwear", "match_type": "PHRASE", "cpc_bid_micros": 2000000},
            {"text": "sports shoes", "match_type": "BROAD", "cpc_bid_micros": 1500000}
        ]
        status: "PAUSED"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/adGroupCriteria:mutate"
        
        # Build keyword operations
        operations = []
        for keyword in keywords:
            operation = {
                "create": {
                    "adGroup": ad_group_resource_name,
                    "status": status,
                    "keyword": {
                        "text": keyword["text"],
                        "matchType": keyword["match_type"]
                    }
                }
            }
            
            # Add custom CPC bid if specified
            if "cpc_bid_micros" in keyword:
                operation["create"]["cpcBidMicros"] = str(keyword["cpc_bid_micros"])
            
            operations.append(operation)
        
        keyword_operation = {"operations": operations}
        
        response = requests.post(url, headers=headers, json=keyword_operation)
        
        if response.status_code != 200:
            return f"Error adding keywords: {response.text}"
        
        result = response.json()
        if result.get('results'):
            output_lines = [f"Successfully added {len(result['results'])} keywords:"]
            output_lines.append("-" * 60)
            
            for i, (keyword, result_item) in enumerate(zip(keywords, result['results'])):
                resource_name = result_item['resourceName']
                bid_info = f" (bid: {keyword.get('cpc_bid_micros', 'default') / 1000000:.2f})" if keyword.get('cpc_bid_micros') else " (using ad group default bid)"
                output_lines.append(f"{i+1}. '{keyword['text']}' ({keyword['match_type']}){bid_info}")
                output_lines.append(f"   Resource: {resource_name}")
            
            output_lines.append(f"\nStatus: {status}")
            output_lines.append("\nNext steps:")
            output_lines.append("1. Create ads for this ad group")
            output_lines.append("2. Enable keywords when ready")
            
            return "\n".join(output_lines)
        else:
            return f"Keyword addition completed but no resource names returned: {result}"
    
    except Exception as e:
        return f"Error adding keywords: {str(e)}"

@mcp.tool()
async def update_keyword_status(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    keyword_resource_names: List[str] = Field(description="List of keyword resource names to update"),
    status: str = Field(description="New keyword status: ENABLED, PAUSED, or REMOVED")
) -> str:
    """
    Update the status of existing keywords (enable, pause, or remove).
    
    This is commonly used to enable keywords that were created in PAUSED status,
    or to pause underperforming keywords.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        keyword_resource_names: List of keyword resource names to update
        status: New status (ENABLED, PAUSED, or REMOVED)
        
    Returns:
        Success message or error message
        
    Example:
        customer_id: "1234567890"
        keyword_resource_names: ["customers/1234567890/adGroupCriteria/12345~67890"]
        status: "ENABLED"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/adGroupCriteria:mutate"
        
        # Build keyword update operations
        operations = []
        for resource_name in keyword_resource_names:
            operations.append({
                "update": {
                    "resourceName": resource_name,
                    "status": status
                },
                "updateMask": "status"
            })
        
        keyword_operation = {"operations": operations}
        
        response = requests.post(url, headers=headers, json=keyword_operation)
        
        if response.status_code != 200:
            return f"Error updating keyword status: {response.text}"
        
        result = response.json()
        if result.get('results'):
            return f"Successfully updated {len(result['results'])} keywords to {status} status"
        else:
            return f"Keyword status update completed: {result}"
    
    except Exception as e:
        return f"Error updating keyword status: {str(e)}"

@mcp.tool()
async def create_responsive_search_ad(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    ad_group_resource_name: str = Field(description="Ad group resource name where the ad will be created"),
    headlines: List[str] = Field(description="List of headlines (3-15 headlines, max 30 chars each)"),
    descriptions: List[str] = Field(description="List of descriptions (2-4 descriptions, max 90 chars each)"),
    final_urls: List[str] = Field(description="List of final URLs where users will land"),
    path1: str = Field(default="", description="Optional display URL path 1"),
    path2: str = Field(default="", description="Optional display URL path 2"),
    status: str = Field(default="PAUSED", description="Initial ad status: PAUSED, ENABLED, or REMOVED")
) -> str:
    """
    Create a responsive search ad in an existing ad group.
    
    Responsive search ads automatically test different combinations of headlines
    and descriptions to find the best performing combinations.
    
    REQUIREMENTS:
    - 3-15 headlines (Google recommends 8-10 for best performance)
    - 2-4 descriptions (Google recommends 3-4 for best performance)
    - Headlines: max 30 characters each
    - Descriptions: max 90 characters each
    
    RECOMMENDED WORKFLOW:
    1. Create campaign and ad group first
    2. Add keywords to the ad group
    3. Create responsive search ads
    4. Enable everything when ready
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        ad_group_resource_name: The resource name of the target ad group
        headlines: List of 3-15 headlines (max 30 chars each)
        descriptions: List of 2-4 descriptions (max 90 chars each)
        final_urls: List of landing page URLs
        path1: Optional display URL path 1 (max 15 chars)
        path2: Optional display URL path 2 (max 15 chars)
        status: Initial status (PAUSED recommended)
        
    Returns:
        Success message with ad resource name or error message
        
    Example:
        customer_id: "1234567890"
        ad_group_resource_name: "customers/1234567890/adGroups/67890"
        headlines: ["Best Running Shoes", "Free Shipping", "Shop Now"]
        descriptions: ["Find your perfect pair today", "Wide selection available"]
        final_urls: ["https://example.com/running-shoes"]
        status: "PAUSED"
    """
    try:
        # Validate input
        if len(headlines) < 3 or len(headlines) > 15:
            return "Error: Must provide 3-15 headlines for responsive search ads"
        
        if len(descriptions) < 2 or len(descriptions) > 4:
            return "Error: Must provide 2-4 descriptions for responsive search ads"
        
        # Check character limits
        for i, headline in enumerate(headlines):
            if len(headline) > 30:
                return f"Error: Headline {i+1} exceeds 30 character limit: '{headline}'"
        
        for i, description in enumerate(descriptions):
            if len(description) > 90:
                return f"Error: Description {i+1} exceeds 90 character limit: '{description}'"
        
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/adGroupAds:mutate"
        
        # Build headline and description assets
        headline_assets = [{"text": headline} for headline in headlines]
        description_assets = [{"text": description} for description in descriptions]
        
        # Build the ad creation operation
        ad_operation = {
            "operations": [{
                "create": {
                    "adGroup": ad_group_resource_name,
                    "status": status,
                    "ad": {
                        "finalUrls": final_urls,
                        "responsiveSearchAd": {
                            "headlines": headline_assets,
                            "descriptions": description_assets
                        }
                    }
                }
            }]
        }
        
        # Add display URL paths if provided
        if path1 or path2:
            ad_operation["operations"][0]["create"]["ad"]["displayUrl"] = f"{final_urls[0]}/{path1}/{path2}".rstrip('/')
        
        response = requests.post(url, headers=headers, json=ad_operation)
        
        if response.status_code != 200:
            return f"Error creating responsive search ad: {response.text}"
        
        result = response.json()
        if result.get('results'):
            ad_resource_name = result['results'][0]['resourceName']
            output_lines = [f"Successfully created responsive search ad"]
            output_lines.append(f"Resource name: {ad_resource_name}")
            output_lines.append(f"Status: {status}")
            output_lines.append(f"\nHeadlines ({len(headlines)}):")
            for i, headline in enumerate(headlines, 1):
                output_lines.append(f"  {i}. {headline}")
            output_lines.append(f"\nDescriptions ({len(descriptions)}):")
            for i, description in enumerate(descriptions, 1):
                output_lines.append(f"  {i}. {description}")
            output_lines.append(f"\nFinal URLs: {', '.join(final_urls)}")
            output_lines.append("\nNext steps:")
            output_lines.append("1. Enable the ad when ready")
            output_lines.append("2. Monitor performance and optimize")
            
            return "\n".join(output_lines)
        else:
            return f"Ad creation completed but no resource name returned: {result}"
    
    except Exception as e:
        return f"Error creating responsive search ad: {str(e)}"

@mcp.tool()
async def add_negative_keywords(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    target_resource_name: str = Field(description="Campaign or ad group resource name where negative keywords will be added"),
    negative_keywords: List[Dict[str, str]] = Field(description="List of negative keyword objects with 'text' and 'match_type'"),
    level: str = Field(default="CAMPAIGN", description="Level to add negatives: CAMPAIGN or AD_GROUP")
) -> str:
    """
    Add negative keywords to a campaign or ad group.
    
    Negative keywords prevent your ads from showing for irrelevant searches,
    helping improve click-through rates and reduce wasted spend.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        target_resource_name: Campaign or ad group resource name for the negative keywords
        negative_keywords: List of negative keyword dictionaries with:
                          - text: The negative keyword text (e.g., "free")
                          - match_type: EXACT, PHRASE, or BROAD
        level: Where to add negatives (CAMPAIGN or AD_GROUP)
        
    Returns:
        Success message with negative keyword resource names or error message
        
    Example:
        customer_id: "1234567890"
        target_resource_name: "customers/1234567890/campaigns/12345"
        negative_keywords: [
            {"text": "free", "match_type": "BROAD"},
            {"text": "cheap", "match_type": "EXACT"},
            {"text": "discount shoes", "match_type": "PHRASE"}
        ]
        level: "CAMPAIGN"
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        
        # Determine the correct endpoint based on level
        if level.upper() == "CAMPAIGN":
            url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/campaignCriteria:mutate"
            target_field = "campaign"
        else:  # AD_GROUP
            url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/adGroupCriteria:mutate"
            target_field = "adGroup"
        
        # Build negative keyword operations
        operations = []
        for neg_keyword in negative_keywords:
            operation = {
                "create": {
                    target_field: target_resource_name,
                    "negative": True,
                    "keyword": {
                        "text": neg_keyword["text"],
                        "matchType": neg_keyword["match_type"]
                    }
                }
            }
            operations.append(operation)
        
        negative_keyword_operation = {"operations": operations}
        
        response = requests.post(url, headers=headers, json=negative_keyword_operation)
        
        if response.status_code != 200:
            return f"Error adding negative keywords: {response.text}"
        
        result = response.json()
        if result.get('results'):
            output_lines = [f"Successfully added {len(result['results'])} negative keywords at {level} level:"]
            output_lines.append("-" * 60)
            
            for i, (neg_keyword, result_item) in enumerate(zip(negative_keywords, result['results'])):
                resource_name = result_item['resourceName']
                output_lines.append(f"{i+1}. -{neg_keyword['text']} ({neg_keyword['match_type']})")
                output_lines.append(f"   Resource: {resource_name}")
            
            output_lines.append(f"\nTarget: {target_resource_name}")
            output_lines.append("\nThese negative keywords will prevent ads from showing for the specified terms.")
            
            return "\n".join(output_lines)
        else:
            return f"Negative keyword addition completed but no resource names returned: {result}"
    
    except Exception as e:
        return f"Error adding negative keywords: {str(e)}"

@mcp.tool()
async def update_budget_amount(
    customer_id: str = Field(description="Google Ads customer ID (10 digits, no dashes)"),
    budget_resource_name: str = Field(description="Budget resource name to update"),
    new_amount_micros: int = Field(description="New daily budget amount in micros (e.g., 100000000 = $100)")
) -> str:
    """
    Update the daily amount of an existing campaign budget.
    
    This allows you to increase or decrease the daily spending limit for campaigns
    using this budget. Changes take effect immediately.
    
    Args:
        customer_id: The Google Ads customer ID as a string (10 digits, no dashes)
        budget_resource_name: The resource name of the budget to update
        new_amount_micros: New daily budget amount in micros (1,000,000 = 1 unit of currency)
        
    Returns:
        Success message or error message
        
    Example:
        customer_id: "1234567890"
        budget_resource_name: "customers/1234567890/campaignBudgets/12345"
        new_amount_micros: 100000000  # $100 daily budget
    """
    try:
        creds = get_credentials()
        headers = get_headers(creds)
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_customer_id}/campaignBudgets:mutate"
        
        # Build the budget update operation
        budget_operation = {
            "operations": [{
                "update": {
                    "resourceName": budget_resource_name,
                    "amountMicros": str(new_amount_micros)
                },
                "updateMask": "amount_micros"
            }]
        }
        
        response = requests.post(url, headers=headers, json=budget_operation)
        
        if response.status_code != 200:
            return f"Error updating budget amount: {response.text}"
        
        result = response.json()
        if result.get('results'):
            return f"Successfully updated budget amount\nBudget: {budget_resource_name}\nNew daily amount: {new_amount_micros / 1000000:.2f} (account currency)"
        else:
            return f"Budget amount update completed: {result}"
    
    except Exception as e:
        return f"Error updating budget amount: {str(e)}"

def main():
    """Main entry point for the MCP server."""
    # Start the MCP server on stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
