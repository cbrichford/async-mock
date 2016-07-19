class MagicMockAsyncContextWrapper:
    """
    MagicMock doesn't like working as an AsyncContextManager with __aenter__/__aexit__,
        so this is a workaround for that.  Calling MagicMockAsyncContextWrapper(obj) on an object created by
        CoroutineBuilder will wrap it in this class, enabling its use in an async with.

    Bug this is working around: https://bugs.python.org/issue26467
    """
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, item):
        return self._obj.__getattr__(item)

    async def __aenter__(self):
        return await self._obj.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._obj.__aexit__(exc_type, exc_val, exc_tb)
