"""!
@file catm.py
@version 1
@author Fumitaka ENDO
@date 2025-01-28T12:05:12+09:00
@brief CATM readout pad generation package 
"""
import numpy as np
from .basepad import TReadoutPadArray
from .basepad import generate_oblong_4_polygon
from .basepad import generate_regular_n_polygon
import argparse 

def get_beam_tpc_array():  
  """!
  @brief get beam tpc pad array
  @detail pad length withou gap = 5. number of pad = 22 (11 x 2)
  @return beam tpc pad array (TReadoutPadArray)
  """
  base_padinfo = generate_regular_n_polygon(3, 4.74, 90, False)

  pad = TReadoutPadArray()
  pad.add_basepad(base_padinfo)
  PADDISTANCE = 5 
  gid = 0 

  for i in range(11):
    pad.add_pads([i*PADDISTANCE/2-12.5, -99, PADDISTANCE/np.sqrt(3)/2*((i-1)%2)-2.886751345948129-255], 0, 0, 180*((i-1)%2), 0, gid)
    pad.id = gid 
    gid += 1
  for i in range(11):
    pad.add_pads([(i)*PADDISTANCE/2-12.5, -99, PADDISTANCE/np.sqrt(3)/2*((i)%2) + np.sqrt(3)*PADDISTANCE/2-2.886751345948129-255], 0, 0, 180*((i)%2), 0, gid)
    pad.id = gid 
    gid += 1

  return pad 

def get_recoil_tpc_array():
  """!
  @brief get recoil tpc pad array
  @detail pad length withou gap = 7. number of pad = 4048 ( (23x2) x 88 )
  @return recoil tpc pad array (TReadoutPadArray)
  """
  base_padinfo = generate_regular_n_polygon(3, 6.9133974596, 90, False)

  pad = TReadoutPadArray()
  pad.add_basepad(base_padinfo)
  PADDISTANCE = 7
  gid = 0 
  zoffset = -152.25

  for j in range(44):

    for i in range(23):
      h = PADDISTANCE*np.sqrt(3)/2
      if i%2 == 0:
        x = -i*h -h/3
      else:
        x = -i*h -h/3 -h/3

      pad.add_pads([x, -99, PADDISTANCE*j + zoffset], 0, 0, -90*((-1)**i), 0, gid)
      pad.id = gid 
      gid += 1

    for i in range(23):
      h = PADDISTANCE*np.sqrt(3)/2
      if i%2 == 0:
        x = -i*h - h*2/3
      else:
        x = -i*h - h/3 
      pad.add_pads([x, -99, PADDISTANCE/2+PADDISTANCE*j + zoffset], 0, 0, -90*((-1)**(i+1)), 0, gid)
      pad.id = gid 
      gid += 1

  for j in range(44):
    for i in range(23):
      h = PADDISTANCE*np.sqrt(3)/2
      if i%2 == 0:
        x = i*h + h/3
      else:
        x = i*h + h*2/3

      pad.add_pads([x, -99, PADDISTANCE*j + zoffset], 0, 0, -90*((-1)**(i+1)), 0, gid)
      pad.id = gid 
      gid += 1

    for i in range(23):
      h = PADDISTANCE*np.sqrt(3)/2
      if i%2 == 0:
        x = i*h + h*2/3
      else:
        x = i*h + h/3
      pad.add_pads([x, -99, PADDISTANCE/2+PADDISTANCE*j + zoffset], 0, 0, -90*((-1)**(i)), 0, gid)
      pad.id = gid 
      gid += 1
        
  return pad 

def get_ssd_array():
  """!
  @brief get ssd pad array
  @return ssd pad array (TReadoutPadArray)
  """
  base_padinfo = generate_oblong_4_polygon(90.6/8, 90.6,'yz',False)

  pad = TReadoutPadArray()
  pad.add_basepad(base_padinfo)
  gid = 0

  for i in range(8):
    pad.add_pads([-255 , 54, -42.55 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  for i in range(8):
    pad.add_pads([-255 , 54,  65.45 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  for i in range(8):
    pad.add_pads([-255 , 54, 168.45 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  
  for i in range(8):
    pad.add_pads([-255 , -54, -42.55 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  for i in range(8):
    pad.add_pads([-255 , -54,  65.45 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  for i in range(8):
    pad.add_pads([-255 , -54, 168.45 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1

  for i in range(8):
    pad.add_pads([255 , 54, -42.55 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  for i in range(8):
    pad.add_pads([255 , 54,  65.45 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  for i in range(8):
    pad.add_pads([255 , 54, 168.45 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  
  for i in range(8):
    pad.add_pads([255 , -54, -42.55 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  for i in range(8):
    pad.add_pads([255 , -54,  65.45 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1
  for i in range(8):
    pad.add_pads([255 , -54, 168.45 + 90.6/8*i - 90.6/2 ], 0, 0, 0, 0, gid)
    pad.id = gid
    gid += 1

  return pad

def check_pad_view():
    """!
    @brief check each pad configuration
    
    @details draw pad alignment using matplotlib
    
    CLI argument:
    @arg -pad select detector (beam tpc, recoil tpc, ssd). default is recoil-tpc
    @arg -plane select draw plane. default is xz
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-pad", help="pad type (beam-tpc or recoil-tpc or ssd) default = recoil-tpc", type=str, default="recoil-tpc")
    parser.add_argument("-plane", help="choose draw plane. default = xz", type=str, default="xz")

    args = parser.parse_args()
    pad_name: str = args.pad
    plane: str = args.plane

    if pad_name == 'recoil-tpc':
      pad_array = get_recoil_tpc_array()

    elif pad_name == 'beam-tpc':
      pad_array = get_beam_tpc_array()

    elif pad_name == 'ssd':
      pad_array = get_ssd_array()

    else:
        print('experiment number does not exist')
    
    if pad_array is not None:
      pad_array.show_pads(plane)