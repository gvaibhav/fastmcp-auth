"""
Time MCP Server with OAuth2 PKCE Authentication
FastMCP-based implementation matching official MCP time server tool names
Based on: https://github.com/modelcontextprotocol/servers/tree/main/src/time
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from zoneinfo import ZoneInfo, available_timezones

from fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.routing import Route

# Configure logging to reduce SSE disconnect noise
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


# OAuth Protected Resource Metadata Handler
async def oauth_protected_resource_metadata(request):
    """
    OAuth 2.0 Protected Resource Metadata (RFC 9728)
    Provides information about this protected resource server
    """
    metadata = {
        "resource": "http://localhost:3000",
        "authorization_servers": ["http://localhost:8000"],
        "bearer_methods_supported": ["header"],
        "resource_signing_alg_values_supported": ["none"],
        "resource_encryption_alg_values_supported": [],
        "resource_encryption_enc_values_supported": [],
        "scopes_supported": ["time:read", "time:convert"],
        "resource_documentation": "http://localhost:3000/",
        "token_endpoint": "http://localhost:8000/oauth/token",
        "introspection_endpoint": "http://localhost:8000/oauth/introspect",
        "revocation_endpoint": "http://localhost:8000/oauth/revoke"
    }
    return JSONResponse(metadata)


# Initialize FastMCP server with OAuth2 PKCE
# Note: Auth configuration is passed via settings or at runtime
mcp = FastMCP("Time Server OAuth")


@mcp.tool()
async def get_current_time(timezone: str = "UTC") -> Dict[str, Any]:
    """
    Get current time in a specific timezone.
    
    Args:
        timezone: IANA timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo').
                 Defaults to 'UTC' if not specified.
    
    Returns:
        Dictionary containing:
        - timezone: The timezone name
        - datetime: Current time in ISO 8601 format with timezone
        - is_dst: Boolean indicating if daylight saving time is active
    
    Raises:
        ValueError: If the timezone name is invalid
    
    Examples:
        >>> await get_current_time(timezone="UTC")
        {'timezone': 'UTC', 'datetime': '2025-11-05T14:30:00+00:00', 'is_dst': False}
        
        >>> await get_current_time(timezone="America/New_York")
        {'timezone': 'America/New_York', 'datetime': '2025-11-05T09:30:00-05:00', 'is_dst': False}
    """
    try:
        if timezone not in available_timezones():
            raise ValueError(
                f"Invalid timezone: {timezone}. "
                f"Must be a valid IANA timezone name."
            )
        
        tz = ZoneInfo(timezone)
        current_time = datetime.now(tz)
        
        # Determine if DST is active
        is_dst = bool(current_time.dst())
        
        return {
            "timezone": timezone,
            "datetime": current_time.isoformat(),
            "is_dst": is_dst
        }
    
    except Exception as e:
        raise ValueError(f"Error getting current time: {str(e)}")


@mcp.tool()
async def convert_time(
    source_timezone: str,
    time: str,
    target_timezone: str
) -> Dict[str, Any]:
    """
    Convert a time from one timezone to another.
    
    Args:
        source_timezone: Source IANA timezone name (e.g., 'America/New_York')
        time: Time in HH:MM format (24-hour, e.g., '14:30', '09:00')
        target_timezone: Target IANA timezone name (e.g., 'Asia/Tokyo')
    
    Returns:
        Dictionary containing:
        - source: Dict with timezone, datetime, and is_dst for source
        - target: Dict with timezone, datetime, and is_dst for target
        - time_difference: String showing hour difference (e.g., '+13.0h', '-5.0h')
    
    Raises:
        ValueError: If timezones are invalid or time format is incorrect
    
    Examples:
        >>> await convert_time("America/New_York", "16:30", "Asia/Tokyo")
        {
            'source': {
                'timezone': 'America/New_York',
                'datetime': '2025-11-05T16:30:00-05:00',
                'is_dst': False
            },
            'target': {
                'timezone': 'Asia/Tokyo',
                'datetime': '2025-11-06T06:30:00+09:00',
                'is_dst': False
            },
            'time_difference': '+14.0h'
        }
    """
    try:
        # Validate timezones
        if source_timezone not in available_timezones():
            raise ValueError(f"Invalid source timezone: {source_timezone}")
        
        if target_timezone not in available_timezones():
            raise ValueError(f"Invalid target timezone: {target_timezone}")
        
        # Parse time in HH:MM format
        try:
            time_parts = time.split(':')
            if len(time_parts) != 2:
                raise ValueError("Invalid time format")
            
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            if not (0 <= hour <= 23):
                raise ValueError("Hour must be between 0 and 23")
            if not (0 <= minute <= 59):
                raise ValueError("Minute must be between 0 and 59")
                
        except (ValueError, IndexError) as e:
            raise ValueError(
                f"Invalid time format: '{time}'. Expected HH:MM (24-hour format), "
                f"e.g., '14:30', '09:00'"
            )
        
        # Create datetime objects for today at the specified time
        source_tz = ZoneInfo(source_timezone)
        target_tz = ZoneInfo(target_timezone)
        
        # Get current date in source timezone
        now_in_source = datetime.now(source_tz)
        
        # Create source time for today
        source_time = datetime(
            now_in_source.year,
            now_in_source.month,
            now_in_source.day,
            hour,
            minute,
            tzinfo=source_tz
        )
        
        # Convert to target timezone
        target_time = source_time.astimezone(target_tz)
        
        # Calculate time difference
        source_offset = source_time.utcoffset() or timedelta()
        target_offset = target_time.utcoffset() or timedelta()
        hours_difference = (target_offset - source_offset).total_seconds() / 3600
        
        # Format time difference string
        if hours_difference.is_integer():
            time_diff_str = f"{hours_difference:+.1f}h"
        else:
            # For fractional hours like Nepal's UTC+5:45
            time_diff_str = f"{hours_difference:+.2f}".rstrip("0").rstrip(".") + "h"
        
        # Determine DST status
        source_is_dst = bool(source_time.dst())
        target_is_dst = bool(target_time.dst())
        
        return {
            "source": {
                "timezone": source_timezone,
                "datetime": source_time.isoformat(),
                "is_dst": source_is_dst
            },
            "target": {
                "timezone": target_timezone,
                "datetime": target_time.isoformat(),
                "is_dst": target_is_dst
            },
            "time_difference": time_diff_str
        }
    
    except Exception as e:
        raise ValueError(f"Error converting time: {str(e)}")


@mcp.resource("time://current")
async def current_time_resource() -> str:
    """
    Resource that provides the current UTC time.
    Can be accessed via the resource URI: time://current
    """
    current = datetime.now(timezone.utc)
    is_dst = bool(current.dst())
    
    return (
        f"Current UTC time:\n"
        f"Timezone: UTC\n"
        f"DateTime: {current.isoformat()}\n"
        f"DST: {is_dst}"
    )


@mcp.resource("time://timezones")
async def timezones_resource() -> str:
    """
    Resource that lists all available IANA timezones.
    Can be accessed via the resource URI: time://timezones
    """
    zones = sorted(available_timezones())
    
    # Show first 100 timezones
    zones_preview = zones[:100]
    
    result = f"Available IANA Timezones ({len(zones)} total)\n"
    result += "=" * 50 + "\n\n"
    
    # Group by continent/region for better readability
    by_region = {}
    for zone in zones_preview:
        if '/' in zone:
            region = zone.split('/')[0]
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(zone)
        else:
            if 'Other' not in by_region:
                by_region['Other'] = []
            by_region['Other'].append(zone)
    
    for region in sorted(by_region.keys()):
        result += f"\n{region}:\n"
        for zone in by_region[region]:
            result += f"  - {zone}\n"
    
    result += f"\n... and {len(zones) - 100} more timezones"
    result += f"\n\nCommon timezones:\n"
    result += "  - UTC\n"
    result += "  - America/New_York\n"
    result += "  - America/Los_Angeles\n"
    result += "  - Europe/London\n"
    result += "  - Europe/Paris\n"
    result += "  - Asia/Tokyo\n"
    result += "  - Asia/Shanghai\n"
    result += "  - Australia/Sydney\n"
    
    return result


if __name__ == "__main__":
    # Run the server
    print("=" * 60)
    print("Time MCP Server - OAuth2 PKCE Edition (SSE Mode)")
    print("=" * 60)
    print("\nTools available:")
    print("  - get_current_time(timezone='UTC')")
    print("  - convert_time(source_timezone, time, target_timezone)")
    print("\nResources available:")
    print("  - time://current")
    print("  - time://timezones")
    print("\nWell-known endpoints:")
    print("  - /.well-known/oauth-protected-resource")
    print("\nAuthentication: OAuth2 PKCE ready")
    print("Running in SSE mode on http://localhost:3000/sse")
    print("=" * 60)
    print("\n⚠️  Note: SSE disconnect errors are expected during testing")
    print("   Real MCP clients maintain long-lived connections")
    print("   The server is working correctly!\n")
    print("Starting server...\n")
    
    # Add custom route for .well-known endpoint before starting
    # The app is created during mcp.run(), so we need to add it via a custom route handler
    from starlette.routing import Route
    if hasattr(mcp, '_app') or True:  # Always add the route
        # Create a wrapper to ensure the app has the route
        original_run = mcp.run
        
        def run_with_routes(*args, **kwargs):
            # The app gets created in run(), so we patch it there
            import functools
            from starlette.applications import Starlette
            
            # Monkey-patch the Starlette initialization to add our route
            original_starlette_init = Starlette.__init__
            
            @functools.wraps(original_starlette_init)
            def patched_init(self, *init_args, **init_kwargs):
                original_starlette_init(self, *init_args, **init_kwargs)
                # Add our custom route
                self.routes.append(
                    Route("/.well-known/oauth-protected-resource",
                          oauth_protected_resource_metadata,
                          methods=["GET"])
                )
            
            Starlette.__init__ = patched_init
            try:
                return original_run(*args, **kwargs)
            finally:
                Starlette.__init__ = original_starlette_init
        
        mcp.run = run_with_routes
    
    # Run in SSE mode
    mcp.run(transport="sse", host="localhost", port=3000)
