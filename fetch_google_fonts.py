def fetch_url(url, filename = None):
		import requests
		try:
			with requests.get(url) as response:
					data = response.content
					if filename is None:
							return data
					with open(filename, "wb") as out:
							out.write(data)
							print(f"Downloaded {len(data)} bytes from {url} to {filename}.")
		except Exception as err:
				print(f"Error downloading {url} to {filename}: {err}")

def process_google_font_css(url):
	import tinycss2
	from io import StringIO
	destcss = StringIO()
	#with open(filename, "rt") as f:
	#  sheet = tinycss2.parse_stylesheet(f.read())
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
						#if isinstance(tok, tinycss2.ast.URLToken):
						#    print(sheet[i].value, sheet[i].content[j].value)
				#print((decl.type, decl.at_keyword, props))
		if "src" in props.keys() and "font-family" in props.keys() and "font-weight" in props.keys():
				localname = props['font-family'].lower().replace(" ", "_")+"-"+str(int(props['font-weight']))+".ttf";
				for tok in decl.content:
						if isinstance(tok, tinycss2.ast.URLToken) and tok.value == (props['src'] if isinstance(props['src'], str) else props['src'][0]):
								fetchqueue.append((localname, tok.value))
								tok.value = localname
				print(decl.serialize())
		else:
				print(f"unparsed stylesheet item (type is {sheet[i].type}: {sheet[i].serialize()}")
		destcss.write(decl.serialize())
	return fetchqueue, destcss.getvalue()
def fetch_and_fix_css_fonts(cssurl, outputfile = None):
		fq, dcss = process_google_font_css(cssurl)
		for localname, url in fq:
				fetch_url(url, localname)
		if outputfile == None:
			outputfile = "output.css"
		with open(outputfile, "wt") as outf:
				outf.write(dcss)
