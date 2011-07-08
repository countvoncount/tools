#!/usr/bin/env python


import sys
import csv
#import datetime
#import itertools
#from urlparse import urlparse, parse_qs

#from urlparse import urlparse, parse_qs
from collections import namedtuple

"""
"""

def main(argv):
    if argv:
        print >>sys.stderr, '*** Error: uses stdin for input'
        sys.exit(1)

    rows = gen_csvrows(sys.__stdin__)
    rows = limit_visitors(rows, max_duration=3600, min_clicks=5)
    #rows = limit_visitors(rows, min_clicks=5)
    rows = add_stats(rows)
    #consume_rows(rows, sys.__stdout__)

    keywords = list()
    for row in rows:
        sale = ' ' if row.revenue == 0 else 'V' if row.mkgsrc=='Vurve' else 'n'
        median = row.data['median_tos']
        avg = row.data['avg_tos']

        action = ''
        if avg < 15:
            action = "PAUSE"
            if row.quality > 6:
                action += '+'

        keywords.append((avg, median, len(row.vtos), sale, action, row.quality, row.keyword))

    keywords.sort()

    fmt = '%10.3f %6d %4d %1s %-10s %4.1f %s'
    prev = 0
    for k in keywords:
        curr = k[0]
        marker(curr, prev, 10)
        marker(curr, prev, 15)
        marker(curr, prev, 20)
        prev = curr
        print fmt%k



def gen_csvrows(csvfile):
    "Generate named tuples from rows csv file."
    csvr = csv.reader(csvfile)

    Row = namedtuple('Row', csvr.next()+['data',])
    for fields in csvr:
        fields.append(dict())
        row = Row(*fields)

        yield row._replace(
            keyword=row.keyword.decode('utf8'),
            revenue=float(row.revenue),
            n_orders=int(row.n_orders),
            kw_cost=float(row.kw_cost),
            quality=float(row.quality),
            vtos=tuple(sorted(eval(row.vtos))),
        )


def consume_rows(rows, csvfile, headers=True):
    "Consumes named tuple 'rows' and generates a csv file."
    csvw = csv.writer(csvfile)

    def _row(row, fields):
        "Return list of values from row in order given by fields."
        def str2utf(o):
            if isinstance(o, basestring):
                return o.encode('utf8')
            return o
        d = row._asdict()
        return [str2utf(d[f]) for f in fields]

    try:
        row = rows.next()
        fields = row._fields[:-1]
        if headers:
            csvw.writerow(fields)
        csvw.writerow(_row(row, fields))
        for row in rows:
            csvw.writerow(_row(row, fields))
    except StopIteration:
        pass


def limit_visitors(stream, min_clicks=0, max_duration=sys.maxint):
    for row in stream:
        row = row._replace(
            vtos=tuple(t if t < max_duration else max_duration for t in row.vtos)
        )
        if len(row.vtos) < min_clicks:
            continue
        yield row


def add_stats(stream, ignore_over=sys.maxint):
    """
    Add 'avg_tos' and 'median_tos' to data.
    """
    for row in stream:
        vis = [t for t in row.vtos if t < ignore_over]
        nvis = len(vis)
        if nvis > 0:
            # avg
            avg = sum(vis)/float(nvis)

            # median
            half,rem = divmod(nvis, 2)
            median = (vis[half-1+rem]+vis[half])/2
        else:
            avg = None
            median = None

        row.data['avg_tos'] = avg
        row.data['median_tos'] = median

        yield row


# Output helpers
def marker(curr, prev, threshold):
    if prev < threshold and curr >= threshold:
        print '-'*5, threshold, '-'*30


if __name__ == "__main__":
    """
    import codecs
    import locale

    locale.setlocale(locale.LC_ALL, '')

    sys.stdin  = (codecs.getreader('utf8'))(sys.__stdin__)
    sys.stdout = (codecs.getwriter('utf8'))(sys.__stdout__)
    sys.stderr = (codecs.getwriter(locale.getlocale()[1]))(sys.__stderr__)
    """

    main(sys.argv[1:])

