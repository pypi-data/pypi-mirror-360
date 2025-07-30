# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

import re
def test_match_criteria(key_dict,match_criteria):
	H='not';G='regex';F='value';E=False;C='key';B=key_dict
	for A in match_criteria['match']:
		if'present'in A:D=A[C]in B
		elif F in A:
			if A[C]not in B:return E
			D=A[F]==B[A[C]]
		elif G in A:
			if A[C]not in B:return E
			D=re.search(A[G],B[A[C]])
		else:raise NotImplementedError("Unrecognized 'match' test type: "+A)
		if D and H in A:return E
		if not D and H not in A:return E
	return True
def find_matched_response_for_input(key_dict,response_manager):
	B='match-criteria'
	for A in response_manager['matched-response']:
		if not B in A:return A
		if test_match_criteria(key_dict,A[B]):return A