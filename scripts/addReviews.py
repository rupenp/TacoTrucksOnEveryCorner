import sys
import json
import argparse
import logging
from yelpapi import YelpAPI
import time

def review_yelp_api(data, use_yelp_api):
    logger = logging.getLogger("queryYelp.query_yelp_api")
    businesses = []

    try:
        for business in data['trucks']:
            try:
                result = use_yelp_api.reviews_query(id=business['id'])
            except YelpAPI.YelpAPIError as e:
                logger.error(e)
                return businesses

            if len(result[u'reviews']) > 0:
                businesses.append({
                    'id': business['id'],
                    'snippet_text': result['reviews'][0]['text']
                })
            time.sleep(0.5)
    except Exception as e:
        logger.error("Got some kind of error")
        logger.error(e)
    return businesses


if __name__ == "__main__":
    api_key = "your-key-here"
    use_yelp_api = YelpAPI(api_key)

    ap = argparse.ArgumentParser()
    ap.add_argument('--us-cities', type=str, default="../data/us-cities.txt", help='list of US cities')
    ap.add_argument('--logfile', type=str, help='log filename')
    ap.add_argument('--inpfile', type=str, default="taco-trucks.json", help='output file')
    ap.add_argument('--outfile', type=str, default="reviews-taco-trucks.json", help='output file')

    args = ap.parse_args()

    formatter_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    if not args.logfile:
        logging.basicConfig(stream=sys.stdout, format=formatter_str, level=logging.DEBUG)
    else:
        logging.basicConfig(filename=args.logfile, format=formatter_str, level=logging.DEBUG)

    logger = logging.getLogger("query-yelp")

    with open(args.inpfile, 'r') as inpfile:
        # out.write(json.dumps({"trucks": map(format_json, businesses)}))
        data = json.load(inpfile)

    logger.info("There are %d taco trucks info in %s" % (len(data), args.inpfile))

    businesses = review_yelp_api(data, use_yelp_api)
    logger.info("Writing %d taco trucks to %s" % (len(businesses), args.outfile))
    with open(args.outfile, 'w') as out:
        # out.write(json.dumps({"trucks": map(format_json, businesses)}))
        out.write(json.dumps({"trucks": businesses}))
