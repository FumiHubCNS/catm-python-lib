"""!
# @file basepad.py
# @version 1.1
# @author Fumitaka ENDO
# @date 2025-07-30T10:42:16+09:00
# @brief Basic readout pad generation package 
"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

class TBasePadShapeClass():
  """!
  @class TBasePadShapeClass
  @brief Generate pad information
  """

  def __init__(self):
    """!
    @brief initialze object
    @param mapping label of axsis (0:x, 1:y, 2:z)
    @param center center position in pad
    @param polygon list of vertices
    @return None
    """
    self.mapping = {'x': 0, 'y': 1, 'z': 2}
    self.center = [0, 0, 0]
    self.polygon = []

  def set_center(self, x, y, z):
    """!
    @brief set center position
    @return None
    """
    self.center = [x, y, z]

  def add_polygon(self, position):
    """!
    @brief add vertex positio to list(self.polygon)
    @return None
    """
    self.polygon.append(position)

  def get_center(self):
    """!
    @brief return center position
    @return self.center
    """
    return self.center

  def get_polygon(self):
    """!
    @brief return vertices list
    @return self.polygon
    """
    return self.polygon

  def get_center_polygon_distance(self):
    """!
    @brief caculate and return center position from vertices list
    @return three component list ([x, y, z])
    """
    distances = []
    
    for i in range(len(self.polygon)):
      dx = self.center[0] - self.polygon[i][0]
      dy = self.center[1] - self.polygon[i][1]
      dz = self.center[2] - self.polygon[i][2]
      distances.append( np.sqrt(dx**2 + dy**2 + dz**2) )

    return distances

  def get_polygon_vertex_distance(self):
    """!
    @brief caculate and return distance between each vertices
    @return distance list ([01, 12, 23, ...])
    """
    distances = []
    for i in range(len(self.polygon)):
      for j in range(i+1, len(self.polygon)):
        dx = self.polygon[i][0] - self.polygon[j][0]
        dy = self.polygon[i][1] - self.polygon[j][1]
        dz = self.polygon[i][2] - self.polygon[j][2]
        distances.append( np.sqrt(dx**2 + dy**2 + dz**2) )
    return distances

  def show_polygon(self, plane='xz'):
    """!
    @brief plot polygon 
    @param plane Select projection plane by str (e.g. 'xz') 
    @return None
    """
    index1 = self.mapping.get(plane[0], 0)
    index2 = self.mapping.get(plane[1], 0)

    xs = [vertex[index1] for vertex in self.polygon ]
    ys = [vertex[index2] for vertex in self.polygon ]

    fig=plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(111)
    fig.patch.set_alpha(0.)
    ax.fill(xs, ys, edgecolor='black', facecolor='#d3d3d3')
    ax.set_aspect('equal')

    plt.xlabel(str(plane[0])+"position [mm]")
    plt.ylabel(str(plane[1])+"position [mm]")
    plt.show()

class TReadoutPadArray():
  """!
  @class TReadoutPadArray
  @brief pad information array
  """

  def __init__(self):
    """!
    @brief initialze object
    @param mapping label of axsis (0:x, 1:y, 2:z)
    @param basepadlist list of base pad information
    @param pads list of vertices
    @param ids list of id
    @param centers list of center
    @param charges  list of charge
    @return None
    """
    self.mapping = {'x': 0, 'y': 1, 'z': 2}
    self.basepadlist = []
    self.pads = []
    self.ids = []
    self.centers = []
    self.charges = []

  def rotate_x(self, position, degree):
    """!
    @brief rotate position with x axis
    @param position origninal position
    @degree rotation angle [deg]
    @return converted position [x, y, z]
    """
    theta = 0.0174533*degree
    x = position[0]
    y = position[1] * np.cos(theta) - position[2] * np.sin(theta)
    z = position[1] * np.sin(theta) + position[2] * np.cos(theta)
    return [x, y, z]

  def rotate_y(self, position, degree):
    """!
    @brief rotate position with y axis
    @param position origninal position
    @degree rotation angle [deg]
    @return converted position [x, y, z]
    """
    theta = 0.0174533*degree
    x =  position[0] * np.cos(theta) + position[2] * np.sin(theta)
    y =  position[1]
    z = -position[0] * np.sin(theta) + position[2] * np.cos(theta)
    return [x, y, z]

  def rotate_z(self, position, degree):
    """!
    @brief rotate position with z axis
    @param position origninal position
    @degree rotation angle [deg]
    @return converted position [x, y, z]
    """
    theta = 0.0174533*degree
    x = position[0] * np.cos(theta) - position[1] * np.sin(theta)
    y = position[0] * np.sin(theta) + position[1] * np.cos(theta)
    z = position[2]
    return [x, y, z]

  def add_basepad(self,baseinfo):
    """!
    @brief add pad info (TBasePadShapeClass)
    @param baseinfo objerct of TBasePadShapeClass
    @return None
    """
    self.basepadlist.append(baseinfo)

  def add_pads(self, center, baseid, degX=0, degY=0, degZ=0, id=0):
    """!
    @brief set pad with position and id
    @param center center new center postion for adding pad 
    @param center baseid id of base pad object
    @param center degX rotation angle by X
    @param center degY rotation angle by Y
    @param center degZ rotation angle by Z
    @param center label od each id
    @return None
    """
    padshape = self.basepadlist[baseid]
    polygon_origin = padshape.get_polygon()

    polygon_new = []

    for i in range(len(polygon_origin)):

      polygon_rot = self.rotate_x(polygon_origin[i], degX)
      polygon_rot = self.rotate_y(polygon_rot, degY)
      polygon_rot = self.rotate_z(polygon_rot, degZ)

      for j in range(len(polygon_rot)):
        polygon_rot[j] = polygon_rot[j] + center[j]

      polygon_new.append(polygon_rot)

    self.pads.append(polygon_new)
    self.ids.append(id)
    self.centers.append(np.mean(polygon_new, axis=0))
    self.charges.append(0)

  def show_pads(self, plane='xz', plot_type='hit', ref=None, color_map=None, 
                check_id=False, check_data=None, check_size=4, tracks=None, 
                xrange=None, yrange=None, block_flag=True, pause_time=0.2, 
                canvassize = [6,5], savepath=None, dpi=300 ):
    """!
    # @brief plot polygon 
    # @param plane Select projection plane by str (e.g. 'xz') 
    # @param ref check listed id position (default is None)  
    # @return None
    """
    index1 = self.mapping.get(plane[0], 0)
    index2 = self.mapping.get(plane[1], 0)

    fig=plt.figure(figsize=(canvassize[0], canvassize[1]))
    ax = fig.add_subplot(111)
    fig.patch.set_alpha(0.)

    for i in range(len(self.pads)):
      xs = [vertex[index1] for vertex in self.pads[i] ]
      ys = [vertex[index2] for vertex in self.pads[i] ]
      xg = self.centers[i][index1]
      yg = self.centers[i][index2]

      if plot_type == 'hit':
        if ref is None:
          ax.fill(xs, ys, edgecolor='black', facecolor='#d3d3d3',lw=0.5)
        else:
          if self.ids[i] in ref:
            ax.fill(xs, ys, edgecolor='black', facecolor="#33b5b1",lw=0.5)
          else:
            ax.fill(xs, ys, edgecolor='black', facecolor='#d3d3d3',lw=0.5)
      elif plot_type == 'map':
        if color_map is None:
          ax.fill(xs, ys, edgecolor='black', facecolor='#d3d3d3',lw=0.5)
        else:
          ax.fill(xs, ys, edgecolor='black', facecolor=color_map[i],lw=0.5)
      else:
        ax.fill(xs, ys, edgecolor='black', facecolor='#d3d3d3',lw=0.5)

      if check_id:
        if check_data is not None:
          ax.text(xg, yg, f"{check_data[i]}", ha="center", va="center", fontsize=check_size, color="black")
        else:
          ax.text(xg, yg, f"{self.ids[i]}", ha="center", va="center", fontsize=check_size, color="black")
      
      if tracks:
        for i in range(len(tracks)):
          if tracks[i][0] == 'line':
              y = np.linspace(tracks[i][2][0], tracks[i][2][1], 2)
              x = tracks[i][1][0] * y + tracks[i][1][1]
              if len(tracks[i]) <= 3:
                ax.plot(x,y,lw=2,color='red')
              else:
                ax.plot(x,y,lw=tracks[i][3][0] ,color=tracks[i][3][1])

    ax.set_aspect('equal')

    plt.xlabel(str(plane[0])+" position [mm]")
    plt.ylabel(str(plane[1])+" position [mm]")

    if xrange:
      ax.set_xlim(xrange)

    if yrange:
      ax.set_ylim(yrange)

    if savepath:
      fig.savefig(savepath, dpi=dpi)
    else:
      plt.show(block=block_flag)
      if block_flag is False:
        plt.pause(pause_time) 

    
    plt.close(fig) 


def generate_regular_n_polygon(n=3, length=3, theta=0, flag=True):
  """!
  @brief generate regular n polygon 
  @param n number of vertex
  @param length length of daistance between each vertex
  @param theta rotation angle
  @param flag plot pad (default:True)
  @return object of TBasePadShapeClass
  """
  base_padinfo = TBasePadShapeClass()

  if n<3:
    print("n must be greater than 2")
  else:
    radius = length / (2 * np.sin(np.pi / n))
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    vertices = [(radius * np.cos(angle), radius * np.sin(angle)) for angle in angles]

    theta = np.radians(theta)
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])
    rotated_vertices = [np.dot(rotation_matrix, vertex) for vertex in vertices]

    for i in range(len(vertices)):
      base_padinfo.add_polygon([rotated_vertices[i][0], 0, rotated_vertices[i][1]])

    if flag:
      base_padinfo.show_polygon('xz')
    return base_padinfo

def generate_oblong_4_polygon(longlength=4, shortlength=2, plane='yz', flag=True):
  """!
  @brief oblong 4 polygon
  @param longlength length of long side
  @param shortlength length of short side
  @param plane projection plane
  @param flag plot pad (default:True)
  @return object of TBasePadShapeClass
  """
  base_padinfo = TBasePadShapeClass()

  if plane=='yz' or plane=='zy':
    base_padinfo.add_polygon([0,  shortlength/2,  longlength/2])
    base_padinfo.add_polygon([0,  shortlength/2, -longlength/2])
    base_padinfo.add_polygon([0, -shortlength/2, -longlength/2])
    base_padinfo.add_polygon([0, -shortlength/2,  longlength/2])

  elif plane=='xy' or plane=='xy':
    base_padinfo.add_polygon([ longlength/2,  shortlength/2, 0])
    base_padinfo.add_polygon([ longlength/2, -shortlength/2, 0])
    base_padinfo.add_polygon([-longlength/2, -shortlength/2, 0])
    base_padinfo.add_polygon([-longlength/2,  shortlength/2, 0])    

  elif plane=='xz' or plane=='xz':
    base_padinfo.add_polygon([ longlength/2, 0,  shortlength/2])
    base_padinfo.add_polygon([ longlength/2, 0, -shortlength/2])
    base_padinfo.add_polygon([-longlength/2, 0, -shortlength/2])
    base_padinfo.add_polygon([-longlength/2, 0,  shortlength/2])    

  if flag:
    base_padinfo.show_polygon(plane)
  return base_padinfo
