# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

_A=None
import sys,os,signal,asyncio,functools
from datetime import datetime,timedelta,UTC
from yangcore.periodic import forever_loop
from.dal import DataAccessLayer,AuthenticationFailed,NodeNotFound
from.rcsvr import RestconfServer
from.native import NativeViewHandler
from.import utils
class ContractNotAccepted(Exception):0
class UnrecognizedAcceptValue(Exception):0
class UnrecognizedModeValue(Exception):0
class BadCommandLineParams(Exception):0
LOOP=_A
SIG=_A
NVH=_A
def signal_handler(name):global SIG;SIG=name;LOOP.stop()
def init(firsttime_cb_func,db_url,cacert_param=_A,cert_param=_A,key_param=_A,app_name=_A):
	F=db_url;E=app_name;C=key_param;B=cert_param;A=cacert_param;assert E is not _A
	if A is not _A and F.startswith('sqlite:'):raise BadCommandLineParams('The "sqlite" dialect does not support the "cacert" parameter.')
	if(B or C)and not A:raise BadCommandLineParams('The "cacert" parameter must be specified whenever the '+'"key" and "cert" parameters are specified.')
	if(B is _A)!=(C is _A):raise BadCommandLineParams('The "key" and "cert" parameters must be specified together.')
	if A is not _A and not os.path.exists(A):raise BadCommandLineParams('The "cacert" parameter is specified but does not exist.')
	if B is not _A and not os.path.exists(B):raise BadCommandLineParams('The "cert" parameter is specified but does not exist.')
	if C is not _A and not os.path.exists(C):raise BadCommandLineParams('The "key" parameter is specified but does not exist.')
	H=False
	try:G=DataAccessLayer(F,A,B,C,_A,_A,_A,E)
	except(SyntaxError,AssertionError,AuthenticationFailed)as D:raise D
	except NotImplementedError:H=True
	if H is True:
		try:I=firsttime_cb_func()
		except ContractNotAccepted:sys.exit(0)
		except Exception as D:raise D
		try:assert E is not _A;G=DataAccessLayer(F,A,B,C,I,_A,_A,E)
		except Exception as D:raise D
	assert G is not _A;return G
def run(dal,endpoint_settings):
	d='periodic_callback';c='somehow_change_callback';b='subtree_change_callback';a='change_callback';Z='delete_callback';Y='create_callback';X='yangcore:native-interface';W='external-endpoint';V='SIGHUP';O='http-over-tcp';J='yangcore:use-for';H=endpoint_settings;G='schema_path';E=dal;D='callback_func';global LOOP;global SIG;global NVH;LOOP=asyncio.new_event_loop();LOOP.add_signal_handler(signal.SIGHUP,functools.partial(signal_handler,name=V));LOOP.add_signal_handler(signal.SIGTERM,functools.partial(signal_handler,name='SIGTERM'));LOOP.add_signal_handler(signal.SIGINT,functools.partial(signal_handler,name='SIGINT'));LOOP.add_signal_handler(signal.SIGQUIT,functools.partial(signal_handler,name='SIGQUIT'))
	while SIG is _A:
		I=[];C=E.handle_get_config_request('/ietf-restconf-server:restconf-server',{});K=LOOP.run_until_complete(C)
		for B in K['ietf-restconf-server:restconf-server']['listen']['endpoints']['endpoint']:
			if O in B and W in B[O]:L=B[O][W]
			else:L=_A
			if B[J]=='native-interface'or B[J]==X:
				NVH=NativeViewHandler(E,LOOP,L);A=H[X]
				if Y in A:
					for P in A[Y]:NVH.register_create_callback(P[G],P[D])
				if Z in A:
					for Q in A[Z]:NVH.register_delete_callback(Q[G],Q[D])
				if a in A:
					for R in A[a]:NVH.register_change_callback(R[G],R[D])
				if b in A:
					for S in A[b]:NVH.register_subtree_change_callback(S[G],S[D])
				if c in A:
					for T in A[c]:NVH.register_somehow_change_callback(T[G],T[D])
				if d in A:
					for M in A[d]:NVH.register_periodic_callback(M['period'],M['anchor'],M[D])
				U=RestconfServer(LOOP,E,B,NVH)
			else:
				N=B[J]
				if N not in H:raise KeyError('Error: support for the configured endpoint "use-for" '+'interface "'+N+'" was not supplied in the '+'"endpoint_settings" parameter in the yangcore.run() method.')
				e=H[B[J]]['yang-library-func']();f=H[N]['view-handler'];g=f(E,e,L,NVH);U=RestconfServer(LOOP,E,B,g)
			I.append(U);del B;B=_A
		del K;K=_A;h=LOOP.create_task(forever_loop(NVH));LOOP.run_forever();h.cancel()
		for F in I:C=F.app.shutdown();LOOP.run_until_complete(C);C=F.runner.cleanup();LOOP.run_until_complete(C);C=F.app.cleanup();LOOP.run_until_complete(C);del F;F=_A
		del I;I=_A
		if SIG==V:SIG=_A
	LOOP.close()