$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#Start").on("click", function() {
        var url = $("#rtmp-url").val();
        var code = $("#rtmp-code").val();
        var message = {
            "rtmp-url": url,
            "rtmp-code": code
        }
        updater.socket.send(JSON.stringify(message));
    });
    updater.start();
})

var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/chatsocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
    },

    showMessage: function(message) {
        console.log(message);
    }
};