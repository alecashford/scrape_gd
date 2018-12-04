import csv
import urllib2, sys
import json
import time
import re
from functools import wraps
from bs4 import BeautifulSoup

BASE_QUERY = "https://www.glassdoor.com/Reviews/san-francisco-reviews-SRCH_IL.0,13_IM759_IP1.htm"
DESIRED_KEYS = ["careerOpportunitiesRating", "compensationAndBenefitsRating", "cultureAndValuesRating", "industry", "industryName", "name", "numberOfRatings", "overallRating", "ratingDescription", "recommendToFriendRating", "sectorName", "seniorLeadershipRating", "website", "workLifeBalanceRating"]

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def get_soup_from_url(url):
    page = make_http_request(url)
    return BeautifulSoup(page)

@retry(urllib2.URLError, tries=4, delay=3, backoff=2)
def make_http_request(url):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(url, headers=hdr)
    page = urllib2.urlopen(req)
    return page

def get_page_count(url):
    soup = get_soup_from_url(url)
    page_count = soup.find_all("div", class_="count margBot floatLt tightBot")
    return int(re.search(r'(?<=of\ )(.*)(?=\ Companies)', page_count[0].text).group().replace(',', ''))

def get_more_info_from_company_page(url):
    soup = get_soup_from_url(url)
    # size = soup.find_all("div", id_="EmpBasicInfo").find_all("div", class_="value")
    try:
        size = soup.select("#EmpBasicInfo .info .infoEntity")[2].select(".value")[0].get_text()
    except:
        size = ""
    try:
        headquarters = soup.select("#EmpBasicInfo .info .infoEntity")[1].select(".value")[0].get_text()
    except:
        headquarters = ""
    try:
        employer_description = soup.select("#EmpBasicInfo .empDescription")[0]["data-full"]
        employer_description = re.sub('"', "'", employer_description)  
    except:
        employer_description = ""
    return {"size" : size, "headquarters" : headquarters, "employer_description" : employer_description}
    # return [size, headquarters, employer_description]

def write_to_csv(line):
    f = open('output.csv','a')
    f.write(line) # Give your csv text here.
    f.close()

def scrape_gd_results_single_page(url):
    soup = get_soup_from_url(url)
    all_company_modules_on_page = soup.find_all("div", class_="eiHdrModule module snug ")

    # scraped_data = []

    for company_module in all_company_modules_on_page:
        memory = company_module.find_all("a", class_="tightAll h2")
        company_name = memory[0].encode_contents().strip() if memory else ""
        memory = company_module.find_all("span", class_="url")
        company_website = memory[0].encode_contents().strip() if memory else ""
        company_gd_url = "https://www.glassdoor.com{}".format(company_module.find_all("a", class_="tightAll h2")[0]['href'].encode('utf-8')) # this needs fixing; getting error: UnicodeEncodeError: 'ascii' codec can't encode character u'\xe9' in position 26: ordinal not in range(128)
        extra_info_from_api = get_info(company_name, company_website)
        extra_info_from_page = get_more_info_from_company_page(company_gd_url)
        # print extra_info_from_page
        # extra_info_from_api["size"] = company_size

        # d = {key: value for (key, value) in extra_info_from_api if key in DESIRED_KEYS}

        # scraped_data.append(extra_info_from_api)
        all_data = extra_info_from_api.copy()
        all_data.update(extra_info_from_page)

        print formatted_line(all_data)
        write_to_csv(formatted_line(all_data))

    # return scraped_data

def key_exists(obj, key):
    if obj:
        if obj.has_key(key) and isinstance(obj[key], unicode):
            return obj[key].encode('utf-8')
        elif obj.has_key(key):
            return obj[key]
    else:
        return ""

def formatted_line(obj):
    return '"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}"\n'.format(
            key_exists(obj, "name"),
            key_exists(obj, "website"),
            key_exists(obj, "size"),
            key_exists(obj, "headquarters"),
            key_exists(obj, "industry"),
            key_exists(obj, "industryName"),
            key_exists(obj, "sectorName"),
            key_exists(obj, "employer_description"),
            key_exists(obj, "numberOfRatings"),
            key_exists(obj, "careerOpportunitiesRating"),
            key_exists(obj, "compensationAndBenefitsRating"),
            key_exists(obj, "cultureAndValuesRating"),
            key_exists(obj, "overallRating"),
            key_exists(obj, "ratingDescription"),
            key_exists(obj, "recommendToFriendRating"),
            key_exists(obj, "seniorLeadershipRating"),
            key_exists(obj, "workLifeBalanceRating"))

def iterate_through_every_gd_page():
    total_results = get_page_count(BASE_QUERY)
    number_of_pages = int(total_results / 5) + (total_results % 5 > 0)
    for i in range(1, number_of_pages + 1):
        query = "https://www.glassdoor.com/Reviews/san-francisco-reviews-SRCH_IL.0,13_IM759_IP{}.htm".format(i)
        page_results = scrape_gd_results_single_page(query)
        time.sleep(5)
        # print formatted_line(page_results)


def remove_http_www(site):
    s = site.replace("https://","")
    s = site.replace("http://","")
    s = s.replace("www.","")
    return s

def get_info(company_name, company_site):
    url = "http://api.glassdoor.com/api/api.htm?t.p=95590&t.k=kuoWqawn5sQ&format=json&v=1&action=employers&q=" + urllib2.quote(company_name)
    data = json.load(make_http_request(url))
    if "response" in data:
        if data["response"]["totalRecordCount"] == 1:
            for idx, company in enumerate(data["response"]["employers"]):
                if remove_http_www(company["website"]) == remove_http_www(company_site):
                    return data["response"]["employers"][int(idx)]
                else:
                    return {}
        elif data["response"]["totalRecordCount"] > 1:
            for idx, company in enumerate(data["response"]["employers"]):
                if remove_http_www(company["website"]) == remove_http_www(company_site):
                    return data["response"]["employers"][int(idx)]
        else:
            return {}
    return {}

def main():
    iterate_through_every_gd_page()

if __name__== "__main__":
  main()


