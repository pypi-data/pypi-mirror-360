# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

from __future__ import annotations
_X='Unrecognized member: '
_W='Query parameters are only supported for "list" and "leaf-list" nodes.'
_V='Unrecognized schema path for "point" node: '
_U='"insert" parameter is "'
_T='The query parameter "point" is required when the '
_S='Unrecognized "insert" query parameter value: '
_R='" is not recognized.'
_Q='The parameter "'
_P='The top-level node-identifier must be prefixed by a namespace followed by a colon.'
_O='Parent data node ('
_N='Input document must contain at least one top-level node.'
_M='Data node ('
_L='Unrecognized schema path: '
_K='Invalid data path: '
_J='Validation failed: '
_I='The "point" node ('
_H='after'
_G='before'
_F=') does not exist.'
_E=None
_D=True
_C='insert'
_B='point'
_A='/'
import asyncio
from urllib.parse import quote
import yangson
class NodeAlreadyExists(Exception):0
class NodeNotFound(Exception):0
class ParentNodeNotFound(Exception):0
class InvalidDataPath(Exception):0
class InvalidInputDocument(Exception):0
class UnrecognizedInputNode(Exception):0
class UnrecognizedQueryParameter(Exception):0
class MissingQueryParameter(Exception):0
class InvalidQueryParameter(Exception):0
class NonexistentSchemaNode(Exception):0
class ValidationFailed(Exception):0
class ValidationLayer:
	def __init__(A,dm,dal):
		A.dm=dm;C=asyncio.get_event_loop();D=dal.handle_get_config_request(_A,{});E=C.run_until_complete(D);A.inst=A.dm.from_raw(E);A.inst2=_E
		try:A.inst.validate()
		except yangson.exceptions.SchemaError as B:assert str(B).startswith('{/} missing-data: expected');assert str(B).endswith(":users'")
	async def handle_get_config_request(C,data_path,query_dict):
		A=data_path;assert query_dict is not _E;assert A!='';assert not(A!=_A and A[-1]==_A)
		try:E=C.dm.parse_resource_id(A)
		except yangson.exceptions.UnexpectedInput as B:raise InvalidDataPath(_K+str(B))from B
		except yangson.exceptions.NonexistentSchemaNode as B:raise NonexistentSchemaNode(_L+A)from B
		try:D=C.inst.goto(E)
		except yangson.exceptions.NonexistentInstance as B:raise NodeNotFound(_M+A+_F)from B
		if not isinstance(D,yangson.instance.ArrayEntry)and isinstance(D.schema_node,yangson.schemanode.SequenceNode):raise InvalidDataPath("RFC 8040 doesn't acknowledge 'list' or 'list-list' nodes as resource targets.")
	async def handle_post_config_request(H,data_path,query_dict,request_body):
		X='Node already exists: ';W="' must contain one element.";V="Input 'list' node '";U="' not a 'list' node.";T="Input node '";E=data_path;D=request_body;C=query_dict
		if len(D)<1:raise InvalidInputDocument(_N)
		if len(D)>1:raise InvalidInputDocument('Input document must not have more than one top-level node.')
		try:Y=H.dm.parse_resource_id(E)
		except yangson.exceptions.NonexistentSchemaNode as A:raise NonexistentSchemaNode('Unrecognized schema path for parent node: '+E)from A
		try:I=H.inst.goto(Y)
		except yangson.exceptions.NonexistentInstance as A:raise ParentNodeNotFound(_O+E+_F)from A
		B=next(iter(D))
		if':'not in B:raise InvalidInputDocument(_P)
		Z,F=B.split(':');M=I.schema_node;J=M.get_child(F,Z)
		if J is _E:raise UnrecognizedInputNode('Input document contains unrecognized top-level node.')
		if not M.ns is _E:assert M.ns==J.ns
		if isinstance(J,yangson.schemanode.SequenceNode):
			if isinstance(J,yangson.schemanode.ListNode):
				a=J.keys[0];b=a[0]
				if not isinstance(D[B],list):raise InvalidInputDocument(T+F+U)
				if len(D[B])!=1:raise InvalidInputDocument(V+F+W)
				N=D[B][0];Q=N[b]
			elif isinstance(J,yangson.schemanode.LeafListNode):
				if not isinstance(D[B],list):raise InvalidInputDocument(T+F+U)
				if len(D[B])!=1:raise InvalidInputDocument(V+F+W)
				N=D[B][0];Q=D[B][0]
			else:raise AssertionError('Logic cannot reach this point')
			if E==_A:G=B;K=_A+G+'='+quote(Q,safe='')
			else:G=F;K=E+_A+G+'='+quote(Q,safe='')
			try:c=H.dm.parse_resource_id(K)
			except yangson.exceptions.NonexistentSchemaNode as A:raise NonexistentSchemaNode('Unrecognized schema path for insertion node: '+K)from A
			try:H.inst.goto(c)
			except yangson.exceptions.NonexistentInstance as A:pass
			else:raise NodeAlreadyExists(X+K)
			for O in C:
				if O not in(_C,_B):raise UnrecognizedQueryParameter(_Q+O+_R)
				if O==_C:
					if C[_C]not in('first',_G,_H,'last'):raise InvalidQueryParameter(_S+C[_C])
					if C[_C]in(_G,_H):
						if _B not in C:raise MissingQueryParameter(_T+_U+C[_C]+'"')
				if O==_B:
					try:d=H.dm.parse_resource_id(C[_B])
					except yangson.exceptions.NonexistentSchemaNode as A:raise NonexistentSchemaNode(_V+C[_B])from A
					try:H.inst.goto(d)
					except yangson.exceptions.NonexistentInstance as A:raise InvalidQueryParameter(_I+C[_B]+_F)from A
					if E!=C[_B].rsplit(_A,1)[0]:raise InvalidQueryParameter(_I+C[_B]+') is not a sibling of the target node ('+K+').')
			try:L=I[G]
			except yangson.exceptions.NonexistentInstance:L=I.put_member(G,yangson.instvalue.ArrayValue([]))
			assert isinstance(L.schema_node,yangson.schemanode.SequenceNode)
			if len(L.value)==0:
				try:e=L.update([N],raw=_D)
				except yangson.exceptions.RawMemberError as A:raise UnrecognizedInputNode('Incompatable node data. '+str(A))from A
				P=e.up()
			else:f=L[-1];P=f.insert_after(N,raw=_D).up()
		else:
			if len(C)>0 and len(C)==1 and'sleep'not in C:raise UnrecognizedQueryParameter(_W)
			if E==_A:G=B;R=_A+B
			else:G=F;R=E+_A+B
			if G in I:raise NodeAlreadyExists(X+R)
			try:
				if M.ns is _E:P=I.put_member(B,D[B],raw=_D).up()
				else:P=I.put_member(F,D[B],raw=_D).up()
			except yangson.exceptions.RawMemberError as A:raise UnrecognizedInputNode(_X+str(A))from A
		S=P.top()
		try:S.validate()
		except Exception as A:raise ValidationFailed(_J+str(A))from A
		H.inst2=S
	async def handle_put_config_request(D,data_path,query_dict,request_body):
		E=request_body;C=data_path;B=query_dict;assert C!='';assert not(C!=_A and C[-1]==_A)
		if len(E)<1:raise InvalidInputDocument(_N)
		I=next(iter(E))
		if':'not in I:raise InvalidInputDocument(_P)
		try:M=D.dm.parse_resource_id(C)
		except yangson.exceptions.UnexpectedInput as A:raise InvalidDataPath(_K+str(A))from A
		except yangson.exceptions.NonexistentSchemaNode as A:raise NonexistentSchemaNode(_L+C)from A
		try:F=D.inst.goto(M)
		except yangson.exceptions.NonexistentInstance as A:
			G=C.rsplit(_A,1)[0]
			if G=='':G=_A
			N=D.dm.parse_resource_id(G)
			try:F=D.inst.goto(N)
			except yangson.exceptions.NonexistentInstance as K:raise ParentNodeNotFound(_O+G+') does not exist. '+str(K))from K
			await D.handle_post_config_request(G,B,E);return
		if isinstance(F.schema_node,yangson.schemanode.SequenceNode):
			for H in B:
				if H not in(_C,_B):raise UnrecognizedQueryParameter(_Q+H+_R)
				if H==_C:
					if B[_C]not in('first',_G,_H,'last'):raise InvalidQueryParameter(_S+B[_C])
					if B[_C]in(_G,_H):
						if _B not in B:raise MissingQueryParameter(_T+_U+B[_C]+'"')
				if H==_B:
					try:O=D.dm.parse_resource_id(B[_B])
					except yangson.exceptions.NonexistentSchemaNode as A:raise NonexistentSchemaNode(_V+B[_B])from A
					try:D.inst.goto(O)
					except yangson.exceptions.NonexistentInstance as A:raise InvalidQueryParameter(_I+B[_B]+_F)from A
					if C.rsplit(_A,1)[0]!=B[_B].rsplit(_A,1)[0]:raise InvalidQueryParameter(_I+B[_B]+') is not a '+'sibling of the target node ("'+C+'").')
		elif len(B)>0 and len(B)==1 and'sleep'not in B:raise UnrecognizedQueryParameter(_W)
		try:
			if C==_A:J=F.update(E,raw=_D)
			elif isinstance(F.schema_node,yangson.schemanode.SequenceNode):J=F.update(E[I][0],raw=_D)
			else:J=F.update(E[I],raw=_D)
		except yangson.exceptions.RawMemberError as A:raise UnrecognizedInputNode(_X+str(A))from A
		except Exception as A:raise NotImplementedError(str(type(A))+' = '+str(A))from A
		L=J.top()
		try:L.validate()
		except Exception as A:raise ValidationFailed(_J+str(A))from A
		D.inst2=L
	async def handle_delete_config_request(E,data_path):
		C=data_path;assert C!=''
		if C==_A:raise NotImplementedError('this path never entered?')
		try:J=E.dm.parse_resource_id(C)
		except yangson.exceptions.NonexistentSchemaNode as B:raise NonexistentSchemaNode('Unrecognized schema path for data node: '+C)from B
		try:D=E.inst.goto(J)
		except yangson.exceptions.NonexistentInstance as B:raise NodeNotFound(_M+C+_F)from B
		G=D.up()
		if isinstance(D,yangson.instance.ArrayEntry):
			A=G.delete_item(D.index)
			if len(A.value)==0:
				F=A.up()
				if isinstance(F.schema_node,yangson.schemanode.SequenceNode):H=F.delete_item(A.index);raise NotImplementedError('tested? list inside a list...')
				H=F.delete_item(A.name);A=H
		else:A=G.delete_item(D.name)
		I=A.top()
		try:I.validate()
		except Exception as B:raise ValidationFailed(_J+str(B))from B
		E.inst2=I