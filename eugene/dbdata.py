#!/usr/bin/env python
## -*- coding: utf-8 -*-

import os, sys
SOPHIE_BASE=os.environ.get('VURVE_SOPHIE_BASE', '.')
VURVE_DATA=os.environ.get('VURVE_DATA', '.')
VURVE_LOG=os.environ.get('VURVE_LOG', '.')

sys.path.append(SOPHIE_BASE)

import csv
import paste
from pylons import config
from sophie.config.environment import load_environment
conf = paste.deploy.appconfig('config:local-production.ini', relative_to=SOPHIE_BASE)
load_environment(conf.global_conf, conf.local_conf)

from sophie.lib.connectors.vurve.db.merchantdb_report import MerchantDbReport
from sophie.lib.connectors.media.google_adwords.adwords_report import AdwordsReport
from sophie.lib.connectors.vurve.pixeldb_report import PixelDbReport
from sophie.lib.controllers.common.store import Store
from sophie.lib.utils.common.timeconv import get_sliding_date_range #, pst_from_timestamp, timestamp_from_datetime, to_timestamp

from nested_dict import nested_dict

def main(argv):
    import getopt
    try:
        sid = None
        numdays = 30
        opts, args = getopt.getopt(argv, "hs:n:", ["help", "sid=", "numdays="])

        for o, a in opts:
            if o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-s", "--sid"):
                sid = int(a)
            elif o in ("-n", "--numdays"):
                numdays = int(a)
            else:
                raise getopt.GetoptError("unknown option {0}".format(o))

        if sid is None:
            raise getopt.GetoptError('store ID (--sid) required')

    except getopt.GetoptError as e:
        print >>sys.stderr, '*** Error:', str(e)
        usage()
        sys.exit(2)

    parse_tos(Store(sid), numdays)


def parse_tos(store, numdays):
    #csvw = csv.writer(open("./S%s.csv" % sid,'wb'))

#    for line in csvreader:
#        if header:
#            header = False
#            continue
#        keyword = line[0]
#        if line[10] == "[]":
#            continue
#        recent_history = ast.literal_eval((line[10][1:]).split('}}}')[0] + '}}}')
#        clicks = recent_history['metrics']['clicks']['value']
#        if clicks > 0:
#            pos = recent_history['metrics']['pos']['value']
#            roi = recent_history['metrics']['roi']['value']
#            imps = recent_history['metrics']['imps']['value']
#            tos = tos_info[keyword] if keyword in tos_info else 0
#            if imps > 0:
#                csvw.writerow([keyword, pos, roi, tos])

    tos_info = get_time_on_site_data(store, numdays)
    sales_info = get_merchant_db_data(store, numdays)
    cost_info = get_adwords_data(store, numdays)

    print >>sys.stderr, [len(c) for c in (tos_info, sales_info, cost_info)]

    csvw = csv.writer(sys.stdout)
    csvw.writerow(["keyword", "mkgsrc", "revenue", "n_orders", "kw_cost", "quality", "vtos"])

    for kw in cost_info:
        #if kw not in cost_info.keys():
        #    roi = "ERROR:adwords"
        #elif kw in sales_info.keys() and "vurve" in sales_info[kw]:
        #if kw in sales_info.keys() and "vurve" in sales_info[kw]:
        #    roi = float(sales_info[kw]["vurve"] - cost_info[kw]/1000000.0)/(cost_info[kw]/1000000.0) if cost_info[kw] > 0 else 0
        #else:
        #    roi = -1
        #ext_sales = 0
        #if kw in sales_info and "nonvurve" in sales_info[kw]:
        #    ext_sales = sales_info[kw]["nonvurve"]
        #try:
        #    ext_sales = sales_info[kw]['nonvurve']
        #except KeyError:
        #    ext_sales = 0
        #tos = tos_info[kw][0] if kw in tos_info else 0
        #nvis = tos_info[kw][1] if kw in tos_info else []
        mkg_source = sales_info[kw].get('marketingSource', '')
        revenue = sales_info[kw].get('revenue', 0.0)
        nord = sales_info[kw].get('order_count', 0)
        kw_cost = cost_info[kw].get('cost', 0)/1000000.0
        quality = cost_info[kw].get('quality')
        tvis = tos_info.get(kw, [])

        csvw.writerow([kw.encode('utf8'), mkg_source, revenue, nord, kw_cost, quality, tvis])



def get_time_on_site_data(store, numdays):
    pixeldb_report = PixelDbReport(store, ["mkg_id","visitor"], ["time_spent"],["add"], None, None)
    start, end = get_sliding_date_range(numdays)
    data = pixeldb_report.get_data(None, None, start, end)

    kw_avg_time_spent = {}
    for e in data["entries"]:
        if e['dimensions']['mkg_id']['value'] is not None:
            kw = e['dimensions']['mkg_id']['value'].lower()
            if kw not in kw_avg_time_spent:
                kw_avg_time_spent[kw] = []
            kw_avg_time_spent[kw].append(e['metrics']['time_spent']['value'])

    return kw_avg_time_spent


def get_merchant_db_data(store, numdays):
    start, end = get_sliding_date_range(numdays)
    merchant_report = MerchantDbReport(store, ["marketingSource","keyword"],
                                           ["revenue", "order_count"], ["add", "add"], None, time_aggregation=None)
    merchant_data = merchant_report.get_data(mode=None, length=None, start_date=start, end_date=end)

    entries = merchant_data["entries"]

    #vurve_sales = filter(lambda x: x["dimensions"]["marketingSource"]["value"] == "Vurve", entries)
    #nonvurve_sales = filter(lambda x: x["dimensions"]["marketingSource"]["value"] != "Vurve", entries)

    keyword_rev_data = nested_dict()

    for e in entries:
        for kw in e['dimensions']['keyword']['value']:
            keyword_rev_data[kw.lower()]['marketingSource'] = e["dimensions"]["marketingSource"]["value"]
            keyword_rev_data[kw.lower()]['revenue'] = e["metrics"]["revenue"]["value"]
            keyword_rev_data[kw.lower()]['order_count'] = e["metrics"]["order_count"]["value"]

    """
    for entry in vurve_sales:
        for kw in entry["dimensions"]["keyword"]["value"]:
            keyword_rev_data[kw.lower()]["vurve"] = entry["metrics"]["revenue"]["value"]

    for entry in nonvurve_sales:
        for kw in entry["dimensions"]["keyword"]["value"]:
            keyword_rev_data[kw.lower()]["nonvurve"] = entry["metrics"]["revenue"]["value"]
    """

    return keyword_rev_data


def get_adwords_data(store, numdays):
    start, end = get_sliding_date_range(numdays)

    adwords_report = AdwordsReport(store, ["kwSite"],
                                           ["cost", "qualityScore"], ["add", "average"], None, time_aggregation=None)
    report = adwords_report.get_data(mode=None, length=None, start_date=start, end_date=end)
    spend_data = nested_dict()
    for entry in report["entries"]:
        kw = entry["dimensions"]["kwSite"]["value"].lower()
        spend_data[kw]['cost'] = entry["metrics"]["cost"]["value"]
        spend_data[kw]['quality'] = entry["metrics"]["qualityScore"]["value"]
    return spend_data


def usage():
    print >>sys.stderr, '\tUsage: <command> -s <store_id> [-n <days_to_report>]'


if __name__ == "__main__":
    import codecs
    import locale

    locale.setlocale(locale.LC_ALL, '')

    """
    sys.stdin  = (codecs.getreader('utf8'))(sys.__stdin__)
    sys.stdout = (codecs.getwriter('utf8'))(sys.__stdout__)
    """
    sys.stderr = (codecs.getwriter(locale.getlocale()[1]))(sys.__stderr__)

    main(sys.argv[1:])






