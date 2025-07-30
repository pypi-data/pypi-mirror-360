# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

import re,os,gc,sys,asyncio,importlib
from datetime import datetime,timedelta,UTC
from yangcore.dal import NodeNotFound
from yangcore import utils
class PluginNotFound(Exception):0
class PluginSyntaxError(Exception):0
class FunctionNotFound(Exception):0
class FunctionNotCallable(Exception):0
async def forever_loop(nvh):
	while True:
		try:await test_plugin_changed(nvh)
		except Exception as A:print('Error reloading plugin! '+str(A)+' [Always test plugins before hot-loading them]')
		await test_password_aging(nvh);await asyncio.sleep(10)
async def test_plugin_changed(nvh):
	N='last-modified-time';M='plugins';L='yangcore';G='module';F='functions';B=nvh
	for A in list(B.plugins.keys()):
		O=importlib.resources.files(L)/M/(A+'.py');H=os.path.getmtime(O)
		if H>B.plugins[A][N]:
			P=re.sub('\\..*','',__name__);I=P+'.plugins.'+A
			for D in list(B.plugins[A][F].values()):del D
			del B.plugins[A][G];del sys.modules[I];J=importlib.resources.files(L)/M/'__pycache__'
			for K in os.listdir(J):
				if K.startswith(A):os.remove(os.path.join(J,K))
			try:Q=importlib.import_module(I)
			except ModuleNotFoundError as C:raise PluginNotFound(str(C))from C
			except SyntaxError as C:raise PluginSyntaxError('SyntaxError: '+str(C))from C
			B.plugins[A][G]=Q
			for E in list(B.plugins[A][F].keys()):
				try:D=getattr(B.plugins[A][G],E)
				except AttributeError as C:raise FunctionNotFound(str(C))from C
				if not callable(D):raise FunctionNotCallable("The plugin function name '"+E+"' is not callable.")
				B.plugins[A][F][E]=D
			B.plugins[A][N]=H
async def test_password_aging(nvh):
	J='password-based';I='user';H='yangcore:aging-timeout';F='authentication';E=nvh
	try:G=await E.dal.handle_get_config_request('/yangcore:preferences/authentication/internal-authenticator/passwords-allowed/aging-timeout',{})
	except NodeNotFound:return
	A=G[H]['amount'];B=G[H]['units']
	if B=='seconds':C=timedelta(seconds=A)
	elif B=='minutes':C=timedelta(minutes=A)
	elif B=='hours':C=timedelta(hours=A)
	elif B=='days':C=timedelta(days=A)
	elif B=='weeks':C=timedelta(weeks=A)
	elif B=='months':C=timedelta(weeks=A*4)
	else:assert B=='years';C=timedelta(weeks=A*52)
	K=datetime.now(UTC);L=await E.dal.handle_get_opstate_request('/yangcore:users',{})
	for D in L['yangcore:users'][I]:
		if F in D:
			if J in D[F]:
				M=D[F][J]['password-last-modified'];N=datetime.fromisoformat(M.replace('Z','+00:00'))
				if K-N<C:continue
				O={'yangcore:user-password-aging':{I:D['login']}};await utils.insert_notification_log_record(E,O)