#!/bin/bash
set -x
curl -k -X POST -d '{"CMD":{"extension-packages":[{"name":"NAME","version":"VERSION"}]}}' -u 'USER:PWD' -H "Content-Type:application/vnd.yang.data+json" https://CONFDVIP:28809/api/operations/sdl:CMD
