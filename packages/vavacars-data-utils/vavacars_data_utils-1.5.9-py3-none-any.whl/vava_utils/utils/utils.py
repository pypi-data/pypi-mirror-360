def get_car_year_band(year):
    if 2004 <= year <= 2006:
        return "2004-2006"
    elif 2007 <= year <= 2009:
        return "2007-2009"
    elif 2010 <= year <= 2012:
        return "2010-2012"
    elif 2013 <= year <= 2015:
        return "2013-2015"
    elif 2016 <= year <= 2018:
        return "2016-2018"
    elif 2019 <= year <= 2022:
        return "2019-2022"
    elif 2023 <= year <= 2025:
        return "2023-2025"

def get_price_band(price):
    if 0 <= price <= 300000:
        return "0-300K"
    elif 300000 <= price <= 500000:
        return "300-500K"
    elif 500000 <= price <= 800000:
        return "500-800K"
    elif 800000 <= price <= 1200000:
        return "800-1200K"
    elif price >= 1200000:
        return "1200K+"