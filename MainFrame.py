#! /usr/bin/python
# ArchiPhen. Program for computer assisted root phenotyping
# Copyright (C) Lionel Dupuy

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# TODO
# Specifying usb ports might save time
# Warning that the content of the camera will be deleted
# modify hook-script
# set env variable for folder to be used in hook script

# Full screen
# Another space bar to quit preview


import wx
import time
from datetime import date
import numpy
import os			# OS
import shutil			# copy files
import  wx			# GUI

# Project Modules
from ProjectManager import ProjectFrame
from ProjectManager import ProjectClass

# Project variables
project_obj = ProjectClass.ProjectClass()
root_folder = ""#"D:\\LIONEL\\DATA\\MEASURED\\CIRC\\CIRC_EXTRACT"
prev_folder = os.getcwd()

project_obj.root_folder = root_folder
project_obj.path = root_folder
# Iproject_obj.pathnitiate project data
app = wx.App(False)
frame = ProjectFrame.ProjectFrame(project_obj)
frame.SetPosition((100, 20)) 
frame.Show()
app.MainLoop()


## Save project settings before leaving
if project_obj.path == project_obj.root_folder:
	print "Project not saved"
else:
	print project_obj.path
	print project_obj.root_folder
	project_obj.save()

vary = raw_input("Press any key to finish")

