#!/usr/bin/env python

import os,sys
SOPHIE_BASE = os.environ.get('VURVE_SOPHIE_BASE','/Users/tiago/vurve/code/sophie');
sys.path.append(SOPHIE_BASE)


from sqlalchemy import create_engine,func,and_,asc
from sqlalchemy import Column,Integer,Unicode,DateTime,ForeignKey,Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sophie.lib.connectors.vurve.db.merchant_db_orm import StoreAccount
from sophie.lib.connectors.vurve.db.pixel_db_orm import Click
from sophie.lib.bigbrother.clicksession_db_orm import  ClickSession, SessionMkg
import sophie.lib.bigbrother.clicksession_db as clickdb

from datetime import timedelta,datetime,date
import paste,pickle
import logging
import yaml
import re
import argparse

#Load the logger 
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

    

def ClicksWhichCorrespondToSessionsWithOneClick():
    sess = clickdb.get_clicksession_db_session()
    pix_sess = clickdb.get_pixel_db_session()
    qry = sess.query(ClickSession.firstclick).filter(and_(ClickSession.click_count==1,ClickSession.qualification_certainty==1)).limit(10)
    for cl in qry:
        print cl.firstclick
        cl_qry = pix_sess.query(Click).filter(Click.id==cl.firstclick).first()
        print cl_qry
        print "Ref {0} \n Time spent: {1}\n Url: {2}".format(cl_qry.ref,cl_qry.time_spent,cl_qry.url)

def AllClicksFor(vis,pubid):
    pix_sess = clickdb.get_pixel_db_session()
    qry = pix_sess.query(Click).filter(and_(Click.visitor==vis,Click.public_id==pubid)).order_by(Click.time_start)
    print "All clicks for {0} {1} ==================================".format(vis,pubid)
    for click in qry:
        print click

if __name__=="__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('-a, --action',dest='action', choices='cs')
   parser.add_argument('-l --limit', type=int, dest='limit', default=None)
   parser.add_argument('-v --visitor', dest='visitor')
   parser.add_argument('-p --publicid', dest='publicid')
   a=parser.parse_args()
   print a
