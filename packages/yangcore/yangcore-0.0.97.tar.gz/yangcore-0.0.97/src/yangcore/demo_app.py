# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

_A=None
import os,importlib.resources as importlib_resources
from yangcore import yangcore
from yangcore.yl import yangcore_native_yang_library
def yangcore_firsttime_callback():
	C='Yes';A='';B=os.environ.get('YANGCORE_ACCEPT_CONTRACT')
	if B is _A:
		print(A);D=importlib_resources.files('yangcore')/'LICENSE'
		with open(D,'r',encoding='utf-8')as E:print(E.read())
		print('First time initialization.  Please accept the license terms.');print(A);print('By entering "Yes" below, you agree to be bound to the terms and '+'conditions contained on this screen with Watsen Networks.');print(A);F=input('Please enter "Yes" or "No": ')
		if F!=C:print(A);print('Thank you for your consideration.');print(A);raise yangcore.ContractNotAccepted()
	elif B!=C:print(A);print('The "YANGCORE_ACCEPT_CONTRACT" environment variable is set to a '+'value other than "Yes".  Please correct the value and try again.');print(A);raise yangcore.UnrecognizedAcceptValue()
	return yangcore_native_yang_library()
def run(db_url,cacert_param=_A,cert_param=_A,key_param=_A):
	C='demo_app'
	try:assert __name__.rsplit('.',1)[1]==C;B=yangcore.init(yangcore_firsttime_callback,db_url,cacert_param,cert_param,key_param,C)
	except Exception as A:print('demo_app.py: yangcore.init() threw exception: '+A.__class__.__name__);print('demo_app.py: str(e) = '+str(A));raise A
	D={'yangcore:native-interface':{'create_callback':[],'delete_callback':[],'change_callback':[]}};yangcore.run(B,D);del B;return 0