# ----------------------------------------------------------------------------------------
# CreateLandCoverMosaic.py
# Version:  ArcGIS 10.3.1 / Python 2.7.8
# Creation Date: 2017-07-17
# Last Edit: 2017-07-25
# Creator(s):  Roy Gilb and DJ Helkowski
# Edited by: Kirsten Hazler
# 
# Summary:
# This model creates a mosaic dataset and places it into an output geodatabase. It then adds raster tiles to the mosaic dataset. Next, the model imports mosaic dataset geometry from an imported footprint. 
# Then, the model sets dataset properties and afterwards, the raster dataset becomes projected. Finally, a colormap is imported from one of the original raster files. 
#
# Usage Tips:
#
# Dependencies:
#
# Syntax: CreateLandCoverMosaic <outputGDB> <mosaicName> <inputRastFolder> <snapRaster> <inputFootprint> <outProjRaster> <inputColormap> <outputDataset> 
# Description: 
# 
# Parameters:
# Mosaic Dataset Name - select a name for your mosaic dataset.
# Output Geodatabase - select a geodatabase for your mosaic dataset to be stored in.
# Input Raster Folder - Select the folder containing the raster files you want to be added to the mosaic dataset. 
#                       These input rasters are in the NAD 1983 HARN State Plane Virginia North OR South FIPS 4502 Feet coordinate system.
# Input Footprint Geometry - Select a feature class whose footprint will match the mosaic dataset.
# Snap Raster - Select a snap raster that is in the Virginia Lambert coordinate system. 
# Output Projected Raster - Select the name and storage of your projected raster.
# Input Raster Colormap - select the raster file from which you want to import a colormap to the output raster dataset. 

# ---------------------------------------------------------------------------
#import modules
import arcpy # to get ArcGIS functionality
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import os # provides access to operating system funtionality such as file and directory paths
import sys # provides access to Python system functions
import traceback # used for error handling
# Set the necessary product code
# import arceditor
# KH Comment: Why the above line importing arceditor? I have never used this in a script run from an Arc toolbox.

# Script arguments
# KH Comment: Pare down the number of user-entered parameters. Have them enter an output TIF; get the output directory from that and then generate the outputGDB and mosaicName automatically. Get the Colormap from the first of the input rasters.
# outputGDB = arcpy.GetParameterAsText(0) # Hard-code this in instead
# mosaicName = arcpy.GetParameterAsText(1) # Hard-code this in instead
inputRastFolder = arcpy.GetParameterAsText(0) #Folder with raster files you want to be added to the mosaic dataset
filterString = arcpy.GetParameterAsText(1) # String (e.g., "N" or "S") used to restrict rasters selected for processing
### In the toolbox, make the above a drop-down with only two options
snapRaster = arcpy.GetParameterAsText(2)
inputFootprint = arcpy.GetParameterAsText(3)
outProjRaster = arcpy.GetParameterAsText(4)
# inputColormap = arcpy.GetParameterAsText(6) # Hard-code this in instead

### Still to do: Edit toolbox to reflect changes in user-specified parameters
### Also clean up the obsolete junk and comments above when done

# Local variables:
cellSizeIn = 3.28084  #You need the input cell size first, which is in feet. Actually it would be more elegant to grab the cell size from one of the input rasters, rather than hard-coding the number.
cellSizeOut = 1  #Set output cell size to 1 (meter), rather than 3.28084 (feet)
resamp = "NEAREST"
outDir = os.path.dirname(outProjRaster)

### To do: create geodatabase named gdbName in outDir
mosaicFile = outDir + os.sep + gdbName + os.sep + "mdTmp"
copyMosaic = outDir + os.sep + "rdTmp.tif"    #Place copied mosaic in same folder as output TIFF
outCoordSys = arcpy.Describe(snapRaster).spatialReference
geoTrans = "NAD_1983_HARN_To_WGS_1984 + WGS_1984_(ITRF00)_To_NAD_1983"
# inCoordSys  = arcpy.Describe(inputColormap).spatialReference ## Need to code this in below, instead

### To do: check the datum of the input snap raster. If it is not NAD_1983, throw error and abort b/c then geoTrans will be inappropriate. Alternatively: make geoTrans a user-specified input, with the current transformation string as the default in the tool.

# Set Geoprocessing environments
arcpy.env.snapRaster = snapRaster

#Loop through folder with all the rasters - look if the tif starts with N or S, and then add them to corresponding (N or S) raster lists 
### To do: create a list containing only the paths to rasters with the specified criterea (i.e., raster name starts with N or S)
# rasterList = 

### To do: get the input coordinate system from the first raster in the list
# inCoordSys # define this variable here

### To do: check coordinate systems of all rasters in list; if not all the same as inCoordSys, throw error and abort.

# Process: Create Mosaic Dataset
arcpy.CreateMosaicDataset_management(outputGDB, mosaicName, inCoordSys, "1", "8_BIT_UNSIGNED", "NONE", "")

arcpy.AddMessage('Mosaic dataset created...')
arcpy.AddMessage('Adding Rasters to the dataset...')

# Process: Add Rasters To Mosaic Dataset
# Replaced inputRastFolder with rasterList
arcpy.AddRastersToMosaicDataset_management(mosaicFile, "Raster Dataset", rasterList, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", inCoordSys)

arcpy.AddMessage('Importing geometry and setting mosaic dataset properties...')

# Process: Import Mosaic Dataset Geometry
arcpy.ImportMosaicDatasetGeometry_management(mosaicFile, "FOOTPRINT", "Name", inputFootprint, "Tile")

# Process: Set Mosaic Dataset Properties
arcpy.SetMosaicDatasetProperties_management(mosaicFile, "4100", "15000", "None;JPEG;LZ77;LERC", "None", "75", "0.01", resamp, "CLIP", "FOOTPRINTS_MAY_CONTAIN_NODATA", "CLIP", "NOT_APPLY", "", "NONE", "NorthWest;Center;LockRaster;ByAttribute;Nadir;Viewpoint;Seamline;None", "NorthWest", "", "", "ASCENDING", "FIRST", "10", "600", "300", "20", "0.8", cellSizeIn, "Basic", "Name;MinPS;MaxPS;LowPS;HighPS;Tag;GroupName;ProductName;CenterX;CenterY;ZOrder;Shape_Length;Shape_Area;Thumbnail", "DISABLED", "", "", "", "", "20", "1000", "THEMATIC", "1", "", "None")

arcpy.AddMessage('Copying mosaic dataset...')

arcpy.CopyRaster_management(mosaicFile, copyMosaic)

arcpy.AddMessage('Projecting mosaic dataset...')
# Process: Project Raster
arcpy.ProjectRaster_management(copyMosaic, outProjRaster, outCoordSys, resamp, cellSizeOut, geoTrans, "", inCoordSys) 

# Process: Add Colormap
arcpy.AddColormap_management(outProjRaster, inputColormap, "")