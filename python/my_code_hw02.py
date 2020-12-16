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
     line = numpy.nonzero(re == 1)
     output = numpy.argwhere(re == 1)
     return line

#def tangent(d,v,q):
    #y = a * x + b


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
    #print('our dataset: ',d)
    #print('our viewpoints',viewpoints)
    #print('our maxdistance',maxdistance)
    #print('our output file',output_file)
    #print('our output file type', type(output_file))
    # [this code can and should be removed/modified/reutilised]
    # [it's just there to help you]

    #-- numpy of input
    npi  = d.read(1)
    print('shape',d.shape)
    print('type', type(d))
    print('type', type(npi))
    print('shape npi ',npi.shape)
    print(npi[0][0])
    print()
    #-- fetch the 1st viewpoint
    v = viewpoints[0]
    #v2 = viewpoints[1]
    #print('viewpoint', v)
    #print('viewpoint', v2)
    #print('viewpoint x', v[0])
    #print('viewpoint y', v[1])

    #cellsize 
    cell_ul,_ = d.xy(v[0],v[1],offset='ul')
    cell_ur,_ = d.xy(v[0],v[1],offset='ur')
    cellsize = cell_ur-cell_ul
    #print('cellsize', cellsize)

    #-- Radius of viewpoint
    radius = maxdistance

    #-- the results of the viewshed in npvs, all values=0
    # This is actually our 'empty' raster to start with
    #npvs = numpy.zeros(d.shape, dtype=numpy.int8)
    npvs = numpy.full(d.shape, 3, dtype=numpy.int8)
    #print('npvs', npvs)
    
    # Now fill the rows and cols according to their index,
    # with following possible values:
    # 0: not visible from the viewpoint(s) (but inside the 
    # max-distance/horizon zone(s))
    # 1: visible from the viewpoint(s)
    # 2: the pixel contains a viewpoint
    # 3: the pixel is outside the max-distance/horizon zone(s)
    
    a = numpy.array([[1, 2, 3], [4, 5, 3], [7, 3, 9]])
    b = numpy.nonzero(a == 3)
    print(b[0],b[1])
    #(array([1, 1, 1, 2, 2, 2]), array([0, 1, 2, 0, 1, 2]))
    #print(b[0][0])
    for row, col in zip(b[0],b[1]):
        print(row,col)
    
    
    for i in viewpoints:
        v = i
        # index of this point in the numpy raster
        vi = vrow, vcol = d.index(v[0], v[1])
        #vi = vrow, vcol
        # This is the value of the centerpoint of the viewshed
        npvs[vrow , vcol] = 2

        for row in enumerate(npvs):
            row_i = row[0]
            for col in enumerate(row[1]):
                col_i = col[0]
                pt = d.xy(row_i,col_i)
                dist = distance(v,pt)
                if dist > (radius - cellsize) and dist < radius and npvs[row_i,col_i] != 2:
                    npvs[row_i,col_i] = 1
                    horizon_point = (row_i, col_i)
                    line = Bresenham_with_rasterio(d,vi,horizon_point)
                    print(line)
                    for row_l, col_l in zip(line[0],line[1]):
                        line_pt = (row_l,col_l)
                        if npvs[row_l,col_l] != 2:
                            #npvs[row_l,col_l] = 1
                            npvs[row_l,col_l] = npi[row_l][col_l]
                            #print(line_pt)
                            #row_li = row_l[0]
                            #for col_l in row_l:
                            #print(row_li, col_l)
                            #print(type(line[0]))
                            #npvs[row_li,col_l] = 1
                #elif dist < (radius - cellsize) and npvs[row_i,col_i] != 2:
                    #npvs[row_i,col_i] = 0
        #npvs[vrow , vcol] = 2
    
    '''
    horizon_points = []
    for row in enumerate(npvs):
        row_i = row[0]
        for col in enumerate(row[1]):
            col_i = col[0]
            if npvs[row_i,col_i] == 1:
                horizon_points.append((row_i,col_i)) 
    #print(horizon_points)       
    
    for i in viewpoints:
        vi = d.index(i[0], i[1])
        for pt in horizon_points:
            pt = d.xy(pt)
            dist = distance(i,pt)
            if dist == (radius):
                

    
    #this is from old main loop
    if npvs[row_i,col_i] != 3:

        for row in enumerate(npvs):
            row_i = row[0]
            for col in enumerate(row[1]):
                col_i = col[0]
                pt = d.xy(row_i,col_i)
                dist = distance(v,pt)
                if dist > radius:
                    npvs[row_i,col_i] = 3

                elif dist > (radius - cellsize) and dist < radius:
                    npvs[row_i,col_i] = 1
                #elif dist < (radius - cellsize) and npvs[row_i,col_i] != 2:
                    #npvs[row_i,col_i] = 0



    
    # One of the horizon points
    #print('first horizon point',horizon_points[0])
    #print('its xy coordinate', d.xy(horizon_points[0][0],horizon_points[0][1]))
    #first_line = Bresenham_with_rasterio(d,vi,horizon_points[0])
    #print(first_line)    
    
    # Fuse numpy arrays
    #mask = (npvs == 0)
    #npvsf = numpy.copy(npvs)
    #npvsf[mask] = first_line[mask]
    '''
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
    
    print("Viewshed file written to '%s'" % output_file)








