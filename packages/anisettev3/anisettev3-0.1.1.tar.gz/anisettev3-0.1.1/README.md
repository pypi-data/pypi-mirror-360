# anisettev3
Python client implementations for [anisette-v3-server](https://github.com/Dadoum/anisette-v3-server).

## Example Usage
```py
from anisettev3 import AnisetteV3SyncClient, MAIN_ANI

a = AnisetteV3SyncClient(MAIN_ANI)
print(a.get_headers())
# Should provision and print generated headers

...

from anisettev3 import AnisetteV3AsyncClient, MAIN_ANI

a = AnisetteV3AsyncClient(MAIN_ANI)
print(await a.get_headers())
# does the same as above, just async
```

## License
MIT, see [`LICENSE`](LICENSE) for details.
