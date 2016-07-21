from unittest.mock import MagicMock, PropertyMock

class MagicMockAsyncContextWrapper(MagicMock):
    """
    MagicMock doesn't like working as an AsyncContextManager with __aenter__/__aexit__,
        so this is a workaround for that.  Just use an instance of this instead of MagicMock,
        and aenter/aexit can be defined as normal using the CoroutineMock

    setProperty allows the caller to simulate properties on the mock object.  you must use .setProperty for each
        update to the property, setting it directly will not work.
    """
    async def __aenter__(self):
        aenter = super().__getattribute__('__aenter__')
        return await aenter()

    async def __aexit__(self, *args, **kwargs):
        aexit = super().__getattribute__('__aexit__')
        return await aexit(*args, **kwargs)

    def setProperty(self, key, value):
        setattr(type(self), key, PropertyMock(return_value=value))