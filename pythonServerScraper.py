from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import sys, os
import subprocess
import urlparse

class MyHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		length = int(self.headers.getheader('content-length'))
		field_data = self.rfile.read(length)
		fields = urlparse.parse_qs(field_data)
		command = 'scrapy crawl southwestFare -a fromCity=%s -a toCity=%s -a days=1 -a startDate=%s;' % (fields['origin'][0], fields['destination'][0], fields['date'][0])
		subprocess.call(command ,shell = True)
		self.send_response(200)
		self.send_header("Content-type", "")
		self.send_header("Access-Control-Allow-Origin", "*")
		self.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin")
		self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
		self.end_headers()
		return

	def do_OPTIONS(self):
		self.send_response(200)
		self.send_header("Content-type", "")
		self.send_header("Access-Control-Allow-Origin", "*")
		self.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin")
		self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
		self.end_headers()
		return


if __name__ == '__main__':
	httpd = HTTPServer(("", 8081), MyHandler)
	httpd.serve_forever()



	



