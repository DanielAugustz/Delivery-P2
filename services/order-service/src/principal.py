from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask

from rotas import order_bp

app = Flask(__name__)
app.register_blueprint(order_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=False)
