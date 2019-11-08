import json
import operator
import random

import requests
from bs4 import BeautifulSoup
from geojson import Feature, FeatureCollection, GeometryCollection, Point

base_url = "http://anitsayac.com/"

app_id = "w92N2c7dXZdtLcmAVd4e"
app_code = "BdOq0CSbt69DhC4gel8jtQ"
points = list()
for year in range(2011, 2020):
    collection = list()
    response = requests.get(base_url, params=dict(year=year))
    soup = BeautifulSoup(response.content, "html.parser")
    for bgyear_class in soup.find_all("span", {"class": f"xxy bgyear{year}"}):
        a = bgyear_class.find("a")
        url = base_url + a.get("href")
        name = a.text
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        for i in soup.find_all("b"):
            if "İl/ilçe:" in i.text:
                city = soup.text.split("İl/ilçe:")[1].split("Tarih:")[0][1:]
                if city:
                    url = f"https://geocoder.api.here.com/6.2/geocode.json?&&city={city}&country=TUR&&app_id={app_id}&app_code={app_code}"
                    latlong_soup = BeautifulSoup(
                        requests.get(url).content, "html.parser"
                    )
                    try:
                        position = json.loads(str(latlong_soup))["Response"]["View"][0][
                            "Result"
                        ][0]["Location"]["DisplayPosition"]
                    except IndexError:
                        pass
                    else:
                        location = dict(
                            longitude=position["Longitude"],
                            latitude=position["Latitude"],
                        )
                        if location not in points:
                            points.append(location)
                        else:
                            location = dict(
                                longitude=random.choice([operator.add, operator.sub])(
                                    position["Longitude"], random.randrange(1, 50) / 999
                                ),
                                latitude=random.choice([operator.add, operator.sub])(
                                    position["Latitude"], random.randrange(1, 50) / 999
                                ),
                            )
                            points.append(location)
                        date = (
                            soup.text.split("İl/ilçe:")[1]
                            .split("Tarih:")[1]
                            .split("Neden öldürüldü:")[0][1:]
                        )
                        reason = (
                            soup.text.split("İl/ilçe:")[1]
                            .split("Tarih:")[1]
                            .split("Neden öldürüldü:")[1]
                            .split("Kim tarafından öldürüldü:")[0][2:]
                        )
                        who = (
                            soup.text.split("İl/ilçe:")[1]
                            .split("Tarih:")[1]
                            .split("Neden öldürüldü:")[1]
                            .split("Kim tarafından öldürüldü:")[1]
                            .split("Korunma talebi:")[0][2:]
                        )
                        req = (
                            soup.text.split("İl/ilçe:")[1]
                            .split("Tarih:")[1]
                            .split("Neden öldürüldü:")[1]
                            .split("Kim tarafından öldürüldü:")[1]
                            .split("Korunma talebi:")[1]
                            .split("Öldürülme şekli:")[0][2:]
                        )
                        death = (
                            soup.text.split("İl/ilçe:")[1]
                            .split("Tarih:")[1]
                            .split("Neden öldürüldü:")[1]
                            .split("Kim tarafından öldürüldü:")[1]
                            .split("Korunma talebi:")[1]
                            .split("Öldürülme şekli:")[1]
                            .split("Kaynak:")[0]
                            .split("Notlar:")[0][2:]
                        )
                        source = (
                            soup.text.split("İl/ilçe:")[1]
                            .split("Tarih:")[1]
                            .split("Neden öldürüldü:")[1]
                            .split("Kim tarafından öldürüldü:")[1]
                            .split("Korunma talebi:")[1]
                            .split("Öldürülme şekli:")[1]
                            .split("Kaynak:")[1][1:]
                            .replace("\n", "")
                        )
                        feature = Feature(
                            geometry=Point(
                                (location["longitude"], location["latitude"])
                            ),
                            properties=dict(
                                name=name,
                                city=city,
                                date=date,
                                reason=reason,
                                who=who,
                                req=req,
                                death=death,
                                year=year,
                                type="boundary",
                                source=source,
                            ),
                        )
                        collection.append(feature)
    femicide = open(f"femicide-{year}.geojson", "w")
    data = FeatureCollection(collection)
    femicide.write(str(data))
