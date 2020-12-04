import requests, re

def fetch_url(url, filename = None):
		import requests
		try:
			with requests.get(url) as response:
					data = response.content
					if filename is None:
							print(f"Downloaded {len(data)} bytes from {url}...")
							return data
					with open(filename, "wb") as out:
							out.write(data)
							print(f"Downloaded {len(data)} bytes from {url} to {filename}.")
		except Exception as err:
				print(f"Error downloading {url} to {filename}: {err}")
				raise err

def fetch_google_fonts(url, outputcss=None, outputdir=None):
	import tinycss2
	from io import StringIO
	import os
	if outputdir is None:
		relpath="./"
	elif outputcss is None:
		relpath=outputdir
	else:
		relpath = os.path.relpath(outputdir, os.path.dirname(outputcss))
		
	destcss = StringIO()
	rawcss = fetch_url(url)
	sheet = tinycss2.parse_stylesheet(rawcss.decode("utf8"))
	rules = []
	fetchqueue = []
	for i in range(0,len(sheet)):
		decl = sheet[i]
		if isinstance(decl, tinycss2.ast.WhitespaceToken):
				destcss.write(decl.serialize())
				continue
		if decl.type == "at-rule":
				props = {}
				lastident = None
				lastvalues = [];
				seencolon = False
				for j in range(0, len(decl.content)):
						tok = decl.content[j]
						if isinstance(tok, tinycss2.ast.WhitespaceToken):
								continue
						elif isinstance(tok, tinycss2.ast.IdentToken) and not seencolon:
								lastident = tok.value
						elif isinstance(tok, tinycss2.ast.LiteralToken) and tok.value == ":":
								seencolon = True
						elif isinstance(tok, tinycss2.ast.LiteralToken) and tok.value == ";":
								if len(lastvalues) < 1:
										continue
								if len(lastvalues) == 1:
										lastvalues = lastvalues[0]
								props[lastident] = lastvalues
								seencolon = False
								lastident = None
								lastvalues = []
						else:
								if hasattr(tok, 'value'):
										lastvalues.append(tok.value)
								else:
										lastvalues.append(tok)
		if "src" in props.keys() and "font-family" in props.keys() and "font-weight" in props.keys():
				localname = props['font-family'].lower().replace(" ", "_")+"-"+str(int(props['font-weight']))+".ttf";
				localpath = os.path.join("." if outputdir is None else outputdir, localname)
				localrel = os.path.join(relpath, localname)
				for tok in decl.content:
						if isinstance(tok, tinycss2.ast.URLToken) and tok.value == (props['src'] if isinstance(props['src'], str) else props['src'][0]):
								fetchqueue.append((localpath, tok.value))
								tok.value = localrel
				#print(decl.serialize())
		else:
				print(f"unparsed stylesheet item (type is {sheet[i].type}: {sheet[i].serialize()}")
		destcss.write(decl.serialize())
	# fetch or return if no paths provided
	if outputdir != None:
		for localpath, url in fetchqueue:
			mkpath(outputdir)
			fetch_url(url, localpath)
	if outputcss != None:
		mkpath(os.path.dirname(outputcss))
		with open(outputcss, "wt") as outf:
			outf.write(destcss.getvalue())
		if outputdir == None:
			return fetchqueue
	else:
		if outputdir != None:
			return destcss.getvalue()
		else:
			return (destcss.getvalue(), fetchqueue)

def parsepath(path):
    ''' returns a tuple of (bool, list) where the first item indicates whether
    path is absolute or relative, and the list contains the components of 
    the path '''
    import os
    parts = []
    base = path
    while base != '':
        oldbase = base
        base, part = os.path.split(base)
        parts = [part] + parts
        if oldbase==base:
            break
    if parts[0] == '':
        return (True, parts[1:])
    else:
        return (False, parts)

def unparsepath(absolute, parts):
    import os
    return os.path.join(*(["/" if absolute else '.'] + parts))

def mkpath(path):
    import os
    absolute, parts = parsepath(path)
    for i in range(0, len(parts)):
        dirpath = unparsepath(absolute, parts[0:i+1])
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        elif not os.path.isdir(dirpath):
            raise NotADirectoryError(dirpath)


'''
def fetch_and_fix_font_css(cssurl, outputfile = None):
		fq, dcss = process_google_font_css(cssurl)
		for localname, url in fq:
			fetch_url(url, localname)
		if outputfile == None:
			outputfile = "output.css"
		with open(outputfile, "wt") as outf:
				outf.write(dcss)
'''

resources = [
	('split-grid.js', 'https://unpkg.com/split-grid@1.0.9/dist/split-grid.js'),
	('svg-pan-zoom.js', 'https://cdn.jsdelivr.net/npm/svg-pan-zoom-container@0.2.7'),
	('popper.js', 'https://unpkg.com/@popperjs/core@2'),
	('tippy.js', 'https://unpkg.com/tippy.js@6')
]

google_font_resources = [
	("./fonts/ibm-plex.css", "./fonts/ibm-plex/", "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed&family=IBM+Plex+Sans:wght@100;400;700&display=swap")
]

for localfile, remoteurl in resources:
	try:
		print(f"Downloading {repr(remoteurl)} to {repr(localfile)}...")
		with requests.get(remoteurl) as res:
			data = res.content
			with open(localfile, "wb") as out:
				out.write(data)
				print(f"Downloaded {len(data)} bytes to {repr(localfile)} from {repr(remoteurl)}.")
	except Exception as err:
		print(f"Error downloading {repr(remoteurl)} to {repr(localfile)}:\n\t{err}")

for cssfile, fontdir, url in google_font_resources:
	try:
		print(f"Fetching/crawling/rewriting google fonts CSS at {repr(url)} into local css {repr(cssfile)} and local fonts in {repr(fontdir)}...")
		fetch_google_fonts(url, cssfile, fontdir)
		print("Done.")
	except Exception as err:
		print(f"Error fetching/crawling/rewriting google fonts CSS at {repr(url)} into local css {repr(cssfile)} and local fonts in {repr(fontdir)}:\n\t{err}")
