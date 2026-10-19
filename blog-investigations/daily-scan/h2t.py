import re,html,sys
def h2t(s):
    s=re.sub(r'<(script|style|svg)[^>]*>.*?</\1>','',s,flags=re.S)
    s=re.sub(r'<(li|p|h\d|div|br|tr)[^>]*>','\n',s)
    s=html.unescape(re.sub(r'<[^>]+>','',s))
    return re.sub(r'\n\s*\n+','\n',s)
if __name__=='__main__':
    print(h2t(open(sys.argv[1],encoding='utf-8',errors='ignore').read()))
