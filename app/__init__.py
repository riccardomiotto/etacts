from flask import Flask
from lib.extensions import cache, iidx, arule, ctgov_idx, tag2group

app = Flask(__name__)

cache.init_app (app)

app.config.from_object ('app.lib.config')

# inverted index
app.jinja_env.globals['iidx'] = iidx

# association rules
app.jinja_env.globals['arule'] = arule

# ctgov index
app.jinja_env.globals['ctgov_idx'] = ctgov_idx

# controlled vocabulary
app.jinja_env.globals['tag2group'] = tag2group

from app import views
