
import http.server
import os
from urllib.parse import unquote
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
import youtube_dl
import json
memory = {}


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."


class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            delay = 3  # seconds
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            query = urlparse(self.path).query
            query_components = dict(qc.split("=") for qc in query.split("&"))
            searchQuery = query_components["query"]
            ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

            with ydl:
                result = ydl.extract_info(
                    'http://www.youtube.com/watch?v='+ query_components["query"],
                    download=False  # We just want to extract the info
                )

            if 'entries' in result:
                # Can be a playlist or a list of videos
                video = result['entries'][0]
            else:
                # Just a video
                video = result
            self.wfile.write(bytes(json.dumps(video), "utf-8"))


if __name__ == '__main__':
    server_address = ('', int(os.environ.get('PORT', '8000')))
    httpd = ThreadHTTPServer(server_address, Shortener)
    httpd.serve_forever()
