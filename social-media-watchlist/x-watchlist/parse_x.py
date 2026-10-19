import json,re,sys
def parse(path):
    t=open(path).read()
    m=re.search(r'\{.*\}', t, re.S)
    # json object up to last '}' before footer
    start=t.find('{'); end=t.rfind('}')
    obj=json.loads(t[start:end+1])
    left=re.search(r'X reads left for this user: (\d+) of (\d+) this minute \(resets at ([^)]+)\), (\d+) of (\d+) today',t)
    return obj,(left.groups() if left else None)
