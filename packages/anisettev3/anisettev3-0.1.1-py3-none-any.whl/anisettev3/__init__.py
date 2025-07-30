import json
import plistlib as plist
import hashlib
from datetime import datetime
from locale import getlocale
from uuid import uuid4
from base64 import b64encode
from secrets import token_bytes

from httpx import AsyncClient, Client, URL
from websockets.sync.client import connect as sync_connect
from websockets.asyncio.client import connect as async_connect

MAIN_ANI = "https://ani.sidestore.io"

def genluid() -> str:
    hash = hashlib.sha256()
    hash.update(b64encode(token_bytes(16)))
    return hash.hexdigest()


class AnisetteV3Client:
    PROV_URL = "https://gsa.apple.com/grandslam/GsService2/lookup"

    def __init__(
        self,
        url: str,
        client_info: str | None = None,
        user_agent: str | None = None,
        serial: str | None = None,
        local_user: str | None = None,
        device: str | None = None,
        adipb: str | None = None,
    ):
        self.url = URL(url)
        self.client_info = client_info if client_info else "<MacBookPro13,2> <macOS;13.1;22C65> <com.apple.AuthKit/1 (com.apple.dt.Xcode/3594.4.19)>"
        self.user_agent = user_agent if user_agent else "akd/1.0 CFNetwork/808.1.4"
        self.serial = serial if serial else "0"
        self.local_user = local_user if local_user else genluid()
        self.device = device if device else str(uuid4()).upper()
        self.adipb = adipb

    @staticmethod
    def _parse_provision_urls(d) -> dict[str, str]:
        l = plist.loads(d)
        return {
            "start": l['urls']['midStartProvisioning'],
            "end": l['urls']['midFinishProvisioning'],
        }

    @property
    def _session_url(self) -> str:
        return "wss://" + self.url.host + "/v3/provisioning_session"

    @property
    def _header_url(self) -> str:
        return "https://" + self.url.host + "/v3/get_headers"

    @property
    def _base_headers(self) -> dict:
        return {
            "X-Apple-I-Client-Time": datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%SZ'),
            "X-Apple-Locale": getlocale()[0],
            "X-Apple-I-TimeZone": datetime.now().astimezone().tzname(),
            "X-Mme-Client-Info": self.client_info,
            "User-Agent": self.user_agent,
            "X-Apple-I-MD-LU": self.local_user,
            "X-Apple-I-MD-M": self.device,
            "X-Apple-I-SRL-NO": self.serial,
            "X-Mme-Device-Id": self.device,
        }

    @property
    def _apple_headers(self) -> dict:
        return {
            "Content-Type": "text/x-xml-plist",
            "Accept": "*/*",
        } | self._base_headers

    @staticmethod
    def _plist_body(req: dict | None = None) -> bytes:
        if req is None: req = {}
        return plist.dumps({"Header": {}, "Request": req})
    
    @property
    def _give_identifier(self) -> str:
        return json.dumps({"identifier": self.local_user})

    @property
    def _give_adipb(self):
        return json.dumps({"identifier": self.local_user, "adi_pb": self.adipb})


class AnisetteV3SyncClient(AnisetteV3Client):
    def __init__(
        self,
        url: str,
        client_info: str | None = None,
        user_agent: str | None = None,
        serial: str | None = None,
        local_user: str | None = None,
        device: str | None = None,
        adipb: str | None = None,
        session: Client = Client(verify=False)
    ):
        super().__init__(url, client_info, user_agent, serial, local_user, device, adipb)
        self._session = session

    def _post(self, url, content) -> bytes:
        return self._session.post(url, content=content, headers=self._apple_headers).text.encode()

    def get_headers(self) -> dict:
        if self.adipb is None: self.provision()
        r = self._session.post(self._header_url, content=self._give_adipb, headers={"Content-Type": "application/json"}).json()
        r.pop('result')
        return self._base_headers | r

    def _fetch_provisioning_urls(self):
        return self._parse_provision_urls(self._session.get(self.PROV_URL, headers=self._apple_headers).text)

    def provision(self):
        if self.adipb is not None: return
        urls = self._fetch_provisioning_urls()
        with sync_connect(self._session_url) as c:
            msg = c.recv()
            while msg != '' and c.state != 3:
                r = json.loads(msg)
                if r['result'] == 'GiveIdentifier':
                    c.send(self._give_identifier)
                elif r['result'] == 'GiveStartProvisioningData':
                    c.send(self._give_start(urls['start']))
                elif r['result'] == 'GiveEndProvisioningData':
                    c.send(self._give_end(urls['end'], r['cpim']))
                elif r['result'] == 'ProvisioningSuccess':
                    self.adipb = r['adi_pb']
                    break
                elif r['result'] == 'Timeout':
                    break
                else:
                    raise ValueError(r)
                msg = c.recv()

    def _give_start(self, url) -> str:
        p = plist.loads(self._post(url, self._plist_body()))
        return json.dumps({"spim": p['Response']['spim']})

    def _give_end(self, url, cpim) -> str:
        p = plist.loads(self._post(url, self._plist_body({"cpim": cpim})))
        return json.dumps({"tk": p['Response']['tk'], "ptm": p['Response']['ptm']})


class AnisetteV3AsyncClient(AnisetteV3Client):
    def __init__(
        self,
        url: str,
        client_info: str | None = None,
        user_agent: str | None = None,
        serial: str | None = None,
        local_user: str | None = None,
        device: str | None = None,
        adipb: str | None = None,
        session: AsyncClient = AsyncClient(verify=False)
    ):
        super().__init__(url, client_info, user_agent, serial, local_user, device, adipb)
        self._session = session

    async def _post(self, url, content) -> bytes:
        return (await self._session.post(url, content=content, headers=self._apple_headers)).text.encode()

    async def get_headers(self) -> dict:
        if self.adipb is None: await self.provision()
        r = (await self._session.post(self._header_url, content=self._give_adipb, headers={"Content-Type": "application/json"})).json()
        r.pop('result')
        return self._base_headers | r
    
    async def _fetch_provisioning_urls(self):
        return self._parse_provision_urls((await self._session.get(self.PROV_URL, headers=self._apple_headers)).text)

    async def provision(self):
        if self.adipb is not None: return
        urls = await self._fetch_provisioning_urls()
        async with async_connect(self._session_url) as c:
            msg = await c.recv()
            while msg != '' and c.state != 3:
                r = json.loads(msg)
                if r['result'] == 'GiveIdentifier':
                    await c.send(self._give_identifier)
                elif r['result'] == 'GiveStartProvisioningData':
                    await c.send(await self._give_start(urls['start']))
                elif r['result'] == 'GiveEndProvisioningData':
                    await c.send(await self._give_end(urls['end'], r['cpim']))
                elif r['result'] == 'ProvisioningSuccess':
                    self.adipb = r['adi_pb']
                    break
                elif r['result'] == 'Timeout':
                    break
                else:
                    raise ValueError(r)
                msg = await c.recv()

    async def _give_start(self, url) -> str:
        p = plist.loads(await self._post(url, self._plist_body()))
        return json.dumps({"spim": p['Response']['spim']})

    async def _give_end(self, url, cpim) -> str:
        p = plist.loads(await self._post(url, self._plist_body({"cpim": cpim})))
        return json.dumps({"tk": p['Response']['tk'], "ptm": p['Response']['ptm']})

