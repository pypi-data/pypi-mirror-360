from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
import json




def get_rate_table():
    app = FirecrawlApp(api_key='fc-1860c43e9098436faa16a3a8512abe82')
    data = app.extract([
      'https://www.x-rates.com/table/?from=USD&amount=1'
    ], prompt='Extract alphabetical order exchange rate table')
    
    json_str = json.dumps(data.data)
    return json_str