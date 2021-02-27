# Ultimate Pit Limit Solved by Using Pseudoflow Algorithm

This is a project where you can solve the ultimate pit limit problem by performing the pseudoflow algorithm developed by Ford and Fulkerson. Thus, if you want to clone it, run cmd on your folder and write `<streamlit run app.py>`.

## Content:
*[1. What is Ford and Fulkerson?](#s1)
*[2. Features of the app](#s2)
*[3. Project Limitations ](#s3)
*[4. Future development ](#s4)


<h3 id = "s1"> 1. What is Ford and Fulkerson? </h3>
    > Must read articles:
    -  "A proposal to find the ultimate pit using Ford Fulkerson algorithm" [link](https://www.scielo.br/scielo.php?pid=S0370-44672014000400006&script=sci_arttext)

    - [I'm an inline-style link with title](https://www.3ds.com/fileadmin/PRODUCTS-SERVICES/GEOVIA/PDF/whitepaper/2017-GEOVIA-WHITEPAPER-PSEUDOFLOW.pdf "PSEUDOFLOW METHOD FOR PIT OPTIMIZATION - Whittle")

    That is an algorithm that helps people to solve the 3D Ultimate Pit Limit problem, firstly introduced by Learch & Grossman in 1963 with Graph Theory.

    The algorithm (FF) works in the following way / you need to do the following steps to make FF works:
        - Treat blocks as a node and its proper value as weights
        - Add two nodes (So, total nodes woould be: #blocks+2):
            - Sink: flows start here
            - Source: flows end here
        - Connect nodes with edges. The edges need to follow the precedences pattern and sink/source to the closest nodes
        - Add capacities
            - Precedences:
                * Assign capacity: 99e9 for all edges that belongs to each block's precedence
            - Using sink and source:
                * If node's weight is below 0, then it is connected to the sink and its following capacity is the absolute value of the block value
                * Elif node's weight is greater or equals to 0, the source is connected to the proper node and its capacity is the block value
        - FF will push the flow from the source to an ore node and it will try to saturate the capacity and it will push from the waste node to pay for the waste block. Therefore, as the maximum flow is found, the problem is solved and that will mean that that all ore nodes have been used to pay waste blocks.
        - The following chart recovered from [I'm an inline-style link with title](https://www.scielo.br/scielo.php?pid=S0370-44672014000400006&script=sci_arttext "Whittle's paper") could help you to understand better what is written: 

        ![Screenshot 2021-02-27 114317](https://user-images.githubusercontent.com/64980133/109393667-16ce4380-78f1-11eb-95c2-79ff26e7b057.png)
            
<h3 id = "s2">### 2. Features of the app?</h3>
    * It can check outliers given your block model in csv format.
        - What do I mean with outliers?
            - Blocks' coordinates that are out of the big block, meaning that the block chosen does not belong to the block formed by all blocks
            - Blocks' coordinates that are not in the gravity center of the block
    * Visualize the block model:
        ![visualize](https://user-images.githubusercontent.com/64980133/109393924-5f3a3100-78f2-11eb-86dc-bb77fcb2518c.png)
    * Visualize Grade - Tonnage Distribution:
        ![gtd](https://user-images.githubusercontent.com/64980133/109393968-8ee93900-78f2-11eb-88e4-9d3fbe7ac45f.png)
    * Parameters to get the blocks' value + Ultimate Pit Limit problem
        ![upl](https://user-images.githubusercontent.com/64980133/109394014-cb1c9980-78f2-11eb-9ead-82c34d5c9b9f.png)
    * Chan! Problem solved!
        ![issue_output](https://user-images.githubusercontent.com/64980133/109107598-030fbb00-7700-11eb-9f92-a0a94f7433c1.png)

<h3 id = "s3">### 3. Project Limitations?</h3>
    * Precedences Pattern:
        - The proper project just have 2 features for precedences:
            * 1 - 5 pattern: which means that if you want to mine a block below the surface, you need to extract 5 blocks avobe that block
            * 1 - 9 pattern: same meaning
    
    ** Therefore, we can implement the overall slope angle feature that will be used to set precedences** There are papers to follow that issue.

<h3 id = "s4">4. Future development?</h3>
    -  [I'm an inline-style link with title](https://www.scielo.br/scielo.php?pid=S0370-44672014000400006&script=sci_arttext "R. Khalokakaie, P. A. Dowd & R. J. Fowell in 2001") wrote a paper where they add variable slope angles in LG algorithm. **I am trying to follow the paper to add that feature** So you can play and **HOPE IT HELPS!**

