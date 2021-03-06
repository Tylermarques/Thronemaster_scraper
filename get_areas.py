from bs4 import BeautifulSoup

with open('areas.html') as areas_file:
    soup = BeautifulSoup(areas_file, 'html.parser')
    areas = soup.find_all('area')
    names = []
    for area in areas:
        names.append(area.attrs['title'])

    print(names)
    print(len(names))

    areas = ['Port of Winterfell', 'Port of Pyke', 'Port of Lannisport', 'Port of Oldtown', 'Port of Sunspear',
             'Port of Storms End', 'Port of Dragonstone', 'Port of White Harbor', 'Bay of Ice', 'Sunset Sea',
             "Ironman's Bay", 'The Golden Sound', 'West Summer Sea', 'Redwyne Straights', 'East Summer Sea',
             'Sea of Dorne', 'Shipbreaker Bay', 'Blackwater Bay', 'The Narrow Sea', 'The Shivering Sea', 'Castle Black',
             'Winterfell', 'Karhold', 'The Stony Shore', 'White Harbor', "Widow's Watch", 'Moat Cailin',
             'Greywater Watch', "Flint's Finger", 'The Twins', 'Seagard', 'The Fingers', 'Pyke',
             'The Mountains of the Moon', 'Riverrun', 'The Eyrie', 'Lannisport', 'Harrenhal', 'Stoney Sept',
             'Crackclaw Point', 'Dragonstone', 'Blackwater', "King's Landing", 'Searoad Marches', 'Kingswood',
             'The Reach', 'Storms End', 'Highgarden', 'The Boneway', 'Dornish Marches', 'Oldtown', 'Three Towers',
             "Prince's Pass", 'Yronwood', 'Sunspear', 'Starfall', 'The Arbor', 'Salt Shore']
