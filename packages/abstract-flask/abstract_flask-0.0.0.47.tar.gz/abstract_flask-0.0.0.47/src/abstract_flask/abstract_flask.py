import os,sys,unicodedata,hashlib,json
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
    abort
    
)

from .request_utils import (dump_if_json,
                            required_keys,
                            parse_request,
                            parse_and_return_json,
                            parse_and_spec_vars,
                            get_only_kwargs
                            )
from .network_tools import get_user_ip
from werkzeug.utils import secure_filename
def jsonify_it(obj):
    if isinstance(obj,dict):
        status_code = obj.get("status_code")
        return jsonify(obj),status_code
def get_bp(name,abs_path=None, **bp_kwargs):
    # if they passed a filename, strip it down to the module name
    if os.path.isfile(name):
        basename = os.path.basename(name)
        name = os.path.splitext(basename)[0]

    bp_name = f"{name}_bp"
    logger  = get_logFile(bp_name)
    logger.info(f"Python path: {sys.path!r}")
    abs_path = abs_path or __name__
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
