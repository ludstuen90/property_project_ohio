import requests
import scrapy


session = requests.Session()
print(session.cookies.get_dict())
formdata = {
                                "Origin": "https://countyfusion5.kofiletech.us",
                                "Upgrade-Insecure-Requests": "1",
                                "Content-Type": "application/x-www-form-urlencoded",
                                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    }

r = session.post('https://countyfusion5.kofiletech.us/countyweb/login.do', data=formdata)

print(session.cookies.get_dict())
print("Ind: ", session.cookies.get('JSESSIONID', ''))
