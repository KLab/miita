from .application import app
from . import views
app.register_blueprint(views.app)