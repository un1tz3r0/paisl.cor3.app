## paisl.cor3.app ##

An interactive browser-based generative vector art-experiment with a bunch of fancy stuff under the hood... produces what I call 'paisl's: a paisl is the building block and basic shape that makes up all paisley patterns.

Utilizes the new(ish) requestAnimationFrame and idleCallback APIs together to perform the recursive geometry computations and DOM updates while not hogging resources and killing the UX. Also demonstrates loading and saving custom types (the ES6 Set and Map for instance, which oddly are not JSON compatible out-of-the-box) using the built-in JSON serialiser to the browser localstorage, parsing the querystring client-side to allow link-sharing without adding anything server-side. and a whole bunch of other stuff that I am drawing a blank on right now.

See the incredibly messy javascript source in js/index.js for the gory details.

## hosting ##

A live version of this is publicly accessible at https://paisl.cor3.app ... check it out.

Currently it is designed to be hosted as a static site on digitalocean's new App Platform PaaS: https://cloud.digitalocean.com/apps. Check it out, there's no server configuration or maintenance, and you can automatically trigger depolyment on changes to a branch of your project's repository. And it's cheap too!
