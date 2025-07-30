# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

_E='/sztpd:devices/device='
_D='sztpd'
_C='device'
_B='activation-code'
_A=None
import os,re,copy,json,base64,datetime,importlib.resources as importlib_resources
from passlib.hash import sha256_crypt
from pyasn1.codec.der.decoder import decode as decode_der
from pyasn1.error import PyAsn1Error
from pyasn1_modules import rfc5652
from cryptography import x509
from yangcore import utils
from yangcore import yangcore
from yangcore.native import NativeViewHandler
from yangcore.dal import CreateCallbackFailed,CreateOrChangeCallbackFailed
from.rfc8572 import RFC8572ViewHandler
from sztpd.yl import sztpd_native_yang_library,sztpd_rfc8572_yang_library
def sztpd_firsttime_callback():
	B='Yes';A=os.environ.get('SZTPD_ACCEPT_CONTRACT')
	if A is _A:
		print('');C=importlib_resources.files(_D)/'LICENSE'
		with open(C,'r',encoding='utf-8')as D:print(D.read())
		print('First time initialization.  Please accept the license terms.');print('');print('By entering "Yes" below, you agree to be bound to the terms\n'+'and conditions contained on this screen with Watsen Networks.');print('');E=input('Please enter "Yes" or "No": ')
		if E!=B:print('');print('Thank you for your consideration.');print('');raise yangcore.ContractNotAccepted()
	elif A!=B:print('');print('The "SZTPD_ACCEPT_CONTRACT" environment variable is set to a\n'+'value other than "Yes".  Please correct the value and try again.');print('');raise yangcore.UnrecognizedAcceptValue()
	return sztpd_native_yang_library()
def run(db_url,cacert_param=_A,cert_param=_A,key_param=_A):
	F='/sztpd:conveyed-information/bootstrap-servers/bootstrap-server/trust-anchor';E='/sztpd:devices/device';B='callback_func';A='schema_path'
	try:assert __name__.rsplit('.',1)[1]==_D;D=yangcore.init(sztpd_firsttime_callback,db_url,cacert_param,cert_param,key_param,_D)
	except Exception as C:print('yangcore.init() threw exception: '+C.__class__.__name__);print(str(C));raise C
	G={'yangcore:native-interface':{'create_callback':[{A:E,B:_handle_device_created},{A:F,B:_handle_bss_trust_anchor_cert_created_or_changed}],'delete_callback':[{A:E,B:_handle_device_deleted}],'change_callback':[{A:'/sztpd:devices/device/activation-code',B:_handle_device_act_code_changed},{A:F,B:_handle_bss_trust_anchor_cert_created_or_changed}]},'sztpd:rfc8572-interface':{'view-handler':RFC8572ViewHandler,'yang-library-func':sztpd_rfc8572_yang_library}};yangcore.run(D,G);del D;return 0
async def _handle_device_created_post_sweep(watched_node_path,conn,opaque):
	e='verification-result';d='failure';c='tenant';b='function';a='functions';Z='plugin';Y='call-function';X='ownership-authorization';N='verification-results';M='dynamic-callout';L='device-type';K='record_id';J='=[^/]*';G=opaque;F=watched_node_path;B=conn;A=G;C=A.dal._get_row_data_for_list_path(F,B);D=re.sub(J,'',F);f=A.dal._get_jsob_for_record_id_in_table(D,C[K],B);O='/sztpd:device-types/device-type='+f[_C][L];C=A.dal._get_row_data_for_list_path(O,B);D=re.sub(J,'',O);P=A.dal._get_jsob_for_record_id_in_table(D,C[K],B)
	if X in P[L]:
		Q='/yangcore:dynamic-callouts/dynamic-callout='+P[L][X][M]['reference'];C=A.dal._get_row_data_for_list_path(Q,B);D=re.sub(J,'',Q);R=A.dal._get_jsob_for_record_id_in_table(D,C[K],B)
		if Y in R[M]:
			E=R[M][Y];assert E[Z]in A.plugins;S=A.plugins[E[Z]];assert a in S;T=S[a];assert E[b]in T;g=T[E[b]];H=F.split('/')
			if H[2]==c:U=H[1].split('=')[1]
			else:U='not-applicable'
			V=H[-1].split('=')[1];h={c:U,'serial-number':[V]};G=_A;I=g(h,G);W=d
			if N in I:
				if e in I[N]:W=I[N][e][0]['result']
			if W==d:raise CreateCallbackFailed('Unable to verify ownership for device: '+V)
		else:raise NotImplementedError('webhooks for ownership verification not implemented yet')
	else:0
async def _handle_device_created(watched_node_path,jsob,jsob_data_path,nvh):
	C=jsob;B=nvh;assert jsob_data_path.startswith(_E);assert isinstance(C,dict);assert _C in C;A=C[_C]
	if B.dal.post_dal_callbacks is _A:B.dal.post_dal_callbacks=[]
	B.dal.post_dal_callbacks.append((_handle_device_created_post_sweep,watched_node_path,B));A['lifecycle-statistics']={'nbi-access-stats':{'created':datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),'num-times-modified':0},'sbi-access-stats':{'num-times-accessed':0}};A['bootstrapping-log']={'bootstrapping-log-record':[]}
	if _B in A and A[_B].startswith('$0$'):A[_B]=sha256_crypt.using(rounds=1000).hash(A[_B][3:])
async def _handle_device_act_code_changed(watched_node_path,jsob,jsob_data_path,nvh):
	C=jsob_data_path;B=jsob;assert C.startswith(_E);assert isinstance(B,dict);assert watched_node_path==C+'/activation-code';assert nvh is not _A;assert _C in B;A=B[_C]
	if _B in A and A[_B].startswith('$0$'):A[_B]=sha256_crypt.using(rounds=1000).hash(A[_B][3:])
async def _handle_device_deleted(data_path,nvh):assert data_path.startswith(_E);assert nvh is not _A
async def _handle_bss_trust_anchor_cert_created_or_changed(watched_node_path,jsob,jsob_data_path,opaque):
	H='": ';B=watched_node_path;I=jsob['bootstrap-server']['trust-anchor'];J=base64.b64decode(I)
	try:K,O=decode_der(J,asn1Spec=rfc5652.ContentInfo())
	except PyAsn1Error as F:raise CreateOrChangeCallbackFailed('Parsing trust anchor certificate CMS structure failed for '+B+' ('+str(F)+')')from F
	L=utils.degenerate_cms_obj_to_ders(K);A=[]
	for M in L:N=x509.load_der_x509_certificate(M);A.append(N)
	D=[A for A in A if A.subject==A.issuer]
	if len(D)==0:raise CreateOrChangeCallbackFailed('Trust anchor certificates must encode a root (self-signed) certificate: '+B)
	if len(D)>1:raise CreateOrChangeCallbackFailed('Trust anchor certificates must encode no more than one root '+'(self-signed) certificate ('+str(len(D))+' found): '+B)
	G=D[0];A.remove(G);C=G
	while len(A)!=0:
		E=[A for A in A if A.issuer==C.subject]
		if len(E)==0:raise CreateOrChangeCallbackFailed('Trust anchor certificates must not encode superfluous certificates. '+'The CMS encodes additional certs not issued by the trust anchor."'+str(C.subject)+H+B)
		if len(E)>1:raise CreateOrChangeCallbackFailed('Trust anchor certificates must encode a single chain of certificates.  Found '+str(len(E))+' certificates issued by "'+str(C.subject)+H+B)
		C=E[0];A.remove(C)