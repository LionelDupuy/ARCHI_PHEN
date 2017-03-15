import pygame
import pygame.camera
from pygame.locals import *
#import wx
import time
from datetime import date
import numpy
import Image
import zbar
from pgu import gui

pygame.init()
pygame.camera.init()
automatic = False
pause = 0.1
size = ( 640 , 480 )
window_size = ( 640 , 480 )
shrunken = size
camlist = pygame.camera.list_cameras()
camera = pygame.camera.Camera(camlist[0], size, "RGBA")
camera.start()
b = (0, 0, 0xFF)
r = (0xFF, 0, 0)
t = (0x5A, 0xAA, 0xAA)
yellow = (255, 255, 0)
red = (255, 0, 0)
class CamControl:
    def __init__(self):
        self.going = True        
        self.window = pygame.display.set_mode( window_size, 0 )
        pygame.display.set_caption("ArchiPhen - Root Phenotyping")
        self.snapshot_raw = pygame.surface.Surface( size, 0, self.window)
        self.last_array = None
        self.diffs = None
        self.ccolor = (0x5A, 0xAA, 0xAA)
		
        self.scanner = zbar.ImageScanner()

        # configure the reader
        self.scanner.parse_config('enable')
        #self.scanner.set_config(0, zbar.Config.ENABLE, 0)
        #self.scanner.set_config(zbar.Symbol.QRCODE, zbar.Config.ENABLE, 1)
        self.label = ""
        self.date = date.today()
		
    def readQRCODE(self, MASK):
		self.label = ""
		pilImage = self.pygame_to_pil_img(MASK).convert('L')
		#pilImage = Image.open("qr.bmp").convert('L')
		pilImage = pilImage.convert('L')
		width, height = pilImage.size
		raw = pilImage.tostring()  
		# wrap image data
		image = zbar.Image(width, height, 'Y800', raw)  

		# scan the image for barcodes
		self.scanner.scan(image)
		# extract results
		
		for symbol in image:
			self.label = symbol.data

		# clean up
		del(image)
    def pygame_to_pil_img(self, pg_surface):
		imgstr = pygame.image.tostring(pg_surface, 'RGB')
		return Image.fromstring('RGB', pg_surface.get_size(), imgstr)
		
    def pil_to_pygame_img(self,pil_img):
		imgstr = pil_img.tostring()
		return pygame.image.fromstring(imgstr, pil_img.size, 'RGB')		
		
    def capture_image(self, date, id):
		self.label = ""
    def run(self):
        self.going = True
        while (self.going):
            pygame.event.pump()
            time.sleep(pause)
			
            # Update video output
            self.snapshot_raw = camera.get_image(self.snapshot_raw)
			
            # Listen for keyboard
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    self.going = False
                if e.type == KEYDOWN and e.key == K_SPACE:
					mask_size = (max_rect.right-max_rect.left,max_rect.bottom-max_rect.top)
					self.snapshot_mask = pygame.surface.Surface( mask_size, 0, self.window)
					s2d = pygame.surfarray.array2d( self.snapshot_raw)
					s2d = s2d[max_rect.left:max_rect.right, max_rect.top:max_rect.bottom]
					pygame.surfarray.blit_array(self.snapshot_mask, s2d)
					self.readQRCODE(self.snapshot_mask)     
                if e.type == KEYDOWN and e.key == K_TAB:
					app = gui.App()
					app = gui.Desktop()
					app.connect(gui.QUIT,app.quit,None)
					
					##The table code is entered much like HTML.
					##::
					c = gui.Table()
					c.tr()
					c.td(gui.Label("Sample ID"))
					
					c.tr()
					c.td(gui.Label(""))
					c.tr()
					
					w = gui.Input(value='',size=8)
					c.td(w,colspan=1)
					def cb():
						self.label = w.value
						app.quit()
					c.tr()
					c.td(gui.Label(""))
					c.tr()
					
					btn = gui.Button("Manual Save")
					btn.connect(gui.CLICK, cb)
					c.td(btn,colspan=1)
					app.run(c)	
            
                if e.type == KEYDOWN and e.key == K_RETURN and self.label != "" and self.date !="":
					self.capture_image(self.date, self.label)
                elif e.type == KEYDOWN and e.key == K_RETURN and (self.label == "" or self.date == ""):
					app = gui.App()
					app = gui.Desktop()
					app.connect(gui.QUIT,app.quit,None)
					c = gui.Table()
					c.tr()
					c.td(gui.Label("DATA NOT SAVED!"))
					
					c.tr()
					c.td(gui.Label(""))
					c.tr()
					
					def cb():
						app.quit()
					c.tr()
					c.td(gui.Label(""))
					c.tr()
					btn = gui.Button("OK")
					btn.connect(gui.CLICK, cb)
					c.td(btn,colspan=1)
					app.run(c)	
            					
            m = pygame.mask.from_threshold(self.snapshot_raw, self.ccolor, (50, 50, 50))
            max_rect = None
            max_area = 0
            for rect in m.get_bounding_rects():
				if rect[2]*rect[3] > max_area:
					max_area = rect[2]*rect[3] 
					max_rect = rect
            if max_area>0:
				pygame.draw.rect(self.snapshot_raw, (250,0,0), max_rect, 5)

            # pick a font you have and set its size
            
            # apply it to text on a label
            if self.label == "":
				myfont = pygame.font.SysFont("Comic Sans MS", 16)
				label = myfont.render("No Genotype detected - press space bar decode QRcode ", 1, red)
            else:
				myfont = pygame.font.SysFont("Comic Sans MS", 16)
				label = myfont.render("GENOTYPE: " + str(self.label), 1, yellow)

            self.window.blit(self.snapshot_raw, (0,0))
            self.window.blit(label, (2, 2))
            pygame.display.flip()
            
              

    def calibrate(self):
		self.going = True
		while (self.going):
			# capture the image
			self.snapshot_raw = camera.get_image(self.snapshot_raw)
			# blit it to the display surface
			#self.window.blit(self.snapshot_raw, (0,0))
			# make a rect in the middle of the screen
			crect = pygame.draw.rect(self.snapshot_raw, (255,0,0), (size[0]/2-20,size[1]/2-20,40,40), 1)
			# get the average color of the area inside the rect
			self.ccolor = pygame.transform.average_color(self.snapshot_raw, crect)
			
			# pick a font you have and set its size
			myfont = pygame.font.SysFont("Comic Sans MS", 16)
            # apply it to text on a label
			label = myfont.render("CALIBRATION: target color then pres Esc", 1, yellow)
			self.window.blit(self.snapshot_raw, (0,0))
			self.window.blit(label, (2, 2))
			pygame.display.flip()
            # Listen for keyboard
			events = pygame.event.get()
			for e in events:
			    if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
			        self.going = False	

# 
					

cam = CamControl()
cam.calibrate()
cam.run()