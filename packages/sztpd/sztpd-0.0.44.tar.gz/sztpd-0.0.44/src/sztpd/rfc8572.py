# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

from __future__ import annotations
_AZ='Unrecognized error-tag: '
_AY='partial-operation'
_AX='operation-failed'
_AW='rollback-failed'
_AV='data-exists'
_AU='resource-denied'
_AT='lock-denied'
_AS='unknown-namespace'
_AR='bad-element'
_AQ='unknown-attribute'
_AP='missing-attribute'
_AO='exception-thrown'
_AN='function-details'
_AM='from-device'
_AL='"ietf-sztp-bootstrap-server:input" is missing.'
_AK='ssl_object'
_AJ='/sztpd:device-types/device-type='
_AI='/ietf-sztp-bootstrap-server:report-progress'
_AH='Resource does not exist.'
_AG='Requested resource does not exist.'
_AF='%Y-%m-%dT%H:%M:%SZ'
_AE='2019-04-30'
_AD='urn:ietf:params:xml:ns:yang:ietf-yang-types'
_AC='ietf-yang-types'
_AB='module-set-id'
_AA='ietf-yang-library:modules-state'
_A9='application/yang-data+xml'
_A8='webhooks'
_A7='callout-type'
_A6='source-ip-address'
_A5='sztpd:device-type'
_A4='sztpd:device'
_A3='access-denied'
_A2='bad-attribute'
_A1='/ietf-sztp-bootstrap-server:get-bootstrapping-data'
_A0='Parent node does not exist.'
_z='Resource can not be modified.'
_y='functions'
_x='/yangcore:dynamic-callouts/dynamic-callout='
_w='/sztpd:devices/device='
_v='2024-10-10'
_u='2013-07-15'
_t='webhook'
_s='exited-normally'
_r='operation-not-supported'
_q='opaque'
_p='rpc-supported'
_o='data-missing'
_n='Unable to parse "input" document: '
_m='device-type'
_l='import'
_k='ietf-sztp-bootstrap-server:input'
_j='Content-Type'
_i=False
_h='plugin'
_g='application/yang-data+json'
_f='malformed-message'
_e='function'
_d='implement'
_c='function-results'
_b='application'
_a='unknown-element'
_Z=True
_Y='call-function'
_X='invalid-value'
_W='path'
_V='method'
_U='source-ip'
_T='serial-number'
_S='conformance-type'
_R='namespace'
_Q='revision'
_P='error-tag'
_O='request'
_N='timestamp'
_M='error'
_L='protocol'
_K='text/plain'
_J='yangcore:dynamic-callout'
_I='ietf-restconf:errors'
_H='+'
_G='name'
_F='return-code'
_E='error-returned'
_D='/'
_C=None
_B='handling'
_A='response'
import importlib.resources as importlib_resources,urllib.parse,datetime,asyncio,base64,json,os,aiohttp,yangson,basicauth
from aiohttp import web
from certvalidator import CertificateValidator,ValidationContext,PathBuildingError
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from passlib.hash import sha256_crypt
from pyasn1.type import univ
from pyasn1.codec.der.encoder import encode as encode_der
from pyasn1.codec.der.decoder import decode as der_decoder
from pyasn1_modules import rfc5652
from yangcore import utils
from yangcore.native import Read
from yangcore.dal import NodeNotFound
from yangcore.rcsvr import RestconfServer
from yangcore.handler import AppRouteHandler
from yangcore.yl import yl_8525_to_7895
from sztpd.yl import sztpd_rfc8572_yang_library
from sztpd import rfc8572_utils
class RFC8572ViewHandler(AppRouteHandler):
	len_prefix_running=len(RestconfServer.root+'/ds/ietf-datastores:running');len_prefix_operational=len(RestconfServer.root+'/ds/ietf-datastores:operational');len_prefix_operations=len(RestconfServer.root+'/operations');id_ct_sztpConveyedInfoXML=rfc5652._buildOid(1,2,840,113549,1,9,16,1,42);id_ct_sztpConveyedInfoJSON=rfc5652._buildOid(1,2,840,113549,1,9,16,1,43);supported_media_types=_g,_A9;yl4errors={_AA:{_AB:'TBD','module':[{_G:_AC,_Q:_u,_R:_AD,_S:_l},{_G:'ietf-restconf',_Q:'2017-01-26',_R:'urn:ietf:params:xml:ns:yang:ietf-restconf',_S:_d},{_G:'ietf-netconf-acm',_Q:'2018-02-14',_R:'urn:ietf:params:xml:ns:yang:ietf-netconf-acm',_S:_l},{_G:'ietf-sztp-bootstrap-server',_Q:_AE,_R:'urn:ietf:params:xml:ns:yang:ietf-sztp-bootstrap-server',_S:_d},{_G:'ietf-yang-structure-ext',_Q:'2020-06-17',_R:'urn:ietf:params:xml:ns:yang:ietf-yang-structure-ext',_S:_d},{_G:'ietf-ztp-types',_Q:_v,_R:'urn:ietf:params:xml:ns:yang:ietf-ztp-types',_S:_d},{_G:'ietf-sztp-csr',_Q:_v,_R:'urn:ietf:params:xml:ns:yang:ietf-sztp-csr',_S:_d},{_G:'ietf-crypto-types',_Q:_v,_R:'urn:ietf:params:xml:ns:yang:ietf-crypto-types',_S:_d}]}};yl4conveyedinfo={_AA:{_AB:'TBD','module':[{_G:_AC,_Q:_u,_R:_AD,_S:_l},{_G:'ietf-inet-types',_Q:_u,_R:'urn:ietf:params:xml:ns:yang:ietf-inet-types',_S:_l},{_G:'ietf-sztp-conveyed-info',_Q:_AE,_R:'urn:ietf:params:xml:ns:yang:ietf-sztp-conveyed-info',_S:_d}]}}
	def __init__(A,dal,yl_obj,proxy_info,nvh):E='sztpd';D='yang';A.dal=dal;A.nvh=nvh;A.proxy_info=proxy_info;B=importlib_resources.files('yangcore')/D;C=importlib_resources.files(E)/D;F=yl_8525_to_7895(yl_obj);A.dm=yangson.DataModel(json.dumps(F),[B,C]);A.dm4conveyedinfo=yangson.DataModel(json.dumps(A.yl4conveyedinfo),[B,C]);G=importlib_resources.files(E)/'yang4errors';A.dm4errors=yangson.DataModel(json.dumps(A.yl4errors),[G,B,C])
	async def _insert_bootstrapping_log_record(C,device_id,bootstrapping_log_record):
		A=bootstrapping_log_record;D=_w+device_id[0]+'/bootstrapping-log';F={'sztpd:bootstrapping-log-record':A};await C.dal.handle_post_opstate_request(D,F)
		try:G=await C.dal.handle_get_config_request('/yangcore:preferences/outbound-interactions/sztpd:relay-bootstrapping-log-record-callout',{})
		except NodeNotFound:return
		E=G['sztpd:relay-bootstrapping-log-record-callout'];D=_x+E;B=await C.dal.handle_get_config_request(D,{});B=B[_J][0];assert E==B[_G];H=B[_Y][_h];I=B[_Y][_e];A[_N]=A[_N].strftime(_AF);A.pop('parent_id');J={'bootstrapping-log-record':A};K=_C;L=await C.nvh.plugins[H][_y][I](J,K);assert L is _C
	async def handle_get_restconf_root(C,request):
		D=request;J=_D;F=await C._check_auth(D,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(D,C.proxy_info);B[_A]={};B[_O]={_V:D.method,_W:D.path};E,K=utils.check_http_headers(D,C.supported_media_types,accept_required=_Z)
		if isinstance(E,web.Response):A=E;L=K;B[_A][_F]=A.status;B[_A][_E]=L;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;I=utils.Encoding[H.rsplit(_H,1)[1].upper()];A=web.Response(status=200);A.content_type=H
		if I==utils.Encoding.JSON:A.text='{\n    "ietf-restconf:restconf" : {\n        "data" : {},\n        "operations" : {},\n        "yang-library-version" : "2019-01-04"\n    }\n}\n'
		else:assert I==utils.Encoding.XML;A.text='<restconf xmlns="urn:ietf:params:xml:ns:yang:ietf-restconf">\n    <data/>\n    <operations/>\n    <yang-library-version>2016-06-21</yang-library-version>\n</restconf>\n'
		B[_A][_F]=A.status;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_get_yang_library_version(C,request):
		D=request;J=_D;F=await C._check_auth(D,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(D,C.proxy_info);B[_A]={};B[_O]={_V:D.method,_W:D.path};E,K=utils.check_http_headers(D,C.supported_media_types,accept_required=_Z)
		if isinstance(E,web.Response):A=E;L=K;B[_A][_F]=A.status;B[_A][_E]=L;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;I=utils.Encoding[H.rsplit(_H,1)[1].upper()];A=web.Response(status=200);A.content_type=H
		if I==utils.Encoding.JSON:A.text='{\n  "ietf-restconf:yang-library-version" : "2019-01-04"\n}'
		else:assert I==utils.Encoding.XML;A.text='<yang-library-version xmlns="urn:ietf:params:xml:ns:'+'yang:ietf-restconf">2019-01-04</yang-library-version>'
		B[_A][_F]=A.status;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_get_opstate_request(C,request):
		D=request;F=D.path[C.len_prefix_operational:];F=_D;G=await C._check_auth(D,F)
		if isinstance(G,web.Response):A=G;return A
		H=G;B={};B[_T]=H[0];B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(D,C.proxy_info);B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_Z)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(H,B);return A
		assert isinstance(E,str);I=E;assert I!=_K;J=utils.Encoding[I.rsplit(_H,1)[1].upper()]
		if F in('',_D,'/ietf-yang-library:yang-library'):A=web.Response(status=200);A.content_type=_g;A.text=json.dumps(sztpd_rfc8572_yang_library())
		else:A=web.Response(status=404);A.content_type=I;J=utils.Encoding[A.content_type.rsplit(_H,1)[1].upper()];K=utils.gen_rc_errors(_L,_a,error_message=_AG);N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(K,J,C.dm4errors,N);B[_A][_E]=K
		B[_A][_F]=A.status;await C._insert_bootstrapping_log_record(H,B);return A
	async def handle_get_config_request(C,request):
		D=request;I=D.path[C.len_prefix_running:];F=await C._check_auth(D,I)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(D,C.proxy_info);B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_Z)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;J=utils.Encoding[H.rsplit(_H,1)[1].upper()]
		if I in('',_D):A=web.Response(status=204)
		else:A=web.Response(status=404);A.content_type=H;J=utils.Encoding[A.content_type.rsplit(_H,1)[1].upper()];K=utils.gen_rc_errors(_L,_a,error_message=_AG);N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(K,J,C.dm4errors,N);B[_A][_E]=K
		B[_A][_F]=A.status;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_post_config_request(C,request):
		D=request;J=D.path[C.len_prefix_running:];F=await C._check_auth(D,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(D,C.proxy_info);B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_i)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;K=utils.Encoding[H.rsplit(_H,1)[1].upper()]
		if J in('',_D):A=web.Response(status=400);I=utils.gen_rc_errors(_b,_X,error_message=_z)
		else:A=web.Response(status=404);I=utils.gen_rc_errors(_L,_a,error_message=_A0)
		A.content_type=H;K=utils.Encoding[A.content_type.rsplit(_H,1)[1]].upper();N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(I,K,C.dm4errors,N);B[_A][_F]=A.status;B[_A][_E]=I;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_put_config_request(C,request):
		D=request;J=D.path[C.len_prefix_running:];F=await C._check_auth(D,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(D,C.proxy_info);B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_i)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;K=utils.Encoding[H.rsplit(_H,1)[1].upper()]
		if J in('',_D):A=web.Response(status=400);I=utils.gen_rc_errors(_b,_X,error_message=_z)
		else:A=web.Response(status=404);I=utils.gen_rc_errors(_L,_a,error_message=_A0)
		A.content_type=H;K=utils.Encoding[A.content_type.rsplit(_H,1)[1]].upper();N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(I,K,C.dm4errors,N);B[_A][_F]=A.status;B[_A][_E]=I;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_delete_config_request(C,request):
		D=request;L=D.path[C.len_prefix_running:];G=await C._check_auth(D,L)
		if isinstance(G,web.Response):A=G;return A
		H=G;B={};B[_T]=H[0];B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(D,C.proxy_info);B[_A]={};B[_O]={_V:D.method,_W:D.path};E,M=utils.check_http_headers(D,C.supported_media_types,accept_required=_i)
		if isinstance(E,web.Response):A=E;N=M;B[_A][_F]=A.status;B[_A][_E]=N;await C._insert_bootstrapping_log_record(H,B);return A
		assert isinstance(E,str);I=E
		if I==_K:J=_C
		else:J=utils.Encoding[I.rsplit(_H,1)[1].upper()]
		if L in('',_D):A=web.Response(status=400);F=_z;K=utils.gen_rc_errors(_b,_X,error_message=F)
		else:A=web.Response(status=404);F=_A0;K=utils.gen_rc_errors(_L,_a,error_message=F)
		A.content_type=I
		if J is _C:A.text=F
		else:O=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(K,J,C.dm4errors,O)
		B[_A][_F]=A.status;B[_A][_E]=K;await C._insert_bootstrapping_log_record(H,B);return A
	async def handle_action_request(C,request):
		D=request;J=D.path[C.len_prefix_operational:];F=await C._check_auth(D,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(D,C.proxy_info);B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_i)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;K=utils.Encoding[H.rsplit(_H,1)[1].upper()]
		if J in('',_D):A=web.Response(status=400);I=utils.gen_rc_errors(_b,_X,error_message='Resource does not support action.')
		else:A=web.Response(status=404);I=utils.gen_rc_errors(_L,_a,error_message=_AH)
		A.content_type=H;K=utils.Encoding[A.content_type.rsplit(_H,1)[1]].upper();N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(I,K,C.dm4errors,N);B[_A][_F]=A.status;B[_A][_E]=I;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_rpc_request(B,request):
		J='sleep';C=request;F=C.path[B.len_prefix_operations:];G=await B._check_auth(C,F)
		if isinstance(G,web.Response):D=G;return D
		E=G;A={};A[_T]=E[0];A[_N]=datetime.datetime.utcnow();A[_U]=utils.get_client_ip_address(C,B.proxy_info);A[_A]={};A[_O]={_V:C.method,_W:C.path}
		if F==_A1:
			async with B.nvh.fifolock(Read):
				if os.environ.get('SZTPD_INIT_MODE')and J in C.query:await asyncio.sleep(int(C.query[J]))
				D=await B._handle_get_bootstrapping_data_rpc(E,C,A);A[_A][_F]=D.status;await B._insert_bootstrapping_log_record(E,A);return D
		if F==_AI:D=await B._handle_report_progress_rpc(E,C,A);A[_A][_F]=D.status;await B._insert_bootstrapping_log_record(E,A);return D
		if F in(''or _D):D=web.Response(status=400);H=_AH
		else:D=web.Response(status=404);H='Unrecognized RPC.'
		I,K=utils.format_resp_and_msg(D,H,_A2,C,B.supported_media_types);A[_A][_F]=I.status;A[_A][_E]=K;await B._insert_bootstrapping_log_record(E,A);return I
	async def _check_auth(A,request,data_path):
		h='num-times-accessed';g='central-truststore-reference';f='identity-certificates';e='activation-code';d='client-cert-var';T='verification';P='sbi-access-stats';K='lifecycle-statistics';I='comment';H='failure';E='outcome';C=request;assert data_path[0]==_D
		def F(request,supported_media_types):
			E=supported_media_types;D='Accept';C=request;B=web.Response(status=401)
			if D in C.headers and any(C.headers[D]==A for A in E):B.content_type=C.headers[D]
			elif _j in C.headers and any(C.headers[_j]==A for A in E):B.content_type=C.headers[_j]
			else:B.content_type=_K
			if B.content_type!=_K:F=utils.Encoding[B.content_type.rsplit(_H,1)[1].upper()];G=utils.gen_rc_errors(_L,_A3);H=A.dm4errors.get_schema_node(_D);B.text=utils.obj_to_encoded_str(G,F,A.dm4errors,H)
			return B
		B={};B[_N]=datetime.datetime.utcnow();B[_U]=utils.get_client_ip_address(C,A.proxy_info);B['source-proxies']=list(C.forwarded);B['host']=C.host;B[_V]=C.method;B[_W]=C.path;J=set()
		if A.proxy_info is not _C and d in A.proxy_info:L=A.proxy_info[d]
		else:L=_C
		M=_C;N=C.transport.get_extra_info('peercert')
		if N is not _C:O=N['subject'][-1][0][1];J.add(O)
		elif L is not _C and C.headers.get(L)is not _C:i=C.headers.get(L);U=bytes(urllib.parse.unquote(i),'utf-8');M=x509.load_pem_x509_certificate(U,default_backend());j=M.subject;O=j.get_attributes_for_oid(x509.ObjectIdentifier('2.5.4.5'))[0].value;J.add(O)
		Q=_C;V=_C;R=C.headers.get('AUTHORIZATION')
		if R is not _C:Q,V=basicauth.decode(R);J.add(Q)
		if len(J)==0:B[E]=H;B[I]='Device provided no identification credentials.';await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		if len(J)!=1:B[E]=H;B[I]='Device provided mismatched authentication credentials ('+O+' != '+Q+').';await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		G=J.pop();D=_C;W=_w+G
		try:D=await A.dal.handle_get_opstate_request(W,{})
		except NodeNotFound:B[E]=H;B[I]='Device "'+G+'" not found for any tenant.';await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		k=_C;assert D is not _C;assert _A4 in D;D=D[_A4][0]
		if e in D:
			if R is _C:B[E]=H;B[I]='Activation code required but none passed for serial number '+G;await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
			X=D[e];assert X.startswith('$5$')
			if not sha256_crypt.verify(V,X):B[E]=H;B[I]='Activation code mismatch for serial number '+G;await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		assert _m in D;l=_AJ+D[_m];Y=await A.dal.handle_get_config_request(l,{})
		if f in Y[_A5][0]:
			if N is _C and M is _C:B[E]=H;B[I]='Client cert required but none passed for serial number '+G;await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
			if N:Z=C.transport.get_extra_info(_AK);assert Z is not _C;a=Z.getpeercert(_Z)
			else:assert M is not _C;a=U
			S=Y[_A5][0][f];assert T in S;assert g in S[T];b=S[T][g];m='/ietf-truststore:truststore/certificate-bags/certificate-bag='+b['certificate-bag']+'/certificate='+b['certificate'];n=await A.dal.handle_get_config_request(m,{});o=n['ietf-truststore:certificate'][0]['cert-data'];p=base64.b64decode(o);q,r=der_decoder(p,asn1Spec=rfc5652.ContentInfo());assert not r;s=utils.degenerate_cms_obj_to_ders(q);t=ValidationContext(trust_roots=s);u=CertificateValidator(a,validation_context=t)
			try:u._validate_path()
			except PathBuildingError:B[E]=H;B[I]="Client cert for serial number '"+G+"' does not validate using trust anchors specified by device-type '"+D[_m]+"'";await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		B[E]='success';await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);v=W+'/lifecycle-statistics';c=datetime.datetime.utcnow().strftime(_AF)
		if D[K][P][h]==0:D[K][P]['first-accessed']=c
		D[K][P]['last-accessed']=c;D[K][P][h]+=1;await A.dal.handle_put_opstate_request(v,D[K]);return G,k
	async def _handle_get_bootstrapping_data_rpc(B,device_id,request,bootstrapping_log_record):
		AL='ietf-sztp-bootstrap-server:output';AK='content';AJ='contentType';AI='sztpd:configuration';AH='sztpd:script';AG='/sztpd:conveyed-information/scripts/script=';AF='hash-value';AE='hash-algorithm';AD='os-version';AC='os-name';AB='address';AA='referenced-definition';A3=device_id;A2='post-configuration-script';A1='configuration';A0='pre-configuration-script';z='trust-anchor';y='port';x='bootstrap-server';w='ietf-sztp-conveyed-info:redirect-information';m='image-verification';l='download-uri';k='boot-image';j='via-onboarding-response';i='via-redirect-response';h='reference';g='selected-response';c='response-manager';U=request;T='ietf-sztp-conveyed-info:onboarding-information';M='via-dynamic-callout';J='managed-response';I='response-details';E='get-bootstrapping-data';D='conveyed-information';C=bootstrapping_log_record;d,AM=utils.check_http_headers(U,B.supported_media_types,accept_required=_Z)
		if isinstance(d,web.Response):A=d;AN=AM;C[_A][_F]=A.status;C[_A][_E]=AN;return A
		assert isinstance(d,str);N=d;assert N!=_K;P=utils.Encoding[N.rsplit(_H,1)[1].upper()];O=_C
		if U.body_exists:
			AO=await U.text();AP=utils.Encoding[U.headers[_j].rsplit(_H,1)[1].upper()];F=B.dm.get_schema_node(_A1)
			try:O=utils.encoded_str_to_obj(AO,AP,B.dm,F)
			except utils.TranscodingError as V:A=web.Response(status=400);n=_n+str(V);A.content_type=N;G=utils.gen_rc_errors(_L,_f,error_message=n);F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,P,B.dm4errors,F);C[_A][_E]=G;return A
			if not _k in O:A=web.Response(status=400);n=_n+_AL;A.content_type=N;G=utils.gen_rc_errors(_L,_f,error_message=n);F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,P,B.dm4errors,F);C[_A][_E]=G;return A
		if O is _C:C[_O]['body']=[_C]
		else:C[_O]['body']=O
		C[_B]={};C[_B][E]={};A4=_C
		if O:
			try:A4=O[_k]
			except KeyError:raise NotImplementedError;A=web.Response(status=400);A.content_type=_g;G=utils.gen_rc_errors(_L,_X,error_message='RPC "input" node missing.');A.text=utils.enc_rc_errors('json',G);return A
			F=B.dm.get_schema_node('/ietf-sztp-bootstrap-server:get-bootstrapping-data/input')
			try:F.from_raw(A4)
			except yangson.exceptions.RawMemberError as V:A=web.Response(status=400);A.content_type=_g;G=utils.gen_rc_errors(_L,_X,error_message='RPC "input" node fails YANG validation here: '+str(V));A.text=utils.enc_rc_errors('json',G);return A
		AQ=_w+A3[0];W=await B.dal.handle_get_config_request(AQ,{});W=W[_A4][0];AR=_AJ+W[_m];Z=await B.dal.handle_get_config_request(AR,{});Z=Z[_A5][0]
		if not any(c in A for A in[W,Z]):A=web.Response(status=404);A.content_type=N;G=utils.gen_rc_errors(_b,_o,error_message='No responses configured.');F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,P,B.dm4errors,F);C[_A][_E]=G;C[_B][E][g]='SZTPD_NO_RESPONSE_CONFIGURED';return A
		H=_C;o={_A6:utils.get_client_ip_address(U,B.proxy_info)}
		if O:o|=O[_k]
		if c in W:p=W[c];H=rfc8572_utils.find_matched_response_for_input(o,p)
		if H is _C and c in Z:p=Z[c];H=rfc8572_utils.find_matched_response_for_input(o,p)
		if H is _C or'none'in H[_A]:
			if H is _C:C[_B][E][g]='SZTPD_NO_MATCH_FOUND'
			else:C[_B][E][g]=H[_G]+" (explicit 'none')"
			A=web.Response(status=404);A.content_type=N;G=utils.gen_rc_errors(_b,_o,error_message='No matching responses configured.');F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,P,B.dm4errors,F);C[_A][_E]=G;return A
		C[_B][E][g]=H[_G];C[_B][E][I]={J:{}}
		if D in H[_A]:
			C[_B][E][I][J]={D:{}};L={}
			if M in H[_A][D]:
				C[_B][E][I][J][D]={M:{}};assert h in H[_A][D][M];q=H[_A][D][M][h];C[_B][E][I][J][D][M][_G]=q;r=await B.dal.handle_get_config_request(_x+q,{});R=r[_J][0];assert q==R[_G];C[_B][E][I][J][D][M][_p]=R[_p];e={};e[_T]=A3[0];e[_A6]=utils.get_client_ip_address(U,B.proxy_info)
				if O:e[_AM]=O
				if _Y in R:
					C[_B][E][I][J][D][M][_A7]=_e;A5=R[_Y][_h];A6=R[_Y][_e];C[_B][E][I][J][D][M][_AN]={_h:A5,_e:A6};C[_B][E][I][J][D][M][_c]={}
					if _q in R:A7=R[_q]
					else:A7=_C
					K=_C
					try:K=await B.nvh.plugins[A5][_y][A6](e,A7)
					except Exception as V:C[_B][E][I][J][D][M][_c][_AO]=str(V);A=web.Response(status=500);A.content_type=N;G=utils.gen_rc_errors(_b,_r,error_message='Server '+'encountered an error while trying to generate '+'a response: '+str(V));F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,P,B.dm4errors,F);C[_A][_E]=G;return A
					assert K and isinstance(K,dict)
					if _I in K:
						assert len(K[_I][_M])==1
						if any(A==K[_I][_M][0][_P]for A in(_X,'too-big',_AP,_A2,_AQ,_AR,_a,_AS,_f)):A=web.Response(status=400)
						elif any(A==K[_I][_M][0][_P]for A in _A3):A=web.Response(status=403)
						elif any(A==K[_I][_M][0][_P]for A in('in-use',_AT,_AU,_AV,_o)):A=web.Response(status=409)
						elif any(A==K[_I][_M][0][_P]for A in(_AW,_AX,_AY)):A=web.Response(status=500)
						elif any(A==K[_I][_M][0][_P]for A in _r):A=web.Response(status=501)
						else:raise NotImplementedError(_AZ+K[_I][_M][0][_P])
						A.content_type=N;G=K;F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,P,B.dm4errors,F);C[_A][_E]=K;C[_B][E][I][J][D][M][_c][_s]='Returning an RPC-error provided by function (NOTE: RPC-error '+'!= exception, hence a normal exit).';return A
					C[_B][E][I][J][D][M][_c][_s]='Returning conveyed information provided by function.'
				elif _A8 in r[_J][0]:C[_B][E][I][J][D][M][_A7]=_t;raise NotImplementedError('webhooks were disabled!')
				else:raise NotImplementedError('unhandled dynamic callout type: '+str(r[_J][0]))
				L=K[D]
			elif i in H[_A][D]:
				C[_B][E][I][J][D]={i:{}};L[w]={};L[w][x]=[];a=H[_A][D][i][h];C[_B][E][I][J][D][i]={AA:a};s=await B.dal.handle_get_config_request('/sztpd:responses/redirect-response='+a,{})
				for AS in s['sztpd:redirect-response'][0]['redirect-information'][x]:
					S=await B.dal.handle_get_config_request('/sztpd:conveyed-information/bootstrap-servers/bootstrap-server='+AS,{});S=S['sztpd:bootstrap-server'][0];f={};f[AB]=S[AB]
					if y in S:f[y]=S[y]
					if z in S:f[z]=S[z]
					L[w][x].append(f)
			elif j in H[_A][D]:
				C[_B][E][I][J][D]={j:{}};L[T]={};a=H[_A][D][j][h];C[_B][E][I][J][D][j]={AA:a};s=await B.dal.handle_get_config_request('/sztpd:responses/onboarding-response='+a,{});Q=s['sztpd:onboarding-response'][0]['onboarding-information']
				if k in Q:
					AT=Q[k];AU=await B.dal.handle_get_config_request('/sztpd:conveyed-information/boot-images/boot-image='+AT,{});X=AU['sztpd:boot-image'][0];L[T][k]={};Y=L[T][k];Y[AC]=X[AC];Y[AD]=X[AD]
					if l in X:
						Y[l]=[]
						for AV in X[l]:Y[l].append(AV)
					if m in X:
						Y[m]=[]
						for A8 in X[m]:t={};t[AE]=A8[AE];t[AF]=A8[AF];Y[m].append(t)
				if A0 in Q:AW=Q[A0];AX=await B.dal.handle_get_config_request(AG+AW,{});L[T][A0]=AX[AH][0]['code']
				if A1 in Q:AY=Q[A1];A9=await B.dal.handle_get_config_request('/sztpd:conveyed-information/configurations/configuration='+AY,{});L[T]['configuration-handling']=A9[AI][0][_B];L[T][A1]=A9[AI][0]['config-data']
				if A2 in Q:AZ=Q[A2];Aa=await B.dal.handle_get_config_request(AG+AZ,{});L[T][A2]=Aa[AH][0]['code']
		else:raise NotImplementedError('unhandled response type: '+str(H[_A]))
		b=rfc5652.ContentInfo()
		if N==_g:b[AJ]=B.id_ct_sztpConveyedInfoJSON;b[AK]=encode_der(json.dumps(L,indent=2),asn1Spec=univ.OctetString())
		else:assert N==_A9;b[AJ]=B.id_ct_sztpConveyedInfoXML;F=B.dm4conveyedinfo.get_schema_node(_D);assert F;Ab=utils.obj_to_encoded_str(L,P,B.dm4conveyedinfo,F,strip_wrapper=_Z);b[AK]=encode_der(Ab,asn1Spec=univ.OctetString())
		Ac=encode_der(b,rfc5652.ContentInfo());u=base64.b64encode(Ac).decode('ASCII');Ad=base64.b64decode(u);Ae=base64.b64encode(Ad).decode('ASCII');assert u==Ae;v={};v[AL]={};v[AL][D]=u;A=web.Response(status=200);A.content_type=N;F=B.dm.get_schema_node(_A1);A.text=utils.obj_to_encoded_str(v,P,B.dm,F);return A
	async def _handle_report_progress_rpc(C,device_id,request,bootstrapping_log_record):
		f='remote-port';e='webhook-results';d='sztpd:relay-progress-report-callout';X='tcp-client-parameters';U='http';K=request;G='dynamic-callout';E='report-progress';B=bootstrapping_log_record;S,g=utils.check_http_headers(K,C.supported_media_types,accept_required=_i)
		if isinstance(S,web.Response):A=S;h=g;B[_A][_F]=A.status;B[_A][_E]=h;return A
		assert isinstance(S,str);J=S
		if J==_K:L=_K
		else:i=J.rsplit(_H,1)[1].upper();L=utils.Encoding[i]
		if not K.body_exists:
			M='RPC "input" node missing (required for "report-progress").';A=web.Response(status=400);A.content_type=J
			if A.content_type==_K:A.text=M
			else:F=utils.gen_rc_errors(_L,_X,error_message=M);H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H)
			B[_A][_E]=A.text;return A
		j=utils.Encoding[K.headers[_j].rsplit(_H,1)[1].upper()];k=await K.text();H=C.dm.get_schema_node(_AI)
		try:Q=utils.encoded_str_to_obj(k,j,C.dm,H)
		except utils.TranscodingError as N:A=web.Response(status=400);M=_n+str(N);A.content_type=J;F=utils.gen_rc_errors(_L,_f,error_message=M);H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H);B[_A][_E]=F;return A
		if not _k in Q:
			A=web.Response(status=400)
			if not _k in Q:M=_n+_AL
			A.content_type=J;F=utils.gen_rc_errors(_L,_f,error_message=M);H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H);B[_A][_E]=F;return A
		B[_O]['body']=Q;B[_B]={};B[_B][E]={};B[_B][E][G]={};V='/yangcore:preferences/outbound-interactions/'+d
		try:l=await C.dal.handle_get_config_request(V,{})
		except NodeNotFound:B[_B][E][G]['no-callout-configured']=[_C];A=web.Response(status=204);return A
		W=l[d];B[_B][E][G][_G]=W;V=_x+W;I=await C.dal.handle_get_config_request(V,{});assert W==I[_J][0][_G];B[_B][E][G][_p]=I[_J][0][_p];O={};O[_T]=device_id[0];O[_A6]=utils.get_client_ip_address(K,C.proxy_info);Y=K.transport.get_extra_info(_AK)
		if Y:
			Z=Y.getpeercert(_Z)
			if Z:O['identity-certificate']=Z
		if Q:O[_AM]=Q
		if _Y in I[_J][0]:
			B[_B][E][G][_A7]=_e;a=I[_J][0][_Y][_h];b=I[_J][0][_Y][_e];B[_B][E][G][_AN]={_h:a,_e:b};B[_B][E][G][_c]={}
			if _q in I[_J][0]:c=I[_J][0][_q]
			else:c=_C
			D=_C
			try:D=await C.nvh.plugins[a][_y][b](O,c)
			except Exception as N:B[_B][E][G][_c][_AO]=str(N);A=web.Response(status=500);A.content_type=J;F=utils.gen_rc_errors(_b,_r,error_message='Server encountered an error while trying '+'to process the progress report: '+str(N));H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H);B[_A][_E]=F;return A
			if D:
				assert isinstance(D,dict);assert len(D)==1;assert _I in D;assert len(D[_I][_M])==1
				if any(A==D[_I][_M][0][_P]for A in(_X,'too-big',_AP,_A2,_AQ,_AR,_a,_AS,_f)):A=web.Response(status=400)
				elif any(A==D[_I][_M][0][_P]for A in _A3):A=web.Response(status=403)
				elif any(A==D[_I][_M][0][_P]for A in('in-use',_AT,_AU,_AV,_o)):A=web.Response(status=409)
				elif any(A==D[_I][_M][0][_P]for A in(_AW,_AX,_AY)):A=web.Response(status=500)
				elif any(A==D[_I][_M][0][_P]for A in _r):A=web.Response(status=501)
				else:raise NotImplementedError(_AZ+D[_I][_M][0][_P])
				A.content_type=J;F=D;H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H);B[_A][_E]=D;B[_B][E][G][_c][_s]='Returning an RPC-error provided by function '+'(NOTE: RPC-error != exception, hence a normal exit).';return A
			B[_B][E][G][_c][_s]='Function returned no output (normal)'
		elif _A8 in I[_J][0]:
			B[_B][E][G][e]={_t:[]}
			for P in I[_J][0][_A8][_t]:
				R={};R[_G]=P[_G]
				if U in P:
					T='http://'+P[U][X]['remote-address']
					if f in P[U][X]:T+=':'+str(P[U][X][f])
					T+='/relay-notification';R['uri']=T
					try:
						async with aiohttp.ClientSession()as m:A=await m.post(T,data=O)
					except aiohttp.client_exceptions.ClientConnectorError as N:R['connection-error']=str(N)
					else:
						R['http-status-code']=A.status
						if A.status==200:break
				else:assert'https'in P;raise NotImplementedError('https-based webhook is not supported yet.')
				B[_B][E][G][e][_t].append(R)
		else:raise NotImplementedError('unrecognized callout type '+str(I[_J][0]))
		A=web.Response(status=204);return A