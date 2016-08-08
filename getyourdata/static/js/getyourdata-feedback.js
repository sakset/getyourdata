window.addEventListener("load", function(evt) {
    // Disable "Leave feedback" if text area is empty
    $("#send_feedback").attr('disabled', true);

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
            }
        }
    })

    $("#id_content").bind('input propertychange', function(evt) {
        if ($("#id_content").val() == "") {
            $("#send_feedback").attr('disabled', true);
        } else {
            $("#send_feedback").attr('disabled', false);
        }
    });

    // Send feedback using AJAX
    $("#send_feedback").attr("type", "button");
    $("#send_feedback").click(function() {
        var data = {
            "content": $("#id_content").val()
        }

        $.post(SEND_FEEDBACK_URL, data, function(data) {
            data = JSON.parse(data);

            if (data["status"] === "success") {
                $("#send_feedback").hide();
                $("#id_content").hide();
                $("#send_feedback").before("<div class='alert alert-success'>"
                    + data["message"] + "</div>");
            } else {
                $("#send_feedback_error").remove();
                $("#send_feedback").before("<div id='send_feedback_error' class='alert alert-danger'>"
                    + data["message"] + "</div>");
            }
        });
    })
});
