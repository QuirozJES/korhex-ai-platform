import asyncio
from backend.modules.scraper import _async_search_account

async def main():
    try:
        res = await _async_search_account('Valero', 'valero.com', 'Energy')
        print('SUCCESS:', len(res.get('sources', [])))
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
