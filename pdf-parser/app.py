from flask import Flask, request, send_file, jsonify
import tempfile
import os
from parser import parse_pdf

app = Flask(__name__)