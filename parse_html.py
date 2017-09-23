from bs4 import BeautifulSoup
import re


def parse_price(price):
    '''
    Parses a string that has strange characters and takes only the digits
    :param price: a dirty string that has inside strange characters like
            "nxa304dsa€ax"
    :return: A touple of 2 strings, first one the price, second one the currency symbol
    '''
    non_decimal = re.compile(r'[^\d.]+')
    price_parsed = non_decimal.sub("", price)
    if len(price) > 0:
        currency = price[-2]
        return(price_parsed, currency)
    else:
        currency = "unkown"
        return("999999", currency)

def parse_duration(duration):
    '''
    Converts duration in time like '37h 5m' into hours
    :param duration: a string like '37h 5m'
    :return: a string which is the duration in hours
    '''
    d = duration.split()
    if len(d) is 1:
        return d[0][0:-1]
    else:
        return(round(float(d[0][0:-1])+float(d[1][0:-1])/60,1))

def parse_date(date):
    '''
    Parses a dirty string date like '\n17/01\nmié.\n' into "17-01"
    :param date: string like '\n17/01\nmié.\n'
    :return: string like "17-01"
    '''
    return(date[1:-6].replace("/","-"))

def parse_arrival_time(time):
    '''
    Cleans the dirty time
    :param time: a string like \n6:55\n+1\n
    :return: parsed time as string like 6:55
    '''
    return time.split("\n")[1]

def parse_kayak_mobile(filename, link=""):
    '''
    Load the HTML code from the file filename and returns a list of dictionaries
    with the parsed information
    :param filename: string full filename of the HTML to parse from Kayak
    :param link: link string where the HTML is from
    :return: list of dictionaries where each one has the parsed information
    '''
    download_date = filename.split("tmp")[0][:-1].split("/")[1]
    try:
        html_code = open(filename, "r").read()
    except FileNotFoundError:
        # No HTML generated
        return []
    soup = BeautifulSoup(html_code, "html.parser")
    boxes = soup.find_all(class_="FResultItemCard")
    dataset = []
    for box in boxes:
        try:
            info = {}
            info["link"] = link
            info["download_date"] = download_date
            info["price"], info["currency"] = parse_price(box.find_all(class_="FResultItem__price")[0].text)
            info["airlines"] = box.find_all(class_="FResultItem__airlines")[0].text[1:-2].replace("\n"," ")
            # Number of flights
            number_destinations = len(box.find_all(class_="FResultItem__LegItem FResultItem__LegItem--withDates"))
            info["number_destinations"] = number_destinations
            # Run the loop if there are multiple destinations
            for i in range(number_destinations):
                info["duration_" + str(i)] = parse_duration(box.find_all(class_="ResultLeg__durationBlock")[i].text)
                info["stops_" + str(i)] = box.find_all(class_="ResultLeg__stopAirports")[i].text
                info["number_stops_" + str(i)] = len(info["stops_" + str(i)].split())
                info["date_" + str(i)] = parse_date(box.find_all(class_="ResultLeg__date")[i].text)
                info["depart_time_" + str(i)] = box.find_all(class_="ResultLeg__time")[i * 2].text
                info["arrival_time_" + str(i)] = parse_arrival_time(box.find_all(class_="ResultLeg__time")[i * 2 + 1].text)
                info["depart_airport_" + str(i)] = box.find_all(class_="ResultLeg__airport")[i * 2].text
                info["arrival_airport_" + str(i)] = box.find_all(class_="ResultLeg__airport")[i * 2 + 1].text
                info["day_week_" + str(i)] = (box.find_all(class_="ResultLeg__timeDay")[i].text).replace(".","")
            dataset.append(info)
        except IndexError:
            # The js didnt load
            return dataset
    return dataset
