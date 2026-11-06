import hashlib
import hmac
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import payments
import voice_access

class Payments(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.state=Path(self.tmp.name)
        self.url=payments.checkout(self.state,'reader-a','es')
        from urllib.parse import urlparse,parse_qs
        self.ref=parse_qs(urlparse(self.url).query)['client_reference_id'][0]
        self.event={'id':'evt_a','type':'checkout.session.completed','livemode':True,'data':{'object':{'id':'cs_a','client_reference_id':self.ref,'payment_link':payments.LINK_ID,'payment_status':'paid','mode':'payment','amount_total':500,'currency':'usd','payment_intent':'pi_a'}}}
    def tearDown(self):self.tmp.cleanup()
    def test_signed_payment_exactly_once_account_bound(self):
        (self.state/'stripe-webhook-secret').write_text('whsec_test_only')
        payload=json.dumps(self.event).encode();stamp=int(time.time())
        signature=hmac.new(b'whsec_test_only',str(stamp).encode()+b'.'+payload,hashlib.sha256).hexdigest()
        with self.assertRaises(Exception): payments.webhook(self.state,payload,'t=0,v1=bad')
        for _ in range(2):payments.webhook(self.state,payload,f't={stamp},v1={signature}')
        self.event['id']='evt_repeated_session';payments.process_event(self.state,self.event)
        self.assertEqual(payments.balance(self.state,'reader-a')['seconds'],1800)
        self.assertEqual(payments.balance(self.state,'reader-b')['seconds'],0)
    def test_unpaid_foreign_links_and_test_events_never_unlock(self):
        obj=self.event['data']['object'];obj['payment_status']='unpaid';payments.process_event(self.state,self.event)
        self.event['id']='evt_b';obj['payment_status']='paid';obj['payment_link']='plink_foreign';payments.process_event(self.state,self.event)
        self.event['livemode']=False
        with self.assertRaises(ValueError):payments.process_event(self.state,self.event)
        self.assertEqual(payments.balance(self.state,'reader-a')['seconds'],0)
    def test_reservation_resume_and_duplicate_termination(self):
        with self.assertRaises(PermissionError):payments.reserve(self.state,'reader-a')
        payments.process_event(self.state,self.event)
        with patch('payments.time.time',return_value=100):
            call,seconds=payments.reserve(self.state,'reader-a');payments.activate(self.state,call,'rtc_test',seconds)
        with self.assertRaises(ValueError):payments.reserve(self.state,'reader-a')
        with self.assertRaises(PermissionError):payments.get_call(self.state,call,'reader-b')
        with patch('payments.time.time',return_value=160):
            payments.finish(self.state,call,'ended');payments.finish(self.state,call,'ended')
        self.assertEqual(payments.balance(self.state,'reader-a')['seconds'],1740)
        self.assertEqual(payments.reserve(self.state,'reader-a')[1],1740)
    def test_refund_before_payment_and_duplicate_usage(self):
        payments.process_event(self.state,{'id':'evt_refund','type':'charge.refunded','livemode':True,'data':{'object':{'payment_intent':'pi_a'}}})
        payments.process_event(self.state,self.event)
        self.assertEqual(payments.balance(self.state,'reader-a')['seconds'],0)
    def test_cost_and_time_limits_are_server_side(self):
        payments.process_event(self.state,self.event);call,seconds=payments.reserve(self.state,'reader-a');payments.activate(self.state,call,'rtc_test',seconds)
        for _ in range(2):payments.record_usage(self.state,call,'response1','response',{},4.0)
        c=payments.get_call(self.state,call);self.assertEqual(c['cost'],4.0)
        self.assertEqual(voice_access.should_close(c,time.time()),'budget')
        c['cost']=0;self.assertEqual(voice_access.should_close(c,c['deadline']+1),'time')
        c['deadline']=time.time()+1000;c['heartbeat']=time.time()-61
        self.assertEqual(voice_access.should_close(c,time.time()),'disconnected')
        c['revoked']=1;self.assertEqual(voice_access.should_close(c,time.time()),'refunded')
    def test_hangup_failure_keeps_lease_and_credit_reserved(self):
        payments.process_event(self.state,self.event);call,seconds=payments.reserve(self.state,'reader-a');payments.activate(self.state,call,'rtc_test',seconds)
        with patch('voice_access.provider_request',side_effect=OSError('offline')):
            self.assertFalse(voice_access.close(self.state,call))
        self.assertEqual(payments.get_call(self.state,call)['status'],'closing')
        with self.assertRaises(ValueError):payments.reserve(self.state,'reader-a')
