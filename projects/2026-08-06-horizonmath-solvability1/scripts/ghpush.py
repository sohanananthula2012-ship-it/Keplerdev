import os,sys,base64,json,urllib.request
TOKEN=os.environ["GITHUB_TOKEN"]; REPO=os.environ["GITHUB_REPO"]; BRANCH=os.environ.get("GITHUB_BRANCH","main")
def push(localpath, repopath, msg):
    with open(localpath,"rb") as f: content=f.read()
    url=f"https://api.github.com/repos/{REPO}/contents/{repopath}"
    # get sha if exists
    sha=None
    req=urllib.request.Request(url+f"?ref={BRANCH}",headers={"Authorization":f"token {TOKEN}","Accept":"application/vnd.github+json"})
    try:
        r=urllib.request.urlopen(req); sha=json.load(r).get("sha")
    except Exception: pass
    data={"message":msg,"content":base64.b64encode(content).decode(),"branch":BRANCH}
    if sha: data["sha"]=sha
    req=urllib.request.Request(url,data=json.dumps(data).encode(),method="PUT",
        headers={"Authorization":f"token {TOKEN}","Accept":"application/vnd.github+json"})
    r=urllib.request.urlopen(req); res=json.load(r)
    print("pushed",repopath,res["content"]["html_url"])
if __name__=="__main__":
    push(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else "update")
