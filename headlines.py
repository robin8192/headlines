import feedparser
from flask import Flask, render_template, request
import json, urllib

import datetime
from flask import make_response


app = Flask(__name__)

URLS = {'weather_url': 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=cb932829eacb6a0e9ee4f38bfbf112ed',
        'currency_url': 'https://openexchangerates.org/api/latest.json?app_id=c23802e168c14e009a809ca7e72f621e'}

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640',
             'ewn': 'https://ewn.co.za/RSS%20Feeds/Latest%20News'}

DEFAULTS = {'publication':'EWN',
            'city': 'Sandton,ZA',
            'currency_from':'USD',
            'currency_to':'ZAR'}

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


@app.route("/")

def home():
    # get customized headlines, based on user input or cookie or default
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)
    # get customized weather based on user input or default
    city = get_value_with_fallback("city")
    weather = get_weather(city)
    # get customized currency based on user input or default
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rate(currency_from, currency_to)
    # return render_template("home.html", publication=publication, articles=articles,weather=weather,
                        #    currency_from=currency_from, currency_to=currency_to, rate=rate,currencies=sorted(currencies))

    # save cookies and return template
    response = make_response(render_template("home.html",
    articles=articles,
    weather=weather,
    currency_from=currency_from,
    currency_to=currency_to,
    rate=rate,
    publication=publication,
    currencies=sorted(currencies)))

    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    
    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    api_url = URLS['weather_url']
    query = urllib.parse.quote(query)
    url = api_url.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {'description':parsed['weather'][0]['description'],
            'temperature':parsed['main']['temp'],
            'city':parsed['name'],                   
            'country': parsed['sys']['country']}
    return weather

def get_rate(frm, to):
    all_currency = urllib.request.urlopen(URLS['currency_url']).read()

    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())

if __name__ == '__main__':
  app.run(port=5000, debug=True)