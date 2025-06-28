"""!
@file trialpad.py
@version 1
@author Fumitka ENDO
@date 2025-06-28T15:53:53+09:00
@brief trial pad configuration utillities
"""
import numpy as np
import catmlib.readoutpad.basepad as basepad
import argparse 

def get_original_beamtpc_pad_array():
	"""!
    @brief get 22 pads configuration considered before h445-1 exp
	@return object of pad array (TReadoutPadArray)
	"""
	base_padinfo = basepad.generate_regular_n_polygon(3, 4.74, 90, False)

	pad = basepad.TReadoutPadArray()
	pad.add_basepad(base_padinfo)
	pad_distance = 5
	gid = 0

	for i in range(11):
		pad.add_pads([i*pad_distance/2, 0, pad_distance/np.sqrt(3)/2*((i-1)%2)], 0, 0, 180*((i-1)%2), 0, gid)
		pad.id = gid
		gid += 1
	for i in range(11):
		pad.add_pads([i*pad_distance/2, 0, pad_distance/np.sqrt(3)/2*((i)%2) + np.sqrt(3)*pad_distance/2], 0, 0, 180*((i)%2), 0, gid)
		pad.id = gid
		gid += 1

	return pad

def get_beamtpc_one_fourth_shift_pad_array():
	"""!
    @brief get 22 pads configuration considered before h445-5 exp
	@return object of pad array (TReadoutPadArray)
	"""
	base_padinfo = basepad.generate_regular_n_polygon(3, 4.74, 90, False)

	pad = basepad.TReadoutPadArray()
	pad.add_basepad(base_padinfo)
	pad_distance = 5
	gid = 0

	for i in range(11):
		pad.add_pads([i*pad_distance/2, 0, pad_distance/np.sqrt(3)/2*((i-1)%2)], 0, 0, 180*((i-1)%2), 0, gid)
		pad.id = gid
		gid += 1
	for i in range(11):
		pad.add_pads([(i+0.5)*pad_distance/2, 0, pad_distance/np.sqrt(3)/2*((i)%2) + np.sqrt(3)*pad_distance/2], 0, 0, 180*((i)%2), 0, gid)
		pad.id = gid
		gid += 1

	return pad

def get_beamtpc_60ch_pad_array():
	"""!
    @brief get 60 pads configuration considered before h445-5 exp
	@return object of pad array (TReadoutPadArray)
	"""
	base_padinfo = basepad.generate_regular_n_polygon(3, 2.75, 90,False)

	pad = basepad.TReadoutPadArray()
	pad.add_basepad(base_padinfo)
	pad_distance = 3
	gid = 0

	nmax=21
	offset = 15.75

	for i in range(nmax+1):
		if i >1:
			pad.add_pads([(i-0.5)*pad_distance/2-offset, 0, pad_distance/np.sqrt(3)/2*((i-1)%2)], 0, 0, 180*((i-1)%2), 0, gid)
			pad.id = gid
			gid += 1
	for i in range(nmax):
		if i >0:
			pad.add_pads([((i+0))*pad_distance/2-offset, 0, pad_distance/np.sqrt(3)/2*((i)%2) + np.sqrt(3)*pad_distance/2], 0, 0, 180*((i)%2), 0, gid)
			pad.id = gid
			gid += 1
	for i in range(nmax):
		if i < nmax-1:
			pad.add_pads([(i+0.5)*pad_distance/2-offset, 0, pad_distance/np.sqrt(3)/2*((i-1)%2) + 2*np.sqrt(3)*pad_distance/2] , 0, 0, 180*((i-1)%2), 0, gid)
			pad.id = gid
			gid += 1

	return pad

def get_trail_beamtpc_array(version=0):
	"""!
    @brief get trial pad configuration of beam tpc 

	@param version select version
	@return object of pad array (TReadoutPadArray)
	"""
	if version == 0:
		return get_beamtpc_one_fourth_shift_pad_array()
	
	elif version == 1:
		return get_beamtpc_one_fourth_shift_pad_array()
	
	elif version == 2:
		return get_beamtpc_60ch_pad_array()
	
def check_pad_configuration():
	"""!
    @brief plot trial pad configuration

    CLI argument:
    @arg pad-type select trial pad type
	@arg pad-version select trail pad version
	@arg pad-plane select pad plane for ploting
	"""

	parser = argparse.ArgumentParser()
	parser.add_argument("-t","--pad-type", help="select trial pad type", type=str, default="beamtpc")
	parser.add_argument("-tv","--pad-version", help="select trail pad version", type=int, default=0)	
	parser.add_argument("-pp","--pad-plane", help="select pad plane for ploting", type=str, default="xz")	
	args = parser.parse_args()
	
	pad_type: str = args.pad_type
	pad_version: int = args.pad_version
	pad_plane: str = args.pad_plane

	if pad_type == "beamtpc":
		pad = get_trail_beamtpc_array(pad_version)
		pad.show_pads(pad_plane)
	
	else:
		print('trial pad type dose not exist')