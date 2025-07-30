# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

import json,importlib.resources as importlib_resources
def sztpd_native_yang_library():
	A=importlib_resources.files('sztpd')/'yang'/'yang-library-nbi.json'
	with open(A,'r',encoding='utf-8')as B:return json.load(B)
def sztpd_rfc8572_yang_library():
	A=importlib_resources.files('sztpd')/'yang'/'yang-library-sbi.json'
	with open(A,'r',encoding='utf-8')as B:return json.load(B)