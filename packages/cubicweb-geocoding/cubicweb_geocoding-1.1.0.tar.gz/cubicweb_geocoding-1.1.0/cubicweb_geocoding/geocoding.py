"""geocoding module using google maps service

Typical KML structure:
<kml xmlns="http://earth.google.com/kml/2.0">
  <Response>
    <name>1600 amphitheatre mountain view ca</name>
    <Status>
      <code>200</code>
      <request>geocode</request>
    </Status>
    <Placemark>
      <address>
        1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA
      </address>
      <AddressDetails Accuracy="8">
        <Country>
          <CountryNameCode>US</CountryNameCode>
          <AdministrativeArea>
            <AdministrativeAreaName>CA</AdministrativeAreaName>
           <SubAdministrativeArea>
             <SubAdministrativeAreaName>Santa Clara</SubAdministrativeAreaName>
             <Locality>
               <LocalityName>Mountain View</LocalityName>
               <Thoroughfare>
                 <ThoroughfareName>1600 Amphitheatre Pkwy</ThoroughfareName>
               </Thoroughfare>
               <PostalCode>
                 <PostalCodeNumber>94043</PostalCodeNumber>
               </PostalCode>
             </Locality>
           </SubAdministrativeArea>
         </AdministrativeArea>
       </Country>
     </AddressDetails>
     <Point>
       <coordinates>-122.083739,37.423021,0</coordinates>
     </Point>
   </Placemark>
  </Response>
</kml>
"""

import urllib

from lxml import etree

URL = "http://maps.google.com/maps/geo?sensor=false&output=kml&q=%s&key=%s"

NAMESPACES = {
    "kml": "http://earth.google.com/kml/2.0",
}


def xpath(node, path):
    return node.xpath(path, namespaces=NAMESPACES)


class UnknownAddress(Exception):
    """raise if an error occurs during geocoding process"""


def extract_info(response):
    try:
        code = int(xpath(response, "kml:Response/kml:Status/kml:code/text()")[0])
    except (IndexError, ValueError):
        raise UnknownAddress("unable to read status code")
    if code != 200:
        raise UnknownAddress("unable to find address info")
    coords = xpath(
        response, "kml:Response/kml:Placemark/kml:Point/kml:coordinates/text()"
    )[0]
    lng, lat, _ = (float(info) for info in coords.split(","))
    # XXX return city name / postalcode as returned by google ?
    return {"latitude": lat, "longitude": lng}


def get_latlng(address, gmapkey):
    try:
        kml = urllib.urlopen(
            URL % (urllib.quote(address.encode("utf-8")), gmapkey)
        ).read()
        tree = etree.fromstring(kml)
        return extract_info(tree)
    except UnknownAddress:
        raise
    except Exception as exc:
        raise UnknownAddress(f"{address!r} ({exc})")


if __name__ == "__main__":
    print(
        get_latlng(
            "10 rue Louis Vicat 75015 Paris",
            "ABQIAAAAAZKTE_iGKkEkfmJ-abtesRTwM0brOpm-All5BF6PoaKBxRWWERT7VGewoYPPmZ1Upon0H9cweSYQ0A",
        )
    )
