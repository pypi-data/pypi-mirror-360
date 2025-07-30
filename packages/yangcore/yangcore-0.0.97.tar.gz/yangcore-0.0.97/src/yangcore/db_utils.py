# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

_G=':memory:'
_F='template1'
_E='postgres'
_D='sqlite'
_C=False
_B='postgresql'
_A=None
import os
from copy import copy
import sqlalchemy as sa
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError,ProgrammingError
from sqlalchemy.orm.session import object_session
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm.exc import UnmappedInstanceError
def _set_url_database(url,database):
	C=database;A=url
	if hasattr(sa.engine,'URL'):B=sa.engine.URL.create(drivername=A.drivername,username=A.username,password=A.password,host=A.host,port=A.port,database=C,query=A.query)
	else:A.database=C;B=A
	assert B.database==C,B;return B
def _get_scalar_result(engine,sql):
	with engine.connect()as A:return A.scalar(sql)
def _sqlite_file_exists(database):
	A=database
	if not os.path.isfile(A)or os.path.getsize(A)<100:return _C
	with open(A,'rb')as B:C=B.read(100)
	return C[:16]==b'SQLite format 3\x00'
def database_exists(url,connect_args=_A):
	E=connect_args;A=url;A=copy(make_url(A));C=A.database;F=A.get_dialect().name;B=_A
	try:
		if F==_B:
			D="SELECT 1 FROM pg_database WHERE datname='%s'"%C
			for G in(C,_E,_F,'template0',_A):
				A=_set_url_database(A,database=G);B=sa.create_engine(A,connect_args=E)
				try:return bool(_get_scalar_result(B,D))
				except(ProgrammingError,OperationalError)as H:pass
			return _C
		elif F=='mysql':A=_set_url_database(A,database=_A);B=sa.create_engine(A,connect_args=E);D="SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s'"%C;return bool(_get_scalar_result(B,D))
		elif F==_D:
			A=_set_url_database(A,database=_A);B=sa.create_engine(A,connect_args=E)
			if C:return C==_G or _sqlite_file_exists(C)
			else:return True
		else:
			D='SELECT 1'
			try:B=sa.create_engine(A,connect_args=E);return bool(_get_scalar_result(B,D))
			except(ProgrammingError,OperationalError):return _C
	finally:
		if B:B.dispose()
def create_database(url,encoding='utf8',template=_A,connect_args=_A):
	K='mssql';I=connect_args;H=encoding;G=template;A=url;A=copy(make_url(A));E=A.database;C=A.get_dialect().name;J=A.get_dialect().driver
	if C==_B:A=_set_url_database(A,database=_E)
	elif C==K:A=_set_url_database(A,database='master')
	elif not C==_D:A=_set_url_database(A,database=_A)
	if C==K and J in{'pymssql','pyodbc'}or C==_B and J in{'asyncpg','pg8000','psycopg2','psycopg2cffi'}:B=sa.create_engine(A,isolation_level='AUTOCOMMIT',connect_args=I)
	else:B=sa.create_engine(A,connect_args=I)
	if C==_B:
		if not G:G=_F
		F="CREATE DATABASE {0} ENCODING '{1}' TEMPLATE {2}".format(quote(B,E),H,quote(B,G))
		with B.connect()as D:D.execute(F)
	elif C=='mysql':
		F="CREATE DATABASE {0} CHARACTER SET = '{1}'".format(quote(B,E),H)
		with B.connect()as D:D.execute(F)
	elif C==_D and E!=_G:
		if E:
			with B.connect()as D:D.execute('CREATE TABLE DB(id int);');D.execute('DROP TABLE DB;')
	else:
		F='CREATE DATABASE {0}'.format(quote(B,E))
		with B.connect()as D:D.execute(F)
	B.dispose()
def quote(mixed,ident):
	A=mixed
	if isinstance(A,Dialect):B=A
	else:B=get_bind(A).dialect
	return B.preparer(B).quote(ident)
def get_bind(obj):
	A=obj
	if hasattr(A,'bind'):B=A.bind
	else:
		try:B=object_session(A).bind
		except UnmappedInstanceError:B=A
	if not hasattr(B,'execute'):raise TypeError('This method accepts only Session, Engine, Connection and declarative model objects.')
	return B