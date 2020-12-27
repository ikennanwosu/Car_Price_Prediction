def scrape_autotrader(num_pages, postcodes):
    """ Crawls Autotrader website to scrape vehicle features and prices.

       Args:
        - num_pages: number of pages per post code to scrape
        - postcodes: a list of at least one postcode to search for postings 

        Returns:
        returns the following list of vehicle features and prices
        - make: manufacturer of the car
        - model: model of a particular car
        - Doors: number of doors
        - Year: year of manufacture of car
        - Body_Type: refers to the shape (car body) of a particular car
        - Mileage: number of miles travelled or covered
        - Engine_Size: the size of the engine
        - Gearbox: transmission type of the vehicle
        - Fuel: fuel that is used to provide power to the car
        - Past_Owners: number of previous owners
        - HorsePower: power produced by the engine
        - Price: - current price of the car
    """

    import re
    import pandas as pd
    import cloudscraper
    from bs4 import BeautifulSoup
    from time import sleep
    from random import randint
    
    # Initiate data storage
    makes = []
    models = []
    doors = []
    reg_year = []
    body_type = []
    mileage = []
    engine_size =[]
    gearbox = []
    fuel_type = []
    past_owners = []
    horse_power = []
    prices = []

    
    # Initialise the Cloudscraper
    scraper = cloudscraper.create_scraper()
    
    for p_code in postcodes:
        
        pc = p_code.replace(" ", "").lower()
        
        for page_num in range(1, num_pages+1):

            url = 'https://www.autotrader.co.uk/car-search?postcode=' + str(pc) +\
             '&radius=1500&include-delivery-option=on&page=' + str(page_num)
            html = scraper.get(url).content
            soup = BeautifulSoup(html, 'html.parser')
            car_list = soup.find_all('li', class_='search-page__result')

            # Controlling the crawl rate
            sleep(randint(2,10))
            
            for post in car_list:
                title = post.h3.text.split()

                try:
                    make = title[0]
                except IndexError:
                    make = None
                makes.append(make)


                # model of vehicle
                def is_float_(string):
                    """
                        Returns True if all characters in a string 
                        are float characters. If not, it returns False.
                    """
                    try:
                        float(string)
                        return True
                    except ValueError:
                        return False

                try:
                    if is_float_(title[2]):
                        model = title[1]
                    else:
                        model = title[1] + ' ' + title[2]
                except IndexError:
                    model = None
                models.append(model)


                # number of doors
                try:
                    door = re.findall(r'\d[d|dr]', ' '.join(title))[0][0]
                    door = pd.to_numeric(door)
                except IndexError:
                    door = None
                doors.append(door)


                # Get attributes in the unordered (bulleted) list within each post
                attrib = post.find('ul', {'class': 'listing-key-specs'}).text.split('\n')


                # vehicle registration year
                try:
                    year = re.findall(r'\d{4}', ' '.join(attrib))[0]
                    year = int(pd.to_numeric(year))
                except IndexError:
                    year = None
                reg_year.append(year)


                # body type
                try:
                    body = attrib[2]
                except IndexError:
                    body = None
                body_type.append(attrib[2])

                
                # vehicle mileage
                try:
                    miles = re.findall(r'\d+,\d+', ' '.join(attrib))[0]
                    miles = pd.to_numeric(miles.replace(',', ''))
                except IndexError:
                    miles = None
                mileage.append(miles)


                # vehicle engine size
                try:
                    size = re.findall(r'\d\.\d', ' '.join(attrib))[0]
                    size = pd.to_numeric(size)
                except IndexError:
                    size = None
                engine_size.append(size)


                # type of gearbox
                try:
                    gbox = re.findall(r'[Mm]anual|[Aa]utomatic', ' '.join(attrib))[0]
                except IndexError:
                    gbox = None
                gearbox.append(gbox)


                # type of fuel
                try:
                    fuel = re.findall(r'[Pp]etrol|[Dd]iesel|[Ee]lectic|[Hh]ybrid', ' '.join(attrib))[0]
                except IndexError:
                    fuel = None
                fuel_type.append(fuel)

                
                # number of owners in the past
                try:
                    num_owners = re.findall(r'\d\s[Oo]', ' '.join(attrib))[0][0]
                    pd.to_numeric(num_owners)
                except IndexError:
                    num_owners = 0
                past_owners.append(num_owners)


                # vehicle horsepower: converts metric horsepower (PS) to mechanical horsepower (BHP)
                try:
                    fuel = re.findall(r'\d+BHP|\d+PS', ' '.join(attrib))
                    val = fuel[0][:2]
                    unit = fuel[0][2:]

                    if unit == 'BHP':
                        bhp = val
                    else:
                        bhp = round(int(val) / 1.014)
                    bhp = pd.to_numeric(bhp)
                except IndexError:
                    bhp = None
                horse_power.append(bhp)

                
                # Asking price of vehicle
                price_ = post.find('div', {'class' : "product-card-pricing__price"}).text
                try:
                    price = re.findall(r'(\d+.\d+)', price_)[0]
                    price = price.replace(',','')
                    price = pd.to_numeric(price)
                except IndexError:
                    price = None
                prices.append(price)
    
    
    return makes, models, doors, reg_year, body_type, mileage, engine_size, gearbox, fuel_type, past_owners, horse_power, prices