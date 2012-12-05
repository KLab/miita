#!/usr/bin/env python
import os
os.environ['MIITA_SETTING_FILE'] = '../setting_local.py'

import miita
miita.app.run(debug=True)
