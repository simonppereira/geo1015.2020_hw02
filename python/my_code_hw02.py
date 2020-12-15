#-- my_code_hw02.py
#-- Assignment 02 GEO1015.2020
#-- [Simon Pena Pereira] 
#-- [5391210] 
#-- Daniel Dobson 
#-- 5152739 

import sys
import math
import numpy 
import rasterio
from rasterio import features

def distance(pt1, pt2):
    """Returns cartesian distance between self and other Point
    """
    dist = math.sqrt((pt1[0] - pt2[0])**2+(pt1[1] - pt2[1])**2)
    return dist 

def Bresenham_with_rasterio(d, viewpoint,horizon_point):
     # d = rasterio dataset as above
     a = viewpoint
     b = horizon_point
     #-- create in-memory a simple GeoJSON LineString
     v = {}
     v["type"] = "LineString"
     v["coordinates"] = []
     v["coordinates"].append(d.xy(a[0], a[1]))
     v["coordinates"].append(d.xy(b[0], b[1]))
     shapes = [(v, 1)]
     re = features.rasterize(shapes, 
                             out_shape=d.shape, 
                             all_touched=True,
                             transform=d.transform)
     # re is a numpy with d.shape where the line is rasterised (values != 0)
     return re

def output_viewshed(d, viewpoints, maxdistance, output_file):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster
     
    Input:
        d:            the input datasets (rasterio format)  
        viewpoints:   a list of the viewpoints (x, y, height)
        maxdistance:  max distance one can see
        output_file:  path of the file to write as output
        
    Output:
        none (but output GeoTIFF file written to 'output-file')
    """  
    # These are print to help you understand the structure of the inputs
    print('our dataset: ',d)
    #print('our viewpoints',viewpoints)
    #print('our maxdistance',maxdistance)
    #print('our output file',output_file)
    #print('our output file type', type(output_file))
    # [this code can and should be removed/modified/reutilised]
    # [it's just there to help you]

    #-- numpy of input
    npi  = d.read(1)
    #print('shape',d.shape)
    #print('type', type(npi))
        
    #-- fetch the 1st viewpoint
    v = viewpoints[0]
    print('viewpoint', v)
    print('viewpoint x', v[0])
    print('viewpoint y', v[1])

    #-- index of this point in the numpy raster
    vrow, vcol = d.index(v[0], v[1])
    vi = vrow, vcol
    print('viewpoint index', vi)
    
    #-- Radius of viewpoint
    radius = maxdistance
    #-- the results of the viewshed in npvs, all values=0
    # This is actually our 'empty' raster to start with
    npvs = numpy.zeros(d.shape, dtype=numpy.int8)
    #print('npvs', npvs)
    
    #-- put that pixel with value 2
    # This is the value of the centerpoint of the viewshed
    npvs[vrow , vcol] = 2
        
    # Cellsize of one rastercell
    cellsize = distance(d.xy(0,0), d.xy(0,1))
    
    # Now fill the rows and cols according to their index,
    # with following possible values:
    # 0: not visible from the viewpoint(s) (but inside the 
    # max-distance/horizon zone(s))
    # 1: visible from the viewpoint(s)
    # 2: the pixel contains a viewpoint
    # 3: the pixel is outside the max-distance/horizon zone(s)

    # The 'empty' raster has default values of 0
    # Now we assign values to cells that are outside of the max-distance/horizon
    # with the value of 3
    # For values on the edge of the horizon, we fill the cellvalue with 1
    horizon_points = []
    for row in enumerate(npvs):
        row_i = row[0]
        for col in enumerate(row[1]):
            col_i = col[0]
            pt = d.xy(row_i,col_i)
            dist = distance(v,pt)
            if dist > maxdistance:
                npvs[row_i,col_i] = 3
            elif dist > (maxdistance - cellsize) and dist < maxdistance:
                npvs[row_i,col_i] = 1
                horizon_points.append((row_i,col_i))

    
    '''
    # Loop in the works:
    # Perform LoS for whole circle. Every point of circle border has value of 1
    # Need Bresenham for this to work.
      
    for cell in npvs:
        horizon_points.append(cell)
    print(horizon_points)
    '''
    #print(horizon_points)
    # One of the horizon points
    print('first horizon point',horizon_points[0])
    print('its xy coordinate', d.xy(horizon_points[0][0],horizon_points[0][1]))
    first_line = Bresenham_with_rasterio(d,vi,horizon_points[0])
    print(first_line)    
    
    # Fuse numpy arrays
    mask = (npvs == 0)
    npvsf = numpy.copy(npvs)
    npvsf[mask] = first_line[mask]

    #-- write this to disk

    with rasterio.open(output_file, 'w', 
                       driver='GTiff', 
                       height=npi.shape[0],
                       width=npi.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=d.crs, 
                       transform=d.transform) as dst:
        dst.write(npvs.astype(rasterio.uint8), 1)

    
    with rasterio.open('out-test-line.tif', 'w', 
                       driver='GTiff', 
                       height=npi.shape[0],
                       width=npi.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=d.crs, 
                       transform=d.transform) as dst:
        dst.write(first_line.astype(rasterio.uint8), 1)

    with rasterio.open('out-test-mask.tif', 'w', 
                       driver='GTiff', 
                       height=npi.shape[0],
                       width=npi.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=d.crs, 
                       transform=d.transform) as dst:
        dst.write(npvsf.astype(rasterio.uint8), 1)
    
    print("Viewshed file written to '%s'" % output_file)








