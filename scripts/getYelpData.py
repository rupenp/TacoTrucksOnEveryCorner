#!/usr/bin/env python

import sys
import json
import argparse
import logging
from yelpapi import YelpAPI

'''Get your auth keys: https://www.yelp.com/developers/manage_api_keys '''


REQ_CATEGORIES = set(['foodtrucks','foodstands'])
# See https://github.com/gfairchild/yelpapi/blob/master/examples/examples.py


def query_yelp_api(locations, use_yelp_api):
    logger = logging.getLogger("queryYelp.query_yelp_api")
    businesses = []

    for idx, loc in enumerate(locations):
        result = use_yelp_api.search_query(term='taco truck', location=loc, categories='foodstands,foodtrucks', limit=50)

        added = 0
        for business in result['businesses']:

            try:
                categories = set([item['alias'] for item in business['categories']])

                if categories & REQ_CATEGORIES:
                        businesses.append(business)
                        added += 1

            except:
                logger.error("%s" % str("Exception occurred"))


        total_businesses = result['total']
        for offset in range(50, total_businesses, 50):
            # print("offset is {}".format(offset))
            # params['offset'] = offset
            # result = client.search(loc, **params)
            result = use_yelp_api.search_query(offset=offset, term='taco truck', location=loc, categories='foodstands,foodtrucks', limit=50)

            added = 0
            for business in result['businesses']:
                try:
                    categories = set([item['alias'] for item in business['categories']])

                    if categories & REQ_CATEGORIES:
                        businesses.append(business)
                        added += 1
                except:
                    logger.error("%s" % str("Exception occurred"))            

        if added:
            logger.info("%d/%d added for %s, #total-businesses: %d" % (added, result['total'], loc, len(businesses)))

    return businesses


if __name__ == '__main__':

    api_key = "your-key-here"
    use_yelp_api = YelpAPI(api_key)

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

    us_cities = map(lambda l: l.strip(), open(args.us_cities))
    # us_cities = ["Alexandria, Virginia"]
    logger.info("Querying Yelp for %d US cities" % len(us_cities))
    businesses = query_yelp_api(us_cities, use_yelp_api)

    logger.info("Writing %d taco trucks to %s" % (len(businesses), args.outfile))
    with open(args.outfile, 'w') as out:
        # out.write(json.dumps({"trucks": map(format_json, businesses)}))
        out.write(json.dumps({"trucks": businesses}))
