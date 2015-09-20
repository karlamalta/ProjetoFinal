var TracTicketReferenceGetCookieRefMode = function() {
    var mode = "";
    var cookies = (document.cookie || "").split(";");
    var length = cookies.length;
    for (var i = 0; i < length; i++) {
        var match = /^\s*trac_ticketref_relationships_mode=(\S*)/.exec(cookies[i]);
        if (match) {
            switch (match[1]) {
            case "extended":
                mode = match[1];
                break;
            default:
                mode = "";
                break;
            }
            break;
        }
    }
    return mode;
};

$(function() {

    var expires = new Date(new Date().getTime() + 365 * 86400 * 1000);
    var extended = "extended"
    var mode = TracTicketReferenceGetCookieRefMode();
    if (mode == extended) {
        $('#tref_summary').removeClass('tref-display-none');
        $('#tref_ticketid').addClass('tref-display-none');
    }

    $('th#h_ticketref').addClass('tref-clickable');
    $('th#h_ticketref').bind('click', function(e) {
        if ($('#tref_summary').hasClass('tref-display-none')) {
            $('#tref_summary').removeClass('tref-display-none');
            $('#tref_ticketid').addClass('tref-display-none');
            mode = extended;
        } else {
            $('#tref_summary').addClass('tref-display-none');
            $('#tref_ticketid').removeClass('tref-display-none');
            mode = "";
        }
        document.cookie = [
            "trac_ticketref_relationships_mode=" + mode,
            "expires=" + expires.toUTCString(),
        ].join("; ");
    });
});
