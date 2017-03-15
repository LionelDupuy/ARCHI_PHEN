import  wx
import time
from datetime import date
import numpy
from PIL import Image
#import zbar
import os,sys                  #   GUI
import subprocess
import shutil
import time
import pylab as plt
#from scripts import*


# run imageJ from interface
# p = subprocess.call(["ImageJ.exe","-batch","ImageJ/BatchExctractLabelsDBCopy.ijm"])
# ImageJ.exe -batch ImageJ/BatchExctractLabelsDBCopy.ijm

# Handle time lapse!

#scanner = zbar.ImageScanner()
# configure the reader
#scanner.parse_config('enable')
#scanner.set_config(0, zbar.Config.ENABLE, 0)
#scanner.set_config(zbar.Symbol.QRCODE, zbar.Config.ENABLE, 1)
label = ""
imsc = 0.35	# scaling of image to fit the screen
# TODO
# Read label better (crop enhance contrast etc...)
# copy files
# record previous file

######################################################################
# join folders
######################################################################
sep = '\\'
if os.name == 'posix':
	sep = '/'

######################################################################
# join folders
######################################################################
# def readQRCODE(ImageFile):
	# label = ""
	# pilImage = Image.open(ImageFile)
	# width, height = pilImage.size
	# #pilImage = pilImage.crop((int(0.18*width), int(0.2*height),int(0.97*width), int(0.95*height)))
	
	# pilImage = pilImage.convert('L')
	# width, height = pilImage.size
	# raw = pilImage.tostring()  
	# # wrap image data
	# image = zbar.Image(width, height, 'Y800', raw)  

	# # scan the image for barcodes
	# scanner.scan(image)
	# # extract results
	# label = []	
	# SY = []
	# for symbol in image:
		# label.append(symbol.data)
		# SY.append(symbol)
	# # clean up
	# del(image)
	# if len(label)>0:
		# return label[-1]
	# else:
		# return ""

	
WinSize = (600, 400)
class ProjectFrame(wx.Frame):
	def __init__(self, project, id = 0, log = None):
		wx.Frame.__init__(self, None, id, 'ArchiPhen', pos=(10, 10), size=WinSize)
		self.SetIcon(wx.Icon('MISC\\ArchiPhen.png', wx.BITMAP_TYPE_PNG))
        #self.log = log
		self.CenterOnScreen()
		self.project = project
		self.CreateStatusBar()
		self.SetStatusText("NOT READY. Please open or create a new project")
		#self.Panel = wx.Panel(self)
		self.CurrentGenotype = ""
		self.LastGenotype = "___#0"
		splitter = wx.SplitterWindow(self, -1)
		panel1 = wx.Panel(splitter, -1)
		panel1.SetBackgroundColour(wx.LIGHT_GREY)
		panel2 = wx.Panel(splitter, -1)
		panel2.SetBackgroundColour(wx.WHITE)
		splitter.SplitVertically(panel1, panel2, WinSize[0]*0.2)	
		self.Centre()

		self.b101 = wx.Button(panel1, 101, "New Project", (10, 10))
		self.Bind(wx.EVT_BUTTON,  self.onButton, self.b101)
		self.b102 = wx.Button(panel1, 102, "Open Project", (10, 50))
		self.Bind(wx.EVT_BUTTON,  self.onButton, self.b102)
		self.b102.SetSize(self.b102.GetBestSize())

		#self.b103 = wx.Button(panel1, 103, "Project Structure", (10, 90))
		#self.Bind(wx.EVT_BUTTON,  self.onButton, self.b103)
		#self.b103.SetSize(self.b102.GetBestSize())

		# Image and coordinates
		self.imW = 0
		self.imH = 0
		self.sc = 1
		################################################################################
		self.control = wx.TextCtrl(panel2, -1, "Welcome to ArchiPhen. Main steps to use the system: \n * Open or create a new project", style=wx.TE_READONLY|wx.TE_MULTILINE)
		bsizer = wx.BoxSizer()
		bsizer.Add(self.control, 1, wx.EXPAND)
		panel2.SetSizerAndFit(bsizer)
		
		
		# FOlders
		self.dest_folder = os.path.dirname(sys.argv[0])
		self.root_folder = os.path.dirname(sys.argv[0])
		
		# Setting up the menu.
		filemenu= wx.Menu()
		filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
		filemenu.AppendSeparator()
		filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

		preparemenu= wx.Menu()
	

		
		importmenu= wx.Menu()
		importmenu.Append(1, "&Prepare Raw data"," Find the ID of the genotype from the barcode and find the region where the root system is placed. Information is required so that import of data is possible")
		#importmenu.Append(1, "&Base Folders"," Set folders")
		importmenu.Append(2, "&Import From Folder"," import all files in the folder. This task reads the id of the genotype and copy both the image of the root and the image of the barcode")

		analysemenu= wx.Menu()
		analysemenu.Append(3, "&Seed image"," select the base of the root system")
		analysemenu.Append(4, "&Test Clicking Time"," Touch vs Mouse")
		#NEWINSERT LXD
		analysemenu.Append(55, "&Trace"," trace the roots")
		analysemenu.Append(11, "&Trace Custom"," Trace Custom")
		analysemenu.Append(66, "&Back-up segmentation results"," back-up segmentation files only")
		#NEWINSERT
		
#######################################################seb##########################################################
		analysemenu.Append(6,"&Calculation","calculate parameters from the database")
		analysemenu.Append(5,"&Errors","correct errors on the database")
		
		browsemenu= wx.Menu()
		browsemenu.Append(7, "&Project structure"," see what's in the database")
		browsemenu.Append(8, "&Custom Script Image"," execute the same script on all images")
		browsemenu.Append(9, "&Custom Script Seed"," execute the same script on all seed point")
		browsemenu.Append(10, "&Custom Script Trace"," execute the same script on all traced roots")

		resultmenu= wx.Menu()
		resultmenu.Append(20, "&View segmented results"," segmented data")
		resultmenu.Append(21, "&View data"," trait data")
		resultmenu.Append(22,"&View error results","error data")
		# xxxxxxx
		self.Bind(wx.EVT_MENU, self.pre_process, id=1)
		self.Bind(wx.EVT_MENU, self.scan_data, id=2)
		self.Bind(wx.EVT_MENU, self.get_seeds, id=3)
		self.Bind(wx.EVT_MENU, self.test_click, id=4)
		
		#NEWINSERT LXD
		self.Bind(wx.EVT_MENU, self.trace, id=55)
		self.Bind(wx.EVT_MENU, self.backup_seg, id=66)
		self.Bind(wx.EVT_MENU, self.trace_custom, id=11)
		#NEWINSERT
#######################################################seb##########################################################
		self.Bind(wx.EVT_MENU, self.get_data, id=6)	
		self.Bind(wx.EVT_MENU, self.get_errors, id=5)	

		self.Bind(wx.EVT_MENU, self.get_project_structure, id=7)
		self.Bind(wx.EVT_MENU, self.run_custom_im, id=8)
		self.Bind(wx.EVT_MENU, self.run_custom_seed, id=9)
		self.Bind(wx.EVT_MENU, self.view_results, id=20)
		self.Bind(wx.EVT_MENU, self.view_data, id=21)
		self.Bind(wx.EVT_MENU, self.view_error, id=22)
		
		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		menuBar.Append(importmenu,"&Import") # Adding the "filemenu" to the MenuBar
		menuBar.Append(analysemenu,"&Analyse") # Analyse image data
		menuBar.Append(browsemenu,"&Browse") # Analyse image data
		menuBar.Append(resultmenu,"&Results") 
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
		self.Show(True)
		
	def onButton(self, event):
		# Create new project
		if event.GetId() == self.b101.GetId():
			# Create an open file dialog
			dialog = wx.FileDialog(self, message="Save new project as ...", defaultDir=self.project.root_folder, style=wx.SAVE)
			# Show the dialog and get user input
			if dialog.ShowModal() == wx.ID_OK:
				self.project.path = dialog.GetPath()
				if not os.path.exists(self.project.path): 
					os.makedirs(self.project.path)
					self.project.save()
					self.SetStatusText("READY FOR SCANING")
				else:
					wx.MessageBox('Project Already Exists', 'Info', 
						style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
			# Destroy the dialog
			dialog.Destroy()

		# Open existing project
		if event.GetId() == self.b102.GetId():
		# Create an open file dialog
			dialog = wx.DirDialog(self, message="Open project", defaultPath=self.project.root_folder,
			style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
			dialog.SetPath(self.project.root_folder)
			# Show the dialog and get user input
			if dialog.ShowModal() == wx.ID_OK:
				self.project.path = dialog.GetPath()
				self.project.path = self.project.path.replace("\n", "")
				self.project.load(self.project.path)
				self.SetStatusText("READY FOR SCANING")
			# Destroy the dialog
			dialog.Destroy()
	

	def CloseWindow(self, event):
		self.Close()

	def get_folder(self, id):
		dlg = wx.DirDialog(self, "Choose Root Folder:")
		if dlg.ShowModal() == wx.ID_OK:
			self.root_folder = dlg.GetPath()
		dlg.Destroy()
	def pre_process(self, id):
		p = subprocess.call(["ImageJ.exe","ImageJ/BatchExctractLabelsDBCopy.ijm"]) # "-batch",
	def scan_data(self, id):
		#################################################################
		# Find all suitable files in the current folder
		#################################################################
		self.get_folder(0)
		
		dir = self.root_folder#os.path.dirname(sys.argv[0])
		sys.path.append(dir)
		file_count = 0
		for f in os.listdir(dir): 
			file, ext = os.path.splitext(f) # Handles no-extension files, etc.
			if ext == '.JPG' or ext == '.jpg' :
				base_row = file.split("-")
				base = base_row[0]
				if len(base_row) == 1:
					if os.path.isfile(dir+ sep+ file + "-QR-.jpg"):
						genotype = readQRCODE(dir+ sep+ file + "-QR-.jpg")
						
						# image properties
						file_tmp1 = file.split('_')
						file_id = file_tmp1[1]
						#os.path.getmtime(dir+ sep+ file +ext)
						
						# Image identifiers
						identifyer = [None,None,None]
						
						# QR code is read correctly
						if len(genotype) > 5: 
							file_count += 1
							text = "Root directory:  " + dir + "\n"
							text += "File:  " + file + "\n"
							text += "Genotype: " + genotype
							self.control.SetValue(text)
							wx.Yield()
							
							# get the data and copy
							identifyer = genotype.split('_')
							self.project.label = genotype
							self.project.get_genotype()
							self.project.import_data(file_id, dir+ sep+ file)
							
							self.LastGenotype = genotype
							
						# QR code not read - manual input of the data required
						else:
							file_count += 1
							pilImage = Image.open(dir+ sep+ file + "-QR-.jpg")
							width, height = pilImage.size
							#pilImage = pilImage.crop((int(0.18*width), int(0.3*height),int(0.97*width), int(0.92*height)))
							width, height = pilImage.size
							sc = 0.3
							pilImage = pilImage.resize((int(width*sc),int(height*sc)), Image.ANTIALIAS)
							img = wx.EmptyImage( *pilImage.size )
							pilImageCopy = pilImage.copy()
							pilImageCopyRGB = pilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
							pilImageRgbData =pilImageCopyRGB.tostring()
							img.SetData( pilImageRgbData )
							identifyer_length = 0
							while identifyer_length != 3:
								self.pnl2 = UnreadLabelFrame(self, -1, "Label not read", size=(int(width*0.7),int(height*0.4)), pos = (400,50), pic = img)
								self.pnl2.ShowModal()
								
								identifyer = (self.CurrentGenotype).split("_")
								identifyer_length = len(identifyer)

								
							genotype = identifyer[0]+'_'+identifyer[1]+'_'+identifyer[2]
							self.project.label = genotype
							self.project.get_genotype()
							self.project.import_data(file_id, dir+ sep+ file)
							
							self.LastGenotype = genotype
					else:
							text = "!!! Could not recover barcode for !!! :\n\n"
							text += "Root directory:  " + dir + "\n"
							text += "File:  " + file + "\n"
							self.control.SetValue(text)
							wx.Yield()

		text = "Import finished :\n\n"
		text += "File added:  " + str(file_count)
		self.control.SetValue(text)
		wx.Yield()		

	def get_seeds(self,id):
		width = 250
		height = 250
		frame = DrawFrame(self, 1, "Pick seeds",size=(int(width*self.sc*1.4),int(height*self.sc)), pos = (80,5))
		frame.ShowModal()

#######################################################seb##########################################################
	def get_data(self,id):
		self.project.create_data_files(self.project.path)

	def get_errors(self,id):
		width = 250
		height = 250
		frame = DrawFrame(self, 5, "Correct errors",size=(int(width*self.sc*1.4),int(height*self.sc)), pos = (80,5))
		frame.ShowModal()

	def view_error(self,id):
		width = 250
		height = 250
		frame = DrawFrame(self, 6, "Browse errors",size=(int(width*self.sc*1.4),int(height*self.sc)), pos = (80,5))
		frame.ShowModal()
		
	def get_project_structure(self,id):
			self.project.get_project_structure()
			self.project.print_project_structure()
			dlg = wx.Dialog(self, 10, title = 'Current Project Status', size=(300, 200))
			wx.TextCtrl(dlg, -1, self.project.project_structure, style=wx.TE_READONLY|wx.TE_MULTILINE)
			dlg.Show(True)
			self.project.path = self.project.path.replace("\n", "")
	def get_project_roots(self,id):
			self.project.get_project_structure()
			self.project.print_project_roots()

	def test_click(self, id):
		self.project.get_project_structure()		# parse the data in the database
		self.sample_seed = self.project.get_project_sample()		
		
		width = 250
		height = 250
		
		# Get sample list of data
		self.project.get_project_structure()		# parse the data in the database
		self.project.get_project_sample()
		
		# Open GUI for handling the data
		frame = DrawFrame(self, 3, "Test Manual Click",size=(int(width*self.sc*1.4),int(height*self.sc)), pos = (80,5))
		frame.ShowModal()	
		
		# Open GUI for handling the data
		frame = DrawFrame(self, 4, "Test Manual Touch",size=(int(width*self.sc*1.4),int(height*self.sc)), pos = (80,5))
		frame.ShowModal()	
#NEWINSERT LXD
	def trace(self,id):
		file_list = self.project.get_seed_file_list()
		for file in file_list: 
			if "SEED" in file:
				file_base = file.replace("_SEED_.txt","")
				print "processing: ", file_base
				p = subprocess.call(["imagej","-macro","C:\\Program Files\\ImageJ\\plugins\\root_tracing\\TraceMacro.txt", file_base])

	def trace_custom(self,id):
		# ######################################################################
		# Load Script
		# ######################################################################
		dlg = wx.DirDialog(self, "Choose Folder To Trace:")
		path_data = ""
		if dlg.ShowModal() == wx.ID_OK:
			path_data = dlg.GetPath()
		dlg.Destroy()

		
		file_list = self.project.get_current_folder_seed_list(path_data)
		
		
		for file in file_list: 
			if "SEED" in file:
				file_base = file.replace("_SEED_.txt","")
				print "processing: ", file_base
				p = subprocess.call(["imagej","-macro","C:\\Program Files\\ImageJ\\plugins\\root_tracing\\TraceMacro.txt", file_base])
									
	def backup_seg(self,id):
		# mkdir
		d = self.project.path + "\\backup\\"
		if not os.path.exists(d):
			os.makedirs(d)
		
		# get all files
		flist = self.project.get_seed_file_list()
		for file in flist:
			## seeds
			out = file
			row = out.split("\\")
			base = row[-1]
			shutil.copyfile(out,d+base)
			
			## out
			out = file.replace("SEED","OUT")
			if os.path.isfile(out):
				row = out.split("\\")
				base = row[-1]
				shutil.copyfile(out,d+base)

			## tip
			out = file.replace("SEED","TIP")
			if os.path.isfile(out):
				row = out.split("\\")
				base = row[-1]
				shutil.copyfile(out,d+base)
			
			## adj
			out = file.replace("SEED","ADJ")
			if os.path.isfile(out):
				row = out.split("\\")
				base = row[-1]
				shutil.copyfile(out,d+base)			
			
			## adj
			out = file.replace("SEED","ASSO")
			if os.path.isfile(out):
				row = out.split("\\")
				base = row[-1]
				shutil.copyfile(out,d+base)				
			
		# ZIP FILE
		output_filename = self.project.path + "\\" +time.strftime("%Y-%m-%d").replace("-","%")+"_" + time.strftime("%H-%M-%S") + "_bck"
		shutil.make_archive(output_filename, 'zip', d)
		
		
		#DELETE
		shutil.rmtree(d, ignore_errors=True)
#\NEWINSERT
		
	def run_custom_im(self,id):
		print "Run custom image script"
		dialog = wx.FileDialog(self, message="Save new project as ...", defaultDir="D:\\LIONEL\\PROGRAMMING\\CODE\\CORE\\ARCHI_SUITE\\ARCHI_PHEN\\V2\\", style=wx.SAVE)
		# Show the dialog and get user input
		path_script = ""
		if dialog.ShowModal() == wx.ID_OK:
			path_script = dialog.GetPath()

		# Destroy the dialog
		dialog.Destroy()

		if path_script !="":
			if (True):
				file_list = self.project.get_image_file_list()
				for file in file_list: 
					#print "\t" + file
					execfile(path_script)
	def run_custom_seed(self,id):
		print "Run custom seed script"
		dialog = wx.FileDialog(self, message="Save new project as ...", defaultDir="D:\\LIONEL\\PROGRAMMING\\CODE\\CORE\\ARCHI_SUITE\\ARCHI_PHEN\\V2\\", style=wx.SAVE)
		# Show the dialog and get user input
		path_script = ""
		if dialog.ShowModal() == wx.ID_OK:
			path_script = dialog.GetPath()

		# Destroy the dialog
		dialog.Destroy()

		if path_script !="":
			if (True):
				file_list = self.project.get_seed_file_list()
				for file in file_list: 
					#print "\t" + file
					execfile(path_script)
	def run_custom_path(self,id):
		print "Run custom Root tracing script"

						
	def view_results(self,id):
		width = 250
		height = 250
		frame = DrawFrame(self, 2, "Browse results",size=(int(width*self.sc*1.4),int(height*self.sc)), pos = (80,5))
		frame.ShowModal()
		#for file in file_list: 
	def view_data(self,id):
		self.project.view_data()
"""
Derived from Overlay a simple grid on a bitmap derived from image file using a PaintDC.

Ray Pasco
pascor(at)verizon(dot)net
2011-04-12-Tue__PM-01-55-16__April

"""
"""
todo:
* rewrite / no rewrite (for moving files)
* Options about which population to  go through
* Navigate through population

"""
class DrawFrame( wx.Dialog ):

#######################################################seb##########################################################
	def __init__( self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
		wx.Dialog.__init__(self, parent, ID, title, pos, size, style)
		self.SetIcon(wx.Icon('\\MISC\\ArchiPhen.png', wx.BITMAP_TYPE_PNG))
		# meta data
		self.parent = parent
		self.pos = pos
		self.imW = 200
		self.imH = 200
		self.imgMargin = 0
		self.sc = self.parent.sc
		self.imsc = imsc
		self.ID = ID
		
		# Build GUI		
		splitter = wx.SplitterWindow(self, -1)
		self.panel1 = wx.Panel(splitter, -1)
		self.panel1.SetBackgroundColour(wx.LIGHT_GREY)
		self.panel2 = wx.Panel(splitter, -1)
		self.panel2.SetBackgroundColour(wx.WHITE)
		splitter.SplitVertically(self.panel1, self.panel2, WinSize[0]*0.4)												#*#
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		box = wx.BoxSizer(wx.HORIZONTAL)
		self.b2 = wx.Button(self.panel1, 2, ">>>>>", (10, 50))
		self.Bind(wx.EVT_BUTTON,  self.onButton, self.b2)
		self.b1 = wx.Button(self.panel1, 1, "<<<<<", (10, 50))
		self.Bind(wx.EVT_BUTTON,  self.onButton, self.b1)
		box.Add(self.b1, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		box.Add(self.b2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		if self.ID == 5:
			self.b3 = wx.ToggleButton(self.panel1, 3, "Association", (10,50))
			self.Bind(wx.EVT_TOGGLEBUTTON,  self.OnToggle, self.b3)
			box.Add(self.b3, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.panel1.SetSizer(sizer)
		sizer.Fit(self.panel1)
		
		# Image panel for viewing
		self.imgPanel = wx.Panel( self.panel2, size=(int(self.imW*self.sc),int(self.imH*self.parent.sc)), pos=(self.imgMargin, self.imgMargin) )  					#*#
 		self.imgPanel.Bind( wx.EVT_LEFT_DOWN, self.OnMouseLeft)
		self.imgPanel.Bind( wx.EVT_RIGHT_DOWN, self.OnMouseRight)
		#if self.ID == 5:
			 #self.imgPanel.Bind( wx.EVT_LEFT_DOWN, self.OnMouseLeftBis)

		# Data structure
		self.plants_X = []
		self.plants_Y = []
		self.seeds = []
		self.tips = []
		self.adj_seeds = []
		self.adj_tips = []
		# Timing
		self.t0 = time.time()
		self.inc = 0

		# Browse image list
		if ID == 1:					# pick only
			self.list = parent.project.get_noseed_file_list()
			self.image_index = 0
			if len(self.list)>0:
				self.image_index = 0
			else:
				self.image_index = -1
			#self.genotype = self.list[0]
			self.list[self.image_index]
			self.OpenImage()																								#*#
			self.SetSize((int(self.imW*self.imsc*1.4),int(self.imH*self.imsc)))																				#*#
			self.imgPanel.SetSize((int(self.imW*self.imsc),int(self.imH*self.imsc)))	

			# Seed data
			self.OpenSeeds()
		if ID == 2:					# view results of segmentation
			self.list = parent.project.get_seed_file_list()
			for i in range(len(self.list)):
				file = self.list[i]
				file = file.replace("SEED","CROP")
				file = file.replace("txt","jpg")
				self.list[i] = file
			self.image_index = 0
			if len(self.list)>0:
				self.list[self.image_index]
				self.OpenImage()

				#--------------------------------------------#
				self.SetSize((int(self.imW*self.imsc*1.4),int(self.imH*self.imsc)))
				self.imgPanel.SetSize((int(self.imW*self.imsc),int(self.imH*self.imsc)))	
				
				# Root data
				self.OpenSeeds()			
				self.OpenPaths()
			
			#ADD DECORATION
			#CHECK WRITE TYPE OF MODIFICATION AND DECORATION PER TYPE
		if ID == 3 or ID == 4:					# view results of segmentation
			self.list = parent.sample_seed
			self.image_index = 0
			if len(self.list)>0:
				self.image_index = 0
			else:
				self.image_index = -1
			#self.genotype = self.list[0]
			self.list[self.image_index]
			self.OpenImage()																								#*#
			self.SetSize((int(self.imW*self.imsc*1.4),int(self.imH*self.imsc)))																				#*#
			self.imgPanel.SetSize((int(self.imW*self.imsc),int(self.imH*self.imsc)))

#######################################################seb##########################################################
		if ID == 5:
			self.list = parent.project.get_error_file_list()
			for i in range(len(self.list)):
				file = self.list[i]
				file = file.replace("SEED","CROP")
				file = file.replace("txt","jpg")
				self.list[i] = file
			self.image_index = 0
			if len(self.list)>0:
				self.list[self.image_index]
				self.OpenImage()

				#--------------------------------------------#
				self.SetSize((int(self.imW*self.imsc*1.4),int(self.imH*self.imsc)))
				self.imgPanel.SetSize((int(self.imW*self.imsc),int(self.imH*self.imsc)))	
				
				# Root data
				self.OpenSeeds()			
				self.OpenPaths()

		if ID == 6:
			self.list = parent.project.get_check_error_file_list()
			for i in range(len(self.list)):
				file = self.list[i]
				file = file.replace("SEED","CROP")
				file = file.replace("txt","jpg")
				self.list[i] = file
			self.image_index = 0
			if len(self.list)>0:
				self.list[self.image_index]
				self.OpenImage()

				#--------------------------------------------#
				self.SetSize((int(self.imW*self.imsc*1.4),int(self.imH*self.imsc)))
				self.imgPanel.SetSize((int(self.imW*self.imsc),int(self.imH*self.imsc)))	
				
				# Root data
				self.OpenSeeds()			
				self.OpenPaths()
				
		# Read the image and repaint.
		wx.EVT_PAINT( self.imgPanel, self.OnPaint )
		

	def OpenSeeds(self):
		self.seeds = []
		self.tips = []
		self.adj_seeds = []
		self.adj_tips = []
		root_directory = self.list[self.image_index].replace("CROP","SEED")
		root_directory = (root_directory.split('.'))[0]

		if os.path.isfile(root_directory+".txt"):
			f = open(root_directory+".txt","r")
			for line in f:
				row = line.split('\t')
				self.seeds.append([int(float(row[0])*self.imsc),int(float(row[1])*self.imsc)])
				
		root_directory = self.list[self.image_index].replace("CROP","TIP")
		root_directory = (root_directory.split('.'))[0]

		if os.path.isfile(root_directory+".txt"):
			f = open(root_directory+".txt","r")
			for line in f:
				row = line.split('\t')
				self.tips.append([int(float(row[0])*self.imsc),int(float(row[1])*self.imsc)])
		
		root_directory = self.list[self.image_index].replace("CROP","ADJ")
		root_directory = (root_directory.split('.'))[0]

		if os.path.isfile(root_directory+".txt"):
			f = open(root_directory+".txt","r")
			for line in f:
				row = line.split('\t')
				if row[0] == "seed":
					#self.adj_seeds.append([int(float(row[1])*self.imsc),int(float(row[2])*self.imsc)])	
					self.adj_seeds.append([int(float(row[1])),int(float(row[2]))])
				elif row[0] == "tip":
					#self.adj_tips.append([int(float(row[1])*self.imsc),int(float(row[2])*self.imsc)])			
					self.adj_tips.append([int(float(row[1])),int(float(row[2]))])			
	def OpenPaths(self):
		root_directory = self.list[self.image_index].replace("CROP","OUT")
		root_directory = (root_directory.split('.'))[0]

		if os.path.isfile(root_directory+".txt"):
			f = open(root_directory+".txt","r")
			self.plants_X = []
			self.plants_Y = []
			root_X = []
			root_Y = []
			index = 0
			for line in f:
				index +=1 
				if "Plant" in line:
					if index>2:
						self.plants_X.append(root_X)
						self.plants_Y.append(root_Y)

						root_X = []
						root_Y = []
				elif "X" in line:
					row = line.split(",")
					X = []
					for i in range(1,len(row)-1):
						X.append(float(row[i])*self.imsc)
					root_X.append(X)
				elif "Y" in line:
					row = line.split(",")
					Y = []
					for i in range(1,len(row)-1):
						Y.append(float(row[i])*self.imsc)
					root_Y.append(Y)		

			self.plants_X.append(root_X)
			self.plants_Y.append(root_Y)

				
	def OpenImage(self):
		file = self.list[self.image_index]
		pilImage = Image.open(file)
		width, height = pilImage.size
		self.imW = width
		self.imH = height

		pilImage = pilImage.resize((int(width*self.imsc),int(height*self.imsc)), Image.ANTIALIAS)
		img = wx.EmptyImage( *pilImage.size )
		pilImageCopy = pilImage.copy()
		pilImageCopyRGB = pilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
		pilImageRgbData =pilImageCopyRGB.tostring()
		img.SetData( pilImageRgbData )
 
		# Read the image file into a bitmap.
		pic = img#pilImageCopyRGB
		self.imgBmap = pic.ConvertToBitmap()
		bmapSize = self.imgBmap.GetSize()
		bmapSizeX, bmapSizeY = bmapSize

		
		# Calc and set the Frame interior size so to allow the bitmap to be centered
		#   with a border around it.
		self.ClientSize = (width, height)#(size[0],size[1])# (2*self.imgMargin+bmapSizeX, 2*self.imgMargin+bmapSizeY)

		# Keep track of OnPaint handler calls just for DEBUG info gathering purposes.
		self.paintCtr = 0
		
	def OnPaint( self, event ):
		self.paintCtr += 1#;  print '----  OnPaint() ', self.paintCtr
		panelDC = wx.PaintDC( self.imgPanel )
		self.redraw(panelDC)
		event.Skip()    # Very important to let all higher level handlers be called.

		#end def OnPaint
    
#end  MainFrame class
	def redraw(self, panelDC):

		# Copy (blit, "Block Level Transfer") a portion of the screen bitmap 
		#   into the returned capture bitmap.
		# The bitmap associated with memDC (captureBmap) is the blit destination.
		#                                                   # Blit (copy) parameter(s):
		imgPos = (0, 0)
		panelDC.DrawBitmapPoint( self.imgBmap, imgPos )

		# Once the BG mode is set to wx.Transparent it cannot be reset to wx.SOLID.
		#panelDC.SetBackgroundMode( wx.TRANSPARENT )     # wx.SOLID or wx.TRANSPARENT
		panelDC.SetBackgroundMode( wx.SOLID )           # wx.SOLID or wx.TRANSPARENT
		panelDC.SetTextForeground( wx.BLACK )
		panelDC.SetTextBackground( wx.WHITE )    # has no effect id bg mode is wx.TRANSPARENT
		genotype_id = self.list[self.image_index].split(sep)
		
		panelDC.DrawText( "  " + genotype_id[-1] +  "  " , 0, 0 )

		# Draw a NxM grid pattern - (n+1)+(m+1) lines.
		# Drawing thicker lines would be a bit trickier.
		numRows, numCols = 3, 3
		gridWid, gridHgt = panelDC.GetSizeTuple()
		cellWid = float( gridWid - 1) / numRows
		cellHgt = float( gridHgt - 1) / numCols
		
		panelDC.SetBrush( wx.Brush( (255,165,0,255), wx.TRANSPARENT) )
		panelDC.SetPen( wx.Pen( (255,165,0,255), 3, wx.SOLID) )
		panelDC.DrawRectangle( 0, 0, gridWid, gridHgt )

		panelDC.SetPen( wx.Pen( (255,165,0,255), 3, wx.SOLID) )
		for rowNum in xrange( numRows + 1) :
			panelDC.DrawLine( 0, rowNum*cellHgt, gridWid, rowNum*cellHgt )

		for colNum in xrange( numCols + 1 ) :
			panelDC.DrawLine( colNum*cellWid, 0, colNum*cellWid, gridHgt )

		# Draw the seeds
		r = 4
		LW = 3
		
		panelDC.SetPen( wx.Pen( wx.RED, LW, wx.SOLID) )
		for pos in self.seeds:
			panelDC.DrawCircle(pos[0]+1, pos[1]+1, r)	

		# Draw the tips
		panelDC.SetPen( wx.Pen( wx.GREEN, LW, wx.SOLID) )
		for pos in self.tips:
			panelDC.DrawCircle(pos[0]+1, pos[1]+1, r)		
		
		# show adjustment
		if self.ID == 2 or self.ID == 5 or self.ID == 6:
			LW = 2
			panelDC.SetPen( wx.Pen( wx.RED, LW, wx.SOLID) )
			for i in range(len( self.adj_seeds)):
				pos = self.seeds[i]
				adj = self.adj_seeds[i]
				
				panelDC.DrawLine(pos[0],pos[1],pos[0]-adj[0]-LW/2, pos[1]-adj[1]-LW/2)	

			panelDC.SetPen( wx.Pen( wx.GREEN, LW, wx.SOLID) )

			for i in range(len( self.adj_tips)):
				pos = self.tips[i]
				adj = self.adj_tips[i]
				panelDC.DrawLine(pos[0],pos[1], pos[0]+1-adj[0], pos[1]+1-adj[1])				
			
		self.SetSize((int(self.imW*self.imsc*1.4),int(self.imH*self.imsc)))																				#*#
		self.imgPanel.SetSize((int(self.imW*self.imsc),int(self.imH*self.imsc)))	
		
		########################################################################
		# Draw path 
		#######################################################################
		colors = [wx.GREEN, wx.RED, wx.CYAN]
		if self.ID==2 or self.ID == 5 or self.ID == 6:
			for i in range(len(self.plants_X)):
				plantX = self.plants_X[i]
				plantY = self.plants_Y[i]
				color = colors[i%3]
				panelDC.SetPen( wx.Pen( color, 2, wx.SOLID) )
				for j in range(0,len(plantX)):
					rootX = plantX[j]
					rootY = plantY[j]
					sub = 1
					for k in range(0,len(rootX)-2*sub,sub):
						panelDC.DrawLine(rootX[k], rootY[k],rootX[k+sub],rootY[k+sub])

		if self.ID == 5 and self.b3.GetValue() == True:
			n = len(self.array_assoc)
			color = colors[i%1]
			panelDC.SetPen( wx.Pen( color, 2, wx.DOT_DASH) )
			if int(n/2) == n/2:
				for i in range(0, n/2):
					array_assoc_seed = self.array_assoc[2 * i]
					array_assoc_tip = self.array_assoc[2 * i + 1]
					panelDC.DrawLine(array_assoc_seed[0], array_assoc_seed[1], array_assoc_tip[0], array_assoc_tip[1])
			elif int(n/2) == n/2 and n > 2:
				for i in range(0, n/2 - 1):
					array_assoc_seed = self.array_assoc[2 * i]
					array_assoc_tip = self.array_assoc[2 * i + 1]
					panelDC.DrawLine(array_assoc_seed[0], array_assoc_seed[1], array_assoc_tip[0], array_assoc_tip[1])

#######################################################seb##########################################################
	
	def onButton(self, event):
		if event.GetId() == self.b1.GetId(): # go back one step
			self.SaveSeeds()
			self.image_index -=1
			self.image_index = max(self.image_index,0)
			self.OpenImage()
			if self.ID < 3:
				self.OpenSeeds()
			if self.ID == 2:
				self.OpenPaths()
			if self.ID == 5:
				self.OpenSeeds()
				self.OpenPaths()
				if self.array_assoc != []:
					assoc = open(self.file_assoc, "w")
					seed = True
					for i in range (0, len(self.array_assoc)):
						array_assoc_in = self.array_assoc[i]
						if seed == True:
							assoc.write(str(array_assoc_in[0]/self.imsc) + "\t" + str(array_assoc_in[1]/self.imsc) + "\t")
							seed = False
						else:
							assoc.write(str(array_assoc_in[0]/self.imsc) + "\t" + str(array_assoc_in[1]/self.imsc) + "\n")
							seed = True
					assoc.close()
			if self.ID == 6:
				self.OpenSeeds()
				self.OpenPaths()
			if self.ID > 2 and self.ID != 5 and self.ID != 6:
				self.seeds = []
				self.tips = []
			self.DC = wx.ClientDC(self.imgPanel)
			self.redraw(self.DC)
			
		if event.GetId() == self.b2.GetId(): # go up one step
			self.SaveSeeds()
			self.image_index +=1
			self.image_index = min(self.image_index,len(self.list)-1)
			self.OpenImage()
			if self.ID < 3:
				self.OpenSeeds()
			if self.ID == 2:
				self.OpenPaths()
			if self.ID == 5:
				self.OpenSeeds()
				self.OpenPaths()
				if self.array_assoc != []:
					assoc = open(self.file_assoc, "w")
					seed = True
					for i in range (0, len(self.array_assoc)):
						array_assoc_in = self.array_assoc[i]
						if seed == True:
							assoc.write(str(int(array_assoc_in[0]/self.imsc)) + "\t" + str(int(array_assoc_in[1]/self.imsc)) + "\t")
							seed = False
						else:
							assoc.write(str(int(array_assoc_in[0]/self.imsc)) + "\t" + str(int(array_assoc_in[1]/self.imsc)) + "\n")
							seed = True
					assoc.close()
			if self.ID == 6:
				self.OpenSeeds()
				self.OpenPaths()
			if self.ID > 2 and self.ID != 5 and self.ID != 6:
				self.seeds = []
				self.tips = []
				
			self.DC = wx.ClientDC(self.imgPanel)
			self.redraw(self.DC)
		self.DC = wx.ClientDC(self.imgPanel)
		self.redraw(self.DC)
		#if event.GetId() == self.b3.GetId():
			#self.onMouseLeftBis()

	def OnMouseLeft(self, event):
		pos_click = self.imgPanel.ScreenToClient(wx.GetMousePosition()) 
		if self.b3.GetValue() == True:
			pos_click = self.imgPanel.ScreenToClient(wx.GetMousePosition())
			i=0
			min_dist = 100000000
			min_index = 0
			j=0
			min_dist_t = 100000000
			min_index_t = 0
			if len(self.seeds)>0:
				for pos in self.seeds:
					dist = (pos[0]-pos_click[0])**2 + (pos[1]-pos_click[1])**2
					if dist < min_dist:
						min_index = i
						min_dist = dist
					i += 1
			if len(self.tips)>0:
				for pos in self.tips:
					dist = (pos[0]-pos_click[0])**2 + (pos[1]-pos_click[1])**2
					if dist < min_dist_t:
						min_index_t = j
						min_dist_t = dist
					j += 1			
			if min_dist <  min_dist_t:
				if min_dist < 100**2:
					seeds = self.seeds[min_index]
					self.array_assoc.append([seeds[0],seeds[1]])
			elif min_dist >=  min_dist_t:
				if min_dist_t < 100**2:
					tips = self.tips[min_index_t]
					self.array_assoc.append([tips[0],tips[1]])
			if len(self.array_assoc) >= 2:
				self.DC = wx.ClientDC(self.imgPanel)
				self.redraw(self.DC)
		elif self.b3.GetValue() == False:
			# delete
			if event.AltDown():
				i=0
				min_dist = 100000000
				min_index = 0
				j=0
				min_dist_t = 100000000
				min_index_t = 0
				if len(self.seeds)>0:
					for pos in self.seeds:
						dist = (pos[0]-pos_click[0])**2 + (pos[1]-pos_click[1])**2
						if dist < min_dist:
							min_index = i
							min_dist = dist
						i += 1
				if len(self.tips)>0:
					for pos in self.tips:
						dist = (pos[0]-pos_click[0])**2 + (pos[1]-pos_click[1])**2
						if dist < min_dist_t:
							min_index_t = j
							min_dist_t = dist
						j += 1			
				if min_dist <  min_dist_t:
					if min_dist < 100**2:
						seeds = self.seeds
						del seeds[min_index]
						self.seeds = seeds
				elif min_dist >=  min_dist_t:
					if min_dist_t < 100**2:
						tips = self.tips
						del tips[min_index_t]
						self.tips = tips
			# add root tip
		
			elif event.ShiftDown():
				#print pos_click[0]/self.parent.sc, " , ", pos_click[1]/self.parent.sc, " / ",self.parent.imW, " , ", self.parent.imH
				self.tips.append(pos_click)			
			# add root base
			else: 			
				#print pos_click[0]/self.parent.sc, " , ", pos_click[1]/self.parent.sc, " / ",self.parent.imW, " , ", self.parent.imH
				self.seeds.append(pos_click)
			self.DC = wx.ClientDC(self.imgPanel)
			self.redraw(self.DC)

	def OnToggle(self, event):
		if self.b3.GetValue() == True:
			self.array_assoc = []
			file = self.list[self.image_index]
			file = file.replace("CROP","ASSOC")
			file = file.replace("jpg","txt")
			self.file_assoc = file
		self.DC = wx.ClientDC(self.imgPanel)
		self.redraw(self.DC)

	def OnMouseRight(self, event):
		pos_click = self.imgPanel.ScreenToClient(wx.GetMousePosition())
		print pos_click[0]/self.parent.sc, " , ", pos_click[1]/self.parent.sc, " / ",self.parent.imW, " , ", self.parent.imH
		i=0
		min_dist = 100000000
		min_index = 0
		if len(self.seeds)>0:
			for pos in self.seeds:
				dist = (pos[0]-pos_click[0])**2 + (pos[1]-pos_click[1])**2
				if dist < min_dist:
					min_index = i
					min_dist = dist
				i += 1
			
			if min_dist < 100**2:
				seeds = self.seeds
				del seeds[min_index]
				self.seeds = seeds
		
		self.DC = wx.ClientDC(self.imgPanel)
		self.redraw(self.DC)
								  # for the position

	def SaveSeeds(self):
		if self.ID < 3:
			if len(self.seeds)>0:
				# save seeds
				root_directory = self.list[self.image_index].replace("CROP","SEED")
				root_directory = (root_directory.split('.'))[0]
				f = open(root_directory+".txt","w")
				for pos in self.seeds:
					f.write(str(int(pos[0]/self.imsc)) + "\t" + str(int(pos[1]/self.imsc)) + "\n")
				f.close()
			
			if len(self.tips)>0:
				# save tips
				root_directory = self.list[self.image_index].replace("CROP","TIP")
				root_directory = (root_directory.split('.'))[0]
				f = open(root_directory+".txt","w")
				for pos in self.tips:
					f.write(str(int(pos[0]/self.imsc)) + "\t" + str(int(pos[1]/self.imsc)) + "\n")
				f.close()

#######################################################seb##########################################################
		elif self.ID == 5:
			if len(self.seeds)>0:
				# save seeds
				root_directory = self.list[self.image_index]
				root_directory = root_directory.replace("CROP","SEED")
				split = root_directory.split("/")
				name = split[-1]
				name_split = name.split("_")
				name_split = name_split[:-1]
				name = ""
				for j in range(0,len(name_split)):
					name = name + name_split[j] + "_"
				split = split[:-1]
				old_directory = ""
				for i in range (0,len(split)):
					old_directory = old_directory + split[i] + "/"
				for filename in os.listdir(old_directory):
					if name in filename:
						new_filename = filename.replace("SEED","SEED_previous")
						os.rename(old_directory + filename,old_directory + new_filename)
				root_directory = (root_directory.split('.'))[0]
				f = open(root_directory+".txt","w")
				for pos in self.seeds:
					f.write(str(int(pos[0]/self.imsc)) + "\t" + str(int(pos[1]/self.imsc)) + "\n")
				f.close()
			
			if len(self.tips)>0:
				# save tips
				root_directory = self.list[self.image_index]
				root_directory = root_directory.replace("CROP","TIP")
				split = root_directory.split("/")
				name = split[-1]
				name_split = name.split("_")
				name_split = name_split[:-1]
				name = ""
				for j in range(0,len(name_split)):
					name = name + name_split[j] + "_"
				split = split[:-1]
				old_directory = ""
				for i in range (0,len(split)):
					old_directory = old_directory + split[i] + "/"
				for filename in os.listdir(old_directory):
					if name in filename:
						new_filename = filename.replace("TIP","TIP_previous")
						os.rename(old_directory + filename,old_directory + new_filename)
				root_directory = (root_directory.split('.'))[0]
				f = open(root_directory+".txt","w")
				for pos in self.tips:
					f.write(str(int(pos[0]/self.imsc)) + "\t" + str(int(pos[1]/self.imsc)) + "\n")
				f.close()
		elif self.ID != 5 and self.ID != 6 and self.ID > 3:
			self.inc += 1
			
			# Time of operation
			DT = time.time() - self.t0
			
			# Get file name where to save
			print self.parent.root_folder
			root_directory = self.parent.project.path + "\\test_" + str(self.ID) + "_" + str(self.inc)+".txt"
			f = open(root_directory,"w")
			f.write("time:" + str(DT) + "\n")

			# Copy raw data
			file = self.list[self.image_index]
			shutil.copy(file, self.parent.project.path + "\\test_" + str(self.ID) + "_" + str(self.inc)+".jpg")	
			if len(self.tips)>0:# save tips
				for pos in self.tips:
					f.write("tips:" + str(int(pos[0]/self.imsc)) + "\t" + str(int(pos[1]/self.imsc)) + "\n")
			
			if len(self.seeds)>0:# save seeds
				for pos in self.seeds:
					f.write("seeds:" +str(int(pos[0]/self.imsc)) + "\t" + str(int(pos[1]/self.imsc)) + "\n")			
			f.close()
class UnreadLabelFrame(wx.Dialog):
	def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, pic = None):
		wx.Dialog.__init__(self, parent, ID, title, pos, size, style)
		self.SetIcon(wx.Icon('MISC\\ArchiPhen.png', wx.BITMAP_TYPE_PNG))
		self.parent = parent
		LG = (parent.LastGenotype).split("_")
		ID = LG[2].split("#")
		LastGenotype = [LG[0],LG[1],ID[0],ID[1]] 
		
		splitter = wx.SplitterWindow(self, -1)
		panel1 = wx.Panel(splitter, -1)
		panel1.SetBackgroundColour(wx.LIGHT_GREY)
		panel2 = wx.Panel(splitter, -1)
		panel2.SetBackgroundColour(wx.WHITE)
		wx.StaticBitmap(panel2, -1, pic.ConvertToBitmap(), (0, 0))
		splitter.SplitVertically(panel1, panel2, WinSize[0]*0.4)	
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(panel1, -1, "Species:")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		self.text1 = wx.TextCtrl(panel1, -1, "", size=(80,-1))
		self.text1.SetValue(LastGenotype[0])
		box.Add(self.text1, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(panel1, -1, "Population:")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		self.text2 = wx.TextCtrl(panel1, -1, "", size=(80,-1))
		self.text2.SetValue(LastGenotype[1])
		box.Add(self.text2, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		box = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(panel1, -1, "ID:")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		self.text3 = wx.TextCtrl(panel1, -1, "", size=(80,-1))
		self.text3.SetValue(LastGenotype[2])
		box.Add(self.text3, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		box = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(panel1, -1, "Rep (#):")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		self.text4 = wx.TextCtrl(panel1, -1, "", size=(80,-1))
		box.Add(self.text4, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
		self.text4.SetValue(LastGenotype[3])
		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		box = wx.BoxSizer(wx.HORIZONTAL)
		self.b1 = wx.Button(panel1, 1, "OK", (10, 50))
		self.Bind(wx.EVT_BUTTON,  self.onOK, self.b1)
		box.Add(self.b1, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		self.b2 = wx.Button(panel1, 2, "Cancel", (10, 50))
		self.Bind(wx.EVT_BUTTON,  self.onButton, self.b2)
		box.Add(self.b2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		panel1.SetSizer(sizer)
		sizer.Fit(panel1)
	def onOK(self,event):
			# Collect saved data
			data = self.text1.GetValue() + "_" + self.text2.GetValue() + "_" +self.text3.GetValue() + "#" +self.text4.GetValue()
			self.parent.CurrentGenotype = data
			self.Destroy()
			
	def onButton(self, event):
		# if event.GetId() == self.b1.GetId():
			# # Collect saved data
			# data = self.text1.GetValue() + "_" + self.text2.GetValue() + "_" +self.text3.GetValue() + "#" +self.text4.GetValue()
			# print "MERDE:  ", data
			# self.parent.CurrentGenotype = data
			# self.Destroy()
			
		if event.GetId() == self.b2.GetId():
			self.parent.CurrentGenotype = ""
			self.Destroy()

	def onButton(self, event):
		if event.GetId() == self.b1.GetId():
			self.Destroy()
			
		if event.GetId() == self.b2.GetId():
			# 
			self.Destroy()
			
	def OnMouseEvt(self, event):
			pos = self.bitIMG.ScreenToClient(wx.GetMousePosition())
			#print pos[0]/self.parent.sc, " , ",pos[1]/self.parent.sc , " / ",self.parent.imW, " , ", self.parent.imH
			# Collect saved data

                                      # for the position
			dc.SelectObject(wx.NullBitmap)

#-------------------------------------------------------------------
if __name__ == '__main__':
    import ProjectClass
    project_obj = ProjectClass.ProjectClass()
    root_folder = "/home/lionel/DATA/"
    project_obj.root_folder = root_folder

    app = wx.App(False)
    frame = ProjectFrame(project_obj)
    frame.Show(True)
    app.MainLoop()
