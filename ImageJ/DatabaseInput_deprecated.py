import time
from datetime import date
import numpy
from PIL import Image
import zbar
import os,sys
import wx                    #   GUI

# Handle time lapse!

scanner = zbar.ImageScanner()
# configure the reader
scanner.parse_config('enable')
#scanner.set_config(0, zbar.Config.ENABLE, 0)
#scanner.set_config(zbar.Symbol.QRCODE, zbar.Config.ENABLE, 1)
label = ""

# TODO
# Read label better (crop enhance contrast etc...)
# copy files
# record previous file


def readQRCODE(ImageFile):
	label = ""
	pilImage = Image.open(ImageFile)
	width, height = pilImage.size
	pilImage = pilImage.crop((int(0.18*width), int(0.2*height),int(0.97*width), int(0.95*height)))
	
	pilImage = pilImage.convert('L')
	width, height = pilImage.size
	raw = pilImage.tostring()  
	# wrap image data
	image = zbar.Image(width, height, 'Y800', raw)  

	# scan the image for barcodes
	scanner.scan(image)
	# extract results
		
	for symbol in image:
		label = symbol.data

	# clean up
	del(image)
	return label

	
	

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(400,300))
		self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE |  wx.TE_READONLY)
		self.CreateStatusBar() # A Statusbar in the bottom of the window
		# FOlders
		self.dest_folder = os.path.dirname(sys.argv[0])
		self.root_folder = os.path.dirname(sys.argv[0])
		
		# Setting up the menu.
		filemenu= wx.Menu()

		# wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
		filemenu.Append(1, "&Base Folders"," Set folders")
		filemenu.Append(2, "&Run"," scan for files")
		filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
		filemenu.AppendSeparator()
		filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

		# xxxxxxx
		self.Bind(wx.EVT_MENU, self.get_folder, id=1)
		self.Bind(wx.EVT_MENU, self.scan_data, id=2)
		
		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
		self.Show(True)


	def get_folder(self, id):
		dlg = wx.DirDialog(self, "Choose Root Folder:")
		if dlg.ShowModal() == wx.ID_OK:
			self.root_folder = dlg.GetPath()
		dlg.Destroy()
			
	def scan_data(self, id):
		#################################################################
		# Find all suitable files in the current folder
		#################################################################
		dir = self.root_folder#os.path.dirname(sys.argv[0])
		sys.path.append(dir)
		for f in os.listdir(dir): 
			file, ext = os.path.splitext(f) # Handles no-extension files, etc.
			if ext == '.JPG':
				base_row = file.split("-")
				base = base_row[0]
				if len(base_row) == 1:
					if os.path.isfile(dir+ "\\"+ file + "-QR-.jpg"):
						genotype = readQRCODE(dir+ "\\"+ file + "-QR-.jpg")
						
						# image properties
						file_tmp1 = file.split('_')
						file_id = file_tmp1[1]
						#os.path.getmtime(dir+ "\\"+ file +ext)
						
						# Image identifiers
						identifyer = [None,None,None]
						
						if len(genotype) > 5:
							text = "Root directory:  " + dir + "\n"
							text += "File:  " + file + "\n"
							text += "Genotype: " + genotype
							self.control.SetValue(text)
							wx.Yield()
							identifyer = genotype.split('_')
							
						else: 
							pilImage = Image.open(dir+ "\\"+ file + "-QR-.jpg")
							width, height = pilImage.size
							pilImage = pilImage.crop((int(0.18*width), int(0.3*height),int(0.97*width), int(0.92*height)))
							width, height = pilImage.size
							sc = 0.6
							pilImage = pilImage.resize((int(width*sc),int(height*sc)), Image.ANTIALIAS)
							img = wx.EmptyImage( *pilImage.size )
							pilImageCopy = pilImage.copy()
							pilImageCopyRGB = pilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
							pilImageRgbData =pilImageCopyRGB.tostring()
							img.SetData( pilImageRgbData )
							
							identifyer_length = 0
							while identifyer_length>-1:# !=3:
								dlg = wx.TextEntryDialog(self, 'Type "Species Population Id" with space as separation', 'Could not read bar code', '')
								dlg.SetValue("")
								
								self.pnl = MyFrame(dlg, -1, "Label not read", size=(int(width*sc),int(height*sc)), pos = (800,100), style = wx.DEFAULT_FRAME_STYLE, pic = img)
								self.pnl.Show(True)
								
								if dlg.ShowModal() == wx.ID_OK:
									txtvalue = dlg.GetValue() #genotype.split('_')
									identifyer = txtvalue.split(' ')
									identifyer_length = len(identifyer)
								dlg.Destroy()
							
						
					else:
							text = "!!! Could not recover barcode for !!! :\n\n"
							text += "Root directory:  " + dir + "\n"
							text += "File:  " + file + "\n"
							self.control.SetValue(text)
							wx.Yield()

class MyFrame(wx.Frame):
    def __init__(
            self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, pic = None
            ):
			
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        panel = wx.Panel(self, -1)
        wx.StaticBitmap(panel, -1, pic.ConvertToBitmap(), (0, 0))



    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()

					
app = wx.App(False)
frame = MainWindow(None, "Sample editor")
app.MainLoop()


			
		