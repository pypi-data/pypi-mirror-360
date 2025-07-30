# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

_W='functions'
_V='function'
_U='plugin'
_T='yangcore:dynamic-callout'
_S='/yangcore:dynamic-callouts/dynamic-callout='
_R='%Y-%m-%dT%H:%M:%SZ'
_Q='content'
_P='certificates'
_O='certificate'
_N='import'
_M='text/plain'
_L='contentType'
_K='Unrecognized encoding = '
_J='utf-8'
_I='implement'
_H='call-function'
_G='timestamp'
_F='conformance-type'
_E='namespace'
_D='revision'
_C='name'
_B='Accept'
_A=None
import re,json,base64,textwrap,importlib.resources as importlib_resources,xml.etree.ElementTree as ET
from urllib.parse import unquote
from xml.dom import minidom
from enum import Enum
import pem,yangson
from aiohttp import web
from pyasn1.type import tag
from pyasn1.codec.der import decoder as der_decoder
from pyasn1.codec.der import encoder as der_encoder
from pyasn1_modules import rfc5652
from pyasn1_modules import rfc5280
from yangson.xmlparser import XMLParser
from.dal import DataAccessLayer,NodeNotFound
import datetime
class RedundantQueryParameters(Exception):0
class MalformedDataPath(Exception):0
class TranscodingError(Exception):0
app_name=re.sub('\\..*','',__name__)
yl4errors={'ietf-yang-library:modules-state':{'module-set-id':'TBD - yl4errors','module':[{_C:'ietf-yang-types',_D:'2013-07-15',_E:'urn:ietf:params:xml:ns:yang:ietf-yang-types',_F:_N},{_C:'ietf-restconf',_D:'2017-01-26',_E:'urn:ietf:params:xml:ns:yang:ietf-restconf',_F:_I},{_C:'ietf-netconf-acm',_D:'2018-02-14',_E:'urn:ietf:params:xml:ns:yang:ietf-netconf-acm',_F:_N},{_C:'ietf-yang-structure-ext',_D:'2020-06-17',_E:'urn:ietf:params:xml:ns:yang:ietf-yang-structure-ext',_F:_I},{_C:'ietf-crypto-types',_D:'2024-10-10',_E:'urn:ietf:params:xml:ns:yang:ietf-crypto-types',_F:_I}]}}
path=importlib_resources.files(app_name)/'yang'
path4errors=importlib_resources.files(app_name)/'yang4errors'
dm4errors=yangson.DataModel(json.dumps(yl4errors),[path4errors,path])
def gen_rc_errors(error_type,error_tag,error_app_tag=_A,error_path=_A,error_message=_A,error_info=_A):
	E=error_info;D=error_message;C=error_path;B=error_app_tag;A={};A['error-type']=error_type;A['error-tag']=error_tag
	if B is not _A:A['error-app-tag']=B
	if C is not _A:A['error-path']=C
	if D is not _A:A['error-message']=D
	if E is not _A:A['error-info']=E
	return{'ietf-restconf:errors':{'error':[A]}}
def enc_rc_errors(encoding,errors_obj):
	B=errors_obj;A=encoding
	if A=='json':return json.dumps(B,indent=2)
	if A=='xml':C=dm4errors.from_raw(B);D=C.to_xml();E=ET.tostring(D).decode(_J);F=minidom.parseString(E);return F.toprettyxml(indent='  ')
	raise NotImplementedError(_K+A)
class Encoding(Enum):JSON=1;XML=2
def obj_to_encoded_str(obj,enc,dm,sn,strip_wrapper=False):
	B=enc
	if B==Encoding.JSON:return json.dumps(obj,indent=2)
	if B==Encoding.XML:
		C=sn.from_raw(obj);D=yangson.instance.RootNode(C,sn,dm.schema_data,C.timestamp);A=D.to_xml()
		if strip_wrapper is True:assert len(A)==1;A=A[0]
		E=ET.tostring(A).decode(_J);F=minidom.parseString(E);return F.toprettyxml(indent='  ')
	raise NotImplementedError(_K+B)
def encoded_str_to_obj(estr,enc,dm,sn):
	B=enc
	if B==Encoding.JSON:
		try:E=json.loads(estr)
		except Exception as A:raise TranscodingError('JSON malformed: '+str(A))from A
		try:C=sn.from_raw(E)
		except Exception as A:raise TranscodingError("JSON doesn't match schema: "+str(A))from A
	elif B==Encoding.XML:
		try:F=XMLParser(estr);G=F.root
		except Exception as A:raise TranscodingError('XML malformed: '+str(A))from A
		try:C=sn.from_xml(G)
		except Exception as A:raise TranscodingError("XML doesn't match schema: "+str(A))from A
	else:raise NotImplementedError(_K+B)
	try:D=yangson.instance.RootNode(C,sn,dm.schema_data,C.timestamp)
	except Exception as A:raise TranscodingError("Object doesn't match schema: "+str(A))from A
	D.validate(ctype=yangson.enumerations.ContentType.all)
	try:H=D.raw_value()
	except Exception as A:raise TranscodingError('Error transcoding: '+str(A))from A
	return H
def multipart_pem_to_der_dict(multipart_pem):
	A={};E=pem.parse(bytes(multipart_pem,_J))
	for F in E:
		C=F.as_text().splitlines();D=base64.b64decode(''.join(C[1:-1]));B=re.sub('-----BEGIN (.*)-----','\\g<1>',C[0])
		if B not in A:A[B]=[D]
		else:A[B].append(D)
	return A
def der_dict_to_multipart_pem(der_dict):
	D='-----\n';C=der_dict;A='';E=C.keys()
	for B in E:
		F=C[B]
		for G in F:H=base64.b64encode(G).decode('ASCII');A+='-----BEGIN '+B+D;A+=textwrap.fill(H,64)+'\n';A+='-----END '+B+D
	return A
def ders_to_degenerate_cms_obj(cert_ders):
	B=rfc5652.CertificateSet().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))
	for E in cert_ders:F,G=der_decoder.decode(E,asn1Spec=rfc5280.Certificate());assert not G;D=rfc5652.CertificateChoices();D[_O]=F;B[len(B)]=D
	A=rfc5652.SignedData();A['version']=1;A['digestAlgorithms']=rfc5652.DigestAlgorithmIdentifiers().clear();A['encapContentInfo']['eContentType']=rfc5652.id_data;A[_P]=B;C=rfc5652.ContentInfo();C[_L]=rfc5652.id_signedData;C[_Q]=der_encoder.encode(A);return C
def degenerate_cms_obj_to_ders(cms_obj):
	A=cms_obj
	if A[_L]!=rfc5652.id_signedData:raise KeyError('unexpected content type: '+str(A[_L]))
	D,H=der_decoder.decode(A[_Q],asn1Spec=rfc5652.SignedData());E=D[_P];B=[]
	for F in E:C=F[_O];assert isinstance(C,rfc5280.Certificate);G=der_encoder.encode(C);B.append(G)
	return B
def parse_raw_path(full_raw_path):
	P='parameter can appear at most once.';O='than once. RFC 8040, Section 4.8 states that each ';N='" appears more ';M='Query parameter "';L='?';G=full_raw_path;D='=';A='/'
	if L in G:assert G.count(L)==1;B,J=G.split(L)
	else:B=G;J=_A
	if B=='':B=A
	elif B[0]!=A:raise MalformedDataPath('The datastore-specific part of the path, '+"when present, must begin with a '/' character.")
	elif B[-1]==A:raise MalformedDataPath("Trailing '/' characters are not supported.")
	if B==A:H=A
	else:
		H='';Q=B[1:].split(A)
		for E in Q:
			if E=='':raise MalformedDataPath("The data path contains a superflous '/' character.")
			if D in E:assert E.count(D)==1;C,K=E.split(D);H+=A+unquote(C)+D+K
			else:H+=A+unquote(E)
	F={}
	if J is not _A:
		R=J.split('&')
		for I in R:
			if D in I:
				C,K=I.split(D,1)
				if C in F:raise RedundantQueryParameters(M+C+N+O+P)
				F[unquote(C)]=K
			else:
				if I in F:raise RedundantQueryParameters(M+C+N+O+P)
				F[unquote(I)]=_A
	return H,F
def format_resp_and_msg(resp,msg,err,request,supported_media_types):
	C=request;B=msg;A=resp
	if _B in C.headers and C.headers[_B]in supported_media_types:A.content_type=C.headers[_B]
	else:A.content_type=_M
	if A.content_type==_M:D=B
	else:D=gen_rc_errors('protocol',err,error_message=B)
	if A.content_type=='application/yang-data+json':A.text=enc_rc_errors('json',D)
	elif A.content_type=='application/yang-data+xml':A.text=enc_rc_errors('xml',D)
	else:A.text=B
	return A,B
def check_http_headers(request,supported_media_types,accept_required,post_body_required=False):
	L='POST';K='". Got: "';J='*/*';I='".';H='" or "';G='missing-attribute';F='bad-attribute';E='Content-Type';B=supported_media_types;A=request;assert isinstance(B,tuple)
	if A.method in('GET','HEAD','DELETE')and E in A.headers:C=web.Response(status=400);D='A "Content-Type" value must not be specified for '+A.method+' requests.';return format_resp_and_msg(C,D,F,A,B)
	if A.body_exists and E not in A.headers:C=web.Response(status=400);D='A "Content-Type" value must be specified when a request '+'body is passed. The "Content-Type" value must be '+'"application/yang-data+json" or '+'"application/yang-data+xml".';return format_resp_and_msg(C,D,G,A,B)
	if A.body_exists and A.headers[E]not in B:C=web.Response(status=400);D='The "Content-Type" value, when specified, must be "'+H.join(B)+K+A.headers[E]+I;return format_resp_and_msg(C,D,F,A,B)
	if accept_required and(_B not in A.headers or A.headers[_B]==J):C=web.Response(status=406);D='An "Accept" value is required for this HTTP request.  The "Accept" '+'must be "'+H.join(B)+I;return format_resp_and_msg(C,D,G,A,B)
	if _B in A.headers and A.headers[_B]!=J and A.headers[_B]not in B:C=web.Response(status=406);D='The "Accept" value, when specified, must be "'+H.join(B)+K+A.headers[_B]+I;return format_resp_and_msg(C,D,F,A,B)
	M=A.method in('PUT','PATCH')or A.method==L and'ietf-datastores:running'in A.path or A.method==L and post_body_required
	if M and not A.body_exists:C=web.Response(status=400);D='A request body is required for this HTTP request.';return format_resp_and_msg(C,D,G,A,B)
	if _B in A.headers and A.headers[_B]!=J:return A.headers[_B],_A
	if E in A.headers:return A.headers[E],_A
	return _M,_A
def get_client_ip_address(request,proxy_info):
	F='Forwarded';E='trusted-proxy-count';D='X-Forwarded-For';B=proxy_info;A=request
	if D in A.headers:
		G=','.join(A.headers.getall(D));H=G.split(',');C=1
		if B is not _A and E in B:C=B[E]
		I=H[-C];return I
	if F in A.headers:J=A.headers.get(F);raise NotImplementedError("The 'Forwarded' header is not supported yet.  Current val is "+str(J))
	return A.remote
async def insert_notification_log_record(nvh,notif_payload):
	G='notification';C=notif_payload;B=nvh;E=datetime.datetime.now(datetime.UTC);H=E.strftime(_R);D='/yangcore:notification-log';I={'yangcore:notification-log-record':{_G:E,G:C}};await B.dal.handle_post_opstate_request(D,I)
	try:J=await B.dal.handle_get_config_request('/yangcore:preferences/outbound-interactions/relay-notification-log-record-callout',{})
	except NodeNotFound:return
	F=J['yangcore:relay-notification-log-record-callout'];D=_S+F;A=await B.dal.handle_get_config_request(D,{});A=A[_T][0];assert F==A[_C];K=A[_H][_U];L=A[_H][_V];P=next(iter(C));M={'notification-log-record':{_G:H,G:C}};N=_A;O=await B.plugins[K][_W][L](M,N);assert O is _A
async def insert_audit_log_record(dal,plugins,audit_log_record):
	C=dal;A=audit_log_record
	if A['method']in{'GET','HEAD'}:return
	D='/yangcore:audit-log';F={'yangcore:audit-log-record':A};await C.handle_post_opstate_request(D,F)
	try:G=await C.handle_get_config_request('/yangcore:preferences/outbound-interactions/relay-audit-log-record-callout',{})
	except NodeNotFound:return
	E=G['yangcore:relay-audit-log-record-callout'];D=_S+E;B=await C.handle_get_config_request(D,{});B=B[_T][0];assert E==B[_C];H=B[_H][_U];I=B[_H][_V];A[_G]=A[_G].strftime(_R);A.pop('parent_id');J={'audit-log-record':A};K=_A;L=await plugins[H][_W][I](J,K);assert L is _A