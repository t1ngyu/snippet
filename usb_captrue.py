# -*- coding=utf-8 -*-

import struct
import subprocess
from collections import namedtuple

'''
USBPCAP FILE FORMAT

Global header:

        uint32 magic_number <format=hex>;   /* magic number */
        if(magic_number != 0xA1B2C3D4) {
            Warning("Not a valid PCAP file");
            return 1;
        }
        uint16 version_major;  /* major version number */
        uint16 version_minor;  /* minor version number */
        int32  thiszone;       /* GMT to local correction */
        uint32 sigfigs;        /* accuracy of timestamps */
        uint32 snaplen;        /* max length of captured packets, in octets */
        uint32 network;        /* data link type */

Frame Header:

        time_t ts_sec;         /* timestamp seconds */
        uint32 ts_usec;        /* timestamp microseconds */
        uint32 incl_len;       /* number of octets of packet saved in file */
        uint32 orig_len;       /* actual length of packet */

USBPCAP:

        uint16       headerLen; /* This header length */
        uint64       irpId;     /* I/O Request packet ID */
        USBD_STATUS  status;    /* USB status code
                                   (on return from host controller) */
        FUNC         function;  /* URB Function */
        uchar        info;      /* I/O Request info */
        
        uint16       bus;       /* bus (RootHub) number */
        uint16       device;    /* device address */
        uchar        endpoint;  /* endpoint number and transfer direction */
        TRANSFER_TYPE transfer;  /* transfer type */
        
        uint32       dataLength;/* Data length */
        uchar data[dataLength];
'''


fmt_global_header = '<IHHiIII'
fmt_frame_header = '<IIII'
fmt_usbpacket_header = '<HQIHBHHBBI'

GlobalHeader = namedtuple(
    'GlobalHeader',
    'magic, version_major, version_minor, thiszone, figfigs, snaplen, network'
)
FrameHeader = namedtuple(
    'FrameHeader',
    'ts_sec, ts_usec, incl_len, orig_len'
)
USBHeader = namedtuple(
    'USBHeader',
    'hdrlen, irqId, status, func, info, bus, device, ep, transtype, datalen'
)

frame_header_size = struct.calcsize(fmt_frame_header)
usbpacket_header_size = struct.calcsize(fmt_usbpacket_header)
global_header_size = struct.calcsize(fmt_global_header)


# start usbpcap
usbpcap = subprocess.Popen([
            'USBPcapCMD.exe',
            '-d', r'\\.\USBPcap3', '-s', '200000', '-b', '10000000', '-o', '-'],
        stdout = subprocess.PIPE
    )

# parse GlobalHeader
data = usbpcap.stdout.read(global_header_size)
global_header= GlobalHeader._make(struct.unpack(fmt_global_header, data))
print(global_header)

def is_output_packet(ep):
    return (ep & 0x80) == 0x00;

try:

    packets = []
    headers = []
    filter_device = None

    while True:
        # parse FrameHeader
        data = usbpcap.stdout.read(frame_header_size)
        frame_header = FrameHeader._make(struct.unpack(fmt_frame_header, data))

        # parse usbheader
        data = usbpcap.stdout.read(frame_header.incl_len)
        usb_header = USBHeader._make(
                struct.unpack_from(fmt_usbpacket_header, data)
            )

        #print(usb_header)
        # filter devices
        if filter_device:
            if usb_header.device != filter_device:
                continue
        else:
            if usb_header.datalen > 100000:
                filter_device = usb_header.device
            continue

        #print(usb_header)
        direction = 'IN'
        if is_output_packet(usb_header.ep):
            direction = 'OUT'
        print('{0}\t{1}\t{2}\t{3:#X}'.format(usb_header.device, direction, usb_header.datalen, data[usb_header.hdrlen+4]))

except KeyboardInterrupt:
    pass
finally:
    usbpcap.kill()
    exit(0)
