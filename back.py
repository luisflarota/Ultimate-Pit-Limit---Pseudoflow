from statistics import mode

import networkx as NetX
import numpy as np
import pandas as pd
import pseudoflow as pf
from plotly.subplots import make_subplots
from scipy import spatial


#transfering csv w/blockmodel to backend
class blockmodel(object):
    def __init__(self, bmodel):
        self.bmodel = bmodel
        
    def columns(self):
        return self.bmodel.columns.values.tolist()

    def summary(self, x, y, z, grade, density):
        def data():
            #See that index of x starts at 0 then... 1!
            self.x_axis = x
            self.y_axis = y
            self.z_axis = z
            self.gr_axis = grade
            self.ds_axis = density
            self.bmodel = self.bmodel.loc[:, [self.x_axis, self.y_axis,self.z_axis, self.gr_axis, self.ds_axis]]
            self.x = self.bmodel.loc[:, x]
            self.y = self.bmodel.loc[:, y]
            self.z = self.bmodel.loc[:, z]
            self.grade = self.bmodel.loc[:, grade]
            self.density = self.bmodel.loc[:, density]
            self.xlong = len(np.unique(self.x))
            self.ylong = len(np.unique(self.y))
            self.zlong = len(np.unique(self.z))
            self.long = self.xlong * self.ylong * self.zlong
            self.source = 0
            self.minx = min(self.x)
            self.maxx = max(self.x)
            self.miny = min(self.y)
            self.maxy = max(self.y)
            self.minz = min(self.z)
            self.maxz = max(self.z)
            self.min_com = min(self.xlong, self.ylong)//2
            self.sink = np.int(1 + self.long)
            self.xunique = self.x.unique()
            self.yunique = self.y.unique()
            self.zunique = self.z.unique()
            self.grademin = min(self.grade)
            self.grademax = max(self.grade)
            self.modex = int(mode(np.diff(np.unique(self.x))))
            self.modey = int(mode(np.diff(np.unique(self.x))))
            self.modez = int(mode(np.diff(np.unique(self.x))))   
  
        return data
    
    #Say go or not given the #rows
    def summary_2(self):
        return self.bmodel.shape[0]

    #Outliers are in csv by purpose
    def cleanning(self):
        self.outliers = []
        cols = [self.x_axis, self.y_axis, self.z_axis, self.gr_axis, self.ds_axis]

        mean_x, std_x = np.mean(self.x), np.std(self.x)
        mean_y, std_y = np.mean(self.y), np.std(self.y)
        mean_z, std_z = np.mean(self.z), np.std(self.z)

        #threshold for sd and mean
        threshold = 2
        for x,y,z,g,dens in zip(self.x, self.y, self.z, self.grade, self.density):
            x_score= (x - mean_x)/std_x
            y_score= (y - mean_y)/std_y
            z_score= (z - mean_z)/std_z
            x_up = x + self.modex
            x_low = x - self.modex
            y_up = y + self.modey
            y_low = y - self.modey
            z_up = z + self.modez
            z_low = z - self.modez
            if np.abs(x_score) > threshold or np.abs(y_score) > threshold or np.abs(z_score) > threshold:
                if type(g) == list:
                    self.outliers.append([x,y,z, g[0],g[1], dens])
                else:
                    self.outliers.append([x,y,z, g, dens])
            elif (x_up not in self.xunique and x_low not in self.xunique) or (y_up not in self.yunique and y_low not in self.yunique) or \
                    (z_up not in self.zunique and z_low not in self.zunique):
                if type(g) == list:
                    self.outliers.append([x,y,z, g[0],g[1], dens])
                else:
                    self.outliers.append([x,y,z, g, dens])
        out = np.array(self.outliers)
        
        for a,b,c in zip(out[:,0], out[:,1], out[:,2]):
            delete = self.bmodel.loc[(self.x == a) & (self.y == b) & (self.z == c)]
            self.bmodel = self.bmodel.drop(delete.index)
        return pd.DataFrame(self.outliers, columns = cols)

    #Solving UPL problem
    def upl(self, x,y,z,grade, density, mc, ic, pc, tc, mp, mr, prec):
        new_m = self.bmodel

        max_z = self.maxz
        if prec == '1-5 pattern':
            prec = 5
        elif prec == '1-9 pattern':
            prec = 9
        b_val = 'bvalue'
        c_off = 'cutoff'
        dic = 'dictator'
        node = 'node'
        new_m.loc[:,c_off] = np.array((mc + pc + (max_z - new_m.loc[:,z])*ic)/
                                ((mp - tc) * mr * 22.04))
                                

        new_m.loc[:,b_val] = np.where((new_m.loc[:,grade] > new_m.loc[:, c_off]), 
                    new_m.loc[:,'ton'] * (((mp - tc) * 22.04 * mr* new_m.loc[:,grade]) - 
                                    pc - mc - (max_z - new_m.loc[:,z])*ic)
                    , (0 - new_m.loc[:,'ton'] * mc))
        new_m = new_m.reset_index(drop = True)
        new_m.loc[:, node] = new_m.index + 1
        new_m.loc[:,dic] = 0
        #We get the new_m fot getting upl
        #node:0, x:1, y:2, z:3, b_val:4, dic:5
        new_m = new_m[[node, x, y, z, b_val, dic, density, grade]]
        Graph = self.get_graph(nm = new_m, prec = prec)
        breakpoints, cuts, info = pf.hpf(Graph, self.source, self.sink, const_cap="const", mult_cap="mult", lambdaRange=[0], roundNegativeCapacity=False)
        
        #Going over the cuts_items finding the nodes inside the resulting UPL.
        Result_upl = {x:y for x, y in cuts.items() if y == [1] and x!=0}
        InsideList = list(Result_upl.keys())
        
        # Set all blocks as zero

        for ind in InsideList: 
            # Set blocks inside UPL as one
            new_m.loc[np.int(ind -1), dic] = 1

        return new_m[new_m.loc[:,dic]==1]

    def get_graph(self, nm, prec):      
        Graph = NetX.DiGraph()
        col_compare = self.zunique[::-1]
        if prec == 9:
            dista = (self.modex**2 + self.modey**2+ self.modez**2)**0.5
        elif prec == 5:
            dista = (self.modex**2 + self.modez**2)**0.5

        for i in range(self.min_com):
            #node:0, x:1, y:2, z:3, b_val:4, dic:5
            upper = np.array(nm[nm.iloc[:,3]== col_compare[i]])
            lower = np.array(nm[nm.iloc[:,3] == col_compare[i+1]])
            #Watch out with index block value
            self.CreateArcs(Graph = Graph, up = upper, low = lower, trigger = i, prec = prec, dist=dista)
            
            nm = nm[(nm.iloc[:,1]!= self.minx + i*self.modex) & (nm.iloc[:,1] != self.maxx - i*self.modex) & (nm.iloc[:,2] != self.miny + i*self.modey) & (nm.iloc[:,2] != self.maxy - i*self.modey)]
        return Graph

    def CreateArcs(self,Graph,up, low, trigger, prec, dist):
        #Create internal arcs:
        tree_upper = spatial.cKDTree(up[:,1:4])
        mask = tree_upper.query_ball_point(low[:,1:4], r = dist + 0.01)
        for _, g in enumerate(mask):
            if len(g) == prec:
                for reach in up[g][:,0]:
                    Graph.add_edge(low[_][0], reach, const = 99e9, mult = 1)
                
        #Create external arcs:
        #if trigger+2  == min_compare:
        #  player = low
        #else:
        player = up
        for node, capacity in zip(player[:,0], player[:,4]):
            cap_abs = np.absolute(np.around(capacity, decimals=2))
            if capacity < 0:
                Graph.add_edge(node, self.sink, const = cap_abs, mult = -1)
            else:
                Graph.add_edge(0, node, const = cap_abs, mult = 1)


        
