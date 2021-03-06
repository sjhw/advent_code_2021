#!/usr/bin/python3

from os import O_NOFOLLOW, ttyname
import re
import sys
from pprint import pprint
from shared import style_list,in_file,grep,separator,printtable
from time import time


def main():

    template=[ "+-----------+",
               "|XX.X.X.X.XX|",
               "+-+A:B:C:D+-+",
               "  |A:B:C:D|  ",
               "  +-------+  " ]
    
    locations=set()
    lookup={"X":0, "A":0, "B":0, "C":0, "D":0, ".":0 }
    namelocs={}

    for a in range(len(template)):
        for b in range(len(template[a])):
            if template[a][b] in "ABCDX.":
                lookup[template[a][b]]+=1
                namelocs[template[a][b]+str(lookup[template[a][b]])]=[template[a][b],a,b]
                locations.add( (a,b ))
                template[a]=("%s.%s"%(template[a][0:b],template[a][b+1:]))
    #print(namelocs)

    
    paths={}
    paths.update(make_routes("ABCD","X",namelocs))
    paths.update(make_routes("X","ABCD",namelocs))
    # for k in [ l for l in paths if l[1][1]=="2" and l[1][0] <= 'D' ]:
    #     paths.pop(k)
    # paths[('A1','A2')]=[[2,3],[3,3]]
    # paths[('B1','B2')]=[[2,5],[3,5]]
    # paths[('C1','C2')]=[[2,7],[3,7]]
    # paths[('D1','D2')]=[[2,9],[3,9]]

    # for k in paths:
    #     print(k,paths[k])
    travellers={}
    tmp=style_list("alphanumlist",in_file("rawdata"))
    for t in tmp:
        travellers[t[1]]={ "type":t[0],"cost":int(t[2]),"total":0,"path":[] }
    # pprint(travellers)

    follow_paths(travellers,paths)

    exit(0)
    
#==============================

ooo=0
minval=999999999
callcount=0

def follow_paths(travellers,paths):

    global ooo,minval,callcount
    callcount+=1

    tot=0
    for t in travellers:
        tot+=travellers[t]["total"]
    if tot>=minval:
        return
    
    # print("")
    aps=avail_paths(travellers,paths)
    # print("travellers")
    # pprint(travellers)
    if len(aps)==0:
        tot=0
        xcount=0
        for t in travellers:
            if t[0]!=travellers[t]["type"]: xcount+=1
            tot+=travellers[t]["total"]
        # pprint(travellers)
        if xcount==0 and tot<minval:
            minval=tot
            print("")
            print("total =",tot)
            print("ooo",ooo)
            print("callcount",callcount)
            pprint(travellers)
        return

    ooo+=1

    if ooo>50:
        ooo-=1
        return

    # if callcount>50000:
    #     print("")
    #     for t in travellers: print(t,travellers[t])
    #     for p in aps: print(p)

    # print("avilable paths...")
    # printtable(aps)
    for ap in range(len(aps)):
        if ooo<=1:
            print("ooo",ooo,"main loop",aps[ap])
        for loc in [ l for l in travellers if l==aps[ap][1] ]:
            already_visited=False
            for p in travellers[loc]["path"]:
                if p==aps[ap][2]:
                    already_visited=True
                    break
            if not already_visited:
                # print("chosen",aps[ap])
                j2=travellers[loc].copy()
                j2["path"]=travellers[loc]["path"].copy()
                j2["path"].append(loc)
                j2["total"]+=aps[ap][3]
                travellers[aps[ap][2]]=j2
                j3=travellers.pop(loc)
                follow_paths(travellers,paths)
                travellers.pop(aps[ap][2])
                travellers[loc]=j3
            break

    ooo-=1
    # pprint(travellers)
    return


def avail_paths(travellers,paths):

    endpaths=[]

    # define non-empty locations as 'occupied'
    occupied=set()
    for loc in travellers:
        for p in [ x for x in paths if x[0]==loc ]:
            occupied.add( (paths[p][0][0],paths[p][0][1]))

    for loc in travellers:
        if loc[0] in ['A','B','C','D']:
            if loc==travellers[loc]["type"]+"2":
                continue
            if loc==travellers[loc]["type"]+"1":
                if loc[0]+"2" in travellers:
                    if travellers[loc[0]+"2"]["type"]==loc[0]:
                        continue
        for p in paths:
            if len(travellers[loc]["path"])>=2: continue
            if p[0]!=loc: continue                       # skip routes not starting at my location
            if p[0][0]=="X" and p[1][0]!=travellers[loc]["type"]: continue  # 'A's must end up in 'A'
            # weed out paths with obsructions
            cnt=0
            for k in paths[p]:
                if (k[0],k[1]) in occupied:
                    cnt+=1
            if cnt>1:
                continue
            # weed out paths which have completed
            endpaths.append( [ travellers[loc]["type"], p[0], p[1], (len(paths[p])-1)*travellers[loc]["cost"] ] )
    
    # remove any [ABCD]1 routes when [ABCD]2 routes are available
    for k in ["A","B","C","D"]:
        j1=-1 ; j2=-1
        for l in range(len(endpaths)):
            if endpaths[l][2]==k+"1": j1=l
            if endpaths[l][2]==k+"2": j2=l
        if j2>=0:
            endpaths=endpaths[0:j1]+endpaths[j1+1:]
    
    # for x in range(len(endpaths)):
    #     if l[2]==['A1','B1','C1','D1'] ]


    return endpaths
        
def make_routes(start,finish,names):

    def single_route(a,b):
        r=[a]
        while a[0]>b[0]:
            a=[a[0]-1,a[1]]
            r.append(a)
        while a[1]>b[1]:
            a=[a[0],a[1]-1]
            r.append(a)
        while a[1]<b[1]:
            a=[a[0],a[1]+1]
            r.append(a)
        while a[0]<b[0]:
            a=[a[0]+1,a[1]]
            r.append(a)
        return r

    result={}
    locs=set()
    for a in names:
        locs.add((names[a][1],names[a][2]))

    for s in start:
        for f in finish:
            for ns in names:
                if names[ns][0]!=s: continue
                for nf in names:
                    if names[nf][0]!=f: continue
                    result[(ns,nf)]=single_route(names[ns][1:],names[nf][1:]) 
    return result

#==============================

separator()
main()
separator()
