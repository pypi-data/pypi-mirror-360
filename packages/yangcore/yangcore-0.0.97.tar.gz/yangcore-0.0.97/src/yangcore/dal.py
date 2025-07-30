# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

_A2='config-true-seq-nodes'
_A1='config-false-prefixes'
_A0='table-name-map'
_z='table-keys'
_y='yangcore_meta'
_x='SELECT schema_name FROM information_schema.schemata;'
_w='sslkey'
_v='sslcert'
_u='sslrootcert'
_t='verify-ca'
_s='sslmode'
_r='Cannot delete: '
_q='[^/]*=[^/]*'
_p='[^:]*:'
_o='demo_app'
_n='yangcore'
_m='global-root'
_l='db_ver'
_k='sqlite'
_j=':memory:'
_i='key'
_h='first'
_g='" already exists.'
_f='Node "'
_e='Parent node ('
_d='datastore_id'
_c='tenant_id'
_b='yang'
_a='.singletons'
_Z='postgresql'
_Y='sort-by'
_X='.*/'
_W='last'
_V=') does not exist.'
_U='mysql'
_T='_idx'
_S='_key'
_R='after'
_Q='before'
_P='insert'
_O='record_id'
_N='point'
_M='ssl'
_L=':'
_K='jsob'
_J='obu_idx'
_I='name'
_H='parent_id'
_G='singletons'
_F='=[^/]*'
_E=True
_D='='
_C=False
_B='/'
_A=None
import os,re,json,enum,datetime
from enum import IntFlag
from dataclasses import dataclass
import importlib.resources as importlib_resources
from urllib.parse import unquote
import yangson,sqlalchemy as sa
from sqlalchemy import Enum
from sqlalchemy.sql import and_
from sqlalchemy.sql import bindparam
from yangcore.yl import yl_8525_to_7895
from.import db_utils
JsobType=sa.JSON
class ContentType(IntFlag):CONFIG_TRUE=1;CONFIG_FALSE=2;CONFIG_ANY=3
@dataclass
class DatabasePath:data_path:str=_A;schema_path:str=_A;jsob_data_path:str=_A;jsob_schema_path:str=_A;table_name:str=_A;record_id:int=_A;inside_path:str=_A;path_segments:list=_A;jsob:dict=_A;node_ptr:dict=_A;prev_ptr:dict=_A
class AuthenticationFailed(Exception):0
class NodeAlreadyExists(Exception):0
class NodeNotFound(Exception):0
class ParentNodeNotFound(Exception):0
class TooManyNodesFound(Exception):0
class InvalidResourceTarget(Exception):0
class CreateCallbackFailed(Exception):0
class ChangeCallbackFailed(Exception):0
class CreateOrChangeCallbackFailed(Exception):0
class DeleteCallbackFailed(Exception):0
class DataAccessLayer:
	def __init__(A,db_url,cacert_param=_A,cert_param=_A,key_param=_A,yl_obj=_A,app_ns=_A,opaque=_A,app_name=_A):
		I='YANGCORE_TEST_PATH';H=yl_obj;G=key_param;F=cert_param;E=cacert_param;D=db_url;B=app_name;assert app_ns is _A;assert opaque is _A;A.engine=_A;A.metadata=_A;A.leafrefs=_A;A.referers=_A;A.ref_stat_collectors=_A;A.global_root_id=_A;A.table_keys=_A;A.schema_path_to_real_table_name=_A;A.config_false_prefixes=_A;A.post_dal_callbacks=_A;A.config_true_obu_seq_nodes=_A;A.module_paths=_A;C=importlib_resources.files(_n)/_b
		if os.environ.get(I):A.module_paths=[os.environ.get(I),C]
		else:
			assert B is not _A;A.app_name=B
			if B==_o:A.module_paths=[C]
			else:J=importlib_resources.files(B)/_b;A.module_paths=[C,J]
		if H is not _A:A._create_new_db(D,H,E,F,G)
		else:A._init_from_existing_db(D,E,F,G)
		assert not hasattr(A,'app_ns');assert not hasattr(A,'opaque');assert A.engine is not _A;assert A.metadata is not _A;assert A.leafrefs is not _A;assert A.referers is not _A;assert A.ref_stat_collectors is not _A;assert A.global_root_id is not _A;assert A.table_keys is not _A;assert A.schema_path_to_real_table_name is not _A;assert A.config_false_prefixes is not _A;assert A.config_true_obu_seq_nodes is not _A
	async def num_elements_in_list(A,data_path):
		B=data_path;C=re.sub(_F,'',B)
		if C!=B:assert NotImplementedError("Nested listed arren't supported yet.")
		D=A.schema_path_to_real_table_name[C];E=A.metadata.tables[D]
		with A.engine.connect()as F:G=F.execute(sa.select(sa.func.count()).select_from(E));H=G.first()[0];return H
	async def handle_get_opstate_request(B,data_path,query_dict):A=data_path;assert A!='';assert not(A!=_B and A[-1]==_B);C=re.sub(_F,'',A);return await B._handle_get_data_request(A,C,ContentType.CONFIG_ANY,query_dict)
	async def handle_get_config_request(D,data_path,query_dict):
		E=data_path;A=re.sub(_F,'',E);F=await D._handle_get_data_request(E,A,ContentType.CONFIG_TRUE,query_dict);B=re.sub(_X,'',A)
		if B!=''and _L not in B:I=re.sub(':.*','',A)[1:];B=I+_L+B
		for C in D.config_false_prefixes:
			if C.startswith(A):
				def G(prev_ptr,curr_ptr,remainder_path):
					D=prev_ptr;B=remainder_path;A=curr_ptr;E=B.split(_B)
					for C in E:
						if isinstance(A,list):
							for F in A:G(A,F,B)
							return
						if C not in A:return
						D=A;A=A[C];B=B.replace(C+_B,'',1)
					D.pop(C)
				J=_A;K=F
				if A==_B:H=C[1:]
				else:H=C.replace(A,B,1)
				G(J,K,H)
		return F
	async def _handle_get_data_request(E,data_path,schema_path,content_type,query_dict):
		P='Node (';I=content_type;G=data_path;F=schema_path
		if I is ContentType.CONFIG_TRUE and any(F.startswith(A)for A in E.config_false_prefixes):raise NodeNotFound(P+G+_V)
		with E.engine.connect()as K:
			A=E._get_dbpath_for_data_path(G,I,K)
			if A is _A:raise NodeNotFound(P+G+_V)
			if G!=_B and A.schema_path in E.schema_path_to_real_table_name:
				M,Q=G.rsplit(_B,1)
				if _D not in Q:
					if M=='':J=_B
					else:J=re.sub(_F,'',M)
					D={};await E._recursively_attempt_to_get_data_from_subtable(A.schema_path,A.record_id,J,A.jsob_data_path,D,I,query_dict,K)
					def N(schema_path):
						B=schema_path.split(_B)
						for A in reversed(B[1:]):
							if _L in A:return A.split(_L)[0]
						raise NotImplementedError('this line should never be reached')
					if D:
						C=next(iter(D))
						if _L not in C:L=N(J);D[L+_L+C]=D[C];D.pop(C)
					else:
						C=F.rsplit(_B,1)[1]
						if _L not in C:L=N(J);C=L+_L+C
						D[C]=[]
					return D
			B=re.sub(_X,'',F);R=B
			if B=='':H=A.node_ptr
			else:
				assert B!=''
				if _L not in B:S=re.sub(':.*','',F)[1:];B=S+_L+B
				H={}
				if A.table_name!=_G and R==A.inside_path:H[B]=[];H[B].append(A.node_ptr);A.node_ptr=H[B][0]
				else:H[B]=A.node_ptr
			T=E._get_list_of_direct_subtables_for_schema_path(F)
			for O in T:U=G+O[len(F):];await E._recursively_attempt_to_get_data_from_subtable(O,A.record_id,F,U,A.node_ptr,I,{},K)
		return H
	async def _recursively_attempt_to_get_data_from_subtable(F,subtable_name,parent_id,jsob_schema_path,jsob_data_path,jsob_iter,content_type,query_dict,conn):
		N=jsob_schema_path;J=query_dict;I=content_type;C=subtable_name
		if not ContentType.CONFIG_FALSE in I:
			if any(C.startswith(A)for A in F.config_false_prefixes):return
		if C in F.config_true_obu_seq_nodes:assert _Y not in J;J[_Y]=_J
		S=F._find_rows_in_table_having_parent_id(C,parent_id,J,conn);K=S.fetchall()
		if len(K)==0:return
		B=jsob_iter
		if N==_B:O=C[1:]
		else:O=C.replace(N+_B,'')
		D=re.sub(_X,'',C);H=re.sub(D+'$','',O)
		if H!='':
			H=H[:-1];T=H.split(_B)
			for L in T:
				try:B=B[L]
				except KeyError:assert ContentType.CONFIG_FALSE in I;B[L]={};B=B[L]
		U=F.schema_path_to_real_table_name[C];P=F.metadata.tables[U]
		if any(C.startswith(A)for A in F.config_false_prefixes):
			B[D]=[]
			for E in K:
				G={}
				for A in P.c:
					if A.name not in(_O,_H,_c,_d):
						if isinstance(A.type,sa.sql.sqltypes.DateTime):
							if re.match('^.*[-+][0-9]{2}:[0-9]{2}$',str(E[A.name])):G[A.name]=E[A.name].astimezone(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
							else:G[A.name]=E[A.name].strftime('%Y-%m-%dT%H:%M:%SZ')
						elif isinstance(A.type,(sa.sql.sqltypes.JSON,sa.sql.sqltypes.PickleType)):
							if E[A.name]is not _A and not(isinstance(E[A.name],list)and len(E[A.name])==0):G[A.name]=E[A.name]
						elif E[A.name]is not _A:G[A.name]=E[A.name]
				B[D].append(G)
		else:
			Q=0
			for M in K:
				R=M[_K];D=next(iter(R))
				if D not in B:B[D]=[]
				B[D].append(R.pop(D));V=F._get_list_of_direct_subtables_for_schema_path(C)
				for W in V:await F._recursively_attempt_to_get_data_from_subtable(W,M[_O],C,jsob_data_path+_D+M[P.c[4].name],B[D][Q],I,{},conn)
				Q+=1
	async def handle_post_config_request(A,data_path,query_dict,request_body,create_callbacks,change_callbacks,opaque):
		E=request_body;B=data_path;assert B!='';assert not(B!=_B and B[-1]==_B);assert'?'not in B;assert isinstance(E,dict)
		with A.engine.begin()as C:
			F=A._get_dbpath_for_data_path(B,ContentType.CONFIG_TRUE,C)
			if F is _A:raise ParentNodeNotFound(_e+B+_V)
			await A._handle_post_config_request(F,query_dict,E,create_callbacks,change_callbacks,opaque,C)
			if A.post_dal_callbacks is not _A:
				assert isinstance(A.post_dal_callbacks,list)
				for D in A.post_dal_callbacks:
					try:await D[0](D[1],C,D[2])
					except Exception as G:A.post_dal_callbacks=_A;raise G
				A.post_dal_callbacks=_A
	async def _handle_post_config_request(B,parent_dbpath,query_dict,request_body,create_callbacks,change_callbacks,opaque,conn):
		a=change_callbacks;V=opaque;U=create_callbacks;L=conn;J=query_dict;F=request_body;A=parent_dbpath;O=A.data_path;b=re.sub(_F,'',O);E=next(iter(F))
		if O==_B:C=E;K=_B+C
		else:C=re.sub(_p,'',E);K=O+_B+C
		M=re.sub(_F,'',K);H=B._get_table_name_for_schema_path(M);assert H is not _A
		if H==A.table_name:
			if C in A.node_ptr:
				if not isinstance(A.node_ptr[C],list):raise NodeAlreadyExists(_f+C+_g)
				assert len(F[E])==1
				if F[E][0]in A.node_ptr[C]:raise NodeAlreadyExists(_f+F[E][0]+_g)
				if M not in B.config_true_obu_seq_nodes:A.node_ptr[C].append(F[E][0])
				else:
					G=_W
					if _P in J:G=J[_P]
					if G==_h:assert _N not in J;A.node_ptr[C].insert(0,F[E][0])
					elif G==_W:assert _N not in J;A.node_ptr[C].append(F[E][0])
					else:
						assert G in(_Q,_R);assert _N in J;P=J[_N].rsplit(_D,1)[1];P=unquote(P);D=A.node_ptr[C].index(P)
						if G==_Q:0
						elif G==_R:D=D+1
						A.node_ptr[C].insert(D,F[E][0])
				if M in U:
					for Y in U[M]:await Y(K+_D+F[E][0],A.jsob,A.jsob_data_path,V)
			else:A.node_ptr[C]=F.pop(E);c=await B._recursively_post_subtable_data(A.record_id,K,A.node_ptr[C],A.jsob,A.jsob_data_path,U,V,L)
			B._update_jsob_for_record_id_in_table(A.table_name,A.record_id,A.jsob,L)
		else:
			assert M in B.table_keys
			if C not in A.node_ptr:A.node_ptr[C]=[];B._update_jsob_for_record_id_in_table(A.table_name,A.record_id,A.jsob,L)
			Q=F[E][0][B.table_keys[H]];d=K;K+=_D+str(Q)
			if M in B.config_true_obu_seq_nodes:I=B._get_obu_idx_list_for_list_path(d,L)
			W={};assert len(F[E])==1;W[C]=F[E][0];R={};R[_H]=A.record_id;R[B.table_keys[H]]=Q
			if M in B.config_true_obu_seq_nodes:R[_J]=-1
			R[_K]={};S=B.schema_path_to_real_table_name[H];N=B.metadata.tables[S]
			try:Z=L.execute(N.insert().values(**R))
			except sa.exc.IntegrityError as e:raise NodeAlreadyExists('Node already exists: '+K)from e
			c=await B._recursively_post_subtable_data(Z.inserted_primary_key[0],K,W[C],W,K,U,V,L);S=B.schema_path_to_real_table_name[H];N=B.metadata.tables[S];L.execute(N.update().where(N.c.record_id==Z.inserted_primary_key[0]).values(jsob=W))
			if M in B.config_true_obu_seq_nodes:
				G=_W
				if _P in J:G=J[_P]
				if G==_h:D=0;T=[(B.table_keys[H],Q),(_J,D)];I.insert(0,T)
				elif G==_W:D=len(I);T=[(B.table_keys[H],Q),(_J,D)];I.append(T)
				else:
					assert G in(_Q,_R);P=J[_N].rsplit(_D,1)[1];D=0
					for X in I:
						if X[0][1]==P:break
						D+=1
					if G==_Q:0
					elif G==_R:D=D+1
					T=[(B.table_keys[H],Q),(_J,D)];I.insert(D,T)
				for X in range(D+1,len(I)):I[X][1]=_J,I[X][1][1]+1
				S=B.schema_path_to_real_table_name[H];N=B.metadata.tables[S];f=B.table_keys[H];g=N.update().where(and_(N.c.parent_id==A.record_id,getattr(N.c,f)==bindparam(_S))).values(obu_idx=bindparam(_T));Z=L.execute(g,[{_S:A[0][1],_T:A[1][1]}for A in I[D:len(I)]])
			else:0
		h=re.sub(_F,'',O)
		if h in a:
			for Y in a[b]:await Y(O,A.jsob,A.jsob_data_path,V)
	async def _recursively_post_subtable_data(C,parent_id,data_path,req_body_iter,jsob,jsob_data_path,create_callbacks,opaque,conn):
		P=parent_id;M=jsob_data_path;L=jsob;I=conn;H=opaque;E=create_callbacks;D=data_path;A=req_body_iter;B=re.sub(_F,'',D)
		if isinstance(A,dict):
			if B in E:
				for Q in E[B]:await Q(D,L,M,H)
			for N in A.copy():
				assert D!=_B
				if _L in N:F=D+_B+re.sub('.*:','',N)
				else:F=D+_B+N
				R=await C._recursively_post_subtable_data(P,F,A[N],L,M,E,H,I)
		elif isinstance(A,list):
			if B in C.table_keys:
				if B in C.config_true_obu_seq_nodes:S=0
				while A:
					J=A.pop(0);assert isinstance(J,dict);V=re.sub(_X,'',B);O={};O[V]=J;K=C.table_keys[B];G={};G[_H]=P;G[K]=J[K]
					if B in C.config_true_obu_seq_nodes:G[_J]=S;S+=1
					G[_K]=O;W=C.schema_path_to_real_table_name[B];X=C.metadata.tables[W]
					try:T=I.execute(X.insert().values(**G))
					except sa.exc.IntegrityError as Y:raise NodeAlreadyExists(_f+K+'" with value "'+G[K]+_g)from Y
					F=D+_D+str(J[K]);R=await C._recursively_post_subtable_data(T.inserted_primary_key[0],F,J,O,F,E,H,I);C._update_jsob_for_record_id_in_table(B,T.inserted_primary_key[0],O,I)
				assert isinstance(A,list);assert len(A)==0
			else:
				assert isinstance(A,list)
				if not(len(A)==1 and A[0]is _A):
					for U in A:F=D+_D+str(U);R=await C._recursively_post_subtable_data(P,F,A[A.index(U)],L,M,E,H,I)
				else:0
		elif B in E:
			for Q in E[B]:await Q(D,L,M,H)
		if B in C.table_keys:return _E
		return _C
	async def handle_post_opstate_request(A,data_path,request_body):
		M='Unrecognized resource schema path: ';I=request_body;E=data_path;B=re.sub(_F,'',E);F=next(iter(I))
		if B==_B:G=F;C=_B+G
		else:G=re.sub(_p,'',F);C=B+_B+G
		J=A._get_table_name_for_schema_path(C)
		if J!=C:raise NodeNotFound(M+C)
		D=I[F];K=re.findall(_q,E)
		if len(K)==0:D[_H]=A.global_root_id
		else:
			L=A._get_table_name_for_schema_path(B)
			if L is _A:raise ParentNodeNotFound(M+B)
			N=K[-1].split(_D)
			with A.engine.connect()as H:D[_H]=A._get_record_id_for_key_in_table(L,N[1],H)
			if D[_H]is _A:raise ParentNodeNotFound('Nonexistent parent resource: '+E)
		O=A.schema_path_to_real_table_name[J];P=A.metadata.tables[O]
		with A.engine.begin()as H:H.execute(P.insert().values(**D))
	async def handle_put_config_request(A,data_path,query_dict,request_body,create_callbacks,change_callbacks,delete_callbacks,opaque=_A):
		B=data_path;assert B!='';assert not(B!=_B and B[-1]==_B)
		with A.engine.begin()as D:
			E=await A._handle_put_config_request(B,query_dict,request_body,create_callbacks,change_callbacks,delete_callbacks,opaque,D)
			if A.post_dal_callbacks is not _A:
				for C in A.post_dal_callbacks:
					try:await C[0](C[1],D,C[2])
					except Exception as F:A.post_dal_callbacks=_A;raise F
				A.post_dal_callbacks=_A
			return E
	async def _handle_put_config_request(B,data_path,query_dict,request_body,create_callbacks,change_callbacks,delete_callbacks,opaque,conn):
		U=delete_callbacks;R=create_callbacks;P=opaque;L=change_callbacks;H=data_path;F=query_dict;D=request_body;C=conn;K=re.sub(_F,'',H);assert isinstance(D,dict)
		if H==_B:A=B._get_dbpath_for_data_path(_B,ContentType.CONFIG_ANY,C);assert A is not _A;await B.recursive_compare_and_put(A.record_id,_B,D,A.node_ptr,_A,A,R,L,U,P,C);M=B.schema_path_to_real_table_name[A.table_name];I=B.metadata.tables[M];C.execute(I.update().where(I.c.record_id==A.record_id).values(jsob=A.jsob));return _C
		assert len(D)==1;assert K!=_B;A=B._get_dbpath_for_data_path(H,ContentType.CONFIG_ANY,C)
		if A is _A:
			assert H!=_B;G,X=H.rsplit(_B,1)
			if G=='':G=_B
			A=B._get_dbpath_for_data_path(G,ContentType.CONFIG_TRUE,C)
			if A is _A:raise ParentNodeNotFound(_e+G+_V)
			await B._handle_post_config_request(A,F,D,R,L,P,C);B._update_jsob_for_record_id_in_table(A.table_name,A.record_id,A.jsob,C);return _E
		Y=next(iter(D));D=D[Y]
		if isinstance(D,list):assert len(D)==1;D=D[0]
		await B.recursive_compare_and_put(A.record_id,H,D,A.node_ptr,A.prev_ptr,A,R,L,U,P,C)
		if K in B.config_true_obu_seq_nodes and F is not _A and _P in F:
			if isinstance(A.prev_ptr,list):A.prev_ptr.remove(A.node_ptr)
			else:assert isinstance(A.prev_ptr,dict);Z,Q=H.rsplit(_D,1);J=B._get_obu_idx_list_for_list_path(Z,C);J=[A for A in J if A[0][1]!=Q]
			N=F[_P]
			if N==_h:
				assert _N not in F
				if isinstance(A.prev_ptr,list):A.prev_ptr.insert(0,A.node_ptr)
				else:E=0;O=[(B.table_keys[K],Q),(_J,E)];J.insert(0,O)
			elif N==_W:
				assert _N not in F
				if isinstance(A.prev_ptr,list):A.prev_ptr.append(A.node_ptr)
				else:E=len(J);O=[(B.table_keys[K],Q),(_J,E)];J.append(O)
			else:
				assert N in(_Q,_R);assert _N in F;V=unquote(F[_N].rsplit(_D,1)[1])
				if isinstance(A.prev_ptr,list):E=A.prev_ptr.index(V)
				else:
					E=0
					for S in J:
						if S[0][1]==V:break
						E+=1
				if N==_Q:0
				elif N==_R:E=E+1
				if isinstance(A.prev_ptr,list):A.prev_ptr.insert(E,A.node_ptr)
				else:O=[(B.table_keys[K],Q),(_J,E)];J.insert(E,O)
			if not isinstance(A.prev_ptr,list):
				for(S,a)in enumerate(J):a[1]=_J,S
				M=B.schema_path_to_real_table_name[K];I=B.metadata.tables[M];b=B.table_keys[K];c=B._get_row_data_for_list_path(H,C);d=I.update().where(and_(I.c.parent_id==c[_H],getattr(I.c,b)==bindparam(_S))).values(obu_idx=bindparam(_T));C.execute(d,[{_S:A[0][1],_T:A[1][1]}for A in J])
		M=B.schema_path_to_real_table_name[A.table_name];I=B.metadata.tables[M];C.execute(I.update().where(I.c.record_id==A.record_id).values(jsob=A.jsob))
		if K in B.config_true_obu_seq_nodes and F is not _A and _P in F:
			G,X=H.rsplit(_B,1)
			if G=='':G=_B
			W=re.sub(_F,'',G)
			if W in L:
				T=B._get_dbpath_for_data_path(G,ContentType.CONFIG_TRUE,C);assert T is not _A
				for e in L[W]:await e(G,T.jsob,T.jsob_data_path,P)
		return _C
	async def recursive_compare_and_put(B,parent_id,data_path,req_body_iter,dbpath_curr_ptr,dbpath_prev_ptr,dbpath,create_callbacks,change_callbacks,delete_callbacks,opaque,conn):
		Y=dbpath_prev_ptr;Q=parent_id;O=delete_callbacks;N=change_callbacks;M=create_callbacks;J=opaque;I=conn;H=dbpath;G=dbpath_curr_ptr;E=req_body_iter;C=data_path;D=re.sub(_F,'',C)
		if isinstance(E,dict):
			S=set(list(E.keys()));T=set(list(G.keys()))
			for A in[A for A in S if A not in T]:
				if isinstance(E[A],list):
					W=_B+A if C==_B else C+_B+A;U=re.sub(_F,'',W)
					if U in B.table_keys:await B.recursive_compare_and_put(Q,W,E[A],[],_A,H,M,N,O,J,I);G[A]=[]
					else:G[A]=[];await B.recursive_compare_and_put(Q,W,E[A],G[A],G,H,M,N,O,J,I)
				else:D=re.sub(_F,'',C);U=_B+A if D==_B else D+_B+A;assert not isinstance(E,list);F=_B+A if C==_B else C+_B+A;G[A]=E[A];d=await B._recursively_post_subtable_data(Q,F,E[A],H.jsob,H.jsob_data_path,M,J,I);assert d is _C
			for A in T-S:
				U=_B+A if D==_B else D+_B+A
				if U in B.config_false_prefixes:0
				else:F=_B+A if C==_B else C+_B+A;await B._recursively_delete_subtable_data(H.record_id,F,G[A],O,J,I);del G[A]
			Z=_C
			for A in T&S:
				F=_B+A if C==_B else C+_B+A;U=re.sub(_F,'',F);e=await B.recursive_compare_and_put(Q,F,E[A],G[A],G,H,M,N,O,J,I)
				if e is _E:Z=_E
			if T-S or(S-T or Z is _E):
				if D in N:
					for R in N[D]:await R(C,H.jsob,H.jsob_data_path,J)
			return _C
		if isinstance(E,list):
			if D in B.table_keys:
				V=[A[B.table_keys[D]]for A in E];L=set(V);K={A[0]for A in B._get_keys_in_table_having_parent_id(D,Q,I)}
				for A in[A for A in V if A not in K]:assert C!=_B;F=C+_D+A;f=[C for C in E if C[B.table_keys[D]]==A][0];g=[f];h=await B._recursively_post_subtable_data(Q,C,g,_A,_A,M,J,I)
				for A in K-L:F=C+_D+A;h,a=C.rsplit(_B,1);assert a!='';await B._recursively_delete_subtable_data(H.record_id,F,Y[a],O,J,I)
				for A in K&L:F=C+_D+A;P=B._get_dbpath_for_data_path(F,ContentType.CONFIG_TRUE,I);assert P is not _A;i=[C for C in E if C[B.table_keys[D]]==A][0];await B.recursive_compare_and_put(P.record_id,F,i,P.node_ptr,P.prev_ptr,P,M,N,O,J,I);B._update_jsob_for_record_id_in_table(P.table_name,P.record_id,P.jsob,I)
				b=_C
				if D in B.config_true_obu_seq_nodes:
					j=B._get_obu_idx_list_for_list_path(C,I);c=[[(_i,A),(_J,V.index(A))]for A in V]
					if c!=j:k=B.schema_path_to_real_table_name[D];X=B.metadata.tables[k];l=B.table_keys[D];m=X.update().where(and_(X.c.parent_id==Q,getattr(X.c,l)==bindparam(_S))).values(obu_idx=bindparam(_T));I.execute(m,[{_S:A[0][1],_T:A[1][1]}for A in c]);b=_E
				n=L-K;o=K-L
				if n or o or b:return _E
				return _C
			L=set(E);K=set(G);G.clear();G.extend(E)
			for A in L-K:
				F=C+_D+unquote(A)
				if D in M:
					for R in M[D]:await R(F,H.jsob,H.jsob_data_path,J)
			for A in K-L:
				F=C+_D+unquote(A)
				if D in O:
					for R in O[D]:await R(F,J)
			if L-K or K-L:return _E
			return _C
		if G!=E:
			p=re.sub('^.*/','',C);Y[p]=E
			if D in N:
				for R in N[D]:await R(C,H.jsob,H.jsob_data_path,J)
		return _C
	async def handle_put_opstate_request(D,data_path,request_body):
		B=data_path;assert B!='';assert not(B!=_B and B[-1]==_B)
		with D.engine.begin()as E:
			C,F=B.rsplit(_B,1);assert F!=''
			if C=='':C=_B
			A=D._get_dbpath_for_data_path(C,ContentType.CONFIG_ANY,E)
			if A is _A:raise ParentNodeNotFound(_e+C+_V)
			A.node_ptr[F]=request_body;D._update_jsob_for_record_id_in_table(A.table_name,A.record_id,A.jsob,E)
	async def handle_delete_config_request(A,data_path,delete_callbacks,change_callbacks,opaque):
		B=data_path;assert B!='';assert B!=_B;assert B[-1]!=_B
		with A.engine.begin()as D:
			await A._handle_delete_config_request(B,delete_callbacks,change_callbacks,opaque,D)
			if A.post_dal_callbacks is not _A:
				for C in A.post_dal_callbacks:
					try:await C[0](C[1],D,C[2])
					except Exception as E:A.post_dal_callbacks=_A;raise E
				A.post_dal_callbacks=_A
	async def _handle_delete_config_request(C,data_path,delete_callbacks,change_callbacks,opaque,conn):
		I=opaque;H=change_callbacks;F=conn;D=data_path;E,G=D.rsplit(_B,1)
		if E=='':E=_B
		A=C._get_dbpath_for_data_path(E,ContentType.CONFIG_TRUE,F)
		if A is _A:raise NodeNotFound(_r+D)
		if _D in G:B,O=G.rsplit(_D,1)
		else:B=G
		assert isinstance(A.node_ptr,dict)
		if B not in A.node_ptr:raise NodeNotFound('Cannot delete '+D+'.')
		await C._recursively_delete_subtable_data(A.record_id,D,A.node_ptr[B],delete_callbacks,I,F)
		if isinstance(A.node_ptr[B],list):
			J=re.sub(_F,'',D)
			if J in C.table_keys:
				L=C._find_rowids_in_table_having_parent_id(J,A.record_id,F);M=L.fetchall()
				if len(M)==0:assert isinstance(A.node_ptr[B],list);assert len(A.node_ptr[B])==0;A.node_ptr.pop(B)
			elif len(A.node_ptr[B])==0:A.node_ptr.pop(B)
		else:A.node_ptr.pop(B)
		C._update_jsob_for_record_id_in_table(A.table_name,A.record_id,A.jsob,F);K=re.sub(_F,'',E)
		if K in H:
			for N in H[K]:await N(E,A.jsob,A.jsob_data_path,I)
	async def _recursively_delete_subtable_data(A,parent_id,data_path,curr_data_iter,delete_callbacks,opaque,conn):
		J=parent_id;I=opaque;F=conn;E=delete_callbacks;C=data_path;B=curr_data_iter;G=re.sub(_F,'',C)
		if isinstance(B,list):
			if G in A.table_keys:
				assert B==[];O,K=C.rsplit(_B,1)
				async def L(data_path,delete_callbacks,opaque,conn):
					D=conn;B=data_path;F=re.sub(_F,'',B);B=unquote(B);C=A._get_dbpath_for_data_path(B,ContentType.CONFIG_TRUE,D)
					if C is _A:raise NodeNotFound(_r+B)
					G=next(iter(C.jsob));H=C.jsob[G];await A._recursively_delete_subtable_data(C.record_id,B,H,delete_callbacks,opaque,D);I=A.schema_path_to_real_table_name[F];E=A.metadata.tables[I];J=D.execute(sa.delete(E).where(E.c.record_id==C.record_id));assert J.rowcount==1
				if _D in K:await L(C,E,I,F)
				else:
					P=[A[0]for A in A._get_keys_in_table_having_parent_id(G,J,F)]
					for D in P:H=C+_D+D;await L(H,E,I,F)
			elif any(G.startswith(A)for A in A.config_false_prefixes):assert B==[];Q=A.schema_path_to_real_table_name[G];M=A.metadata.tables[Q];F.execute(sa.delete(M).where(M.c.parent_id==J))
			else:
				O,K=C.rsplit(_B,1)
				if _D in K:D=unquote(K.rsplit(_D)[1]);assert D in B;H=C;await A._recursively_delete_subtable_data(J,H,D,E,I,F);B.remove(D)
				else:
					while len(B)!=0:
						D=B[0]
						if D is _A:break
						H=C+_D+D;await A._recursively_delete_subtable_data(J,H,D,E,I,F);B.pop(0)
		elif isinstance(B,dict):
			for N in B.keys():assert C!=_B;H=C+_B+N;await A._recursively_delete_subtable_data(J,H,B[N],E,I,F)
		else:0
		if not isinstance(B,list)and not any(G.startswith(A)for A in A.config_false_prefixes):
			if G in E:
				for R in E[G]:await R(C,I)
	def _find_rows_in_table_having_parent_id(E,table_name,parent_id,query_dict,conn):
		H='limit';G='offset';F='direction';B=query_dict;I=E.schema_path_to_real_table_name[table_name];C=E.metadata.tables[I];A=sa.select(C).where(C.c.parent_id==parent_id)
		if _Y in B:D=getattr(C.c,B[_Y])
		else:D=C.c.record_id
		if F in B and B[F]=='backwards':A=A.order_by(D.desc())
		else:A=A.order_by(D.asc())
		if G in B:A=A.offset(int(B[G]))
		if H in B:A=A.limit(int(B[H]))
		J=conn.execute(A).mappings();return J
	def _find_rowids_in_table_having_parent_id(B,table_name,parent_id,conn):C=B.schema_path_to_real_table_name[table_name];A=B.metadata.tables[C];D=conn.execute(sa.select(A.c.record_id).where(A.c.parent_id==parent_id).order_by(A.c.record_id));return D
	def _get_keys_in_table_having_parent_id(A,table_name,parent_id,conn):B=table_name;D=A.schema_path_to_real_table_name[B];C=A.metadata.tables[D];E=conn.execute(sa.select(getattr(C.c,A.table_keys[B])).where(C.c.parent_id==parent_id));return E
	def _get_list_of_direct_subtables_for_schema_path(D,schema_path):
		A=schema_path
		if A!=_B:assert A[-1]!=_B;A+=_B
		C=[]
		for B in sorted(D.schema_path_to_real_table_name.keys()):
			if str(B).startswith(A):
				if not any(A for A in C if str(B).startswith(A+_B)):
					if str(B)!=_B:C.append(str(B))
		return C
	def _get_record_id_for_key_in_table(B,table_name,key,conn):
		C=table_name;E=B.schema_path_to_real_table_name[C];D=B.metadata.tables[E];F=conn.execute(sa.select(D.c.record_id).where(getattr(D.c,B.table_keys[C])==key));A=F.fetchall();assert A is not _A
		if len(A)==0:return
		if len(A)>1:raise TooManyNodesFound()
		return A[0][0]
	def _get_jsob_iter_for_path_in_jsob(D,jsob,path):
		B=path;assert jsob is not _A;assert B[0]!=_B;A=jsob
		if B!='':
			for C in B.split(_B):
				if C!=''and C not in A:return
				A=A[C]
				if isinstance(A,list):assert len(A)==1;A=A[0]
		return A
	def _get_jsob_for_record_id_in_table(B,table_name,record_id,conn):
		F=record_id;C=table_name;K=B.schema_path_to_real_table_name[C];A=B.metadata.tables[K]
		if C in B.table_keys:D=conn.execute(sa.select(A.c.jsob).where(A.c.record_id==F));G=D.first();assert G is not _A;return G[0]
		D=conn.execute(sa.select(A).where(A.c.record_id==F)).mappings();H=D.first();assert H is not _A;I=C.rsplit(_B,1)[1];J={I:{}}
		for E in A.c:
			if E.name not in(_O,_H,_c,_d):J[I][E.name]=H[E.name]
		return J
	def _insert_jsob_into_table(B,parent_id,table_name,new_jsob,conn,obu_idx=_A):
		F=obu_idx;D=table_name;C=new_jsob;H=B.schema_path_to_real_table_name[D];I=B.metadata.tables[H];E=next(iter(C));A={};A[_H]=parent_id
		if D in B.table_keys:
			A[B.table_keys[D]]=C[E][B.table_keys[D]]
			if F is not _A:A[_J]=F
			A[_K]=C
		else:
			for G in C[E].keys():A[G]=C[E][G]
		J=conn.execute(I.insert().values(**A));return J.inserted_primary_key[0]
	def _update_jsob_for_record_id_in_table(A,table_name,record_id,new_jsob,conn):C=A.schema_path_to_real_table_name[table_name];B=A.metadata.tables[C];conn.execute(sa.update(B).where(B.c.record_id==record_id).values(jsob=new_jsob))
	def _get_table_name_for_schema_path(D,schema_path):
		B=len(_B);C=_G
		for A in D.schema_path_to_real_table_name.keys():
			if schema_path.startswith(A)and len(A)>B:B=len(A);C=A
		return C
	def _get_obu_idx_list_for_list_path(B,list_path,conn):
		D=list_path;assert D[0]==_B;assert D!=_B;assert D[-1]!=_B;C='';E=B.global_root_id;K=D[1:].split(_B)
		for F in K:
			if _D in F:
				L,M=F.split(_D);C+=_B+L;I=B._get_table_name_for_schema_path(C);G=B.schema_path_to_real_table_name[I];A=B.metadata.tables[G];J=conn.execute(sa.select(A.c.record_id,A.c.parent_id).where(and_(A.c.parent_id==E,getattr(A.c,B.table_keys[I])==M))).mappings();H=J.fetchone()
				if H is _A:return
				assert J.fetchone()is _A;assert E==H[_H];E=H[_O]
			else:C+=_B+F
		G=B.schema_path_to_real_table_name[C];A=B.metadata.tables[G];N=conn.execute(sa.select(getattr(A.c,B.table_keys[C]),A.c.obu_idx).where(A.c.parent_id==E).order_by(A.c.obu_idx));O=N.fetchall();P=[A._mapping.items()._items for A in O];return P
	def _get_row_data_for_list_path(A,data_path,conn):
		B=data_path;assert B[0]==_B;assert B!=_B;assert B[-1]!=_B;G=B[1:].split(_B);assert _D in G[-1];D='';H=A.global_root_id
		for E in G:
			if _D in E:
				K,L=E.split(_D);D+=_B+K;I=A._get_table_name_for_schema_path(D);M=A.schema_path_to_real_table_name[I];C=A.metadata.tables[M];J=conn.execute(sa.select(C.c.record_id,C.c.parent_id).where(and_(C.c.parent_id==H,getattr(C.c,A.table_keys[I])==L))).mappings();F=J.fetchone()
				if F is _A:return
				assert J.fetchone()is _A;H=F[_O]
			else:D+=_B+E
		return F
	def _get_dbpath_for_data_path(B,data_path,content_type,conn):
		D=conn;C=data_path;A=DatabasePath();A.data_path=C;A.schema_path=re.sub(_F,'',C);A.table_name=B._get_table_name_for_schema_path(A.schema_path)
		if A.table_name is _A:return
		if C!=_B and A.table_name==A.schema_path:
			G,N=C.rsplit(_B,1)
			if _D not in N:
				if G=='':H=_B
				else:H=re.sub(_F,'',G)
				A.table_name=B._get_table_name_for_schema_path(H);assert A.table_name is not _A
		if A.table_name==_G:A.jsob_data_path=_B;A.jsob_schema_path=_B
		else:
			A.jsob_data_path=C;A.jsob_schema_path=re.sub(_F,'',A.jsob_data_path)
			while A.jsob_schema_path!=A.table_name:O=A.jsob_data_path;A.jsob_data_path=re.sub('(.*=[^/]*)/.*','\\g<1>',A.jsob_data_path);assert A.jsob_data_path!=O;A.jsob_schema_path=re.sub(_F,'',A.jsob_data_path)
		if ContentType.CONFIG_FALSE in content_type and any(A.table_name.startswith(B)for B in B.config_false_prefixes):raise InvalidResourceTarget('RFC 8040 does not allow queries on lists directly and, because '+"YANGcore doesn't support keys on 'config false' lists, it is "+"never possible to query for 'dbpath.table_name' to be returned. "+"The 'val' layer should've rejected this query... ")
		if A.jsob_schema_path==_B:A.record_id=B.global_root_id
		else:
			assert A.jsob_schema_path in B.table_keys;assert _D in A.jsob_data_path;I=A.jsob_data_path.split(_B);assert _D in I[-1];E=I[-1].split(_D)
			try:A.record_id=B._get_record_id_for_key_in_table(A.table_name,E[1],D)
			except TooManyNodesFound:
				J=B._get_row_data_for_list_path(A.jsob_data_path,D)
				if J is _A:A.record_id=_A
				else:A.record_id=J[_O]
			if A.record_id is _A:return
		assert A.data_path.startswith(A.jsob_data_path);K=A.data_path[len(A.jsob_data_path):];assert A.schema_path.startswith(A.jsob_schema_path);L=A.schema_path[len(A.jsob_schema_path):]
		if A.table_name==_G:A.inside_path=A.schema_path[1:]
		else:M=re.findall(_q,A.jsob_data_path);assert len(M)!=0;E=M[-1].split(_D);A.inside_path=E[0];P=re.sub('^'+A.table_name,'',A.schema_path);assert P==L;A.inside_path+=L
		assert A.inside_path==''or A.inside_path[0]!=_B;A.jsob=B._get_jsob_for_record_id_in_table(A.table_name,A.record_id,D);A.node_ptr=A.jsob;A.prev_ptr=_A
		if A.inside_path=='':A.path_segments=[''];return A
		A.path_segments=A.inside_path.split(_B);Q=''
		for F in A.path_segments:
			Q+=_B+F
			if F not in A.node_ptr:return
			A.prev_ptr=A.node_ptr;A.node_ptr=A.node_ptr[F]
		if isinstance(A.node_ptr,list):
			if _D in K:
				R=unquote(K.rsplit(_D,1)[1])
				try:S=A.node_ptr.index(R)
				except Exception:return
				A.prev_ptr=A.node_ptr;A.node_ptr=A.node_ptr[S]
		return A
	def _init_from_existing_db(A,url,cacert_param,cert_param,key_param):
		K=key_param;J=cert_param;I=cacert_param;E=url
		if not(E.startswith('sqlite:///')or E.startswith(_U)or E.startswith(_Z)):raise SyntaxError('The database url contains an unrecognized dialect.')
		C={}
		if E.startswith(_Z):
			if I is not _A:
				C[_s]=_t;C[_u]=I
				if J is not _A:C[_v]=J
				if K is not _A:C[_w]=K
		elif E.startswith(_U):
			if I is not _A:
				C[_M]={};C[_M]['ca']=I;C[_M]['mode']=6
				if J is not _A:C[_M]['cert']=J
				if K is not _A:C[_M][_i]=K
		A.engine=sa.create_engine(E,connect_args=C)
		try:
			if A.engine.url.database==_j or not db_utils.database_exists(A.engine.url,connect_args=C):raise NotImplementedError(str(A.engine.url))
		except sa.exc.OperationalError as H:
			if H.orig and'Access denied'in str(H.orig):N=re.sub('^.*"','',re.sub('")$','',str(H.orig)));raise AuthenticationFailed('Authentication failed: '+N)from H
			raise H
		A.db_schema=_A;A.table_keys={};A.config_false_prefixes={};A.config_true_obu_seq_nodes={};A.schema_path_to_real_table_name={};A.leafrefs={};A.referers={};A.ref_stat_collectors={}
		if A.engine.dialect.name==_k:A.schema_path_to_real_table_name[_B]=_G;A.schema_path_to_real_table_name[_G]=_G
		else:A.db_schema=A.engine.url.database;A.schema_path_to_real_table_name[_B]=A.db_schema.join(_a);A.schema_path_to_real_table_name[_G]=A.db_schema+_a;O=A.engine.execute(_x);L=O.fetchall();P=[L[A][0]for A in range(len(L))];assert A.db_schema in P
		A.metadata=sa.MetaData(bind=A.engine,schema=A.db_schema);A.metadata.reflect()
		for Q in A.metadata.tables.values():
			for F in Q.c:
				if isinstance(F.type,(sa.sql.sqltypes.BLOB,sa.sql.sqltypes.PickleType)):F.type=sa.PickleType()
				if A.engine.dialect.name==_U and isinstance(F.type,sa.dialects.mysql.types.LONGTEXT):F.type=sa.JSON()
				elif isinstance(F.type,sa.sql.sqltypes.JSON):F.type=sa.JSON()
		B=A.metadata.tables[A.schema_path_to_real_table_name[_G]]
		with A.engine.connect()as G:
			D=G.execute(sa.select(B.c.jsob).where(B.c.name==_y));M=D.first()[0]
			if M[_l]!=1:raise AssertionError('The database version ('+M[_l]+') is unexpected.')
			D=G.execute(sa.select(B.c.record_id).where(B.c.name==_m));A.global_root_id=D.first()[0];D=G.execute(sa.select(B.c.jsob).where(B.c.name==_z));A.table_keys=D.first()[0];D=G.execute(sa.select(B.c.jsob).where(B.c.name==_A0));A.schema_path_to_real_table_name=D.first()[0];D=G.execute(sa.select(B.c.jsob).where(B.c.name==_A1));A.config_false_prefixes=D.first()[0];D=G.execute(sa.select(B.c.jsob).where(B.c.name==_A2));A.config_true_obu_seq_nodes=D.first()[0]
	def _load_yang_dir_file(A,filename):
		if A.app_name==_o:B=importlib_resources.files(_n)
		else:B=importlib_resources.files(A.app_name)
		C=B/_b/filename
		with open(C,'r',encoding='utf-8')as D:return json.load(D)
	def _init_new_db_with_factory_default(A):
		a='import-only-module';Z='module';Y='local-address';U='endpoint';N='datastore';M='local-bind';K='ietf-yang-library:yang-library';J='schema';I='module-set'
		if os.environ.get('YANGCORE_TEST_DAL'):
			B=_B;C=A.schema_path_to_real_table_name[B];D=A.metadata.tables[C]
			with A.engine.begin()as E:G=E.execute(D.insert().values(name=_m,jsob={}))
			A.global_root_id=G.inserted_primary_key[0];return
		b=A._load_yang_dir_file('factory-default.json');c=A._load_yang_dir_file('yang-library-nbi.json');d={'yangcore:audit-log':{'audit-log-record':[]},'yangcore:notification-log':{'notification-log-record':[]}};H=b|c|d;O=H['ietf-restconf-server:restconf-server']['listen']['endpoints'];V={U:O[U].pop(0)};O=V[U]['http-over-tcp']['tcp-server-parameters'];P=[]
		for e in O[M]:P.append({M:e})
		O[M]=[];assert len(P)==2;L=[]
		while len(H[K][I]):f=H[K][I].pop(0);L.append({I:f})
		Q=[]
		while len(H[K][J]):g=H[K][J].pop(0);Q.append({J:g})
		W=[]
		while len(H[K][N]):h=H[K][N].pop(0);W.append({N:h})
		if(S:=os.environ.get('YANGCORE_INIT_PORT')):
			try:T=int(S)
			except ValueError as i:raise ValueError('Invalid "YANGCORE_INIT_PORT" value ('+S+').')from i
			if T<=0 or T>2**16-1:raise ValueError('The "YANGCORE_INIT_PORT" value ('+S+') is out of range [1..65535].')
			for R in P:R[M]['local-port']=T
		j=H;B=_B;C=A.schema_path_to_real_table_name[B];D=A.metadata.tables[C]
		with A.engine.begin()as E:G=E.execute(D.insert().values(name=_m,jsob=j))
		A.global_root_id=G.inserted_primary_key[0];B='/ietf-restconf-server:restconf-server/listen/endpoints/endpoint';C=A.schema_path_to_real_table_name[B];D=A.metadata.tables[C]
		with A.engine.begin()as E:k=E.execute(D.insert().values(parent_id=A.global_root_id,name='default startup endpoint',jsob=V))
		l=k.inserted_primary_key[0]
		for R in P:
			F={};F[_H]=l;F[Y]=R[M][Y];F[_K]=R;B='/ietf-restconf-server:restconf-server/listen/endpoints/'+'endpoint/http-over-tcp/tcp-server-parameters/local-bind';C=A.schema_path_to_real_table_name[B];D=A.metadata.tables[C]
			with A.engine.begin()as E:G=E.execute(D.insert().values(**F))
		assert len(L)==1;B='/ietf-yang-library:yang-library/module-set';C=A.schema_path_to_real_table_name[B];D=A.metadata.tables[C]
		with A.engine.begin()as E:F={_H:A.global_root_id,_I:L[0][I][_I],Z:L[0][I][Z],a:L[0][I][a]};G=E.execute(D.insert().values(**F));m=G.inserted_primary_key[0]
		assert len(Q)==1;B='/ietf-yang-library:yang-library/schema';C=A.schema_path_to_real_table_name[B];D=A.metadata.tables[C]
		with A.engine.begin()as E:F={_H:A.global_root_id,_I:Q[0][J][_I],I:Q[0][J][I]};G=E.execute(D.insert().values(**F))
		B='/ietf-yang-library:yang-library/datastore';C=A.schema_path_to_real_table_name[B];D=A.metadata.tables[C]
		with A.engine.begin()as E:
			for X in W:F={_H:A.global_root_id,_I:X[N][_I],J:X[N][J]};G=E.execute(D.insert().values(**F))
	def _create_new_db(A,url,yl_obj,cacert_param=_A,cert_param=_A,key_param=_A):
		L='_sztp_ref_stats_stmt';J=yl_obj;I=url;H=key_param;G=cert_param;F=cacert_param;assert isinstance(J,dict);B={}
		if I.startswith(_Z):
			if F is not _A:
				B[_s]=_t;B[_u]=F
				if G is not _A:B[_v]=G
				if H is not _A:B[_w]=H
		elif I.startswith(_U):
			if F is not _A:
				B[_M]={};B[_M]['ca']=F;B[_M]['mode']=6
				if G is not _A:B[_M]['cert']=G
				if H is not _A:B[_M][_i]=H
		A.engine=sa.create_engine(I,connect_args=B)
		if A.engine.url.database!=_j and db_utils.database_exists(A.engine.url,connect_args=B):raise AssertionError('Database already exists (call init() first).')
		if A.engine.url.database!=_j:
			if A.engine.dialect.name==_U:db_utils.create_database(A.engine.url,encoding='utf8mb4',connect_args=B)
			else:db_utils.create_database(A.engine.url,connect_args=B)
		A.db_schema=_A
		if A.engine.dialect.name in(_U,_Z):
			A.db_schema=str(A.engine.url.database);E=A.engine.execute(_x);K=E.fetchall();M=[K[A][0]for A in range(len(K))]
			if A.db_schema not in M:A.engine.execute(f"CREATE SCHEMA IF NOT EXISTS {A.db_schema};")
		A.metadata=sa.MetaData(schema=A.db_schema);D=sa.Table(_G,A.metadata,sa.Column(_O,sa.Integer,primary_key=_E),sa.Column(_I,sa.String(250),unique=_E),sa.Column(_K,JsobType));A.metadata.create_all(bind=A.engine)
		with A.engine.begin()as C:C.execute(D.insert(),{_I:_y,_K:{_l:1}});C.execute(D.insert(),{_I:'yang-library',_K:J})
		A.table_keys={_G:_I,_B:_I};A.config_true_obu_seq_nodes={};A.config_false_prefixes={};A.schema_path_to_real_table_name={};A.leafrefs={};A.referers={};A.ref_stat_collectors={}
		if A.engine.dialect.name==_k:A.schema_path_to_real_table_name[_B]=_G;A.schema_path_to_real_table_name[_G]=_G
		else:A.schema_path_to_real_table_name[_B]=A.db_schema+_a;A.schema_path_to_real_table_name[_G]=A.db_schema+_a
		def N(self,stmt,sctx):assert stmt is not _A;assert sctx is not _A;self.globally_unique=_E
		yangson.schemanode.SchemaNode._sztp_globally_unique_stmt=N;yangson.schemanode.SchemaNode._stmt_callback['yangcore:globally-unique']='_sztp_globally_unique_stmt'
		def O(self,stmt,sctx):assert sctx is not _A;self.ref_stats=stmt.argument
		setattr(yangson.schemanode.SchemaNode,L,O);yangson.schemanode.SchemaNode._stmt_callback['yangcore:ref-stats']=L;P=yl_8525_to_7895(J);A.dm=yangson.DataModel(json.dumps(P),A.module_paths);A._recursive_gen_tables(A.dm.schema,_G)
		with A.engine.begin()as C:E=C.execute(D.insert(),{_I:_A0,_K:A.schema_path_to_real_table_name});E=C.execute(D.insert(),{_I:_z,_K:A.table_keys});E=C.execute(D.insert(),{_I:_A1,_K:A.config_false_prefixes});E=C.execute(D.insert(),{_I:_A2,_K:A.config_true_obu_seq_nodes})
		A._init_new_db_with_factory_default()
	def _recursive_gen_tables(D,node,parent_table_name):
		N='ref_stats';G=parent_table_name;C=node
		if issubclass(type(C),yangson.schemanode.ListNode):
			B=[];B.append(sa.Column(_O,sa.Integer,primary_key=_E));O=D.schema_path_to_real_table_name[G];B.append(sa.Column(_H,sa.Integer,sa.ForeignKey(O+'.record_id'),index=_E,nullable=_C));B.append(sa.Column(_c,sa.String(250),index=_E,nullable=_E))
			class S(enum.Enum):UNIVERSAL=0;OPERATIONAL=1;RUNNING=2;STARTUP=3;SYSTEM=4;INTENDED=5;FACTORY=6
			B.append(sa.Column(_d,sa.Integer,index=_E,nullable=_E))
			if C.config is _E:
				if len(C.keys)>1:raise NotImplementedError('YANGcore supports lists with at most one key.')
				E=C.get_child(*C.keys[0]);D.table_keys[C.data_path()]=E.name
				if isinstance(E.type,yangson.datatype.StringType):B.append(sa.Column(E.name,sa.String(250),nullable=_C))
				elif isinstance(E.type,yangson.datatype.Uint32Type):B.append(sa.Column(E.name,sa.Integer,nullable=_C))
				elif isinstance(E.type,yangson.datatype.IdentityrefType):B.append(sa.Column(E.name,sa.String(250),nullable=_C))
				elif isinstance(E.type,yangson.datatype.UnionType):B.append(sa.Column(E.name,sa.String(250),nullable=_C))
				elif isinstance(E.type,yangson.datatype.LeafrefType):B.append(sa.Column(E.name,sa.String(250),nullable=_C))
				else:raise NotImplementedError('Unsupported key node type: '+str(type(E.type)))
				if hasattr(E,'globally_unique'):B.append(sa.UniqueConstraint(E.name))
				else:B.append(sa.UniqueConstraint(E.name,_H))
				if C.user_ordered is _E:B.append(sa.Column(_J,sa.Integer,index=_E,nullable=_C))
				B.append(sa.Column(_K,JsobType,nullable=_C))
			else:
				assert C.config is _C;assert hasattr(C,N)is _C
				for A in C.children:
					if issubclass(type(A),yangson.schemanode.LeafNode):
						if isinstance(A.type,yangson.datatype.StringType):
							if str(A.type)=='date-and-time(string)':B.append(sa.Column(A.name,sa.DateTime(timezone=_E),index=_E,nullable=A.mandatory is _C or A.when is not _A))
							else:B.append(sa.Column(A.name,sa.String(250),index=_E,nullable=A.mandatory is _C or A.when is not _A))
						elif isinstance(A.type,yangson.datatype.Uint16Type):B.append(sa.Column(A.name,sa.SmallInteger,index=_E,nullable=A.mandatory is _C or A.when is not _A))
						elif isinstance(A.type,yangson.datatype.InstanceIdentifierType):B.append(sa.Column(A.name,sa.String(250),nullable=A.mandatory is _C or A.when is not _A))
						elif isinstance(A.type,yangson.datatype.LeafrefType):B.append(sa.Column(A.name,sa.String(250),nullable=A.mandatory is _C or A.when is not _A))
						elif isinstance(A.type,yangson.datatype.IdentityrefType):B.append(sa.Column(A.name,sa.String(250),nullable=A.mandatory is _C or A.when is not _A))
						elif isinstance(A.type,yangson.datatype.EnumerationType):B.append(sa.Column(A.name,sa.String(250),index=_E,nullable=A.mandatory is _C or A.when is not _A))
						elif isinstance(A.type,yangson.datatype.UnionType):
							J=0
							for K in A.type.types:
								if issubclass(type(K),yangson.datatype.StringType):J+=1
								else:raise NotImplementedError('Unhandled union type: '+str(type(K)))
							if J==len(A.type.types):B.append(sa.Column(A.name,sa.String(250),index=_E,nullable=A.mandatory is _C or A.when is not _A))
							else:raise NotImplementedError('FIXME: not all union subtypes are stringafiable')
						else:raise NotImplementedError('Unhandled leaf type: '+str(type(A.type)))
					elif issubclass(type(A),yangson.schemanode.ChoiceNode):
						H=_E
						for I in A.children:
							assert isinstance(I,yangson.schemanode.CaseNode)
							if len(I.children)>1:H=_C;break
							for P in I.children:
								if not isinstance(P,yangson.schemanode.LeafNode):H=_C;break
						if H is _E:B.append(sa.Column(A.name,sa.String(250),index=_E,nullable=A.mandatory is _C or A.when is not _A))
						else:B.append(sa.Column(A.name,JsobType,nullable=A.mandatory is _C or A.when is not _A))
					elif issubclass(type(A),yangson.schemanode.AnydataNode):B.append(sa.Column(A.name,JsobType,nullable=A.mandatory is _C or A.when is not _A))
					elif issubclass(type(A),yangson.schemanode.LeafListNode):B.append(sa.Column(A.name,JsobType,nullable=A.mandatory is _C or A.when is not _A))
					elif issubclass(type(A),yangson.schemanode.ListNode):B.append(sa.Column(A.name,JsobType,nullable=A.mandatory is _C or A.when is not _A))
					elif issubclass(type(A),yangson.schemanode.ContainerNode):B.append(sa.Column(A.name,JsobType,nullable=A.mandatory is _C or A.when is not _A))
					elif issubclass(type(A),yangson.schemanode.NotificationNode):0
					else:raise NotImplementedError('Unhandled list child type: '+str(type(A)))
			Q=re.sub('^/.*:','',C.data_path()).split(_B)
			if D.engine.dialect.name==_k:F=''
			else:F=D.db_schema+'.'
			for R in Q:F+=R[0]
			while F in D.schema_path_to_real_table_name.values():F+='2'
			D.schema_path_to_real_table_name[C.data_path()]=F
			if D.db_schema is _A:L=sa.Table(F,D.metadata,*B)
			else:L=sa.Table(re.sub('^'+D.db_schema+'.','',F),D.metadata,*B)
			L.create(bind=D.engine);G=C.data_path()
		if C.config is _C and issubclass(type(C),yangson.schemanode.DataNode):
			M=C.data_path()
			if not any(M.startswith(A)for A in D.config_false_prefixes):D.config_false_prefixes[M]=_E
		if C.config is _E and issubclass(type(C),yangson.schemanode.SequenceNode)and C.user_ordered is _E:D.config_true_obu_seq_nodes[C.data_path()]=_A
		if hasattr(C,N):D.ref_stat_collectors[C.data_path()]=_A
		if issubclass(type(C),yangson.schemanode.InternalNode):
			if not(isinstance(C,yangson.schemanode.ListNode)and C.config is _C)and not isinstance(C,yangson.schemanode.RpcActionNode)and not isinstance(C,yangson.schemanode.NotificationNode):
				for A in C.children:D._recursive_gen_tables(A,G)