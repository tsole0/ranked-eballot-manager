$(document).ready(function() {
    // Get CSRF token from cookie
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    // Set up AJAX request with CSRF token included in headers
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        }
    });

    // Handle form submission
    $('#upload-form').submit(function(e) {
        e.preventDefault(); // Prevent default form submission

        var formData = new FormData();
        formData.append('csv_file', $('#csv-file')[0].files[0]);

        $.ajax({
            url: 'upload_csv/', // URL to your Django view function
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#results-container').html(response.results); // Update results container with response
            },
            error: function(xhr, status, error) {
                console.error(error);
            }
        });
    });
});
