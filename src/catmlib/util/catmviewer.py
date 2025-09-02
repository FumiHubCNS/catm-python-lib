"""!
@file catmviewer.py
@version 1
@author Fumitaka ENDO
@date 2025-01-28T13:22:04+09:00
@brief analysis utilities related to CAT-M 
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.gridspec import GridSpec
from matplotlib.colors import to_hex

def get_color_list(values, cmap_name="viridis", fmt="hex"):
    """!
    @brief Find the index of the nearest point.

    This function searches an array and returns the index of the element
    whose value is closest to the given reference value.

    @param array   The reference array in which to search for the nearest element.
    @param value   The reference value to compare against.
    @return        The index of the element in the array that is nearest to the reference value.
    """
    if len(values) == 0:
        return np.array([]), []

    vmin = int(np.floor(np.min(values)))
    vmax = int(np.ceil(np.max(values)))
    bins = np.arange(vmin, vmax + 1)  # 刻み幅1

    # bins の数で等間隔に色を切り出す
    cmap = plt.get_cmap(cmap_name, len(bins))
    rgba = [cmap(i) for i in range(len(bins))]  # 各要素は (r,g,b,a), 0-1

    if fmt == "hex":
        colors = [to_hex(c[:3]) for c in rgba]  # "#RRGGBB"
    elif fmt == "rgb":
        colors = [tuple(int(round(ch * 255)) for ch in c[:3]) for c in rgba]  # (R,G,B)
    else:
        raise ValueError("fmt must be 'hex' or 'rgb'")

    return list(bins), list(colors)

def get_color_array(values,bins,colors):
    color_array = []
    for i in range(len(values)):
        color_array.append(colors[bins.index(int(values[i]))])
    
    return color_array


def find_nearest_index(array, value):
    """!
    @brief find index of nearest point
    @param array reference array for sorting index
    @param reference value
    @return index value
    """
    array = np.array(array)  
    index = np.abs(array - value).argmin() 
    return index

def calculate_track_dipole_magnet_analytical_solution(v0=np.array([1,0,0]), x0=np.array([0,0,0]), omega=1, t=0):
    """!
    @brief analytical solution for equation of moyion in uniform magnetic field
    @param v0 initial vector [m] (numpy.array([x,y,z]))
    @param x0 initial position [m] (numpy.array([x,y,z]))
    @param omega cyclotron frequency (qB/m [C][T][m]^-1) 
    @param t list of time, which you want to calculate the position
    @return list of 3 component : [x1,x2,..,x3],[y1,y2,..,y3], [z1,z2,..,z3]
    """
    x = v0[0]/omega * np.sin( omega * t ) + v0[2]/omega * ( 1.0 - np.cos( omega * t ) ) + x0[0]
    y = v0[1] * t + x0[1]
    z = v0[2]/omega * np.sin( omega * t ) - v0[0]/omega * ( 1.0 - np.cos( omega * t ) ) + x0[2]

    return x,y,z

def calculate_unit_vector(v=np.array([-0.2, 0.01, 0.01])):
    """!
    @brief calculate and return unit vector
    @param v vector (np.array([-x, y, z]))
    @return unit vector of input vector
    """
    uv = v/np.linalg.norm(v)
    return uv

def calculate_extrapolated_position(position, direction, target_value, direction_to_extrapolate=2):
    """!
    @brief calculate and return extrapolated_position
    @param position reference position
    @param direction refarence vector
    @param target_value extrapolated value
    @param direction_to_extrapolate extrapolated axis
    @return extrapolated position (np.array([x, y, z]))
    """
    x0, y0, z0 = position
    vx, vy, vz = direction

    # extrapolate along X
    if direction_to_extrapolate == 0:  
        if vx == 0:
            raise ValueError("can not be changed due to the X component of vector is zero")
        t = (target_value - x0) / vx
        y_target = y0 + t * vy
        z_target = z0 + t * vz
        return np.array([target_value, y_target, z_target])
    
    # extrapolate along Y
    elif direction_to_extrapolate == 1:  
        if vy == 0:
            raise ValueError("can not be changed due to the Y component of vector is zero")
        t = (target_value - y0) / vy
        x_target = x0 + t * vx
        z_target = z0 + t * vz
        return np.array([x_target, target_value, z_target])
    
    # extrapolate along Z
    elif direction_to_extrapolate == 2:  
        if vz == 0:
            raise ValueError("can not be changed due to the Z component of vector is zero")
        t = (target_value - z0) / vz
        x_target = x0 + t * vx
        y_target = y0 + t * vy
        return np.array([x_target, y_target, target_value])

    else:
        raise ValueError("extrapolation direction must be specified as 0 (x), 1 (y), or 2 (z).")

def plot_3d_trajectory(x=[], y=[], z=[], u=[], v=[], w=[], 
                       x_lim=None, y_lim=None, z_lim=None, 
                       bpad=None, rpad=None, spad=None, 
                       bid=None, rid=None, sid=None, 
                       anaflag=-1, showflag=True, savepath=None, user_colors=['#B844A0','#36797A','#36797A','#B844A0']
                       ):
    """!
    @brief plot 3 disimensional trajectories
    @param x point data list : [[x1,x2,..x3],[x1,x2,..x3],[x1,x2,..x3]]
    @param y point data list : [[y1,y2,..y3],[y1,y2,..y3],[y1,y2,..y3]]
    @param z point data list : [[z1,z2,..z3],[z1,z2,..z3],[z1,z2,..z3]]
    @param u line data list : [[x1,x2,..x3],[x1,x2,..x3],[x1,x2,..x3]]
    @param v line data list : [[y1,y2,..y3],[y1,y2,..y3],[y1,y2,..y3]]
    @param w line data list : [[z1,z2,..z3],[z1,z2,..z3],[z1,z2,..z3]]
    @param x_lim draw range for X
    @param y_lim draw range for Y
    @param z_lim draw range for Z
    @param bpad beam tpc pad info (TReadoutPadArray)
    @param rpad recoil tpc pad info (TReadoutPadArray)
    @param spad silicon pad info (TReadoutPadArray)
    @param bid beam tpc hit id
    @param rid recoil tpc hit id
    @param sid silicon hit id 
    @param anaflag analysis flag (-1:tpc, 1:si)
    @param showflag draw flag (default : True) 
    @param savepath save path 
    @param user_colors color set 
    @return None
    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
  
    # Label
    ax.set_xlabel('Z position [mm]')
    ax.set_ylabel('X position [mm]')
    ax.set_zlabel('Y Position [mm]')
    ax.xaxis.pane.set_edgecolor('k')
    ax.yaxis.pane.set_edgecolor('k')
    ax.zaxis.pane.set_edgecolor('k')
    ax.xaxis.pane.set_facecolor('w')
    ax.yaxis.pane.set_facecolor('w')
    ax.zaxis.pane.set_facecolor('w')
    ax.grid(False)

    if x_lim:
        ax.set_xlim(x_lim)
    if y_lim:
        ax.set_ylim(y_lim)
    if z_lim:
        ax.set_zlim(z_lim)
    if x_lim and y_lim and z_lim:
        ax.set_box_aspect([abs(x_lim[0]-x_lim[1]),abs(y_lim[0]-y_lim[1]),abs(z_lim[0]-z_lim[1])])

    # XZ projection all
    if bpad != None:
      for i in range(len(bpad.pads)):
        tri = [[bpad.pads[i][0][2],bpad.pads[i][0][0],bpad.pads[i][0][1]],[bpad.pads[i][1][2],bpad.pads[i][1][0],bpad.pads[i][1][1]],[bpad.pads[i][2][2],bpad.pads[i][2][0],bpad.pads[i][2][1]]]
        triangle = Poly3DCollection([np.array(tri)], color='gray', alpha=0.3, edgecolor='gray')
        ax.add_collection3d(triangle)

    if rpad != None:
      for i in range(len(rpad.pads)):
        tri = [[rpad.pads[i][0][2],rpad.pads[i][0][0],rpad.pads[i][0][1]],[rpad.pads[i][1][2],rpad.pads[i][1][0],rpad.pads[i][1][1]],[rpad.pads[i][2][2],rpad.pads[i][2][0],rpad.pads[i][2][1]]]
        triangle = Poly3DCollection([np.array(tri)], color='gray', alpha=0.3, edgecolor='gray')
        ax.add_collection3d(triangle)

    if spad != None:
      for i in range(len(spad.pads)):
        rec = [[spad.pads[i][0][2],spad.pads[i][0][0],spad.pads[i][0][1]],[spad.pads[i][1][2],spad.pads[i][1][0],spad.pads[i][1][1]],[spad.pads[i][2][2],spad.pads[i][2][0],spad.pads[i][2][1]],[spad.pads[i][3][2],spad.pads[i][3][0],spad.pads[i][3][1]]]
        rectangle = Poly3DCollection([np.array(rec)], color='gray', alpha=0.3, edgecolor='gray')
        ax.add_collection3d(rectangle)

    # XZ projection hit
    if bpad != None:
      for j in range(len(bid)):
        i = int(bid[j])
        tri = [[bpad.pads[i][0][2],bpad.pads[i][0][0],bpad.pads[i][0][1]],[bpad.pads[i][1][2],bpad.pads[i][1][0],bpad.pads[i][1][1]],[bpad.pads[i][2][2],bpad.pads[i][2][0],bpad.pads[i][2][1]]]
        triangle = Poly3DCollection([np.array(tri)], color=user_colors[1])
        ax.add_collection3d(triangle)

    if rpad != None:
      for j in range(len(rid)):
        i = int(rid[j])
        tri = [[rpad.pads[i][0][2],rpad.pads[i][0][0],rpad.pads[i][0][1]],[rpad.pads[i][1][2],rpad.pads[i][1][0],rpad.pads[i][1][1]],[rpad.pads[i][2][2],rpad.pads[i][2][0],rpad.pads[i][2][1]]]
        triangle = Poly3DCollection([np.array(tri)], color=user_colors[0])
        ax.add_collection3d(triangle)
    
    if anaflag ==1:
      if spad != None:
        for j in range(len(sid)):
          i = int(sid[j])
          rec = [[spad.pads[i][0][2],spad.pads[i][0][0],spad.pads[i][0][1]],[spad.pads[i][1][2],spad.pads[i][1][0],spad.pads[i][1][1]],[spad.pads[i][2][2],spad.pads[i][2][0],spad.pads[i][2][1]],[spad.pads[i][3][2],spad.pads[i][3][0],spad.pads[i][3][1]]]
          rectangle = Poly3DCollection([np.array(rec)], color=user_colors[0])
          ax.add_collection3d(rectangle)

    # XZ Projection line
    for i in range(len(u)-1):
      ax.plot(u[i], v[i], w[i]-w[i]-99. ,c=user_colors[i],lw=1, linestyle=(0, (5, 1, 1, 1)))

    # plot track
    label_titles = ['Hit Pattern (RecoilTPC&SSD)','Hit Pattern (BeamTPC)']
    for i in range(len(x)):
      ax.scatter(x[i], y[i], z[i],c=user_colors[i],label=label_titles[i])

    label_titles = ['Track (Recoil Particle)','','Track (Beam Particle)','']

    if anaflag == 1:
      for i in range(len(u)):
        ax.plot(u[i], v[i], w[i],c=user_colors[i],label=label_titles[i]) 
    else:
      for i in range(len(u)-1):
        ax.plot(u[i], v[i], w[i],c=user_colors[i],label=label_titles[i]) 

    ax.legend(loc="upper right", bbox_to_anchor=(1.05, 0.95))

    ax.view_init(50, 230)
    plt.tight_layout()

    if showflag == True:
      plt.show()

    if savepath:
        fig.savefig(savepath)
    
    plt.close(fig)


def plot_2d_trajectory(x=[], y=[], z=[], u=[], v=[], w=[], 
                              x_lim=None, y_lim=None, z_lim=None, 
                              bpad=None, rpad=None, spad=None, 
                              bid=None, rid=None, sid=None, 
                              anaflag=-1, showflag=True, savepath=None, user_colors=['#B844A0','#36797A','#36797A','#B844A0']
                              ):
    """!
    @brief plot 3 disimensional trajectories
    @param x point data list : [[x1,x2,..x3],[x1,x2,..x3],[x1,x2,..x3]]
    @param y point data list : [[y1,y2,..y3],[y1,y2,..y3],[y1,y2,..y3]]
    @param z point data list : [[z1,z2,..z3],[z1,z2,..z3],[z1,z2,..z3]]
    @param u line data list : [[x1,x2,..x3],[x1,x2,..x3],[x1,x2,..x3]]
    @param v line data list : [[y1,y2,..y3],[y1,y2,..y3],[y1,y2,..y3]]
    @param w line data list : [[z1,z2,..z3],[z1,z2,..z3],[z1,z2,..z3]]
    @param x_lim draw range for X
    @param y_lim draw range for Y
    @param z_lim draw range for Z
    @param bpad beam tpc pad info (TReadoutPadArray)
    @param rpad recoil tpc pad info (TReadoutPadArray)
    @param spad silicon pad info (TReadoutPadArray)
    @param bid beam tpc hit id
    @param rid recoil tpc hit id
    @param sid silicon hit id 
    @param anaflag analysis flag (-1:tpc, 1:si)
    @param showflag draw flag (default : True) 
    @param savepath save path 
    @param user_colors color set 
    @return None
    """
    fig = plt.figure(figsize=(12, 10))  

    gs = GridSpec(2, 3, height_ratios=[5, 0.375], width_ratios=[0.5, 2, 0.5]) 
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, 1], sharex=ax1)
    axl = fig.add_subplot(gs[0, 0], sharey=ax1)  
    axr = fig.add_subplot(gs[0, 2], sharey=ax1)  

    #top
    for i in range(len(rpad.pads)):
        xs = [vertex[0] for vertex in rpad.pads[i]]
        ys = [vertex[2] for vertex in rpad.pads[i]]
        ax1.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)

    k=0
    for j in range(len(rid)):
        i = int(rid[j])
        xs = [vertex[0] for vertex in rpad.pads[i]]
        ys = [vertex[2] for vertex in rpad.pads[i]]
        if k==0:
            ax1.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[3], lw=0.5, zorder=0, label="Hit Pattern (RecoilTPC&SSD)")
        else:
            ax1.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[3], lw=0.5, zorder=0)
        k=k+1
    
    ax1.set_aspect('equal')  # アスペクト比を等しく設定
    ax1.set_xlim(-160, 160)  # X軸の範囲を固定
    ax1.set_ylim(-170, 230) 

    if len(v) >= 2:
      ax1.plot(v[0],u[0], lw=2, color=user_colors[0], alpha=0.5, label="Track (Recoil Particle)")
      ax1.plot(v[1],u[1], lw=2, color=user_colors[1], alpha=0.5, label="Track (Beam Particle)")

    if anaflag ==1:
      ax1.plot(v[3],u[3], lw=2, color=user_colors[0], alpha=0.5)
    ax1.legend(loc='upper right')

    # bottom
    for i in range(len(bpad.pads)):
        xs = [vertex[0] for vertex in bpad.pads[i]]
        ys = [vertex[2] for vertex in bpad.pads[i]]
        ax2.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)

    k=0
    for j in range(len(bid)):
        i = int(bid[j])
        xs = [vertex[0] for vertex in bpad.pads[i]]
        ys = [vertex[2] for vertex in bpad.pads[i]]
        if k == 0:
            ax2.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[2], lw=0.5, zorder=0, label="Hit Pattern (BeamTPC)")
        else:
            ax2.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[2], lw=0.5, zorder=0)
        k=k+1

    if len(v) >= 2:
      ax2.plot(v[2],u[2], lw=2, color=user_colors[1], alpha=0.5, label="Track (Beam Particle)")

    ax2.set_xlabel('X position [mm]')
    ax2.set_ylim(-255 -15 , -255 +15) 
    ax2.set_aspect('equal')  
    ax2.legend(loc='lower right')

    # left
    for i in range(len(spad.pads)):
      if spad.ids[i] < 48:
        zos = [vertex[2] for vertex in spad.pads[i]]

        if spad.ids[i] < 24:
          ys = [min(zos), min(zos), max(zos), max(zos)]
          xs = [-255, -255-8, -255-8, -255]
          axl.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)
        else:
          ys = [min(zos), min(zos), max(zos), max(zos)]
          xs = [-255, -255+8, -255+8, -255]
          axl.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)

    if anaflag ==1:
      for j in range(len(sid)):
          i = int(sid[j])
          if i < 48:
            zos = [vertex[2] for vertex in spad.pads[i]]
            if spad.ids[i] < 24:
              ys = [min(zos), min(zos), max(zos), max(zos)]
              xs = [-255, -255-8, -255-8, -255]
              axl.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[3], lw=0.5, zorder=0)
            else:
              ys = [min(zos), min(zos), max(zos), max(zos)]
              xs = [-255, -255+8, -255+8, -255]
              axl.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[3], lw=0.5, zorder=0)        

      axl.plot(v[3],u[3], lw=2, color=user_colors[3], alpha=0.5)

    axl.set_aspect('equal')
    axl.set_ylabel('Z position [mm]')
    axl.set_xlim(-255 -15 , -255 +15) 

    # right
    for i in range(len(spad.pads)):
      if spad.ids[i] >= 48:
        zos = [vertex[2] for vertex in spad.pads[i]]

        if spad.ids[i] < 72:
          ys = [min(zos), min(zos), max(zos), max(zos)]
          xs = [255, 255-8, 255-8, 255]
          axr.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)
        else:
          ys = [min(zos), min(zos), max(zos), max(zos)]
          xs = [255, 255+8, 255+8, 255]
          axr.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)

    if anaflag ==1:
      for j in range(len(sid)):
          i = int(sid[j])
          if i >= 48:
            zos = [vertex[2] for vertex in spad.pads[i]]
            if spad.ids[i] < 24:
              ys = [min(zos), min(zos), max(zos), max(zos)]
              xs = [255, 255-8, 255-8, 255]
              axr.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[3], lw=0.5, zorder=0)
            else:
              ys = [min(zos), min(zos), max(zos), max(zos)]
              xs = [255, 255+8, 255+8, 255]
              axr.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[3], lw=0.5, zorder=0)       

      axr.plot(v[3],u[3], lw=2, color=user_colors[3], alpha=0.5)

    axr.set_aspect('equal') 
    axr.set_xlim(255 -15 , 255 +15) 
    
    plt.tight_layout()

    if showflag == True:
      plt.show()

    if savepath:
        fig.savefig(savepath)
    
    plt.close(fig) 

def plot_2d_categories( x_lim=None, y_lim=None, z_lim=None, 
                        bpad=None, rpad=None, spad=None,
                        bid=None, rid=None, sid=None,
                        blabel=None, rlabel=None, slabel=None,
                        showflag=True, savepath=None, 
                        user_colors=[['#B844A0'],['#36797A'],["#5CA3EF"]],
                        legendFlag=False,
                        title_name="Map file checker (Cobo, AsAd, AGET, Channel), [-1] = all"
                        ):
    """!
    @brief plot categories with 2 disimension 
    @param x_lim draw range for X
    @param y_lim draw range for Y
    @param z_lim draw range for Z
    @param bpad beam tpc pad info (TReadoutPadArray)
    @param rpad recoil tpc pad info (TReadoutPadArray)
    @param spad silicon pad info (TReadoutPadArray)
    @param bid beam tpc categories list ([ [1,2,...], [3,6...] ])
    @param rid recoil tpc categories list ([ [1,2,...], [3,6...] ])
    @param sid silicon hit categories list ([ [1,2,...], [3,6...] ])
    @param showflag draw flag (default : True) 
    @param savepath save path 
    @param user_colors color set 
    @param title_name plot title
    @return None
    """
    fig = plt.figure(figsize=(12, 10))  

    gs = GridSpec(2, 3, height_ratios=[5, 0.375], width_ratios=[0.5, 2, 0.5]) 
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, 1], sharex=ax1)
    axl = fig.add_subplot(gs[0, 0], sharey=ax1)  
    axr = fig.add_subplot(gs[0, 2], sharey=ax1)  

    #top
    for i in range(len(rpad.pads)):
        xs = [vertex[0] for vertex in rpad.pads[i]]
        ys = [vertex[2] for vertex in rpad.pads[i]]
        ax1.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)

    for j in range(len(rid)):
        k=0
        for jj in range(len(rid[j])):
          i = int(rid[j][jj])
          xs = [vertex[0] for vertex in rpad.pads[i]]
          ys = [vertex[2] for vertex in rpad.pads[i]]
          if k==0:
              ax1.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[0][j], lw=0.5, zorder=0, label=rlabel[j])
          else:
              ax1.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[0][j], lw=0.5, zorder=0)
          k=k+1
    
    ax1.set_aspect('equal')  # アスペクト比を等しく設定
    ax1.set_xlim(-160, 160)  # X軸の範囲を固定
    ax1.set_ylim(-170, 230) 

    # bottom
    for i in range(len(bpad.pads)):
        xs = [vertex[0] for vertex in bpad.pads[i]]
        ys = [vertex[2] for vertex in bpad.pads[i]]
        ax2.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)

    for j in range(len(bid)):
        k=0
        for jj in range(len(bid[j])):
          i = int(bid[j][jj])
          xs = [vertex[0] for vertex in bpad.pads[i]]
          ys = [vertex[2] for vertex in bpad.pads[i]]
          if k==0:
              ax2.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[1][j], lw=0.5, zorder=0, label=blabel[j])
          else:
              ax2.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[1][j], lw=0.5, zorder=0)
          k=k+1
    
    ax2.set_xlabel('X position [mm]')
    ax2.set_ylim(-255 -15 , -255 +15) 
    ax2.set_aspect('equal')

    # left
    for i in range(len(spad.pads)):
      if spad.ids[i] < 48:
        zos = [vertex[2] for vertex in spad.pads[i]]

        if spad.ids[i] < 24:
          ys = [min(zos), min(zos), max(zos), max(zos)]
          xs = [-255, -255-8, -255-8, -255]
          axl.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)
        else:
          ys = [min(zos), min(zos), max(zos), max(zos)]
          xs = [-255, -255+8, -255+8, -255]
          axl.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)

    for j in range(len(sid)):
        k=0
        for jj in range(len(sid[j])):
          i = int(sid[j][jj])
          if spad.ids[i] < 48:
            zos = [vertex[2] for vertex in spad.pads[i]]

            if spad.ids[i] < 24:
              ys = [min(zos), min(zos), max(zos), max(zos)]
              xs = [-255, -255-8, -255-8, -255]
            else:
              ys = [min(zos), min(zos), max(zos), max(zos)]
              xs = [-255, -255+8, -255+8, -255]

            if k==0:
                axl.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[2][j], lw=0.5, zorder=0, label=slabel[j])
            else:
                axl.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[2][j], lw=0.5, zorder=0)
            k=k+1

    axl.set_aspect('equal')
    axl.set_ylabel('Z position [mm]')
    axl.set_xlim(-255 -15 , -255 +15) 

    # right
    for i in range(len(spad.pads)):
      if spad.ids[i] >= 48:
        zos = [vertex[2] for vertex in spad.pads[i]]

        if spad.ids[i] < 72:
          ys = [min(zos), min(zos), max(zos), max(zos)]
          xs = [255, 255-8, 255-8, 255]
          axr.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)
        else:
          ys = [min(zos), min(zos), max(zos), max(zos)]
          xs = [255, 255+8, 255+8, 255]
          axr.fill(xs, ys, edgecolor='#a9a9a9', facecolor='#d3d3d3', lw=0.5, zorder=-2)

    for j in range(len(sid)):
        k=0
        for jj in range(len(sid[j])):
          i = int(sid[j][jj])
          if spad.ids[i] >= 48:
            zos = [vertex[2] for vertex in spad.pads[i]]
            if spad.ids[i] < 72:
              ys = [min(zos), min(zos), max(zos), max(zos)]
              xs = [255, 255-8, 255-8, 255]
            else:
              ys = [min(zos), min(zos), max(zos), max(zos)]
              xs = [255, 255+8, 255+8, 255]

            if k==0:
                axr.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[2][j], lw=0.5, zorder=0, label=slabel[j])
            else:
                axr.fill(xs, ys, edgecolor='#a9a9a9', facecolor=user_colors[2][j], lw=0.5, zorder=0)
            k=k+1

    axr.set_aspect('equal') 
    axr.set_xlim(255 -15 , 255 +15) 

    if legendFlag:
      handles, labels = [], []
      for ax in [ax1, ax2, axl, axr]:
          h, l = ax.get_legend_handles_labels()
          handles.extend(h)
          labels.extend(l)
          
      seen = set()
      unique_handles_labels = []
      for h, l in zip(handles, labels):
          if l not in seen:
              unique_handles_labels.append((h, l))
              seen.add(l)
      
      unique_handles, unique_labels = zip(*unique_handles_labels)
      fig.legend(unique_handles, unique_labels, loc='upper center', bbox_to_anchor=(0.5, 0.95), ncol=4, fontsize=10)
    
    fig.suptitle(title_name)
    plt.tight_layout()

    if showflag == True:
      plt.show()

    if savepath:
        fig.savefig(savepath)
    
    plt.close(fig) 

def check_catm_view():
    """!
    @brief plot catm readpad using matplotlib 
    """
  
    import catmlib.readoutpad.catm as catpad
      
    beamtpc = catpad.get_beam_tpc_array()
    recoiltpc = catpad.get_recoil_tpc_array()
    ssd = catpad.get_ssd_array()

    x_range = (260, -260)
    y_range = (-100, 100)
    z_range = (-270, 220)

    bid, rid, sid = [], [], [] 
    rlabel, blabel, slabel = [], [], []
    user_colors=[ [], [], [] ]

    plot_2d_categories( z_range, x_range, y_range, beamtpc, recoiltpc, ssd, bid, rid, sid, blabel, rlabel, slabel, True, None, user_colors, False, "catm readpad view at XZ plane")