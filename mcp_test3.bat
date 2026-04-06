@echo off
(echo {"jsonrpc":"2.0","id":"1","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}) 
echo {"jsonrpc":"2.0","method":"notifications/initialized","params":{}}
echo {"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"hfss_stop_app","arguments":{"force":true}}}
echo {"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"hfss_start_app","arguments":{"non_graphical":false}}}
echo {"jsonrpc":"2.0","id":"4","method":"tools/call","params":{"name":"hfss_get_session_status","arguments":{}}}
