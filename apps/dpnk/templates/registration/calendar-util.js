{% load i18n %}
{% load l10n %}

function events_overlap(event1, event2) {
    if(event1.end && event2.end) {
        return ((event1.start >= event2.start && event1.start < event2.end) ||
                (event1.end > event2.start && event1.end <= event2.end));
    } else {
        return false;
    }
}

function get_trip_url(event) {
    commute_mode = event.extendedProps.commute_mode;
    cmo = commute_modes[commute_mode];
    if(!cmo) return;
    return "/view_trip/" + format_date(event.start) + "/" + event.extendedProps.direction
}

function ajax_req_json(url, json, method, success) {
    $.ajax(url, {
        data : JSON.stringify(json),
        contentType : 'application/json',
        type : method,
        headers: {
            'X-CSRFToken': "{{ csrf_token }}"
        },
        error: function(jqXHR, status, error) {
            if (error) {
                show_message(error + " " + jqXHR.responseText);
            } else if (jqXHR.statusText == 'error') {
                show_message("{% trans 'Chyba připojení' %}");
            }
        },
        success: success
    });
}