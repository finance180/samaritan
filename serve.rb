require 'webrick'

server = WEBrick::HTTPServer.new(
  Port: 8080,
  DocumentRoot: File.join(Dir.pwd, 'dashboard')
)

trap('INT') { server.shutdown }
server.start
