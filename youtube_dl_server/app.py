import functools
import logging
import traceback
import sys

from flask import Flask, Blueprint, current_app, jsonify, request, redirect, abort
#from flask_limiter import Limiter
#from flask_limiter.util import get_remote_address
import yt_dlp
from yt_dlp.version import __version__ as youtube_dl_version
import yt_dlp.utils
yt_dlp.utils.std_headers['User-Agent'] = ""

from .version import __version__


if not hasattr(sys.stderr, 'isatty'):
    # In GAE it's not defined and we must monkeypatch
    sys.stderr.isatty = lambda: False


class SimpleYDL(yt_dlp.YoutubeDL):
    def __init__(self, *args, **kargs):
        super(SimpleYDL, self).__init__(*args, **kargs)
        self.add_default_info_extractors()


def get_videos(url, extra_params):
    '''
    Get a list with dict for every video founded
    '''
    
    epString = ""
    ydl_params = {
        'no_cache_dir': True,
        'geo_bypass ': True,
        'force_ipv4': True,
        'user_agent': epString,
        'logger': current_app.logger.getChild('yt_dlp'),
    }

    newsysparam = {
        'extractor_args': {'youtube': {'player_client': ['web']}},
    }

    if request.args['newsys'] == "yes"
        ydl_params.update(newsysparam)

    ydl_params.update(extra_params)
    yt_dlp.utils.std_headers['User-Agent'] = ""
    ydl = SimpleYDL(ydl_params)
    res = ydl.extract_info(url, download=False)
    return res


def flatten_result(result):
    r_type = result.get('_type', 'video')
    if r_type == 'video':
        videos = [result]
    elif r_type == 'playlist':
        videos = []
        for entry in result['entries']:
            videos.extend(flatten_result(entry))
    elif r_type == 'compat_list':
        videos = []
        for r in result['entries']:
            videos.extend(flatten_result(r))
    return videos


api = Blueprint('api', __name__)


def route_api(subpath, *args, **kargs):
    return api.route('/api/' + subpath, *args, **kargs)


def set_access_control(f):
    @functools.wraps(f)
    def wrapper(*args, **kargs):
        response = f(*args, **kargs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    return wrapper


@api.errorhandler(yt_dlp.utils.DownloadError)
@api.errorhandler(yt_dlp.utils.ExtractorError)
def handle_youtube_dl_error(error):
    logging.error(traceback.format_exc())
    result = jsonify({'error': str(error)})
    result.status_code = 500
    return result


class WrongParameterTypeError(ValueError):
    def __init__(self, value, type, parameter):
        message = '"{}" expects a {}, got "{}"'.format(parameter, type, value)
        super(WrongParameterTypeError, self).__init__(message)


@api.errorhandler(WrongParameterTypeError)
def handle_wrong_parameter(error):
    logging.error(traceback.format_exc())
    result = jsonify({'error': str(error)})
    result.status_code = 400
    return result


@api.before_request
def block_on_user_agent():
    pathee = request.path
    if pathee == "/api/regexUpdater" :
        abort(404)

    user_agent = ''
    forbidden_uas = current_app.config.get('FORBIDDEN_USER_AGENTS', [])

    
    if user_agent in forbidden_uas :
        abort(429)


def query_bool(value, name, default=None):
    if value is None:
        return default
    value = value.lower()
    if value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        raise WrongParameterTypeError(value, 'bool', name)


ALLOWED_EXTRA_PARAMS = {
    'format': str,
    'playliststart': int,
    'playlistend': int,
    'playlist_items': str,
    'playlistreverse': bool,
    'matchtitle': str,
    'rejecttitle': str,
    'writesubtitles': bool,
    'writeautomaticsub': bool,
    'allsubtitles': bool,
    'player_client': str,
    'subtitlesformat': str,
    'subtitleslangs': list,
    'httpchunksize' : str,
	'username': str,
	'password': str,
	'source_address': str,
	'geo_bypass': bool,
	'geo_bypass_country': str,
	'proxy': str,
	'force_ipv4': bool,
}


def get_result():
    url = request.args['url']
    extra_params = {}
    for k, v in request.args.items():
        if k in ALLOWED_EXTRA_PARAMS:
            convertf = ALLOWED_EXTRA_PARAMS[k]
            if convertf == bool:
                convertf = lambda x: query_bool(x, k)
            elif convertf == list:
                convertf = lambda x: x.split(',')
            extra_params[k] = convertf(v)
    return get_videos(url, extra_params)


@route_api('info')
@set_access_control
def info():
    url = request.args['url']
    result = flatten_result(get_result())
    test = {
        'url': url,
        "videos": [{'url':result[0]['url']}],
    }
    return jsonify(test)
   
    #if query_bool(request.args.get('flatten'), 'flatten', False):
    #    result = flatten_result(result)
    #    key = 'videos'

@route_api('utubePlay')
@set_access_control
def utubePlay():
    url = request.args['url']
    f_id = request.args['formatId']
    result = flatten_result(get_result())
    _formats = result[0]['formats']
    _title = result[0]['title']
    videoUrl = ''
    audioUrl = ''

    for _f in _formats:
        if (_f['format_id'] == f_id):
            videoUrl = _f['url']
        if(_f['format_id'] == '18'):
            audioUrl = _f['url']

    test = {
        'title': {'title':_title},
        'video': {'url':videoUrl},
        'audio': {'url':audioUrl}
    }

    return jsonify(test)

@route_api('internal')
@set_access_control
def internal():
    url = request.args['url']
    f_id = request.args['formatId']
    result = flatten_result(get_result())
    _formats = result[0]['formats']
    _title = result[0]['title']
    videoUrl = ''
    audioUrl = ''

    
    test = {
        'title': {'title':_title},
        'video': {'url':_formats},
    }

    return jsonify(test)

@route_api('subtitle')
@set_access_control
def subtitle():
    url = request.args['url']
    result = flatten_result(get_result())
    test = {
        'url': url,
        "subtitles": [result[0]['subtitles']]
    }

    return jsonify(test)

@route_api('schoolupdate')
@set_access_control
def schoolupdate():
    url = request.args['url']
    result = flatten_result(get_result())
   
    _formats = result[0]['formats']
    testxx = ''

    for key in d_formats.items():
        if(key['format_id'] == '18')
            testxx = key['url']

    test = {
        'url': url,
        "videos": testxx,
    }

    return jsonify(test)

@route_api('play')
def play():
    result = flatten_result(get_result())
    return redirect(result[0]['url'])


@route_api('extractors')
@set_access_control
def list_extractors():
    ie_list = [{
        'name': ie.IE_NAME,
        'working': ie.working(),
    } for ie in yt_dlp.gen_extractors()]
    return jsonify(extractors=ie_list)


@route_api('version')
@set_access_control
def version():
    result = {
        'youtube-dl': youtube_dl_version,
        'youtube-dl-api-server': __version__,
    }
    return jsonify(result)

@route_api('regexUpdater')
def regexUpdater():
     return redirect("http://test-youtube-unity.herokuapp.com/api/regexUpdater", code=302)

app = Flask(__name__)
app.register_blueprint(api)
app.config.from_pyfile('../application.cfg', silent=True)
#limiter = Limiter(
#    app,
#    key_func=get_remote_address,
#    default_limits=["200 per day", "20 per hour"]
#)