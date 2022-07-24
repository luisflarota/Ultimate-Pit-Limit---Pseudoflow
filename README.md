# Solving the Ultimate Pit Limit Problem by Applying the Pseudoflow Algorithm 

<div style='text-align:center'><em>"Know how to solve every problem that has been solved." - R. Feynman (1988)</em>
``Programming Language: Python``

--- 

<h2> Content </h2>

[1. Some Introduction](#s1) <br>
[2. The Problem](#s2) <br>
[3. The Solution ](#s3) <br>
[4. Building an Application](#s4) <br>
[5. Future Work Ideas](#s5) <br>
[6. References](#s6) <br>
----

<h2 id = "s1"> 1. Some Introduction </h2>
Mining Engineers, <u>and this is my kindly opinion</u>, have learned about solving the Ultimate Pit Limit Problems by easy examples, i.e., Lerchs-Grossman 2D Algorithm. However, that is not what we actually see when running an open-pit mining operation. Most of the current problems, including this, have been solved by software programs, and some mining engineers become users rather than doers. That being said, I decided to code the solution of the ultimated pit limit problem by applying the Pseudoflow algorithm (Hochbaum, 2008).

----

<h2 id = "s2"> 2. The Problem </h2>


<!-- [LINK TO ARXIV \[0\]](http://arxiv.org/abs/2004.12770)

[LINK TO CODE](https://github.com/ceyzaguirre4/DACT-MAC) -->


Given a 3D block model, how do we find the economic envelope/volume that contains the maximum value and fits in within our operational constraints? i.e. maximum slope angles?

![bm](https://user-images.githubusercontent.com/64980133/180667596-10ac9bf8-094a-431e-84dc-6a197d4aa083.png)
![up_](https://user-images.githubusercontent.com/64980133/180667604-5f10c4c0-ce63-4ed6-a301-59c655b92734.png)

----

<h2 id = "s3"> 3. The Solution </h2>

The solution follows a paper from <b>Geovia Whittle, published in 2017</b>. They explain how the Pseudoflow algorithm works in detail (Geovia, 2017). To make life easier, this is a summary on how the algorithm works:

1- Estimate **each block's value** based on economic parameters:<br>
~~~python
Cutoff Grade = (MiningCost + ProcessingCost*(1 + Dilution))/(MetalPrice*Recovery)
for block in [1 ... Blocks]:
  block_value = (grade_of_block*Recovery*MetalPrice - (ProcessingCost+MiningCost))*Tons
  if grade_of_block < CutoffGrade:
    block_value = -MiningCost*Tons
~~~

2- Create a directed graph with our block model. For that:
  - Nodes: We will have 3 types of nodes:
      * Source: The graph starts here. Also, where the flow will start.
      * Sink: The graph ends here. Also, where the flow will end.
      * A block: Considered as a node
  - Edges:
      * Source -> a block: `if the block's value is positive`; the edge's weight will be the block value.
      * Block -> block: `if allowed by the precedence, i.e, 1-5 precedence (45 degrees)`; the edge's weight will be the block value.
      * Block -> sink: `if the block's value is negative`; the edge's weight will be the block value (negative).

  Hint: You can use ['Networkx'](https://networkx.org/) to build your graph or do it by your own using dictionaries in Python.

~~~python
def create_graph(self, bmodel, precedence):
    # Create an empty directed graph.
    Graph = NetX.DiGraph()
    if precedence == 9:
        distance = (self.modex**2 + self.modey**2+ self.modez**2)**0.5
    elif precedence == 5:
        distance = (self.modex**2 + self.modez**2)**0.5
    for step in range(steps_z):
        upper_bench = np.array(bmodel[bmodel.iloc[:,3]== col_compare[step]])
        lower_bench = np.array(bmodel[bmodel.iloc[:,3] == col_compare[step]])
        self.create_edges(
          Graph=Graph, up=upper, low =lower, trigger=step, prec=precedence, dist=distance)
        # Shrink the block model when going down - it reduces the computational time.
        bmodel = bmodel[
          (bmodel.iloc[:,1]!= self.minx+i*self.modex)
          &(bmodel.iloc[:,1]!=self.maxx-i*self.modex)
          &(bmodel.iloc[:,2] != self.miny+i*self.modey)
          &(bmodel.iloc[:,2] != self.maxy-i*self.modey)]
    return Graph

def create_edges(self,Graph,up, low, trigger, prec, dist):
    # Create internal edges - Block to block.
    tree_upper = spatial.cKDTree(up[:,1:4])
    # Get the closest block for each block, yet complying the precedences.
    mask = tree_upper.query_ball_point(low[:,1:4], r = dist + 0.01)
    for _, g in enumerate(mask):
        if len(g) == prec:
            for reach in up[g][:,0]:
              # Add internal edge + adding a weight of 99e9 (infinite).
                Graph.add_edge(low[_][0], reach, const = 99e9, mult = 1)
    #Create external edges - Source to block to sink.
    player = up
    for node, capacity in zip(player[:,0], player[:,4]):
        cap_abs = np.absolute(np.around(capacity, decimals=2))
        # Create an edge from a node to the sink if bvalue less than 0
        if capacity < 0:
            Graph.add_edge(node, self.sink, const = cap_abs, mult = -1)
        # Otherwise the source is connected to the block.
        else:
            Graph.add_edge(0, node, const = cap_abs, mult = 1)
~~~

3- The algorithm will **push the flow** from the source to an **ore node** and it will **try to saturate the capacity**. Furthermore, it will **push from the waste node to pay waste blocks**. Therefore, as the maximum flow is found, the problem is solved and that will mean that waste blocks were paid. The following chart extracted from ['Whittle's paper'](https://www.scielo.br/scielo.php?pid=S0370-44672014000400006&script=sci_arttext) would help you better understand what is written above: 

![Screenshot 2021-02-27 114317](https://user-images.githubusercontent.com/64980133/109393667-16ce4380-78f1-11eb-95c2-79ff26e7b057.png)
        
--- 

<h2 id = "s4"> 4. Building an Application </h2>

To solve this problem dynamically, and also to make people playing with it, a web application has been created by using [Streamlit](https://streamlit.io/).

Features of the Application:

* It can <ins>check outliers</ins> after you upload a block model in .csv format. If you do not have it, <ins>use a default one. We have everything for you!</ins>

  - What do we mean with outliers?
     - Block's coordinates that are out of the big block, meaning that an *specific block does not belong to a 3D cubic beatiful form.*
     - Block's coordinates that are <ins>not in the proper gravity center</ins>.


* <ins>3D Visualization:</ins> Select some lower and upper bounds for what you want to see and grades' ranges and we will color-code based on it.

![visualize](https://user-images.githubusercontent.com/64980133/109393924-5f3a3100-78f2-11eb-86dc-bb77fcb2518c.png)

<br>
* <ins>GradeTonnage Distribution </ins>

![gtd](https://user-images.githubusercontent.com/64980133/109393968-8ee93900-78f2-11eb-88e4-9d3fbe7ac45f.png)

<br>
* <ins>Input the economic parameters to get the blocks' value</ins>

![upl](https://user-images.githubusercontent.com/64980133/109394014-cb1c9980-78f2-11eb-9ead-82c34d5c9b9f.png)

<br>
* <ins>Run the Algorithm and visualize your **beatiful pit limit**</ins>
  
![issue_output](https://user-images.githubusercontent.com/64980133/109107598-030fbb00-7700-11eb-9f92-a0a94f7433c1.png)

---

<h2 id = "s5"> 5. Future Work Ideas </h2>

- <ins>Add a variety of slope angles</ins>. At this point in time, we are just evaluating 2 precedences which are equivalent to 45 and 40 degrees approximately.
- <ins>Evaluate a set of revenue factors</ins> and see where to mine first - which nested pit has the highest value. Also, <ins>visualize it</ins>.
- Use some Operations Research techniques to <ins>draw automated inpit and expit ramps</ins>. Dr. Yarmuch developed an algorithm to solve this problem and 
his [paper](https://www.sciencedirect.com/science/article/abs/pii/S030505481930173X) is worth reading.



---
  
  
<h2 id = "s6"> 6. References </h2>

 - Hochbaum, D. S. (2008). The pseudoflow algorithm: A new algorithm for the maximum-flow problem. Operations research, 56(4), 992-1009.
 - Souza, F. R., Melo, M., & Pinto, C. L. L. (2014). A proposal to find the ultimate pit using Ford Fulkerson algorithm. Rem: Revista Escola de Minas, 67, 389-395.
 - Yarmuch, J. L., Brazil, M., Rubinstein, H., & Thomas, D. A. (2020). Optimum ramp design in open pit mines. Computers & Operations Research, 115, 104739.
