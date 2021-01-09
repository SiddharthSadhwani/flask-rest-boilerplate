from datetime import datetime, timedelta
from flask import jsonify, abort, request, Blueprint
import pandas as pd
import random
import os,sys
from py2neo import Graph,Node,Relationship,NodeMatcher
import pickle
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from IPython import get_ipython
sns.set()

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)

REQUEST_API = Blueprint('request_api', __name__)


def get_blueprint():
    """Return the blueprint for the main app module"""
    return REQUEST_API

@REQUEST_API.route('/Complete_Tree', methods=['GET'])
def get_tree():
    graph=Graph("bolt://localhost:7687",auth=("neo4j","admin"))
    G=nx.DiGraph()
    query="MATCH(n {Name: \"PHYSICS\"}) CALL apoc.path.subgraphAll(n,{relationshipFilter:\"HAS>|EXTENDED>\",bfs:false}) YIELD nodes,relationships UNWIND relationships AS r Return startNode(r).Name,id(startNode(r)),Type(r),r.Weight,endNode(r).Name,id(endNode(r));"
    k=graph.run(query)
    lt=[]
    for i in k:
        G.add_node(i[0])
        G.add_node(i[4])
        G.add_weighted_edges_from([(i[0],i[4],i[3])])
        dt={}
        dt["start"]=i[0]
        dt["type"]=i[1]
        dt["end"]=i[2]
        lt.append(dt)
        print(dt)
    plt.figure()
    nx.draw_networkx(G,pos=None,arrows=True,with_labels=True)
   # nx.draw_networkx_edge_labels(G,pos,weight)
    plt.show()
    print("----------------------------------------------------------------------------------------")
    return jsonify(lt)

@REQUEST_API.route('/Sub_Tree/<string:_name>', methods=['GET'])
def get_subtree(_name):
    graph=Graph("bolt://localhost:7687",auth=("neo4j","admin"))
    print(_name)
    G=nx.DiGraph()
    st=_name	
    query="MATCH(n {Name: '%s'}) CALL apoc.path.subgraphAll(n,{relationshipFilter:\"HAS>|EXTENDED>\",bfs:false}) YIELD nodes,relationships UNWIND relationships AS r Return startNode(r).Name,id(startNode(r)),Type(r),r.Weight,endNode(r).Name,id(endNode(r)) Order By r.Weight DESC;"%(st)
    print(query)
    k=graph.run(query)
    lt=[]
    for i in k:
        G.add_node(i[0])
        G.add_node(i[4])
        G.add_weighted_edges_from([(i[0],i[4],i[3])])
        dt={}
        dt["start"]=i[0]
        dt["type"]=i[2]
        dt["weight"]=i[3]
        dt["end"]=i[4]
        lt.append(dt)
        print(dt)
    plt.figure()
    nx.draw_networkx(G,pos=None,arrows=True,with_labels=True)
   # nx.draw_networkx_edge_labels(G,pos,weight)
    plt.show()
    print("----------------------------------------------------------------------------------------")
    return jsonify(lt)

@REQUEST_API.route('/Leafs_EM', methods=['GET'])
def leafs():
    graph=Graph("bolt://localhost:7687",auth=("neo4j","admin"))
    query="MATCH (n:Concept) RETURN n"
    print(query)
    k=graph.run(query)
    lt=[]
    for i in k:
        lt.append(i)
        print(i)
    return jsonify(lt)

@REQUEST_API.route('/EM_Taxo', methods=['GET'])
def get_Taxo():
    graph=Graph("bolt://localhost:7687",auth=("neo4j","admin"))
    query="MATCH(n {Name: \"PHYSICS\"}) CALL apoc.path.subgraphAll(n,{relationshipFilter:\"HAS>\",bfs:false}) YIELD nodes,relationships UNWIND relationships AS r Return startNode(r).Name,TYPE(r),endNode(r).Name;"
    k=graph.run(query)
    lt=[]
    for i in k:
        dt={}
        dt["start"]=i[0]
        dt["type"]=i[1]
        dt["end"]=i[2]
        lt.append(dt)
        print(dt)
    print("----------------------------------------------------------------------------------------")
    return jsonify(lt)

@REQUEST_API.route('/Shortest_Path/<string:_start>/<string:_end>', methods=['GET'])
def get_shortest(_start,_end):
    graph=Graph("bolt://localhost:7687",auth=("neo4j","admin"))
    query="MATCH (from {Name:'%s'}), (to {Name:'%s'}) CALL apoc.algo.dijkstraWithDefaultWeight(from, to, 'HAS>|EXTENDED>', 'Weight',1) yield path as path, weight as wt With wt , reduce(output=[], n IN relationships(path) | output+n ) as nodeCollection Order BY wt Limit 1 UNWIND nodeCollection as client RETURN distinct startNode(client).Name,Type(client),endNode(client).Name"%(_start,_end)
    k=graph.run(query)
    lt=[]
    for i in k:
        dt={}
        dt["start"]=i[0]
        dt["type"]=i[1]
        dt["end"]=i[2]
        lt.append(dt)
        print(dt)
    print("----------------------------------------------------------------------------------------")
    return jsonify(lt)
