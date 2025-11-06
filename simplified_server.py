"""
SIMPLIFIED TIME MCP SERVER - No OAuth
Updated to match official MCP time server tool signatures

For quick testing and development without authentication.
Tool signatures match: https://github.com/modelcontextprotocol/servers/tree/main/src/time
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from zoneinfo import ZoneInfo, available_timezones

from fastmcp import FastMCP


# Initialize FastMCP server WITHOUT authentication
mcp = FastMCP("Time Server - Simple")


@mcp.tool()
async def get_current_time(timezone: str = "UTC") -> Dict[str, Any]:
    """
    Get current time in a specific timezone.
    
    Args:
        timezone: IANA timezone name (default: "UTC")
    
    Returns:
        Dictionary with timezone, datetime (ISO 8601), and is_dst (boolean)
    
    Example:
        >>> await get_current_time(timezone="America/New_York")
        {
            'timezone': 'America/New_York',
            'datetime': '2025-11-05T09:30:00-05:00',
            'is_dst': False
        }
    """
    try:
        if timezone not in available_timezones():
            raise ValueError(f"Invalid timezone: {timezone}")
        
        tz = ZoneInfo(timezone)
        current_time = datetime.now(tz)
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
        source_timezone: Source IANA timezone name
        time: Time in HH:MM format (24-hour)
        target_timezone: Target IANA timezone name
    
    Returns:
        Dictionary with source, target (each with timezone, datetime, is_dst),
        and time_difference (like "+9.0h")
    
    Example:
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
                
        except (ValueError, IndexError):
            raise ValueError(
                f"Invalid time format: '{time}'. Expected HH:MM (24-hour), e.g., '14:30'"
            )
        
        # Create datetime objects
        source_tz = ZoneInfo(source_timezone)
        target_tz = ZoneInfo(target_timezone)
        
        now_in_source = datetime.now(source_tz)
        
        source_time = datetime(
            now_in_source.year,
            now_in_source.month,
            now_in_source.day,
            hour,
            minute,
            tzinfo=source_tz
        )
        
        target_time = source_time.astimezone(target_tz)
        
        # Calculate time difference
        source_offset = source_time.utcoffset() or timedelta()
        target_offset = target_time.utcoffset() or timedelta()
        hours_difference = (target_offset - source_offset).total_seconds() / 3600
        
        if hours_difference.is_integer():
            time_diff_str = f"{hours_difference:+.1f}h"
        else:
            time_diff_str = f"{hours_difference:+.2f}".rstrip("0").rstrip(".") + "h"
        
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


if __name__ == "__main__":
    print("=" * 60)
    print("Time MCP Server - Simple (No Authentication)")
    print("=" * 60)
    print("\nTool signatures match official MCP time server")
    print("\nTools available:")
    print("  - get_current_time(timezone='UTC')")
    print("  - convert_time(source_timezone, time, target_timezone)")
    print("\nAuthentication: NONE")
    print("Perfect for local testing and development!")
    print("=" * 60)
    print("\nStarting server...\n")
    
    mcp.run()


"""
USAGE COMPARISON:

Official MCP Time Server:
    get_current_time(timezone="America/New_York")
    convert_time(source_timezone="UTC", time="14:30", target_timezone="Asia/Tokyo")

This Simple Server:
    ✅ EXACTLY THE SAME signatures!
    ✅ Same parameter names
    ✅ Same return format
    ✅ Only difference: No OAuth authentication

WHEN TO USE THIS VERSION:
- ✅ Local development and testing
- ✅ Learning how MCP works
- ✅ Quick prototyping
- ✅ Internal tools where auth isn't needed
- ✅ Verifying tool behavior before adding OAuth

WHEN TO USE FULL VERSION (server.py):
- ✅ Production deployments
- ✅ When OAuth gateway integration is needed
- ✅ Public-facing services
- ✅ Multi-user environments
"""
