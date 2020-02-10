from struct import unpack_from, pack, calcsize
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class PacketParser:
    buffer = b''

    def parse(self, data):
        self.buffer += data
        while True:
            if len(self.buffer) < 8:
                break
            length = unpack_from('>I', self.buffer, 0)[0]
            if length < 4:
                raise Exception(f'Invalid length: {length}')
            if len(self.buffer) < 4 + length:
                break
            checksum = 0
            for d in self.buffer[4: 4 + length - 4]:
                checksum += d
            checksum += unpack_from('>I', self.buffer, length)[0]
            checksum &= 0xFFFF
            if checksum != 0:
                raise Exception(f'checksum error: {checksum}')

            p = self.buffer[4: 4 + length - 4]
            self.buffer = self.buffer[4 + length:]
            yield p

class FakeServer(Protocol):
    ''' fake server '''

    PACKET_VERSION_REQUEST = 0
    PACKET_VERSION_RESPONSE = 1
    PACKET_COORDINATE = 2
    parser = None

    def connectionMade(self):
        print('client connected.')
        self.parser = PacketParser()

    def connectionLost(self, reason):
        print('client disconnected.')

    def dataReceived(self, data):
        for p in self.parser.parse(data):
            packet_type = p[0]
            if packet_type == self.PACKET_VERSION_REQUEST:
                self.print_request(p)
                self.accept()
            elif packet_type == self.PACKET_COORDINATE:
                self.print_coordinate(p)
            else:
                raise Exception('Unexpect packet: type={packet_type}')

    def accept(self):
        data = pack('>IBBI', 2+4, self.PACKET_VERSION_RESPONSE, 1, (0-self.PACKET_VERSION_RESPONSE-1)&0xFFFF)
        print('[SEND]', str(data))
        self.transport.write(data)

    def print_request(self, p):
        version, device_type, button_max, x_max, y_max, pressure_max, distance_max = unpack_from('>BBBHHHH', p,1)
        print('version     :', version     )
        print('device_type :', device_type )
        print('button_max  :', button_max  )
        print('x_max       :', x_max       )
        print('y_max       :', y_max       )
        print('pressure_max:', pressure_max)
        print('distance_max:', distance_max)

    def print_coordinate(self, p):
        frame, timestamp, contact_count, button = unpack_from('>IIBH', p, 1)
        contacts = []
        for i in range(contact_count):
            contacts.append(unpack_from('>HHHHHff', p, 1 + calcsize('>IIBH') + i * calcsize('>HHHHHff')))
        contact_info = ' '.join([f'<{x[0]}|{x[1]},{x[2]:5}|{x[3]:5},{x[4]:5},{x[5]:2.1f},{x[6]:2.1f}>' for x in contacts])
        print('[{}][{}] {} {} {}'.format(timestamp, frame, contact_count, button, contact_info))


class FakeServerFactory(Factory):
    def buildProtocol(self, addr):
        return FakeServer()


reactor.listenTCP(9000, FakeServerFactory())
reactor.run()

