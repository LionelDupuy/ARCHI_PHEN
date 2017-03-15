import ij.*;
import ij.measure.*;
import ij.plugin.*;
import ij.plugin.filter.*;
import ij.process.*;
import ij.process.AutoThresholder.Method;
import ij.gui.*;
import ij.gui.PolygonRoi;
import ij.plugin.filter.GaussianBlur;
import ij.plugin.ContrastEnhancer;

import java.awt.*;
import java.awt.Polygon;
import java.awt.Rectangle;

import java.lang.Math.*;
import ij.plugin.frame.RoiManager;
import ij.plugin.filter.MaximumFinder;
import ij.process.ImageConverter;
import ij.process.EllipseFitter;
import ij.plugin.ImageCalculator;

import ij.io.FileInfo;
import java.lang.String;

import ij.gui.Roi;
import ij.gui.Roi.*;
import ij.gui.ShapeRoi;
import ij.plugin.frame.RoiManager;
import java.awt.Color;
import java.awt.Rectangle;
import java.awt.Font;
import ij.gui.TextRoi;
import java.util.*;
import java.awt.font.*;

import java.io.*;

public class root_analysis_bounds implements PlugIn {
	@SuppressWarnings("unchecked") 
	// constants
	int width = 0;
	int height = 0;
	// data structure

	ArrayList[] roi_list;
	ImagePlus IProcessed;
	ImageProcessor IP;
	ImagePlus imp_result;				// results for calibration
	ImageStack main_stack;
	
	int n_slice;
	ArrayList[] roi_id_slice;
	double max_rg;
	public void run(String arg) {
		if (IJ.versionLessThan("1.26i"))
			return;
		ImagePlus imp = IJ.getImage();
		init_data(imp);
		particle_analysis(imp);	// find regions in the image
	}
	
	public void init_data(ImagePlus imp) 
	{
		// Image Data
		IProcessed = imp;//new ImagePlus("segmented",imp.getProcessor());
		IP = IProcessed.getProcessor();
		main_stack = imp.getStack();
		width = IP.getWidth();
		height = IP.getHeight();
		n_slice = IProcessed.getStackSize();		
	}
	public void particle_analysis(ImagePlus imp)
	{
		//IP = imp.getProcessor();
		// filtering
		IJ.run("Duplicate...", "title=XXX duplicate range=1-" + IProcessed.getStackSize());
		IJ.run("8-bit");
		ImagePlus imp2 = IJ.getImage();
		//ImagePlus imp_hue =  new ImagePlus("Kinematics",IP);  // temporry output
	    	//ImageStack stack = imp_hue.createEmptyStack();

		ImageProcessor ip0 = imp.getProcessor();
		ImageProcessor ip1 = imp2.getProcessor();
		ImageProcessor hip = getImageHue(ip0, ip1);

		imp2.draw();
		IJ.setAutoThreshold(imp2, "Default");
		//IJ.setOption("BlackBackground", false);
		IJ.run("Convert to Mask", "method=Default background=Black");
		IJ.run("Invert", "stack");

		////////////////////////////////////////////////////////////
		//Do particle analysis for leaf shape. Should find only one big object per image
 		/////////////////////////////////////////////////////////////
		IJ.run("Set Measurements...", "  area center bounding stack feret's redirect=None decimal=3");
		IJ.run("Analyze Particles...", "size=500000-Infinity circularity=0.00-1.00 show=Nothing add stack"); // show=Nothing

		// get individual ROI data
		imp2.changes = false; 
		imp2.close();
		imp.show();
		RoiManager.getInstance().select(0);
		
		IJ.run("Crop");
		FileInfo im_file = imp.getOriginalFileInfo();
		String im_name = im_file.fileName;
		String im_directory = im_file.directory;

		String[] parts = im_name.split("\\.");
		IJ.saveAs("Jpeg", im_directory + parts[0] + "-CROP-.jpg");
		IJ.selectWindow("ROI Manager"); 
		//IJ.run("Close"); 
		IJ.run("Close All");
		}
	
	public int getLabelThreshold(ImageProcessor ip_in, ImageProcessor var_in) 
	{
		int w = var_in.getWidth();
		int h = var_in.getHeight();
		for (int i=0;i<w;i++)
		{
			for (int j=0;j<h;j++)
			{
			int var = var_in.getPixel(i,j);
			int[] rgb = new int[3];
			ip_in.getPixel(i,j,rgb);
			int i_label = getLabelIndex(var,rgb[0]);
			var_in.set(i,j,i_label);
			}	
		}
		return 1;
	}

	
	public int getLabelIndex(int var, int I)
	{
	return Math.min(var,I);	
	}
	public ImageProcessor getImageHue(ImageProcessor ip_in, ImageProcessor ip_out) 
	{
		int w = ip_in.getWidth();
		int h = ip_in.getHeight();
		for (int i=0;i<w;i++)
		{
			for (int j=0;j<h;j++)
			{
			int[] rgb = new int[3];
			ip_in.getPixel(i,j,rgb);
			int hue = getHue(rgb[0],rgb[1],rgb[2]);
			ip_out.set(i,j,hue);
			}	
		}
	  	return ip_out;
	}		
	public int getHue(int r, int g, int b) 
	{
	  int hue = 0;
	  hue = (int)(Math.atan2(1.732050808 * (r - b), (2 * r - g - b)) * 57.295779513);
	  return hue;
	}
	
}


