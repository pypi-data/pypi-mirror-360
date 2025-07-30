#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import warnings

from os import path
from spiceitup.logs.log import Log
from spiceitup.plot.plot_map import PlotMap
from spiceitup.utils.internal_utils import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from spiceitup.main.footer import Footer
from spiceitup.main.header import Header
from spiceitup.main.menu_bar import MenuBar
import qdarkgraystyle
from spiceitup.main.menu import Menu
from spiceitup.main.winc import WindowsContainer

class Main(QMainWindow):
    windows = []  # list of Window objects, see Window.py
    are_data_loaded = False  # becomes True when data.fits are loaded
    global_plots = {}  # global_plots[win_key] = {'plot_key': PlotMap or PlotLine, 'plot_key2': ...}
    s_plot_size = None
    s_font_size = None
    f_winc = None
    f_menu = None
    m_menu_bar = None
    f_header = None
    f_footer = None
    dh = None  # dh is a DataHandling instance
    ths = []  # QThreads
    thws = []  # thread workers
    rts = []  # list of RunThread
    nb_running_threads = 0
    fit_maps_are_generating = {}  # contains {win_key: Boolean, ...}
    fit_maps_are_generated = {}  # at least once contains {win_key: Boolean, ...}
    is_loading_data = False
    is_generate_maps_warned = False
    are_grey_bars_warned = False
    fit_maps_warning = False  # True when shown once
    double_click = False  # becomes True the first click during settings.
    updating_profile = {}  # {'win_key': bool, ...} True while I(lambda) is updating
    force_third_D = False  # used when mouse click finished to guarantee last display
    lambda_I_bar_moves = False  # avoid recursive behavior when moving I(lambda)'s vertical bar
    updating_levels = []  # contains RunThread instances related to running levels process
    lambda_unit = True  # Angstrom otherwise cube index
    qs_fit_label = {} # {'win_key': {'fit_1': QLabel(), 'fit_2': QLabel(), 'fit_3': QLabel()}, ...}
    nb_available_bin = {}  # {'win_key': <nb>} in order to hide fit if nb < 4
    python_state = None  # when not None, a state is being restored

    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        Log.p('------------------------- Application was run')
        self.initialization()
        central_widget = QFrame()
        self.setCentralWidget(central_widget)
        hbox = QHBoxLayout(central_widget)

        # /!\ order matters
        self.f_footer = Footer(self)
        self.f_menu = Menu(self)
        self.f_menu.setFixedWidth(self.f_menu.minimumSizeHint().width())
        self.f_winc = WindowsContainer(self)
        self.f_header = Header(self)
        self.m_menu_bar = MenuBar(self)

        s1 = QSplitter(Qt.Horizontal)
        #win_label.setStyleSheet("border: 1px solid black;")
        
        s1.addWidget(self.f_menu)
        s1.addWidget(self.f_winc)
        s1.setSizes(split_w_pc(0.2))

        s2 = QSplitter(Qt.Vertical)
        s2.addWidget(s1)
        s2.addWidget(self.f_footer)
        s2.setSizes(split_h_pc(0.85))
        
        s0 = QSplitter(Qt.Vertical)
        s0.addWidget(self.f_header)
        s0.addWidget(s2)
        s0.setSizes(split_h_pc(0.05))
        
        hbox.addWidget(s0)

        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))

        self.setWindowTitle('SPICE-IT Quicklook')
        
    """def __del__(self):
        for th in self.th:
            th.quit()"""

    def get_rt_by_progress_id(self, progress_id):
        for rt in self.rts:
            if rt.progress_id == progress_id:
                return rt
        return None

    def update_thread_text(self, q_nb_threads):
        text = '<font color="' + Const.green_text + \
               '">No process in background.</font>'
        if self.nb_running_threads > 0:
            plur = ''
            if self.nb_running_threads > 1:
                plur = 'es'
            text = '<font color="' + Const.red_text + \
                   '">Running ' + str(self.nb_running_threads) + \
                   ' process' + plur + ' in background...</font>'
        q_nb_threads.setText(text)

    def update_nb_threads(self, nb, add_it=False):
        if add_it:
            self.nb_running_threads += nb
        else:
            self.nb_running_threads = nb
        if self.nb_running_threads < 0:
            self.nb_running_threads = 0
        self.update_thread_text(self.f_menu.q_nb_threads)

    def get_window(self, win_key):
        for w in self.windows:
            if w.win_key == win_key:
                return w
        return None

    def all_plots(self, given_win_key=None):
        plots = []
        for win_key, plot_bloc in self.global_plots.items():
            if given_win_key is None or given_win_key == win_key:
                for plot_key, plot in plot_bloc.items():
                    plots.append(plot)
        return plots  # list of PlotMap and/or PlotLine
    
    def get_plots(self, given_plot_key):
        plots = []
        for win_key, plot_bloc in self.global_plots.items():
            for plot_key, plot in plot_bloc.items():
                if given_plot_key == plot_key:
                    plots.append(plot)
        return plots  # list of PlotMap or PlotLine
    
    def get_plot_bloc(self, given_plot):
        """plot_bloc is the parent element from a specific plot, it is a dict
        which is a value-element of global_plots and containing all the PlotMaps
        and PlotLines of one window"""
        for win_key, plot_bloc in self.global_plots.items():
            for plot_key, plot in plot_bloc.items():
                if plot == given_plot:
                    return plot_bloc
        return None

    def unlink_axes(self):
        for win_key, plot_bloc in self.global_plots.items():
            keys = ['x_y', 'lambda_y', 'fit_1', 'fit_2', 'fit_3']
            for key in keys:
                plot_bloc[key].main_plot_item.setXLink(None)
                plot_bloc[key].main_plot_item.setYLink(None)
    
    def link_axes(self, between_windows=False):
        previous_lambda_y = None
        previous_x_y = None
        
        self.unlink_axes()
        for win_key, plot_bloc in self.global_plots.items():
            # Zoom / Pane link
            #plot_bloc['x_y'].main_plot_item.setYLink(plot_bloc['lambda_y'].main_plot_item)
            #generates zoom issues
            if between_windows:
                if previous_lambda_y is not None:  # not the first window
                    PlotMap.link_maps(previous_x_y, plot_bloc['x_y'])
                    PlotMap.link_maps(previous_lambda_y, plot_bloc['lambda_y'], True)
                previous_x_y = plot_bloc['x_y']
                previous_lambda_y = plot_bloc['lambda_y']
            else:
                PlotMap.link_maps(plot_bloc['x_y'], plot_bloc['fit_1'])
            PlotMap.link_maps(plot_bloc['fit_1'], plot_bloc['fit_2'])
            PlotMap.link_maps(plot_bloc['fit_2'], plot_bloc['fit_3'])

    def update_vertical_bar(self, plot_bloc):
        if plot_bloc['lambda_y'].vertical_bar is not None:  # otherwise plot is not ready yet
            third_D_lambda = plot_bloc['x_y'].iv.timeLine.value()
            if not self.lambda_I_bar_moves:
                plot_bloc['lambda_I'].vertical_bar.setValue(int(third_D_lambda))
            lambda_value_scaled = int(third_D_lambda * self.f_menu.s_lambda_rescaling.value())
            plot_bloc['lambda_y'].vertical_bar.setValue(lambda_value_scaled)
        if plot_bloc['x_y'].vertical_bar is not None:  # otherwise plot is not ready yet
            third_D_x = plot_bloc['lambda_y'].iv.timeLine.value() * self.dh.step * self.f_menu.s_x_rescaling.value()
            plot_bloc['x_y'].vertical_bar.setValue(int(third_D_x))
            for i in range(1, 4):
                if plot_bloc['fit_' + str(i)].vertical_bar is not None:
                    plot_bloc['fit_' + str(i)].vertical_bar.setValue(int(third_D_x))

    def abscissa_factor(self, plot_key):
        factor = 1
        if plot_key == 'x_y' or 'fit' in plot_key:
            factor = self.dh.step * self.f_menu.s_x_rescaling.value()
        elif plot_key == 'lambda_y':
            factor = self.f_menu.s_lambda_rescaling.value()
        return float(factor)
            
    def initialization(self):
        if not path.isdir(Const.default_data_path):
            Log.p(Const.default_data_path + ' does not exist.', 'warn')
            Const.default_data_path = ''
        
    def applyStyle(self, app):
        css_content = self.read_css()
        if Const.debug_mode:
            css_content += self.read_css(True)
        qdgs_css = qdarkgraystyle.load_stylesheet().replace('opacity: 100;', '')  # Fix tooltip Windows issue
        app.setStyleSheet(qdgs_css + css_content)
        
    def read_css(self, debug=False):
        debug_str = '_debug' if debug else ''
        file = open('spiceitup/style/style' + debug_str + '.css', mode='r')
        css_content = file.read()
        file.close()
        return css_content
