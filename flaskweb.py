import base64
from flask import Flask, Response
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg

app = Flask(__name__)

@app.route('/plot.png')
def plot_png(fig):
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_figure(output)
    return Response(output.getvalue(), mimetype='image/png')