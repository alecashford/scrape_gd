import csv
import urllib2, sys
# from BeautifulSoup import BeautifulSoup
import json
from time import sleep
import re
from bs4 import BeautifulSoup
# from random import randint


site= "https://www.glassdoor.com/Reviews/san-francisco-reviews-SRCH_IL.0,13_IM759_IP1.htm"
hdr = {'User-Agent': 'Mozilla/5.0'}
req = urllib2.Request(site,headers=hdr)
page = urllib2.urlopen(req)
soup = BeautifulSoup(page)
# print soup
print soup.find_all("div", class_="eiHdrModule module snug ")

print soup.find_all("a", class_="tightAll h2")

def get_soup_from_url(url):
    site= "https://www.glassdoor.com/Reviews/san-francisco-reviews-SRCH_IL.0,13_IM759_IP1.htm"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(site,headers=hdr)
    page = urllib2.urlopen(req)
    return BeautifulSoup(page)

def get_company_size(url):
    soup = get_soup_from_url(url)
    size = soup.find_all("div", id_="EmpBasicInfo").find_all("div", class_="value")
    return re.sub(' employees', '', size)


def scrape_gd_results_single_page(url):
    soup = get_soup_from_url(url)
    all_company_modules_on_page = soup.find_all("div", class_="eiHdrModule module snug ")

    scraped_data = []

    for company_module in all_company_modules_on_page:
        company_name = company_module.find_all("a", class_="tightAll h2")[0].encode_contents().strip()
        company_website = company_module.find_all("span", class_="url")[0].encode_contents().strip()
        company_gd_url = "www.glassdoor.com{}".format(company_module.find_all("a", class_="tightAll h2")[0]['href'])
        extra_info_from_api = get_info(company_name, company_website)
        company_size = get_company_size(company_gd_url)
        extra_info_from_api["size"] = company_size
        scraped_data.append(extra_info_from_api)

    return scraped_data


def iterate_through_every_gd_page():
    pass

def remove_http_www(site):
    s = site.replace("https://","")
    s = site.replace("http://","")
    s = s.replace("www.","")
    return s

def get_info(company_name, company_site):
    url = "http://api.glassdoor.com/api/api.htm?t.p=95590&t.k=kuoWqawn5sQ&format=json&v=1&action=employers&q=" + urllib2.quote(company_name)
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(url,headers=hdr)
    response = urllib2.urlopen(req)
    data = json.load(response)
    if data["response"]["totalRecordCount"] == 1:
        for idx, company in enumerate(data["response"]["employers"]):
            if remove_http_www(company["website"]) == remove_http_www(company_site):
                return data["response"]["employers"][int(idx)]
            else:
                return None
    elif data["response"]["totalRecordCount"] > 1:
        for idx, company in enumerate(data["response"]["employers"]):
            if remove_http_www(company["website"]) == remove_http_www(company_site):
                return data["response"]["employers"][int(idx)]
    else:
        return None

# file = open('/Users/aashford/Documents/companies.csv', 'rb')
# reader = csv.reader(file)
# ofile  = open('/Users/aashford/Documents/my_companies.csv', "wb")
# writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

# interesting_categories = ["3D Printing", "Ad Targeting", "Aerospace", "Analytics", "Artificial Intelligence", "Assisitive Technology", "Audio", "Augmented Reality", "Automated Kiosk", "Big Data", "Big Data Analytics", "Bioinformatics", "Biometrics", "Brokers", "Business Analytics", "Business Development", "Business Information Systems", "Business Intelligence", "Business Productivity", "Computer Vision", "Content Discovery", "Data Mining", "Data Visualization", "Deep Information Technology", "Defense", "Diagnostics", "Disruptive Models", "Drones", "Early-Stage Technology", "Electric Vehicles", "Electronic Health Records", "Emerging Markets", "Face Recognition", "Finance Technology", "Genetic Testing", "Geospatial", "Health Care Information Technology", "Health Diagnostics", "Home Automation", "Image Recognition", "Internet TV", "Internet of Things", "Machine Learning", "Maps", "Mobile Payments", "Motion Capture", "Music", "Natural Language Processing", "New Technologies", "Personal Finance", "Personal Health", "Predictive Analytics", "Productivity Software", "Quantified Self", "Robotics", "Smart Building", "Space Travel", "Speech Recognition", "Stock Exchanges", "Watch", "Wealth Management", "Wearables"]
# uninteresting_categories = ["Agriculture", "Air Pollution Control", "Alternative Medicine", "Alumni", "Animal Feed", "Aquaculture", "Archiving", "Artists Globally", "Assisted Living", "Babies", "Baby Safety", "Beauty", "Cable", "Call Center Automation", "Celebrity", "Child Care", "Collectibles", "College Campuses", "College Recruiting", "Colleges", "Comics", "Construction", "Cosmetics", "Dental", "Diabetes", "Discounts", "Document Management", "Elder Care", "Email Marketing", "Email Newsletters", "Facebook Applications", "Farming", "Fashion", "Fertility", "Flash Sales", "Flowers", "Food Processing", "Furniture", "Gambling", "Gift Card", "Heavy Industry", "High School Students", "High Schools", "Home Decor", "Hospitality", "Hotels", "Indians", "Jewelry", "K-12 Education", "Kids", "Kinect", "Landscaping", "Limousines", "Mobile Games", "Mobility", "Nightclubs", "Nightlife", "Non Profit", "Nonprofits", "Oil & Gas", "Oil and Gas", "Online Gaming", "Organic Food", "Parenting", "Pets", "Plumbers", "Racing", "Recycling", "Religion", "Senior Citizens", "Senior Health", "Shoes", "Skate Wear", "Soccer", "Sporting Goods", "Sports", "Sports Stadiums", "Sunglasses", "Surfing Community", "Taxis", "Tea", "Teachers", "Teenagers", "Theatre", "Toys", "Underserved Children", "Waste Management", "Water", "Water Purification", "Weddings"]
# interesting_cities = ["Berkeley", "El Cerrito", "Emeryville", "Hayward", "Oakland", "Richmond", "San Francisco", "San Leandro", "Walnut Creek"]

# interesting_rows = ["name", "homepage_url", "category_list", "funding_total_usd", "status", "city", "funding_rounds", "founded_at", "first_funding_at", "last_funding_at", "careerOpportunitiesRating", "compensationAndBenefitsRating", "cultureAndValuesRating", "numberOfRatings", "overallRating", "workLifeBalanceRating", "careerOpportunitiesRating", "seniorLeadershipRating", "recommendToFriendRating"]
# writer.writerow(interesting_rows)

# for row in reader:
#     of_interest = False
#     row_cats = row[2].split("|")
#     for cat in row_cats:
#         if cat in interesting_categories:
#             of_interest = True
#         if cat in uninteresting_categories:
#             of_interest = False
#             break
#     if row[5] not in interesting_cities:
#         of_interest = False
#     if of_interest:
#         info = get_info(row[0], row[1])
#         if info:
#             row.append(info["careerOpportunitiesRating"])
#             row.append(info["compensationAndBenefitsRating"])
#             row.append(info["cultureAndValuesRating"])
#             row.append(info["numberOfRatings"])
#             row.append(info["overallRating"])
#             row.append(info["workLifeBalanceRating"])
#             row.append(info["careerOpportunitiesRating"])
#             row.append(info["seniorLeadershipRating"])
#             row.append(info["recommendToFriendRating"])
#         interesting_rows.append(row)
#         writer.writerow(row)
#         sleep(.5)

# # for row in interesting_rows:
# #     writer.writerow(row)

# file.close()
# ofile.close()