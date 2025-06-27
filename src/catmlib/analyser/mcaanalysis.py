##
# @file mcaanalysis.py
# @version 1
# @author Fumitaka ENDO
# @date 2025-01-30T10:52:52+09:00
# @brief analysis utilities related to MCA (Kromek)
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import catmlib.util as util
import plotly.express as px
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter
from iminuit import Minuit
from iminuit.cost import LeastSquares
import plotly.graph_objects as go
import glob

class TMultiChannelAnalyzer():
  ##
  # @class TMultiChannelAnalyzer
  # @brief analysis package for analysing data acquired by MCA

  def __init__(self):
    ##
    # @brief initialze object
    # @param Qmeas calculated measured charge
    # @param Qmeas_err calculated error of measured charge
    # @param dEdX stopping power in certain point
    # @param dL effective pad length
    # @param W elecrton-ion piar creation energy
    # @param Qe elementary charge
    # @param G calculated gain
    # @param G_err calculated error of gain
    # @param E calculated theoretical energy deposit in pad
    # @param a 1-st order term of calibration parameter 
    # @param b 0-th order term of calibration parameter 
    # @param calib_path calibration data path
    # @param datas gain measurement datas 
    # @param input_values gain measurement datas path
    # @param calib_fit_xs data list for the data point x near each peak 
    # @param calib_fit_ys data list for the gausian value near each peak 
    # @param calib_means mean values list from fitting result by iminuit
    # @param calib_sigmas sigma values list from fitting result by iminuit
    # @param data_files list of data path
    # @param data_files_name list of data path name 
    # @param datas_x lits of mca data points (x)
    # @param datas_y lits of mca data points (y)
    # @param datas_h lits of mca data points (frequency)
    # @param datas_peak_count list of found peak count
    # @param datas_peak_indices list of found peak index
    # @param datas_fit_xs list of data point x picked up mca data around peak 
    # @param datas_fit_ys list of gausian values picked up mca data around peak 
    # @param datas_fit_oys list of data point y picked up mca data around peak 
    # @param datas_means list of fitted mean value
    # @param datas_sigmas list of fitted sigma value
    # @param voltages input voltage values
    # @return None
    self.Qmeas = []
    self.Qmeas_err = []
    self.dEdX = 1e6    # [eV/mm]
    self.dL = 12       # [mm]
    self.W = 26        # [eV]
    self.Qe = 1.602e-7 # [pC]
    self.G = []
    self.G_err = []
    self.E = 1 
    self.a = 1
    self.b = 0
    self.calib_path = None
    self.datas = []
    self.input_values = []
    self.calib_fit_xs = []
    self.calib_fit_ys =[]
    self.calib_means = []
    self.calib_sigmas = []
    self.data_files = []
    self.data_files_name = []
    self.datas_x = []
    self.datas_y = []
    self.datas_h = []
    self.datas_peak_count = []
    self.datas_peak_indices = []
    self.datas_fit_xs = []
    self.datas_fit_ys = []
    self.datas_fit_oys = []
    self.datas_means = []
    self.datas_sigmas = []
    self.voltages = []
  
  def get_Qmeas(self):
    ##
    # @brief get calculated measured charge and error 
    # @return Qmeas and error of Qmeas ([float, float, ... , float], [float, float, ... , float])
    return self.Qmeas, self.Qmeas_err
  
  def get_Gain(self):
    ##
    # @brief get calculated gain and error 
    # @return Gain and error of Gain ([float, float, ... , float], [float, float, ... , float])
    return self.G, self.G_err

  def set_voltages(self, val):
    ##
    # @brief set list of voltage value
    # @param val reference values [float, float, ... , float]
    # @return None
    self.voltages = val

  def set_dEdX(self, val):
    # @brief set energy loss in small interval at certain point
    # @param val reference values 
    # @return None
    self.dEdX = val 

  def set_dL(self, val):
    ##
    # @brief set effective pad length
    # @param val reference values 
    # @return None
    self.dL = val

  def set_W(self, val):
    ##
    # @brief set electron-ion pair cratrion energy
    # @param val reference values 
    # @return None
    self.W = val

  def calculate_Qmeas(self):
    ##
    # @brief calculate measured charge 
    #
    # More details: 
    # calculation result is stored to `self.Qmeas` and `self.Qmeas_err`
    #
    # @return None
    if len(self.datas_means)*len(self.datas_sigmas)>0:
      self.Qmeas = self.linear( np.array(self.datas_means).flatten(), self.b, self.a)
      self.Qmeas_err = self.a * np.array(self.datas_sigmas).flatten()
    else:
       print('measured values are empty.') 

  def calculate_Gain(self):
    ##
    # @brief calculate gain 
    #
    # More details: 
    # calculation result is stored to self.G and self.G_err
    #
    # @return None
    if len(self.Qmeas)*len(self.Qmeas_err)>0:
      self.G = self.Qmeas / ( self.dEdX * self.dL * self.Qe / self.W ) 
      self.G_err = self.Qmeas_err / ( self.dEdX * self.dL * self.Qe / self.W ) 
    else:
       print('measured values are empty.') 

  def gaussian(self, x, amplitude, mean, sigma):
    ##
    # @brief calculate gaussian value
    # @param amplitude constant
    # @param mean mean value
    # @param sigma sigma value
    # @return gaus(amplitude, mean, sigma)
    return amplitude * np.exp(-0.5 * ((x - mean) / sigma) ** 2)

  def linear(self, x, p0, p1):
    ##
    # @brief calculate liner transform value
    # @param x reference values
    # @param p0 coefficient of 0-th order term
    # @param p1 coefficient of 1-st order term
    # @return gaus(amplitude, mean, sigma)
    return p0 + p1 * x
  
  def set_calibration_file_path(self, file_path):
    ##
    # @brief set path of calibration data
    # @param file_path file path for mca data
    # @return None
    self.calib_path = file_path

  def set_input_values(self, values):
    ##
    # @brief set path of measured data
    # @param file_path file path for mca data
    # @return None
    self.input_values = values
  
  def find_peak(self, smooth_parameter=3, input_label='calib' ,debug=False):
    ##
    # @brief search peaks for calibraion data
    #
    # More details: 
    # should be set before executinf this function. 
    # result id stored to, self.calib_data_peak_count and self.calib_data_peak_indices for calibration, self.datas_peak_count, self.datas_peak_indices for data
    #
    # @param smooth_parameter smear parameter for original histogram
    # @param input_label label for data (calibration:'calib', data list:'data')
    # @param debug debug flag. if true, dump peak finding result (default:False)
    # @return None
    if input_label == 'calib':
      self.calib_data_x, self.calib_data_y = util.dataforming.read_spe_file(self.calib_path)
      self.calib_data_h = util.dataforming.create_histogram_data_from_points(self.calib_data_x, self.calib_data_y)
      smoothed_data = gaussian_filter(self.calib_data_y, smooth_parameter)
      self.calib_data_peak_count, self.calib_data_peak_indices = util.dataforming.find_peaks(smoothed_data)
      
      if debug:
        print("(calibration) number of peak:", self.calib_data_peak_count,", index of peak:", self.calib_data_peak_indices)

    else:
      for i in range(len(self.data_files)):

        file_name = os.path.basename(self.data_files[i])
        data_x, data_y = util.dataforming.read_spe_file(self.data_files[i])
        data_h = util.dataforming.create_histogram_data_from_points(data_x, data_y)
        smoothed_data = gaussian_filter(data_y, smooth_parameter)
        data_peak_count, data_peak_indices = util.dataforming.find_peaks(smoothed_data)
                
        self.datas_x.append(data_x)
        self.datas_y.append(data_y)
        self.datas_h.append(data_h)
        self.datas_peak_count.append(data_peak_count)
        self.datas_peak_indices.append(data_peak_indices)
        self.data_files_name.append(os.path.splitext(file_name)[0])

        if debug:
          print("(data) :", i, " number of peak:", data_peak_count, ", index of peak:", data_peak_indices)

  def fit_calibration_data(self, width=30, initial_sigma=10, plot_flag=False):
    ##
    # @brief peak fitting for calibration data
    #
    # More details: 
    # fitting result is stored to `self.calib_fit_xs`, `self.calib_fit_ys`, `self.calib_means`,  `self.calib_sigmas`
    #
    # @param width fitting range from center position (`self.calib_data_x[self.calib_data_peak_indices[i]]`)
    # @param initial_sigma initial value for using iminuit fitting 
    # @param plot_flag plot flag. if true, draw data by plotly (default:False)
    # @return None
    for i in range(len(self.calib_data_peak_indices)):
      xarr = np.array(self.calib_data_x)
      yarr = np.array(self.calib_data_y)

      fit_min, fit_max = self.calib_data_x[self.calib_data_peak_indices[i]] - width, self.calib_data_x[self.calib_data_peak_indices[i]] + width 
      mask = (xarr >= fit_min) & (xarr <= fit_max)
      xarr_mask = xarr[mask]
      yarr_mask = yarr[mask]


      least_squares = LeastSquares(xarr_mask, yarr_mask, np.ones_like(yarr_mask), self.gaussian)
      m = Minuit(least_squares, amplitude=self.calib_data_y[self.calib_data_peak_indices[i]],  mean=self.calib_data_x[self.calib_data_peak_indices[i]], sigma=initial_sigma)
      m.errordef = 1
      m.migrad()

      self.calib_fit_xs.append(xarr_mask)
      self.calib_fit_ys.append(self.gaussian(xarr_mask, m.values['amplitude'], m.values['mean'], m.values['sigma']))

      self.calib_means.append(m.values['mean'])
      self.calib_sigmas.append(m.values['sigma'])

    if plot_flag:
      categories = ["mca"] * len(self.calib_data_h) 
      df = pd.DataFrame({'Value': self.calib_data_h, 'Category': categories})
      fig = px.histogram(df, x='Value', color='Category', nbins=1023, labels={'Value': 'Channel'}, title='MCA Histogram')

      for i in range(len(self.calib_means)):
          fig.add_trace(
            go.Scatter(
              x=self.calib_fit_xs[i], y=self.calib_fit_ys[i], mode='lines', 
              name=f"FID:{i}, ({self.calib_means[i]:3.2f}, {self.calib_sigmas[i]:3.2f})", 
              line=dict(color='red', width=1.5), opacity=0.5))
          
      fig.show()

  def calculate_calibration_parameters(self, plot_flag=False):
    ##
    # @brief calculate calibration paramters 
    #
    # More details: 
    # calibraion paramter is determined by iminuit fitting.
    #
    # his function sould be executed after executing `self.fit_calibration_data()`.
    # fitting result is stored to `self.a`(1st), `self.b`(0th)

    # @param plot_flag plot flag. if true, draw data by plotly (default:False)
    # @return None
    if len(self.calib_sigmas) == len(self.input_values):
      self.calib_means_err = []
      for i in range(len(self.calib_means)):
          self.calib_means_err.append(self.calib_sigmas[i]/self.calib_means[i])

      least_squares = LeastSquares(self.input_values, self.calib_means, self.calib_means_err, self.linear)
      m = Minuit(least_squares, p0=0, p1=100)
      m.errordef = 1
      m.migrad()
      params = m.values

      self.b = -params['p0']/params['p1']
      self.a = 1/params['p1']         

      if plot_flag:
        fig = go.Figure(
          data = go.Scatter(
            y=self.input_values, x=self.calib_means, 
            error_x=dict(type='data', array=self.calib_means_err, thickness=2, width=5, visible=True),
            mode='markers', name='fitted data plot'))
        fig.update_layout(title='Input Values vs Fitted Values', yaxis_title='Input values', xaxis_title='Fitted value', title_x=0.05, title_font=dict(size=20))
        fig.add_trace(
          go.Scatter(
            x=np.array(self.calib_means), y=self.linear(np.array(self.calib_means), self.b , self.a), mode='lines', 
            name=f"{self.b:.3f}+{self.a:.3f}x", 
            line=dict(color='red', width=2), opacity=0.5))
        fig.show()
    else:
      print('peak number does not match input list.')
      print('calibration parameter calculation process wad skipped.')
      
  def remove_fitted_peak(self, list_label='calib', index_list=[]):
    ##
    # @brief remove specific peak
    # @param list_label label for data (calibration:'calib', data list:'data')
    # @param index_list list of index to be deleted
    # @return None
    if list_label == 'calib':
      for index in sorted(index_list, reverse=True):
          if 0 <= index < len(self.calib_sigmas):  
              del self.calib_sigmas[index]
      
      for index in sorted(index_list, reverse=True):
          if 0 <= index < len(self.calib_means):  
              del self.calib_means[index]
    else:
        for i in range(len(self.datas_means)):
          for index in sorted(index_list[i], reverse=True):
              if 0 <= index < len(self.datas_fit_xs[i]):  
                  del self.datas_fit_xs[i][index]

          for index in sorted(index_list[i], reverse=True):
              if 0 <= index < len(self.datas_fit_ys[i]):  
                  del self.datas_fit_ys[i][index]

          for index in sorted(index_list[i], reverse=True):
              if 0 <= index < len(self.datas_fit_oys[i]):  
                  del self.datas_fit_oys[i][index]

          for index in sorted(index_list[i], reverse=True):
              if 0 <= index < len(self.datas_means[i]):  
                  del self.datas_means[i][index]

          for index in sorted(index_list[i], reverse=True):
              if 0 <= index < len(self.datas_sigmas[i]):  
                  del self.datas_sigmas[i][index]

  def get_data_file_path_list(self, filepath='./*spe'):
    ##
    # @brief sort and set data file list
    #
    # More details: 
    # can use wildcard with input path  
    #
    # @param filepath file path
    # @return None
    self.data_files = sorted(glob.glob(filepath))
  
  def add_data_file_path_list(self, filepath='./*spe'):
    ##
    # @brief sort and add data file list
    #
    # More details: 
    # can use wildcard with input path  
    #
    # @param filepath file path
    # @return None
    add_files = sorted(glob.glob(filepath))
    for i in range(len(add_files)):
      self.data_files.append(add_files[i])
  
  def check_data_file(self):
    ##
    # @brief dump load file list
    # @return None
    for i in range(len(self.data_files)):
      print(self.data_files[i])

      
  def fit_data(self, width=30, initial_sigma=10):
    ##
    # @brief peak fitting for list of mca data
    #
    # More details: 
    # fitting result is stored to `self.datas_fit_xs`, `self.datas_fit_ys`, `self.datas_fit_oys`, `self.datas_means`, `self.datas_sigmas`
    #
    # @param width fitting range from center position (`self.calib_data_x[self.calib_data_peak_indices[i]]`)
    # @param initial_sigma initial value for using iminuit fitting 
    # @return None
    for j in range(len(self.datas_x)):

      data_fit_xs = []
      data_fit_ys = []
      data_fit_oys = []
      data_means = []
      data_sigmas = []
      
      for i in range(len(self.datas_peak_indices[j])):
        xarr = np.array(self.datas_x[j])
        yarr = np.array(self.datas_y[j])

        fit_min, fit_max = self.datas_x[j][self.datas_peak_indices[j][i]] - width, self.datas_x[j][self.datas_peak_indices[j][i]] + width 
        mask = (xarr >= fit_min) & (xarr <= fit_max)
        xarr_mask = xarr[mask]
        yarr_mask = yarr[mask]
        
        least_squares = LeastSquares(xarr_mask, yarr_mask, np.ones_like(yarr_mask), self.gaussian)
        m = Minuit(least_squares, amplitude=self.datas_y[j][self.datas_peak_indices[j][i]],  mean=self.datas_x[j][self.datas_peak_indices[j][i]], sigma=initial_sigma)
        m.errordef = 1
        m.migrad()

        data_fit_xs.append(xarr_mask)
        data_fit_ys.append(self.gaussian(xarr_mask, m.values['amplitude'], m.values['mean'], m.values['sigma']))
        data_fit_oys.append(yarr_mask)
        data_means.append(m.values['mean'])
        data_sigmas.append(m.values['sigma'])
      
      self.datas_fit_xs.append(data_fit_xs)
      self.datas_fit_ys.append(data_fit_ys)
      self.datas_fit_oys.append(data_fit_oys)
      self.datas_means.append(data_means)
      self.datas_sigmas.append(data_sigmas)
      
  def draw_fitted_datas(self):
    ##
    # @brief draw fitting result for list of mca data
    # @return None
    k = 0
    
    for i in range(len(self.datas_fit_xs)):
      for j in range(len(self.datas_fit_xs[i])):

        data_h = util.dataforming.create_histogram_data_from_points(self.datas_fit_xs[i][j], self.datas_fit_oys[i][j])

        if k == 0:
          categories = [f"{self.data_files_name[i]}, FID:{i}, HID:{j}"] * len(data_h)
          histograms = data_h

        else:
          categories = categories + [f"{self.data_files_name[i]}, FID:{i}, HID:{j}"] * len(data_h)
          histograms = histograms + data_h
        
        k = k + 1
    
    df = pd.DataFrame({'Value': histograms, 'Category': categories})
    fig = px.histogram(df, x="Value", color="Category", nbins=1023, opacity=0.75)

    for i in range(len(self.datas_fit_xs)):
      for j in range(len(self.datas_fit_xs[i])):
        fig.add_trace(
          go.Scatter(
            x=self.datas_fit_xs[i][j], y=self.datas_fit_ys[i][j], mode='lines', 
            name=f"FID:{i}, HID:{j}, ({self.calib_means[i]:3.2f}, {self.calib_sigmas[i]:3.2f})", 
            line=dict(color='black', width=1.5), opacity=0.5))

    fig.show()

  def draw_gain_curve(self):
    ##
    # @brief draw fitting result for list of mca data
    #
    # More details: 
    # this function should be executed after executing `self.draw_fitted_datas()`, `self.calculate_Qmeas()`, `self.calculate_Gain()`
    #
    # @return None
    fig = go.Figure(
      data = go.Scatter(
        x=self.voltages, y=self.G, 
        error_y=dict(type='data', array=self.G_err, thickness=2, width=5, visible=True),
        name='fitted data plot'))
    fig.update_layout(title='Gain Curve', yaxis_title='Gain', xaxis_title='Voltage [V]', title_x=0.05, title_font=dict(size=20))
    # fig.add_trace(
    #   go.Scatter(
    #     x=np.array(self.calib_means), y=self.linear(np.array(self.calib_means), self.b , self.a), mode='lines', 
    #     name=f"{self.b:.3f}+{self.a:.3f}x", 
    #     line=dict(color='red', width=2), opacity=0.5))
    fig.show()