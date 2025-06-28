"""!
@file tracksimulation.py
@version 1
@author Fumitaka ENDO
@date 2025-06-28T15:45:26+09:00
@brief simple tracking simulrator with difution parameter of drift electron
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from matplotlib.path import Path
import matplotlib.colors as mcolors
import catmlib.simulator.trialpad as btpad
import argparse 

class TrackSimulator():
	"""!
	@class TrackSimulator
	@brief simple track simulation class
	"""

	def __init__(self):
		"""!
		@brief initialze object
		@param mapping label of axsis (0:x, 1:y, 2:z)
		@param beaminfo text for debug
		@param dedx stoppoing power [MeV/mm] (default: 0.0708)
		@param W electron-ion generation energy [eV] (default: 37 eV [deuteron])
		@param gain gem gain (default: 100)
		@param pC charge converstion parameter (default: 1.0e12 [C to pC])
		@param Qe elementary charge [C] (default: 1.602e-19 [C])
		@param gaus_sigma difusion parameter  (default: 0)
		@param uniform_width unused paramater (default: 0)
		@param mc_track_pram list for storing tracking parameters (default: [])

		@return None
		"""
		self.mapping = {'x': 0, 'y': 1, 'z': 2}
		self.beaminfo = "136Xe@100[MeV/u] in D2gas@40[kPa]"
		self.dedx = 0.0708 #MeV/mm
		self.W = 37 #eV
		self.gain = 100
		self.pC = 1.0e12 # C to pC
		self.Qe = 1.602e-19 #C
		self.gaus_sigma = 0
		self.uniform_width = 0
		self.mc_track_pram = []

	def set_beaminfo(self, beaminfo):
		"""!
		@brief set beam information
		@return None
		"""
		self.beaminfo = beaminfo

	def set_dedx(self, dedx):
		"""!
		@brief set stoping power
		@return None
		"""
		self.dedx = dedx

	def set_gain(self, gain):
		"""!
		@brief set gem gain
		@return None
		"""
		self.gain = gain

	def set_padarray(self, data):
		"""!
		@brief set pad array object
		@return None
		"""
		self.padsinfo = data

	def genarate_track(self, start_point, e_angle, a_angle, z_range, points):
		"""!
		@brief generate tracking parameter

		@param start_point starting point [x, y, z]
		@param e_angle elevation angle in degree
		@param a_angle azimuth angle in degree
		@param z_range track distance
		@param points number of dividing point
		
		@return None
		"""

		theta = 0.0174533 * e_angle
		phi = 0.0174533 * a_angle
		vector = np.array([np.sin(theta)*np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])

		t_max = z_range / vector[2]
		t_values = np.linspace(0, t_max, points)
		line_points = np.array([np.array(start_point) + t * vector for t in t_values])

		self.track_point = line_points

	def show_track(
			self, plane='xz',track_flag='track', map_values=[], 
			png_save_path=None,
			fig_flag=False
		):
		"""!
		@brief generate tracking parameter

		@param plane starting point [x, y, z]
		@param track_flag elevation angle in degree
		@param map_values list of count of reached electorons in each pad
		@param png_save_path save path
		@param fig_flag save flag
		
		@return None
		"""
		index1 = self.padsinfo.mapping.get(plane[0], 0)
		index2 = self.padsinfo.mapping.get(plane[1], 0)

		fig=plt.figure(figsize=(6, 5))
		ax = fig.add_subplot(111)
		fig.patch.set_alpha(0.)

		if len(map_values) == len(self.padsinfo.pads):
			for i in range(len(self.padsinfo.pads)):
				xs = [vertex[index1] for vertex in self.padsinfo.pads[i] ]
				ys = [vertex[index2] for vertex in self.padsinfo.pads[i] ]
				color = self.padsinfo.charges[i]/max(self.padsinfo.charges)
				ax.fill(xs, ys, edgecolor='black', facecolor=str(self.value_to_color(color)), lw=0.5, zorder=1)
		else:
			for i in range(len(self.padsinfo.pads)):
				xs = [vertex[index1] for vertex in self.padsinfo.pads[i] ]
				ys = [vertex[index2] for vertex in self.padsinfo.pads[i] ]
				ax.fill(xs, ys, edgecolor='black', facecolor='#d3d3d3', lw=0.5, zorder=1)


		if track_flag == 'track':
			ax.plot(self.track_point[:, index1], self.track_point[:, index2], zorder=2)
		elif track_flag == 'ionized':
			ax.plot(self.track_electron_points[:, index1], self.track_electron_points[:, index2],lw=1, zorder=2)
		elif track_flag == 'difused':
			ax.plot(self.track_electron_points[:, index1], self.track_electron_points[:, index2], c='#483d8b',lw=1, zorder=4)
			ax.scatter(self.track_difused_points[:, index1], self.track_difused_points[:, index2],s=2,alpha=0.25, c='#ee82ee', zorder=3)
		ax.set_aspect('equal')

		plt.xlabel(str(plane[0])+" position [mm]")
		plt.ylabel(str(plane[1])+" position [mm]")
		plt.show()
		if fig_flag:
			if png_save_path is not None:
				plt.savefig(png_save_path)

	def value_to_color(self, value):
		"""!
		@brief plot utilities
		@detail calculate color from counts

		@param value counts
		
		@return mcolors.to_hex(rgba_color)

		"""
		if not 0 <= value <= 1:
			raise ValueError("Value must be between 0 and 1")
		rgba_color = cm.terrain_r(value)
		hex_color = mcolors.to_hex(rgba_color)
		return hex_color

	def get_value_null_distribution(self, value):
		"""!
		@brief tracking utilities

		@param value
		
		@return value
		"""
		return value

	def get_value_gaus_distribution(self, value, sigma):
		"""!
		@brief genarate random value with gaussian function

		@param value refference value
		@param sigma standard deviation
		
		@return np.random.normal(value, sigma)
		"""
		return np.random.normal(value, sigma)

	def get_value_uniform_distribution(self, value, width):
		"""!
		@brief genarate random value with uniform function

		@param value refference value
		@param width width of uniform function
		
		@return np.random.uniform(value, sigma)
		"""
		return	np.random.uniform(value-width,value+width)

	def monte_carlo_track(self, nmax=10, track_parameters=[25/2,0,-2,0,0], xyzea_ditribution='null,null,null,null,null',xyzea_parameter='0,0,0,0,0' ):
		"""!
		@brief genarate random value with uniform function
		@detail execute monte carlo simulation. after executing, added track parameter to `self.mc_track_pram`

		@param nmax number of loop
		@param track_parameters list of trackin parameters
		@param xyzea_ditribution list of distributtion type along each axis (default : 'null,null,null,null,null')
		@param xyzea_parameter list of parameters for each function (default : '0,0,0,0,0')
		
		@return None
		"""
		self.mc_track_pram = []

		xyzea_ditribution_list = xyzea_ditribution.split(',')
		xyzea_parameter_list = [float(x) for x in xyzea_parameter.split(',')]


		for j in range(nmax):
			track_parameters_new = []

			for i in range(len(track_parameters)):
				if xyzea_ditribution_list[i] == 'null':
					track_parameters_new.append( self.get_value_null_distribution(track_parameters[i]) )
				elif xyzea_ditribution_list[i] == 'gaus':
					track_parameters_new.append( self.get_value_gaus_distribution(track_parameters[i],xyzea_parameter_list[i]) )
				elif xyzea_ditribution_list[i] == 'uniform':
					track_parameters_new.append( self.get_value_uniform_distribution(track_parameters[i], xyzea_parameter_list[i]) )

			self.mc_track_pram.append(track_parameters_new)

	def genarate_ionized_electrons(self, start_point, e_angle, a_angle, z_range, points=100):
		"""!
		@brief genarate electrons and ions

		@param start_point starting point [x, y, z]
		@param e_angle elevation angle in degree
		@param a_angle azimuth angle in degree
		@param z_range track distance
		@param points number of electron/ion to be generated

		@return None
		"""
		theta = 0.0174533 * e_angle
		phi = 0.0174533 * a_angle
		vector = np.array([np.sin(theta)*np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])

		t_max = z_range / vector[2]
		L = np.linalg.norm( t_max * vector )

		num_of_electron = int(self.dedx*10e6 * L / self.W)
		self.track_electron_points_factor = int( num_of_electron / points )

		e_values = np.linspace(0, t_max, points)
		electron_points = np.array([np.array(start_point) + t * vector for t in e_values])

		self.track_electron_points = electron_points

	def calclate_difused_point(self, plane='xz', gain=1, sigma=1):
		"""!
		@brief genarate electrons and ions

		@plane select plane to be smeared
		@gain difusion gain [note] this parameter is not realistic value based on physical process.  
		@sigma paramter for smearing

		@return None
		"""
		index1 = self.mapping.get(plane[0], 0)
		index2 = self.mapping.get(plane[1], 0)

		random_points = []

		for i in range(len(self.track_electron_points)):

			center = [self.track_electron_points[i][index1], self.track_electron_points[i][index2]]
			cov_matrix = [[sigma, 0], [0, sigma]]

			num_points = gain

			for j in range(num_points):
				difused_points = np.random.multivariate_normal(center, cov_matrix)
				xpos = difused_points[0]
				ypos = self.track_electron_points[i][1]
				zpos = difused_points[1]
				random_points.append([xpos, ypos, zpos])

			self.track_difused_points = np.array(random_points)

	def calclate_pad_electrons(self):
		"""!
		@brief Determine whether the generated electron reaches the each pad.
		@return None
		"""
		xzpads=[]

		for i in range(len(self.padsinfo.charges)):
			self.padsinfo.charges[i]=0

		for i in range(len(self.padsinfo.pads)):
			projected_polygon=[]
			for vertex in self.padsinfo.pads[i]:
				projected_polygon.append([vertex[0], vertex[2]])
			xzpads.append(projected_polygon)

		for i in range(len(self.track_difused_points)):
			pointxz = (np.array([self.track_difused_points[i][0], self.track_difused_points[i][2]]))
			for j in range(len(xzpads)):
				polygon_path = Path(xzpads[j])
				is_inside = polygon_path.contains_point(pointxz)
				if is_inside == True:
					self.padsinfo.charges[j] += 1

	def calclate_pad_charge(self, difusion_gain=1):
		"""!
		@brief calculate the total chrage in each pad
		@param difusion_gain modify the difusion gain, which is used in `calclate_difused_point` method
		@return None
		"""
		for i in range(len(self.padsinfo.charges)):
			self.padsinfo.charges[i] = self.padsinfo.charges[i] *self.track_electron_points_factor * self.gain * self.Qe * self.pC /difusion_gain

def init_track_simulator(
		pad, num=1, start_y=19.8, deg_theta=0, deg_phi=0, 
		mc_option='gaus,gaus,null,gaus,gaus' ,mc_prm='5,5,5,10,10', 
		gain=60, difusion_gain=20, difusion=0.5, 
		png_save_path=None ,flag=True):
	"""!
	@brief initialize track simulator
	
	@param pad pad object to be used 
	@param num maximum number of loop (default = 1)
	@param start_y (default = 19.8)
	@param deg_theta (default = 0)
	@param deg_phi (default = 0)
	@param mc_option distribution along each axis for smearing electron (default = 'gaus,gaus,null,gaus,gaus')
	@param mc_prm list of paramters for distributions (default = '5,5,5,10,10') 
	@param gain gem gain (default = 60)
	@param difusion_gain difusion gain (default = 20)
	@param difusion difufsion parameter (default = 0.5) 
	@param png_save_path output file path 
	@param flag save flag

	@return simulator object (TrackSimulator)
	"""
	simulator = TrackSimulator()
	simulator.set_padarray(pad)

	x_values = [point[0] for point in simulator.padsinfo.centers]
	z_values = []
	for i in range(len( simulator.padsinfo.pads)):
		z_values.append([point[2] for point in simulator.padsinfo.pads[i]])
	z_values = [item for sublist in z_values for item in sublist]

	simulator.monte_carlo_track(num, [np.mean(x_values), start_y, min(z_values)-1, deg_theta, deg_phi], mc_option ,mc_prm)
	prm = simulator.mc_track_pram[0]
	pos = [prm[0],prm[1],prm[2]]

	simulator.set_gain(gain)

	simulator.genarate_ionized_electrons(pos,prm[3],prm[4], max(z_values)-min(z_values)+2 )
	simulator.calclate_difused_point('xz', difusion_gain, difusion)
	simulator.calclate_pad_electrons()
	simulator.calclate_pad_charge(difusion_gain)

	if flag:
		simulator.show_track('xz', 'difused', simulator.padsinfo.charges, png_save_path, flag)

	return simulator

def chk_mc_prm(simulator, flag=True, png_save_path=None):
	"""!
	@brief check generated parameter 
	
	@param png_save_path output file path 
	@param flag save flag

	@return simulator object (TrackSimulator)
	"""
	data = simulator.mc_track_pram
	x = [prm[0] for prm in data ]
	y = [prm[1] for prm in data ]
	z = [prm[2] for prm in data ]
	e_angle = [prm[3] for prm in data ]
	a_angle = [prm[4] for prm in data ]

	fig=plt.figure(figsize=(10, 10))
	fig.patch.set_alpha(0.)

	ax = fig.add_subplot(221)
	ax.hist2d(x, y, bins=30, cmap='Blues')
	ax.set_xlabel("x position [mm]")
	ax.set_ylabel("y position [mm]")

	ax = fig.add_subplot(222)
	ax.hist2d(y, z, bins=30, cmap='Blues')
	ax.set_xlabel("y position [mm]")
	ax.set_ylabel("z position [mm]")

	ax = fig.add_subplot(223)
	ax.hist2d(z, x, bins=30, cmap='Blues')
	ax.set_xlabel("z position [mm]")
	ax.set_ylabel("x position [mm]")

	ax = fig.add_subplot(224)
	ax.hist2d(e_angle, a_angle, bins=30, cmap='Blues')
	ax.set_xlabel("theta [deg]")
	ax.set_ylabel("phi [deg]")
	plt.show()

	if flag:
		if png_save_path is not None:
			plt.savefig(png_save_path)

def simulate_pad_charge(simulator, gain=60, difusion_gain=20, difusion=0.5):
	"""!
	@brief simulate position and charge 
	
	@param simulator simulator object
	@param gain gem gain (default = 60)
	@param difusion_gain difusion gain (default = 20)
	@param difusion difufsion parameter (default = 0.5) 

	@return x positions, charges ([],[])
	"""
	xpos = []
	charge = []

	z_values = []
	for i in range(len( simulator.padsinfo.pads)):
		z_values.append([point[2] for point in simulator.padsinfo.pads[i]])
	z_values = [item for sublist in z_values for item in sublist]

	simulator.set_gain(gain)

	for i in range(len(simulator.mc_track_pram)):
		icharge = []

		prm = simulator.mc_track_pram[i]
		pos = [prm[0], prm[1], prm[2]]

		simulator.genarate_ionized_electrons(pos, prm[3], prm[4], max(z_values)-min(z_values)+2 )
		simulator.calclate_difused_point('xz', difusion_gain, difusion)
		simulator.calclate_pad_electrons()
		simulator.calclate_pad_charge(difusion_gain)

		for j in range(len(simulator.padsinfo.charges)):
			icharge.append(simulator.padsinfo.charges[j])

		x_values = [point[0] for point in simulator.padsinfo.centers]
		xpos.append(sum(np.array(x_values)*np.array(icharge))/sum(np.array(icharge)))

		charge.append(icharge)

	return xpos, charge

def calculate_pad_charge_threshold(centers, charge, threshold=0.08):
	"""!
	@brief remove data using threshold
	
	@param centers list of center position for each pad
	@param charge list of charge for each pad
	@param threshold threshold value to removing the data
	
	@return x positions, charges ([],[])
	"""
	xpos_thre = []
	charge_thre = []

	for i in range(len(charge)):
		icharge_thre = []

		for j in range(len(charge[i])):
			if charge[i][j] > threshold:
				icharge_thre.append(charge[i][j])
			else:
				icharge_thre.append(0)

		x_values = [point[0] for point in centers]
		xpos_thre.append(sum(np.array(x_values)*np.array(icharge_thre))/sum(np.array(icharge_thre)))
		charge_thre.append(icharge_thre)

	return xpos_thre, charge_thre

def calculate_xposition_from_charge(
		centers, xpos, charge, gain=60, 
		difusion_gain=20, difusion=0.5, threshold=0.2,
		global_threshold_value = 0.2,
		png_save_path=None, flag=True
	):
	"""!
	@brief calculate x position using removed charge list
	
	@param centers list of center position for each pad
	@param charge list of charge for each pad
	@param xpos list of position
	@param threshold threshold value to removing the data
	@param gain gem gain (default = 60)
	@param difusion_gain difusion gain (default = 20)
	@param difusion difufsion parameter (default = 0.5) 
	@param global_threshold_value global threshold value to removing the data
	@param png_save_path output file path 
	@param flag save flag
	"""

	xpos_thre, charge_thre = calculate_pad_charge_threshold(centers, charge, threshold)

	fig=plt.figure(figsize=(16, 12))
	fig.patch.set_alpha(0.)
	fig.suptitle(f"Simulation Result @ gain:{gain}, difusion_gain{difusion_gain}:, difusion:{difusion}, threshold:{threshold}")

	ax = fig.add_subplot(321)
	flattened_charge = [item for sublist in charge for item in sublist]
	flattened_charge = [item for item in flattened_charge if item != 0]
	ax.hist(flattened_charge, bins=100, alpha=0.5)
	ax.set_xlabel("original charge in pad [pC]")

	ax = fig.add_subplot(322)
	flattened_charge = [item for sublist in charge_thre for item in sublist]
	flattened_charge = [item for item in flattened_charge if item != 0]
	ax.hist(flattened_charge, bins=100, alpha=0.5)
	ax.set_xlabel("cut charge in pad [pC]")

	ax = fig.add_subplot(323)
	ax.hist(xpos, bins=400, log=True, alpha=0.5)
	ax.set_xlabel("original x position [mm]")

	ax = fig.add_subplot(324)
	ax.hist(xpos_thre, bins=400, log=True, alpha=0.5)
	ax.set_xlabel("simulated x position [mm]")

	ax = fig.add_subplot(325)
	resolution = []
	for i in range(len(xpos_thre)):
		resolution.append( xpos[i] - xpos_thre[i] )
	ax.hist(resolution, bins=100, alpha=0.5)
	ax.set_xlabel("position difference [mm]")
	
	ax = fig.add_subplot(326)
	multiplicuities=[]
	for i in range(len(charge)):
		multiplicuity=0
		for j in range(len(charge[i])):
			if charge[i][j] > global_threshold_value:
				multiplicuity = multiplicuity + 1
		multiplicuities.append(multiplicuity)
	ax.hist(multiplicuities, bins=15, range=(-0.5, 14.5), alpha=0.5)
	ax.set_xlabel("measured pad multiplicity")

	plt.show()
	if flag:
		if png_save_path is not None:
			plt.savefig(png_save_path)

def execute_simulataion():
	"""!
    @brief method for script to execute mc simulation

    CLI argument:
    @arg pad-type select trial pad type
    @arg pad-version select trail pad version
	@arg nmax select trial pad type
	@arg gem-gain select trail pad version
	@arg difusion-gain select trail pad version
	@arg difusion-value select trail pad version
	@arg global-threshold-value select trail pad version
	@arg flag-track-example plot track example
	@arg flag-mc-parameter plot generated track parameter
	@arg flag-position-charge plot postion and charge
    """
	parser = argparse.ArgumentParser()
	parser.add_argument("-t","--pad-type", help="select trial pad type", type=str, default="beamtpc")
	parser.add_argument("-tv","--pad-version", help="select trail pad version", type=int, default=0)	
	parser.add_argument("-nm","--nmax", help="select trial pad type", type=int, default=1)
	parser.add_argument("-gg","--gem-gain", help="select trail pad version", type=int, default=120)	
	parser.add_argument("-dg","--difusion-gain", help="select trail pad version", type=int, default=20)	
	parser.add_argument("-dv","--difusion-value", help="select trail pad version", type=int, default=0.5)	
	parser.add_argument("-gtv","--global-threshold-value", help="select trail pad version", type=int, default=0.2)	
	parser.add_argument("-fte","--flag-track-example", help="plot track example", action="store_true")
	parser.add_argument("-fmc","--flag-mc-parameter", help="plot generated track parameter", action="store_true")
	parser.add_argument("-fpc","--flag-position-charge", help="plot postion and charge", action="store_true")
	args = parser.parse_args()

	pad_type: str = args.pad_type
	pad_version: int = args.pad_version
	n_max: int = args.nmax
	gem_gain: float = args.gem_gain
	difusion_gain: float = args.difusion_gain
	difusion_value: float = args.difusion_value
	global_threshold_value: float = args.global_threshold_value
	chk_flag_example: bool = args.flag_track_example
	chk_flag_mc_prm: bool = args.flag_mc_parameter
	chk_flag_charge: bool = args.flag_position_charge
	
	padobj = None

	if pad_type == "beamtpc":
		padobj = btpad.get_trail_beamtpc_array(pad_version)
		
	if padobj is not None:
		simulator = init_track_simulator(
			padobj, n_max, gain=gem_gain, difusion_gain=difusion_gain, 
			difusion=difusion_value, png_save_path=None, flag=chk_flag_example
		)

		pad_array = simulator.padsinfo.centers

		if chk_flag_mc_prm:
			chk_mc_prm(simulator, flag=False)

		if chk_flag_charge:
			xpos, charge = simulate_pad_charge(simulator, gain=gem_gain, difusion_gain=difusion_gain, difusion=difusion_value)

			calculate_xposition_from_charge(
				pad_array, xpos, charge, 
				gem_gain, difusion_gain, difusion_value, 
				global_threshold_value, png_save_path=None, flag=False
			)
	
	else:
		print('trial pad type dose not exist')
	