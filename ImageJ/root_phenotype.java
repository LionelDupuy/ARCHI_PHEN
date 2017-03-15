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
import ij.plugin.Histogram;
import java.awt.Color;
import java.awt.Rectangle;
import java.awt.Font;
import ij.gui.TextRoi;
import java.util.*;
import java.awt.font.*;

import java.io.*;
//java.io.PrintWriter;
public class root_phenotype implements PlugIn {
	@SuppressWarnings("unchecked") 
	// constants
	int width = 0;
	int height = 0;
	// data structure
	ImagePlus IProcessed;
	ImageProcessor IP;
	ImagePlus imp_result;				// results for calibration
	ImageStack main_stack;
	
	int n_slice;
	double max_rg;
	public void run(String arg) {
		if (IJ.versionLessThan("1.26i"))
			return;
			
		ImagePlus imp = IJ.getImage();
		init_data(imp);
		skeleton(imp);	// find regions in the image
	}
	
	public void init_data(ImagePlus imp) 
	{

		// Image Data
		IProcessed = imp;//new ImagePlus("segmented",imp.getProcessor());
		IP = IProcessed.getProcessor();
		main_stack = imp.getStack();
		width = IP.getWidth();
		height = IP.getHeight();
		IJ.makeRectangle(100, 100, width-200, height-200);
		IJ.run("Crop");	
	}
	public void skeleton(ImagePlus imp)
	{
		//IP = imp.getProcessor();
		// prepare the image to store the data
/*		IJ.run("Duplicate...", "title=imp2 duplicate range=1-" + IProcessed.getStackSize());
		IJ.run("8-bit");
		ImagePlus imp2 = IJ.getImage();
		// get hue image
		ImageProcessor ip0 = imp.getProcessor();
		ImageProcessor ip1 = imp2.getProcessor();
		ImageProcessor hip = getImageHue(ip0, ip1);
		imp2.draw();
		IJ.run("Invert", "stack");
		// filters
		IJ.run("Median...", "radius=5");
		//IJ.run("Enhance Contrast...", "saturated=0.4");
		IJ.run("Subtract Background...", "rolling=50");// light");
		IJ.run("Enhance Contrast...", "saturated=0.4");
		*/
		
		// get red image
		imp.draw();
		IJ.run("Duplicate...", "title=imp2 duplicate range=1-" + IProcessed.getStackSize());
		IJ.run("8-bit");
		ImagePlus imp2 = IJ.getImage();
		ImageProcessor ip0 = imp.getProcessor();
		ImageProcessor ip1b = imp2.getProcessor();
		ImageProcessor hipb = getImageRed(ip0, ip1b);
		imp2.draw();

	
		// filters
		IJ.run("Median...", "radius=5");
		//IJ.run("Enhance Contrast...", "saturated=0.4");
		IJ.run("Subtract Background...", "rolling=50");// light");
		IJ.run("Enhance Contrast...", "saturated=0.4");

		
		
		// thresholding
		//IJ.setAutoThreshold(imp2, "MaxEntropy dark");
		//IJ.run("Convert to Mask", "method=MaxEntropy background=Black");
		IJ.setAutoThreshold(imp2, "Triangle dark"); 
		IJ.run("Convert to Mask", "method=Triangle background=Black");
	
		// distance map
		IJ.run("Distance Map");
		
		// skeletonize
		IJ.run("Duplicate...", "title=imp3 duplicate");
		IJ.run("Gaussian Blur...", "sigma=5");
		ImagePlus imp3 = IJ.getImage();
		//IJ.setAutoThreshold(imp2, "MaxEntropy dark");
		//IJ.run("Convert to Mask", "method=MaxEntropy background=Black");
		IJ.setThreshold(0, 3);
		IJ.run("Convert to Mask", "background=Black");
		IJ.run("Invert", "stack");
		/*IJ.run("Dilate");
		IJ.run("Dilate");
		IJ.run("Dilate");
		IJ.run("Dilate");
		IJ.run("Dilate");*/
		IJ.run("Skeletonize");

		
		// particle analysis
		IJ.run("Set Measurements...", "  area center bounding stack feret's redirect=None decimal=3");
		IJ.run("Analyze Particles...", "size=250-Infinity circularity=0.00-1.00 show=Nothing add stack"); // show=Nothing
		
		// merge the two ROIs
		RoiManager.getInstance().runCommand("Select All");
		RoiManager.getInstance().runCommand("Combine");
		IJ.run("Create Mask");
		
		// close imp3 (skeleton but with large segments) and rename the mask imp3
		imp3.changes = false; 
		imp3.close();
		imp3 = IJ.getImage();
		imp3.setTitle("imp3");
		
		// merge the distance map with the skeleton
		IJ.run("Image Calculator...", "image1=imp2 MIN image2=imp3"); 
		imp3.changes = false; 
		imp3.close();
		RoiManager.getInstance().runCommand("Select All");
		RoiManager.getInstance().runCommand("Combine");
		
		// save the result
		FileInfo im_file = imp.getOriginalFileInfo();
		String im_name = im_file.fileName;
		String im_directory = im_file.directory;
		String[] parts = im_name.split("\\.");
		IJ.saveAs("Tiff", im_directory + parts[0] + "-SKEL-.Tiff");
		
		// extract histogram
		int [] histogram; 
		ImageProcessor ip2 = imp2.getProcessor();
		histogram = ip2.getHistogram();
		int ln = histogram.length;
		
		try
		{
			PrintWriter out = new PrintWriter(im_directory + parts[0] + "-HIST-.txt");
			for (int i=0;i<ln;i++)
			{
				out.println(""+ i +","+ histogram[i] +"\n");
			}
			out.close( );
		}
		catch ( IOException e)
		{
		}

		////////////////////////////////////////////////////////////
		//Close everything
 		/////////////////////////////////////////////////////////////
		//IJ.run("Close All");
		
		
		}
	public void trace(ImagePlus imp)
	{
		//IP = imp.getProcessor();
		// filtering
		IJ.run("Duplicate...", "title=XXX duplicate range=1-" + IProcessed.getStackSize());
		IJ.run("8-bit");
		ImagePlus imp2 = IJ.getImage();

		ImageProcessor ip0 = imp.getProcessor();
		ImageProcessor ip1 = imp2.getProcessor();
		ImageProcessor hip = getImageRed(ip0, ip1);
		imp2.draw();
		IJ.run("Median...", "radius=10");
		IJ.run("Gaussian Blur...", "sigma=8");
		IJ.run("Subtract Background...", "rolling=50");
		IJ.run("Enhance Contrast...", "saturated=0.4");
		//setAutoThreshold("MaxEntropy dark");
		IJ.setAutoThreshold(imp2, "MaxEntropy dark");
		//IJ.setOption("BlackBackground", false);
		IJ.run("Convert to Mask", "method=MaxEntropy background=Black");
		//IJ.run("Invert", "stack");

		/*
		////////////////////////////////////////////////////////////
		//Do particle analysis for leaf shape. Should find only one big object per image
 		/////////////////////////////////////////////////////////////
		IJ.run("Set Measurements...", "  area center bounding stack feret's redirect=None decimal=3");
		IJ.run("Analyze Particles...", "size=5000-Infinity circularity=0.00-1.00 show=Nothing add stack"); // show=Nothing
		int n_ROI = RoiManager.getInstance().getgetCount();
		
		IJ.roiManager("Select", IJ.newArray(n_ROI));
		IJ.roiManager("Combine");
		IJ.run("Create Mask");
		*/
		//IJ.run("Invert", "stack");
		//IJ.run("Distance Map");
		//IJ.run("Find Maxima...", "noise=2 output=[Point Selection] light");
		// get individual ROI data
		
		
		
		/*imp2.changes = false; 
		imp2.close();
		imp.show();
		RoiManager.getInstance().select(0);
		IJ.run("Crop");
		FileInfo im_file = imp.getOriginalFileInfo();
		String im_name = im_file.fileName;
		String im_directory = im_file.directory;

		String[] parts = im_name.split("\\.");
		IJ.saveAs("Jpeg", im_directory + parts[0] + "-CROP-.jpg");
		IJ.run("Close All");*/
		
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
	public ImageProcessor getImageRed(ImageProcessor ip_in, ImageProcessor ip_out) 
	{
		int w = ip_in.getWidth();
		int h = ip_in.getHeight();
		for (int i=0;i<w;i++)
		{
			for (int j=0;j<h;j++)
			{
			int[] rgb = new int[3];
			ip_in.getPixel(i,j,rgb);
			int red = getRed(rgb[0],rgb[1],rgb[2]);
			ip_out.set(i,j,red);
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
	public int getRed(int r, int g, int b) 
	{
	  int hue = 0;
	  hue = (int)(r);
	  return hue;
	}	
}


