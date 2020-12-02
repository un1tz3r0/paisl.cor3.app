import requests, re

resources = '''
svg-pan-zoom.js		https://cdn.jsdelivr.net/npm/svg-pan-zoom-container@0.2.7
popper.js					https://unpkg.com/@popperjs/core@2
split-grid.js			https://unpkg.com/split-grid@1.0.9/dist/split-grid.js
tippy.js					https://unpkg.com/tippy.js@6
'''

google_font_resources = [
	("ibm-plex.css", "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed&family=IBM+Plex+Sans:wght@100;400;700&display=swap")
]

for line in resources.splitlines():
	try:
		localfile, remoteurl = re.compile("[ \t]+",2).split(line, 2)
		try:
			with requests.get(remoteurl) as res:
				data = res.content
				with open(localfile, "wb") as out:
					out.write(data)
					print(f"Downloaded {len(data)} bytes to {repr(localfile)} from {repr(remoteurl)}.")
		except Exception as err:
			print(f"Error downloading {repr(remoteurl)} to {repr(localfile)}:\n\t{err}")
	except:
		continue

for cssfile, url in google_font_resources:
	try:
		fetch_and_fix_css_fonts(url, cssfile)
	except Exception as err:
		print(f"Error fetching/crawling/rewriting google fonts CSS at {repr(url)} into {repr(cssfile)}:\n\t{err}")
