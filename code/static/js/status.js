function fetchdata(){
            alert("Hello");
                $.ajax({
                type : 'post'
                url : '/status',
            })
            .done(function(data) {
                if (data.armed)
                {
                    $('#armedTag').text(data.armed);
                }
                if (data.is_sensing)
                {
                    $('#sensingTag').text(data.is_sensing);
                }
                if (data.led_enabled)
                {
                    $('#ledEnabledTag').text(data.led_enabled);
                }
                if (data.led_color)
                {
                    $('#ledColorTag').text(data.led_enabled);
                }
            });
}


$(document).ready(function() {
    setInterval(fetchdata, 1000)
   });