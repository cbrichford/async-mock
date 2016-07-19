import asyncio
from unittest.mock import MagicMock

def SimpleCoroutineMock(f=lambda *args, **kwargs: None, loop=None):
    builder = CoroutineMockBuilder(loop=loop)
    return builder.addDelegate(f).build().mock()


class CoroutineMock(object):
    def __init__(self, loop, returnSequence, block:asyncio.Event):
        self.__start = asyncio.Event(loop=loop)
        self.__end = asyncio.Event(loop=loop)
        self.__returnSequence = tuple(returnSequence)
        if (len(self.__returnSequence) < 1):
            self.__returnSequence = (lambda *args, **kwargs: None, )
        self.__returnSequenceLen = len(self.__returnSequence)
        self.__block = block
        self.__mock = self.__createMock()

    def __createMock(self):
        returnIndex = 0

        async def cr(*args, **kwargs):
            nonlocal returnIndex
            try:
                self.__end.clear()
                self.__start.set()
                if (self.__block is not None):
                    await self.__block.wait()
                    self.__block.clear()
                returnFunc = self.__returnSequence[returnIndex % self.__returnSequenceLen]
                returnIndex += 1
                return returnFunc(*args, **kwargs)
            finally:
                self.__start.clear()
                self.__end.set()

        return MagicMock(wraps=cr)

    def start(self):
        return self.__start

    def end(self):
        return self.__end

    def unblock(self):
        self.__block.set()

    def mock(self):
        return self.__mock


class CoroutineMockBuilder(object):
    def __init__(self, loop):
        self.__loop = loop
        self.__block = None
        self.__returnSequence = []

    def blocks(self):
        return self.blocksOn(asyncio.Event(loop=self.__loop))

    def blocksOn(self, event:asyncio.Event):
        self.__block = event
        return self

    def exception(self, e, repeats=1):
        def r(*args, **kwargs):
            raise e
        self.__returnSequence.extend([r] * repeats)
        return self

    def returns(self, v, repeats=1):
        def r(*args, **kwargs):
            return v
        self.__returnSequence.extend([r] * repeats)
        return self

    def addDelegate(self, f, repeats=1):
        self.__returnSequence.extend([f] * repeats)
        return self

    def build(self):
        return CoroutineMock(self.__loop, self.__returnSequence, self.__block)
