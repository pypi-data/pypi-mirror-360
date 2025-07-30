# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

import importlib.resources as importlib_resources,copy,json
def yangcore_native_yang_library():
	A=importlib_resources.files('yangcore')/'yang'/'yang-library-nbi.json'
	with open(A,'r',encoding='utf-8')as B:return json.load(B)
def yl_8525_to_7895(yl_8525_obj):
	J='import-only-module';I='ietf-yang-library:modules-state';G='conformance-type';F='module-set';E='ietf-yang-library:yang-library';D='module';B=yl_8525_obj;H={I:{'module-set-id':'TBD',D:[]}};C=H[I][D]
	if D in B[E][F][0]:
		for A in B[E][F][0][D]:C.append(copy.copy(A))
		for A in C:A[G]='implement'
	if J in B[E][F][0]:
		for K in B[E][F][0][J]:C.append(copy.copy(K))
		for A in C:
			if G not in A:A[G]='import'
	return H