import dpkt
import socket
import pygeoip

# Load the GeoIP database
gi = pygeoip.GeoIP('GeoLiteCity.dat')

def retKML(dstip, srcip):
    try:
        dst = gi.record_by_name(dstip)
        src = gi.record_by_name('x.x.x.x')
        if dst is None or src is None:
            return ''
        dstlongitude = dst['longitude']
        dstlatitude = dst['latitude']
        srclongitude = src['longitude']
        srclatitude = src['latitude']

        kml = (
            '<Placemark>\n'
            f'<name>{dstip}</name>\n'
            '<extrude>1</extrude>\n'
            '<tessellate>1</tessellate>\n'
            '<styleUrl>#transBluePoly</styleUrl>\n'
            '<LineString>\n'
            '<coordinates>\n'
            f'{srclongitude},{srclatitude}\n'
            f'{dstlongitude},{dstlatitude}\n'
            '</coordinates>\n'
            '</LineString>\n'
            '</Placemark>\n'
        )
        return kml
    except:
        return ''

def plotIPs(pcap):
    kmlPts = ''
    for (ts, buf) in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            if not isinstance(eth.data, dpkt.ip.IP):
                continue
            ip = eth.data
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)
            kml = retKML(dst, src)
            if kml:
                kmlPts += kml
        except:
            continue
    return kmlPts

def main():
    with open('wire.pcap', 'rb') as f:
        pcap = dpkt.pcap.Reader(f)
        kmlheader = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<Style id="transBluePoly">
  <LineStyle>
    <width>1.5</width>
    <color>501400E6</color>
  </LineStyle>
</Style>
'''
        kmlfooter = '</Document>\n</kml>'
        kmldoc = kmlheader + plotIPs(pcap) + kmlfooter

        with open("ip_trace.kml", "w", encoding="utf-8") as out_file:
            out_file.write(kmldoc)
        print("[✓] KML file 'ip_trace.kml' generated. Open it with Google Earth.")

if __name__ == '__main__':
    main()
