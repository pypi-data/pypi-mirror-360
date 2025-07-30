import os
import shutil
import tempfile

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

def setup_assets(app, user_assets_folder = None):
    """
    Copies component JS into user's assets folder or a temp one.
    """
    if user_assets_folder is None:
        user_assets_folder = tempfile.mkdtemp()

    target_path = os.path.join(user_assets_folder, "authInterceptor.js")
    shutil.copy(os.path.join(ASSETS_PATH, "authInterceptor.js"), target_path)

    app.assets_folder = user_assets_folder
