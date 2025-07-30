import os,sys,unicodedata,hashlib,json,logging
from flask_cors import CORS
from abstract_utilities import make_list,get_media_types,get_logFile
from multiprocessing import Process

from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
    current_app,
    Flask,
    redirect,
    send_from_directory,
    abort,
    Flask,
    has_request_context
    
)
from abstract_queries import USER_IP_MGR
from .file_utils import *
from .request_utils import *
from .network_utils import *

from werkzeug.utils import secure_filename
def get_from_kwargs(keys,**kwargs):
    output_js = {}
    for key in keys:
        if key in kwargs:
            output_js[key]= kwargs.get(key)
            del kwargs[key]
    return output_js,kwargs
def get_name(name,abs_path=None):
    if os.path.isfile(name):
        basename = os.path.basename(name)
        name = os.path.splitext(basename)[0]
    abs_path = abs_path or __name__
    return name,abs_path
def jsonify_it(obj):
    if isinstance(obj,dict):
        status_code = obj.get("status_code")
        return jsonify(obj),status_code
def get_bp(name,abs_path=None, **bp_kwargs):
    # if they passed a filename, strip it down to the module name
    name,abs_path = get_name(name,abs_path=None)
    bp_name = f"{name}_bp"
    logger  = get_logFile(bp_name)
    logger.info(f"Python path: {sys.path!r}")
    # build up only the kwargs they actually gave us
    bp = Blueprint(
        bp_name,
        abs_path,
        **bp_kwargs,
    )
    return bp, logger
class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            # `request` is the current flask.Request proxy
            ip_addr = get_ip_addr(req=request)
            user = USER_IP_MGR.get_user_by_ip(ip_addr)
            record.remote_addr = ip_addr
            record.user = user
        else:
            record.remote_addr = None
            record.user = None
        return super().format(record)
def addHandler(app,name=None):
    name = name or os.path.splitext(os.path.abspath(__file__))[0]
    audit_handler = logging.FileHandler("{name}.log")
    audit_fmt     = RequestFormatter(
        "%(asctime)s %(remote_addr)s %(user)s %(message)s"
    )
    audit_handler.setFormatter(audit_fmt)
    app.logger.addHandler(audit_handler)
    
    @app.before_request
    def record_ip_for_authenticated_user():
        if hasattr(request, 'user') and request.user:
            # your get_user_by_username gives you .id
            user = get_user_by_username(request.user["username"])
            if user:
                log_user_ip(user["id"], request.remote_addr)
    @app.route("/api/endpoints", methods=["POST"])
    @app.route("/api/endpoints", methods=["GET"])
    def get_endpoints():
        import sys, os, importlib
        endpoints=[]
        for rule in app.url_map.iter_rules():
            
            # skip dynamic parameters if desired, include all
            methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
            endpoints.append((rule.rule, ", ".join(methods)))
        rules = sorted(endpoints, key=lambda x: x[0])
        try:

            return jsonify(rules), 200
        finally:
            sys.path.pop(0)
    return app
def register_bps(app,bp_list):
    for bp in bp_list:
        app.register_blueprint(bp)
    return app
def get_Flask_app(*args,**kwargs):
    """Quart app factory."""
    keys = ['name','bp_list']
    values , kwargs = get_from_kwargs(keys,**kwargs)
    name = values.get('name')
    bp_list = values.get('bp_list')
    for arg in args:
        if not name and not isinstance(arg,list):
            name = arg
        elif not bp_list:
            bp_list = arg
    bp_list = bp_list or []
    name,abs_path = get_name(name)
    app = Flask(name,**kwargs)
    app = addHandler(app,name=name)
    app = register_bps(app,bp_list)
    return app

