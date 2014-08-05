'''
DNS Server. Run it locally.
'''

from twisted.internet import reactor, defer
from twisted.names import client, dns, error, server
from twisted.web.client import Agent
from twisted.internet.protocol import Protocol

SERVICE_URL = '' # Example: 'http://1.1.1.1:5000/resolve/%s/A/'

class HTTPConsumer(Protocol):
    def __init__(self, name, finished):
        self.name = name
        self.finished = finished
        self.buffer = ''

    def dataReceived(self, bytes):
        self.buffer += bytes

    def connectionLost(self, reason):
        if self.buffer:
            answer = dns.RRHeader(
                name=self.name,
                payload=dns.Record_A(address=b'%s' % (self.buffer, )))
            answers = [ answer ]
            authority = []
            additional = []
            self.finished.callback([ answers, authority, additional ])
        else:
            self.finished.fail(error.DomainError())


class DynamicResolver(object):

    def __init__(self):
        self.agent = Agent(reactor)

    def query(self, query, timeout=None):
        name = query.name.name
        if query.type == dns.A:
            httpResolveResponse = self.agent.request(
                'GET',
                SERVICE_URL % name,
                None)

            def consumeBody(response):
                finished = defer.Deferred()
                if response.code == 500:
                    return defer.fail(error.DomainError())
                else:
                    response.deliverBody(HTTPConsumer(name, finished))
                return finished

            return httpResolveResponse.addCallback(consumeBody)
        else:
            return defer.fail(error.DomainError())

def main():
    factory = server.DNSServerFactory(
        clients=[DynamicResolver(), client.Resolver(resolv='/etc/resolv.conf')]
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(10053, protocol)
    reactor.listenTCP(10053, factory)

    reactor.run()

if __name__ == '__main__':
    raise SystemExit(main())
