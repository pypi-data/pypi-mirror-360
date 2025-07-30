from beni import bcrypto
from beni.btype import XPath


async def decryptFileIgnoreError(file: XPath, password: str):
    try:
        await bcrypto.decryptFile(file, password)
    except:
        pass
