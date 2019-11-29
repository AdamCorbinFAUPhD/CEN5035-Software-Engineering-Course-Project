function fetchdata(){
                $.ajax({
                type : 'POST',
                url : '/status/'
            })
            .done(function(data) {
                if (data)
                {
                    $('#armedTag').text(data.armed);
                    $('#sensingTag').text(data.is_sensing);
                    $('#ledEnabledTag').text(data.led_enabled);
                    $('#ledColorTag').text(data.led_color);
                }
            });
}


$(document).ready(function() {
    setInterval(fetchdata, 1000)
   });