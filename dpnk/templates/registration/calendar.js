{% load i18n %}
{% load l10n %}
{% load static %}
var day_types = {
    "possible-vacation-day": {{possible_vacation_days|safe}},
    "active-day": {{active_days|safe}},
    "locked-day": {{locked_days|safe}},
    "non-working-day": {{non_working_days|safe}},
};
var commute_modes = {
    {% for cm in commute_modes %}
    '{{cm.slug}}': {
        'eco': {{cm.eco|yesno:"true,false" }},
        'does_count': {{cm.does_count|yesno:"true,false" }},
    },
    {% endfor %}
}
var possible_vacation_days = day_types["possible-vacation-day"];
var vacation_id = {{first_vid}};
var full_calendar;
{% for cm in commute_modes %}
{% if cm.does_count and cm.eco %}
var route_options_{{cm.slug}} = {
    "{% trans 'Zadat Km ručně' %}": function () {
        $("#km-{{cm.slug}}").val(0);
    },
    "{% trans 'Nahrat GPX soubor' %}": function () {
        console.log("TODO");
    },
    "{% trans 'Nakreslit trasu do mapy' %}": function () {
        console.log("TODO");
    },
    {% for trip in trips %}
    {% if trip.commute_mode == cm %}
    "{% trans 'Stejně jako' %} {{trip.date}} {{trip.get_direction_display }} ({{trip.distance}} Km)": function () {
        $("#km-{{cm.slug}}").val({{trip.distance|stringformat:"f"}});
    },
    {% endif %}
    {% endfor %}
};

function on_route_select_{{cm.slug}}() {
    var sel = document.getElementById("route_select_{{cm.slug}}");
    route_options_{{cm.slug}}[sel.value]();
}
{% endif %}
{% endfor %}



function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function format_date(date){
    return date.getFullYear() + '-' + pad((date.getMonth() + 1).toString(), 2) + '-' + pad(date.getDate().toString(), 2);
}


function events_overlap(event1, event2) {
    if(event1.end && event2.end) {
        return ((event1.start >= event2.start && event1.start < event2.end) ||
                (event1.end > event2.start && event1.end <= event2.end));
    } else {
        return false;
    }
}

function add_vacation(startDate, endDate) {
    startDateString = format_date(startDate);
    real_end_date = new Date(endDate);
    real_end_date.setDate(real_end_date.getDate() - 1);
    endDateString = format_date(real_end_date);
    if(possible_vacation_days.indexOf(startDateString) >= 0 && possible_vacation_days.indexOf(endDateString) >= 0){
        new_event = {
            title: "{% trans 'Dovolená' %}",
            start: startDate,
            end: endDate,
            allDay: true,
            vacation_id: vacation_id++,
        }
        events = full_calendar.getEvents();
        for (eid in events) {
            if (events[eid].extendedProps.vacation_id) {
                if (events_overlap(new_event, events[eid])) {
                    e2 = events[eid]
                    return;
                }
            }
        }
        full_calendar.addEvent(new_event);
        $.post("{% url 'calendar' %}", {
            on_vacation: true,
            start_date: startDateString,
            end_date: endDateString,
            csrfmiddlewaretoken: "{{ csrf_token }}",
        },
               function(returnedData){
               }
              ).fail(function(jqXHR, textStatus, errorThrown) {
                  window.alert("{% trans 'Propojení selhalo' %}");
              });
    }
}

function remove_vacation(info) {
    var event = info.event;
    startDateString = format_date(event.start)
    endDateString = format_date(event.end)
    event.remove() //todo remove
    $.post("{% url 'calendar' %}", {
        on_vacation: false,
        start_date: startDateString,
        end_date: endDateString,
        csrfmiddlewaretoken: "{{ csrf_token }}",
    },
           function(returnedData){
               event.remove()
           }
          ).fail(function(jqXHR, textStatus, errorThrown) {
              window.alert("{% trans 'Propojení selhalo' %}");
          });
}

document.addEventListener('DOMContentLoaded', function() {
    {% for cm in commute_modes %}
    {% if cm.does_count and cm.eco %}
    var sel = document.getElementById("route_select_{{cm.slug}}");
    for(var key in route_options_{{cm.slug}}){
        var option = document.createElement("option");
        option.value = key;
        option.text = key;
        sel.appendChild(option);
    }
    {% endif %}
    {% endfor %}

    var calendarEl = document.getElementById('calendar');
    if($(window).width() > $(window).height()) {
        defaultView = 'dayGridMonth';
    } else {
        defaultView = 'listMonth';
    }
    full_calendar = new FullCalendar.Calendar(calendarEl, {
        events: {{events|safe}},
        eventOrder: 'order',
        selectable: true,
        lang: '{{ LANGUAGE_CODE }}',
        locale: '{{ LANGUAGE_CODE }}',
        height: 'auto',
        firstDay: 1,
        plugins: [ 'interaction', 'dayGrid', 'list' ],
        selectable: true,
        defaultView: defaultView,
        header: {
            right: 'dayGridMonth,listMonth, now, prev,next',
        },
        select: function(info) {
            console.log(info)
            add_vacation(info.start, info.end);
        },
        eventRender: function(info) {
            console.log(info);
            // Remove time column from Agenda view
            if(info.el.children[0].classList.contains("fc-list-item-time")){
                info.el.children[1].remove();
                info.el.children[0].remove();
                info.el.children[0].colSpan=3
            }
            var direction_icon = null;
            exp = info.event.extendedProps
            if (exp.direction == 'trip_to'){
                direction_icon = document.createElement("i");
                direction_icon.className='fa fa-industry xs';
            } else if (exp.direction == 'trip_from') {
                direction_icon = document.createElement("i");
                direction_icon.className='fa fa-home xs';
            }
            if (direction_icon) {
                info.el.firstChild.append(direction_icon);
            }
            var mode_icon = null;
            if (exp.commute_mode == 'bicycle'){
                mode_icon = document.createElement("i");
                mode_icon.className='fa fa-bicycle xs';
            } else if (exp.commute_mode == 'by_foot') {
                mode_icon = document.createElement("i");
                mode_icon.className='fa fa-running xs';
            }
            if (mode_icon) {
                info.el.firstChild.prepend(mode_icon);
            }
            if (info.event.extendedProps.vacation_id) { // https://stackoverflow.com/questions/26530076/fullcalendar-js-deleting-event-on-button-click#26530819
                var trash_icon =  document.createElement("i");
                var trash_button = document.createElement("button");
                trash_button.className = 'btn btn-default btn-xs trash-button';
                trash_button.append(trash_icon);
                trash_button.onclick = function(){remove_vacation(info)};
                trash_icon.className = 'fa fa-trash sm';
                info.el.firstChild.append(trash_button);
            }
        },
        eventClick: function(info) {
            console.log(info);
            if(info.event.extendedProps.placeholder){
                commute_mode = $("div#nav-commute-modes a.active")[0].hash.substr(1);
                cmo = commute_modes[commute_mode];
                info.event.setExtendedProp('commute_mode', commute_mode);
                if(cmo.eco && cmo.does_count){
                    km = $('#km-'+commute_mode).val()
                    info.event.setProp('title', km + " Km");
                } else {
                    info.event.setProp('title', "");
                }
            }
            if(info.event.extendedProps.modal_url){
                $('#trip-modal').modal({show:true});
                $('.modal-body').empty();
                $('.modal-spinner').show();
                $('.modal-body').load(info.event.extendedProps.modal_url + " #inner-content", function(){
                    $('.modal-spinner').hide();
                });
            }
        },
        dayRender: function (cell) {
            var set = false;
            var num_eco_trips = 0;
            var events_this_day = [];
            var events = full_calendar.getEvents();
            for (i in events){
                if(format_date(events[i].start) == format_date(cell.date)){
                    var event = events[i];
                    events_this_day.push(event);
                    if(event.extendedProps['commute_mode__eco']){
                        num_eco_trips++;
                    }
                }
            }
            if (num_eco_trips == 1) {
                cell.el.classList.add('one-ride-day');
            } else if (num_eco_trips > 1) {
                cell.el.classList.add('two-ride-day');
            }
            for (key in day_types) {
                if (day_types[key].indexOf(format_date(cell.date)) >= 0) {
                    cell.el.classList.add(key);
                    set = true;
                }
            }
            if (!set){
                cell.el.classList.add("out-of-competition-day");
            }
        },
    });
    full_calendar.render();
});
