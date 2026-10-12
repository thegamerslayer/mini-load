"""
Proxy module: Request-forwarding core.
"""
import httpx
from src.strategies import round_robin

async def forward(pool,method,path,query,headers,body):
    backend = round_robin(pool)
    url = backend.url + path
    
    async with httpx.AsyncClient() as client:
        response = await client.request(method,url,params=query,headers=headers,content=body)
        
        return response
    