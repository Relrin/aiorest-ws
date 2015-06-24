# -*- coding: utf-8 -*-
from server import run_server
from command_line import CommandLine

cmd = CommandLine()
cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
cmd.define('-port', default=8080, help='listened port', type=int)
args = cmd.parse_command_line()

# variant 1
run_server(ip=args.ip, port=args.port)

# variant 2
# or we can run it without any arguments
# run_server()

# variant 3
# if necessary to create encrypted WebSockets, just add to arguments
# your certificate and private key
# run_server(cert=path_to_my_cert, key=my_private_key)
