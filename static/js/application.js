$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#Start").on("click", function() {
        console.log($("#Start").text())
        if ($("#Start").text() === "Start"){
            var url = $("#rtmp-url").val();
            var code = $("#rtmp-code").val();
            var message = {
                "rtmp-url": url,
                "rtmp-code": code
            }
            var rpc = websocketClient.formatMessage("startDouyuTv", message);
            websocketClient.send(rpc);
        }
    });
    websocketClient.init();
})

var websocketClient = {
    ws: null,

    init: function() {
        var url = "ws://" + location.host + "/websocket";
        this.ws = new WebSocket(url);
        this.ws.onopen = this.onopen;
        this.ws.onmessage = this.onmessage
        this.ws.onerror = this.onerror;
        this.ws.onclose = this.onclose;
    },

    send: function(message){
        if (this.ws){
            this.ws.send(message);
        }
    }, 

    onopen: function() {
        var message = websocketClient.formatMessage("onopen", "WebSocket onopen");
        console.log("WebSocketOpen!");
    },

    onmessage: function(event) {
        console.log(JSON.parse(event.data));
    },

    onclose: function(event){
        console.log("WebSocketClose!", event);
    }, 

    onerror: function(event){
        console.log("WebSocketError!", event);
    },

    formatMessage: function(rpcName, rpcMessage){
        var rpc = {
            "rpcVersion": "1.0",
            "rpcUrl": "/FFmpegHandler",
            "rpcName": rpcName,
            "rpcMessage": rpcMessage,
        };
        return JSON.stringify(rpc);
    }
};