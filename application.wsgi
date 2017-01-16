activate_this = '/usr/lib/facebook-sample-chatbot-client/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
sys.path.append('/usr/lib/facebook-sample-chatbot-client')
from app import app as application