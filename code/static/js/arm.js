function arm_disarm(){
            console.log("Hello");
                $.ajax({
                type : 'POST',
                url : '/arm_disarm/'
            })
}