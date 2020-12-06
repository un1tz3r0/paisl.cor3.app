def showinfo():
    import os, sys
    import pprint
    import glob,pathlib
    
    print(f"os.environ:")
    for k,v in os.environ.items():
        print(f"  {repr(k)}: {repr(v)},")
    print(f"\n")
    
    print(f"sys.path:")
    for v in sys.path:
        print(f"  {repr(v)}")
    print(f"\n")
    
    def printtree(root):
        print(f"tree under {repr(root)}:")
        for name in pathlib.Path(root).rglob("**/*"):
            print("  {}".format(name))
        print(f"\n")
    
    printtree(".")
    printtree(os.environ['HOME'])
    
    
showinfo()


import requests, re, shutil, os, pathtools.patterns, pathtools.path, glob
import tinycss2
from io import StringIO

def find_files(dirpath=".", incls=["*"], excls=[]):
		for base, dirs, files in pathtools.path.walk(dirpath):
				relbase=os.path.relpath(base, dirpath)
				for f in list(files) + list([d + os.path.sep for d in dirs]):
						relf = os.path.join(relbase, f)
						srcf = os.path.join(base, f)
						if pathtools.patterns.match_path(relf, incls, excls):
								yield (srcf, relf)

def copy_files(srcdir="src", destdir="build", incls=["*"], excls=["**/.*/**", "**/.*", "**/*~", "**/*.save", "**/*.save.*"]):
		print(f"Copying files from {repr(srcdir)} to {repr(destdir)}...")
		for fromPath, toRelPath in find_files(srcdir, incls, excls):
				print(f"  Copying {repr(toRelPath)}... ", end="")
				toPath = os.path.join(destdir, toRelPath)
				try:
						if not toRelPath.endswith("/"):
							if not os.path.exists(os.path.dirname(toPath)):
								mkpath(os.path.dirname(toPath))
							shutil.copy2(fromPath, toPath)
							print(f"ok.")
						else:
							if not (os.path.exists(toPath) and os.path.isdir(toPath)):
								mkpath(os.path.dirname(toPath))
								print("created.")
							else:
								print("exists.")
				except Exception as err:
						print(f"error: {err}")

def fetch_url(url, filename = None):
		import requests
		try:
			if filename != None:
				if not os.path.exists(os.path.dirname(filename)):
					mkpath(os.path.dirname(filename))
			with requests.get(url) as response:
					data = response.content
					if filename is None:
							print(f"Downloaded {len(data)} bytes from {url}")
							return data
					with open(filename, "wb") as out:
							out.write(data)
							print(f"Downloaded {len(data)} bytes from {url} to {filename}.")
		except Exception as err:
				print(f"Error downloading {url}: {err}")
				raise err

def fetch_google_fonts(url, outputcss=None, outputdir=None):
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
		props = {}
		if decl.type == "at-rule":
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
			mkpath(os.path.dirname(localpath))
			fetch_url(url, localpath)
	if outputcss != None:
		mkpath(os.path.dirname(outputcss))
		buf = destcss.getvalue().encode("utf8")
		with open(outputcss, "wb") as outf:
			outf.write(buf)
		print(f"Wrote {len(buf)} bytes to {outputcss}.")
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
		return os.path.join(*(["/" if absolute else '.'] + parts))

def mkpath(path):
		absolute, parts = parsepath(path)
		for i in range(0, len(parts)):
				dirpath = unparsepath(absolute, parts[0:i+1])
				if not os.path.exists(dirpath):
						os.mkdir(dirpath)
				elif not os.path.isdir(dirpath):
						raise NotADirectoryError(dirpath)

def fetch_resources(*resources):
	global build_directory
	for localfile, remoteurl in resources:
		try:
			localfile = os.path.join(build_directory, localfile)
			print(f"Downloading {repr(remoteurl)} to {repr(localfile)}...")
			with requests.get(remoteurl) as res:
				data = res.content
				if not os.path.exists(os.path.dirname(localfile)):
					mkpath(os.path.dirname(localfile))
				with open(localfile, "wb") as out:
					out.write(data)
					print(f"Downloaded {len(data)} bytes to {repr(localfile)} from {repr(remoteurl)}.")
		except Exception as err:
			print(f"Error downloading {repr(remoteurl)} to {repr(localfile)}:\n\t{err}")

def fetch_google_font_resources(*google_font_resources):
	global build_directory
	for cssfile, fontdir, url in google_font_resources:
		try:
			cssfile = os.path.join(build_directory, cssfile)
			fontdir = os.path.join(build_directory, fontdir)
			print(f"Fetching/crawling/rewriting google fonts CSS at {repr(url)} into local css {repr(cssfile)} and local fonts in {repr(fontdir)}...")
			fetch_google_fonts(url, cssfile, fontdir)
			print("Done.")
		except Exception as err:
			print(f"Error fetching/crawling/rewriting google fonts CSS at {repr(url)} into local css {repr(cssfile)} and local fonts in {repr(fontdir)}:\n\t{err}")

def copy_source_files():
	global src_directory
	global build_directory
	copy_files(src_directory, build_directory)

# ----------------------------------------------------------------------------------------------------

src_directory = "src"
build_directory = "static"

fetch_resources(
	('js/split-grid.js', 'https://unpkg.com/split-grid@1.0.9/dist/split-grid.js'),
	('js/svg-pan-zoom.js', 'https://cdn.jsdelivr.net/npm/svg-pan-zoom-container@0.2.7'),
	('js/popper.js', 'https://unpkg.com/@popperjs/core@2'),
	('js/tippy.js', 'https://unpkg.com/tippy.js@6'),
	('css/svg-arrow.css', 'https://unpkg.com/tippy.js@6/dist/svg-arrow.css')
)

fetch_google_font_resources(
	("fonts/ibm-plex.css", "fonts/ibm-plex/", "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed&family=IBM+Plex+Sans:wght@100;400;700&display=swap")
)

copy_source_files()
