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
     # Extract coordinates of a and b
     ax, ay = d.xy(a[0], a[1])
     bx, by = d.xy(b[0], b[1])

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
     
     # output is an index array that has the indices of elements
     # that are non-zero, and value == 1
     output = numpy.argwhere(re == 1)
    
    # Here we reorder and sort (if necessary) the output, 
    # such that the order starts from viewpoint (x,y) to horizonpoint (x,y)
     if bx >= ax and by > ay: # Upper right quadrant is ok...
        output = numpy.nonzero(re == 1)
        outputx = numpy.sort(output[0])
        outputx[::-1].sort()
        outputy = numpy.sort(output[1])
        output = [i for i in zip(outputx, outputy)]
     elif bx <= ax and by >= ay: # Upper left quadrant is good!
        output = numpy.argwhere(re == 1)
        output = numpy.flipud(output)
     elif bx <= ax and by <= ay: # Lower left quadrant is ok...
        output = numpy.nonzero(re == 1)
        outputx = numpy.sort(output[0])
        outputy = numpy.sort(output[1])
        outputy[::-1].sort()
        output = [i for i in zip(outputx, outputy)]
     else:                         # Lower right quadrant is good!
        output = numpy.argwhere(re == 1)
        
     return output, re


def slope(v,q,dx,zv,zq):
    """
    Function that computes slope of tangent
    Inputs:
    v:              Coordinates x, y of viewpoint
    q:              Cell q to update slope from               
    dx:             delta x or cartesian distance between points 
    zv:             height value of viewpoint 
    zq:             height       
    Output:
    m:              slope 
    """
    y = zq
    b = zv
    a = (y - b)/dx
    return a

def tangent_curr(a,x,b):
    """
    Function that computes tangent 
    Inputs:
    a:              previous slope
    x:              dx of vq (cartesian distance)
    b:              viewpoint height 
    Outputs:
    y:              tangent height at given cell q
    """
    y = (a*x) + b
    return y

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
    #-- numpy of input
    npi  = d.read(1)
    shape = npi.shape
    #-- fetch the 1st viewpoint
    v = viewpoints[0]

    #cellsize 
    cell_ul,_ = d.xy(v[0],v[1],offset='ul')
    cell_ur,_ = d.xy(v[0],v[1],offset='ur')
    cellsize = cell_ur-cell_ul

    #-- Radius of viewpoint
    radius = maxdistance

    
    #-- the results of the viewshed in npvs, all values=3
    # This is actually our 'empty' raster to start with
    npvs = numpy.full(d.shape, 3, dtype=numpy.int8)

    # Now fill the rows and cols according to their index,
    # with following possible values:
    # 0: not visible from the viewpoint(s) (but inside the 
    # max-distance/horizon zone(s))
    # 1: visible from the viewpoint(s)
    # 2: the pixel contains a viewpoint
    # 3: the pixel is outside the max-distance/horizon zone(s)

    for i in viewpoints:
        #-- numpy of input
        npi  = d.read(1)
        # The viewpoint (x,y,z)
        v = i
        vco = (v[0],v[1])
        # index of this point in the numpy raster
        vi = vrow, vcol = d.index(v[0], v[1])

        # This is the heigth value of the centerpoint of the viewshed
        h = npi[vrow][vcol] + v[2]

        # We mark the viewpoint with value 2 on the raster 
        npvs[vrow,vcol] = 2 

        # Loop though every raster cell and enumerate 
        # (indices of row and column respectively)
        for row in enumerate(npvs):
            row_i = row[0]
            for col in enumerate(row[1]):
                col_i = col[0]
                idx = row_i, col_i
                pt = d.xy(row_i,col_i)
                dist = distance(vco,pt)
                # Here, four if statements follow, that consist of if, else statements
                # It is checked if a point on the horizon, finds itself on one of the 
                # extents of the raster (8 possibilities)
                if dist > (radius - cellsize) and dist < radius and row_i == 0:
                    if col_i < vcol:
                        for col_t in range(col_i,vcol+2):
                            horizon_point = (0,col_t)
                            output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                            slope_last = [-100]
                            # For each cell on rasterized line, 
                            # compute tangent between viewpoint (v) and cell (qi)
                            for cell in output:
                                cell_pt_i = ptix, ptiy = cell[0], cell[1]
                                cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                                dist_vq = distance(vco,cell_co_pt)
                                zq = npi[ptix,ptiy]
                                y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                                # If cell height is lower than tangent hight, 
                                # map cell invisible (0).
                                if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                                    npvs[ptix,ptiy] = 0
                                # If cell height is higher than tangent,
                                # map cell visible (1) and update slope tangent
                                elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                                    npvs[ptix,ptiy] = 1
                                    slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                                    slope_last.append(slope_curr)
                    else:
                        for col_t in range(vcol,col_i+2):
                            horizon_point = (0,col_t)
                            output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                            slope_last = [-100]
                            # For each cell on rasterized line, 
                            # compute tangent between viewpoint (v) and cell (qi)
                            for cell in output:
                                cell_pt_i = ptix, ptiy = cell[0], cell[1]
                                cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                                dist_vq = distance(vco,cell_co_pt)
                                zq = npi[ptix,ptiy]
                                y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                                # If cell height is lower than tangent hight, 
                                # map cell invisible (0).
                                if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                                    npvs[ptix,ptiy] = 0
                                # If cell height is higher than tangent,
                                # map cell visible (1) and update slope tangent
                                elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                                    npvs[ptix,ptiy] = 1
                                    slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                                    slope_last.append(slope_curr)
                elif dist > (radius - cellsize) and dist < radius and row_i == (shape[0]-1):
                    if col_i < vcol:
                        for col_t in range(col_i,vcol+2):
                            horizon_point = (shape[0],col_t)
                            output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                            slope_last = [-100]
                            # For each cell on rasterized line, 
                            # compute tangent between viewpoint (v) and cell (qi)
                            for cell in output:
                                cell_pt_i = ptix, ptiy = cell[0], cell[1]
                                cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                                dist_vq = distance(vco,cell_co_pt)
                                zq = npi[ptix,ptiy]
                                y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                                # If cell height is lower than tangent hight, 
                                # map cell invisible (0).
                                if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                                    npvs[ptix,ptiy] = 0
                                # If cell height is higher than tangent,
                                # map cell visible (1) and update slope tangent
                                elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                                    npvs[ptix,ptiy] = 1
                                    slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                                    slope_last.append(slope_curr)
                    else:
                        for col_t in range(vcol,col_i+2):
                            horizon_point = (shape[0],col_t)
                            output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                            slope_last = [-100]
                            # For each cell on rasterized line, 
                            # compute tangent between viewpoint (v) and cell (qi)
                            for cell in output:
                                cell_pt_i = ptix, ptiy = cell[0], cell[1]
                                cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                                dist_vq = distance(vco,cell_co_pt)
                                zq = npi[ptix,ptiy]
                                y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                                # If cell height is lower than tangent hight, 
                                # map cell invisible (0).
                                if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                                    npvs[ptix,ptiy] = 0
                                # If cell height is higher than tangent,
                                # map cell visible (1) and update slope tangent
                                elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                                    npvs[ptix,ptiy] = 1
                                    slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                                    slope_last.append(slope_curr)
                elif dist > (radius - cellsize) and dist < radius and col_i == 0:
                    if row_i < vrow:
                        for row_t in range(row_i,vrow+2):
                            horizon_point = (row_t,0)
                            output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                            slope_last = [-100]
                            # For each cell on rasterized line, 
                            # compute tangent between viewpoint (v) and cell (qi)
                            for cell in output:
                                cell_pt_i = ptix, ptiy = cell[0], cell[1]
                                cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                                dist_vq = distance(vco,cell_co_pt)
                                zq = npi[ptix,ptiy]
                                y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                                # If cell height is lower than tangent hight, 
                                # map cell invisible (0).
                                if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                                    npvs[ptix,ptiy] = 0
                                # If cell height is higher than tangent,
                                # map cell visible (1) and update slope tangent
                                elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                                    npvs[ptix,ptiy] = 1
                                    slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                                    slope_last.append(slope_curr)
                    else:
                        for row_t in range(vrow,row_i+2):
                            horizon_point = (row_t,0)
                            output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                            slope_last = [-100]
                            # For each cell on rasterized line, 
                            # compute tangent between viewpoint (v) and cell (qi)
                            for cell in output:
                                cell_pt_i = ptix, ptiy = cell[0], cell[1]
                                cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                                dist_vq = distance(vco,cell_co_pt)
                                zq = npi[ptix,ptiy]
                                y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                                # If cell height is lower than tangent hight, 
                                # map cell invisible (0).
                                if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                                    npvs[ptix,ptiy] = 0
                                # If cell height is higher than tangent,
                                # map cell visible (1) and update slope tangent
                                elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                                    npvs[ptix,ptiy] = 1
                                    slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                                    slope_last.append(slope_curr)
                elif dist > (radius - cellsize) and dist < radius and col_i == (shape[1]-1):
                    if row_i < vrow:
                        for row_t in range(row_i,vrow+2):
                            horizon_point = (row_t,0)
                            output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                            slope_last = [-100]
                            # For each cell on rasterized line, 
                            # compute tangent between viewpoint (v) and cell (qi)
                            for cell in output:
                                cell_pt_i = ptix, ptiy = cell[0], cell[1]
                                cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                                dist_vq = distance(vco,cell_co_pt)
                                zq = npi[ptix,ptiy]
                                y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                                # If cell height is lower than tangent hight, 
                                # map cell invisible (0).
                                if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                                    npvs[ptix,ptiy] = 0
                                # If cell height is higher than tangent,
                                # map cell visible (1) and update slope tangent
                                elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                                    npvs[ptix,ptiy] = 1
                                    slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                                    slope_last.append(slope_curr)
                    else:
                        for row_t in range(vrow,row_i+2):
                            horizon_point = (row_t,0)
                            output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                            slope_last = [-100]
                            # For each cell on rasterized line, 
                            # compute tangent between viewpoint (v) and cell (qi)
                            for cell in output:
                                cell_pt_i = ptix, ptiy = cell[0], cell[1]
                                cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                                dist_vq = distance(vco,cell_co_pt)
                                zq = npi[ptix,ptiy]
                                y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                                # If cell height is lower than tangent hight, 
                                # map cell invisible (0).
                                if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                                    npvs[ptix,ptiy] = 0
                                # If cell height is higher than tangent,
                                # map cell visible (1) and update slope tangent
                                elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                                    npvs[ptix,ptiy] = 1
                                    slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                                    slope_last.append(slope_curr)
                elif dist > (radius - cellsize) and dist <= radius:
                    horizon_point = (row_i, col_i)
                else:
                    continue
                output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                slope_last = [-100]
                # For each cell on rasterized line, 
                # compute tangent between viewpoint (v) and cell (qi)
                for cell in output:
                    cell_pt_i = ptix, ptiy = cell[0], cell[1]
                    cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                    dist_vq = distance(vco,cell_co_pt)
                    zq = npi[ptix,ptiy]
                    y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                    # If cell height is lower than tangent hight, 
                    # map cell invisible (0).
                    if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                        npvs[ptix,ptiy] = 0
                    # If cell height is higher than tangent,
                    # map cell visible (1) and update slope tangent
                    elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                        npvs[ptix,ptiy] = 1
                        slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                        slope_last.append(slope_curr)


                            
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








