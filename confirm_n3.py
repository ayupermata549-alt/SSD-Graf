import sys, os, time; sys.path.insert(0, os.getcwd())
import networkx as nx, pulp
from supersubdivision_graf_algorithm import build_ssd_ladder
from lower_bound_ladder import params

def exact(k,n,ub,tl):
    G,_,_=build_ssd_ladder(k,n); nV,p,d=params(k,n)
    dist=dict(nx.all_pairs_shortest_path_length(G))
    nodes=list(G.nodes()); M=ub+d+1
    prob=pulp.LpProblem("r",pulp.LpMinimize)
    f={v:pulp.LpVariable(f"f{i}",0,ub,cat="Integer") for i,v in enumerate(nodes)}
    S=pulp.LpVariable("S",0,ub,cat="Integer"); prob+=S
    for v in nodes: prob+=S>=f[v]
    for i in range(len(nodes)):
        for j in range(i+1,len(nodes)):
            u,w=nodes[i],nodes[j]; need=d+1-dist[u][w]
            y=pulp.LpVariable(f"y{i}_{j}",cat="Binary")
            prob+=f[u]-f[w]>=need-M*(1-y); prob+=f[w]-f[u]>=need-M*y
    t0=time.time(); prob.solve(pulp.PULP_CBC_CMD(msg=False,timeLimit=tl))
    el=time.time()-t0; st=pulp.LpStatus[prob.status]
    trust = (st=="Optimal" and el<tl*0.9)
    print(f"k={k} n={n} ub={ub}: S={pulp.value(S)} [{st}] {el:.0f}s "
          f"-> {'TRUSTED OPTIMAL' if trust else 'NOT trustworthy (timeout/incumbent)'}", flush=True)

exact(1,3,33,2400)
