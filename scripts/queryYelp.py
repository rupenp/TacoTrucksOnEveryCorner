#!/usr/bin/env python

import os
import sys
import json
import time
import logging
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

'''Get your auth keys: https://www.yelp.com/developers/manage_api_keys '''
CONSUMER_KEY = "FNU9ojLPp0Qqi5yTraSqhA"
CONSUMER_SECRET = "3FIKLVp6CRhYx6r0FtKy_lXRWHw"
TOKEN = "IeOLgXSADR-IWIAIRaIKp6Dlnd6kQlhq"
TOKEN_SECRET = "R0y_CrO43COv-i7J9WjFhCtV9eE"
auth = Oauth1Authenticator(
          consumer_key=CONSUMER_KEY,
          consumer_secret=CONSUMER_SECRET,
          token=TOKEN,
          token_secret=TOKEN_SECRET)

client = Client(auth)

QUERY = { 'term': 'taco truck','category_filter':'foodstands,foodtrucks'}

REQ_CATEGORIES = set(['foodtrucks','foodstands'])

def query_yelp_api(locations, params=QUERY):
    logger = logging.getLogger("queryYelp.query_yelp_api")
    businesses = []
    for idx, loc in enumerate(locations):
        result = client.search(loc, **params)
        added = 0
        for business in result.businesses:
            try:
                categories = set(map(lambda x:x.alias, business.categories))
                if categories & REQ_CATEGORIES:
                    businesses.append(business)
                    added += 1
            except:
                logger.error("%s" % str(ex))
        total_businesses = result.total
        for offset in range(20, total_businesses, 20):
            params['offset'] = offset
            result = client.search(loc, **params)
            for business in result.businesses:
                try:
                    categories = set(map(lambda x:x.alias, business.categories))
                    if categories & REQ_CATEGORIES:
                        businesses.append(business)
                        added += 1
                except:
                    continue
        if added:
            logger.info("%d/%d added for %s, #total-businesses: %d" % (added, result.total, loc, len(businesses)))
    return businesses

def format_json(business_obj):
    o = {f: business_obj.__getattribute__(f) for f in business_obj._fields}
    try:
        o['categories'] = (map(lambda x:x.alias, business_obj.categories))
    except:
        o['categories'] = []
    try:
        loc = {f: business_obj.location.__getattribute__(f) for f in business_obj.location._fields}
        loc.update({f: business_obj.location.coordinate.__getattribute__(f) \
                for f in business_obj.location.coordinate._fields})
        o['location'] = loc
    except:
        o['location'] = {}
    
    return o


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--us-cities', type=str, default="../data/us-cities.txt", help='list of US cities')
    ap.add_argument('--logfile', type=str, help='log filename')
    ap.add_argument('--outfile', type=str, required=True, help='output file')
    
    args = ap.parse_args()

    formatter_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    if not args.logfile:
        logging.basicConfig(stream=sys.stdout, format=formatter_str, level=logging.DEBUG)
    else:
        logging.basicConfig(filename=args.logfile, format=formatter_str, level=logging.DEBUG)

    logger = logging.getLogger("query-yelp")

    us_cities = map(lambda l:l.strip(), open(args.us_cities))

    logger.info("Querying Yelp for %d US cities" % len(us_cities))
    businesses = query_yelp_api(us_cities)
    logger.info("Writing %d taco trucks to %s" % (len(businesses), args.outfile))
    with open(args.outfile, 'w') as out:
        out.write(json.dumps({"trucks": map(format_json, businesses)}))
