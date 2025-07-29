import abc
import uuid
from typing import Any


class Asset(abc.ABC):
    id = uuid.uuid4()
    host: 'Host'
    @abc.abstractmethod
    def __hash__(self):
        ...
    @abc.abstractmethod
    def jsonify(self):
        ...


class Host(Asset):
    host = None

    hostname: str

    def __hash__(self):
        return hash((type(self), self.hostname))

    def jsonify(self):
        return {'type': 'host', 'metadata': {'hostname': self.hostname}}


class Service(Asset):
    port: int
    protocol: str
    service_name: str
    version_str: str
    metadata: dict[str, Any]

    def __hash__(self):
        return hash((type(self), self.host, self.port, self.protocol, self.service_name, self.version_str))

    def jsonify(self):
        return {
            'type': 'service',
            'metadata': {
                'port': self.port,
                'protocol': self.protocol,
                'service_name': self.service_name,
                'version_str': self.version_str,
                **self.metadata
            }
        }


class Loot(abc.ABC):
    id = uuid.uuid4()
    discovered_asset: Asset
    @abc.abstractmethod
    def __hash__(self):
        ...
    @abc.abstractmethod
    def jsonify(self):
        ...


class Vulnerability(Loot):
    name: str
    description: str
    type: str
    severity: str
    metadata: dict[str, Any]

    def __hash__(self):
        return hash((type(self), self.name, self.type, self.severity))

    def jsonify(self):
        return {
            'type': 'vulnerability',
            'discovered_at': self.discovered_asset.id,
            'metadata': {
                'name': self.name,
                'description': self.description,
                'type': self.type,
                'severity': self.severity,
                **self.metadata
            }
        }
