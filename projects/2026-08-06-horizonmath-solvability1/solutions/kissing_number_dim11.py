def proposed_solution():
    import itertools, math
    r2 = math.sqrt(2.0); s = 1.0/r2
    pts = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1,-1):
            for sj in (1,-1):
                v=[0.0]*11; v[i]=si*s; v[j]=sj*s; pts.append(v)
    for signs in itertools.product([0.5,-0.5],repeat=8):
        if sum(1 for x in signs if x<0)%2==0:
            pts.append([x/r2 for x in signs]+[0.0,0.0,0.0])
    # D3 in coords 8,9,10 : (+-1,+-1,0) perms normalized
    for i,j in itertools.combinations(range(3),2):
        for si in (1,-1):
            for sj in (1,-1):
                v=[0.0]*11; v[8+i]=si*s; v[8+j]=sj*s; pts.append(v)
    return {"points": pts}
