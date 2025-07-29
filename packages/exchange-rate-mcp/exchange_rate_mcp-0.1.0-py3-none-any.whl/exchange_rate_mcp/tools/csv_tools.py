from exchange_rate_mcp.server import mcp
from exchange_rate_mcp.tools.extract_data import get_rate_table



@mcp.tool()
def get_exchange_rate() ->str:
    """get exchange rate based on USD"""
    return get_rate_table()
    
    
    
@mcp.tool()
def get_exchange_rates() ->str:
    """return the exchange rates from USD"""
    return ""
    
