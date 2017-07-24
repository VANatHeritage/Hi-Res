# ----------------------------------------------------------------------------------------
# CreateLandCoverMosaic.py
# Version:  ArcGIS 10.3.1 / Python 2.7.8
# Creation Date: 2017-07-17
# Last Edit: 2017-07-19
# Creator(s):  Roy Gilb and DJ Helkowski
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
import arceditor

# Script arguments
outputGDB = arcpy.GetParameterAsText(0)
mosaicName = arcpy.GetParameterAsText(1)
inputRastFolder = arcpy.GetParameterAsText(2) #Folder with raster files you want to be added to the mosaic dataset
snapRaster = arcpy.GetParameterAsText(3)
inputFootprint = arcpy.GetParameterAsText(4)
outProjRaster = arcpy.GetParameterAsText(5)
inputColormap = arcpy.GetParameterAsText(6)

# Local variables:
mosaicFile = outputGDB + os.sep + mosaicName
cellSize = 1 #3.28084                     #Set output cell size to 1 (meter), rather than 3.28084 feet
resamp = "NEAREST"
copyMosaic = "F:\Gilb_Work\LandCover\Land_Cover_Raster_Tiles_Southern_Rivers_Area_3\SouthRivers3_Output\mosaic_copy.tif"    #Note - need to parameterize the output folder here

outCoordSys = arcpy.Describe(snapRaster).spatialReference
inCoordSys  = arcpy.Describe(inputColormap).spatialReference


# Set Geoprocessing environments
arcpy.env.snapRaster = snapRaster

#Loop through folder with all the rasters - look if the tif starts with N or S, and then add them to corresponding (N or S) raster lists 

# Process: Create Mosaic Dataset
arcpy.CreateMosaicDataset_management(outputGDB, mosaicName, inCoordSys, "1", "8_BIT_UNSIGNED", "NONE", "")

arcpy.AddMessage('Mosaic dataset created...')
arcpy.AddMessage('Adding Rasters to the dataset...')

# Process: Add Rasters To Mosaic Dataset
arcpy.AddRastersToMosaicDataset_management(mosaicFile, "Raster Dataset", inputRastFolder, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", inCoordSys)

arcpy.AddMessage('Importing geometry and setting mosaic dataset properties...')

# Process: Import Mosaic Dataset Geometry
arcpy.ImportMosaicDatasetGeometry_management(mosaicFile, "FOOTPRINT", "Name", inputFootprint, "Tile")

# Process: Set Mosaic Dataset Properties
arcpy.SetMosaicDatasetProperties_management(mosaicFile, "4100", "15000", "None;JPEG;LZ77;LERC", "None", "75", "0.01", resamp, "CLIP", "FOOTPRINTS_MAY_CONTAIN_NODATA", "CLIP", "NOT_APPLY", "", "NONE", "NorthWest;Center;LockRaster;ByAttribute;Nadir;Viewpoint;Seamline;None", "NorthWest", "", "", "ASCENDING", "FIRST", "10", "600", "300", "20", "0.8", cellSize, "Basic", "Name;MinPS;MaxPS;LowPS;HighPS;Tag;GroupName;ProductName;CenterX;CenterY;ZOrder;Shape_Length;Shape_Area;Thumbnail", "DISABLED", "", "", "", "", "20", "1000", "THEMATIC", "1", "", "None")

arcpy.AddMessage('Copying mosaic dataset...')

arcpy.CopyRaster_management(mosaicFile, copyMosaic)    #Note - need to parameterize the output folder or file here (copyMosaic)

arcpy.AddMessage('Projecting mosaic dataset...')
# Process: Project Raster
arcpy.ProjectRaster_management(copyMosaic, outProjRaster, outCoordSys, resamp, cellSize, "NAD_1983_To_HARN_Virginia", "", inCoordSys) #NAD_1983_HARN_To_WGS_1984 + WGS_1984_(ITRF00)_To_NAD_1983  ?

# Process: Add Colormap
arcpy.AddColormap_management(outProjRaster, inputColormap, "")

