  $(document).ready(function() {

    function onResponse(returnData){
        response = JSON.parse(returnData);
        console.log(response)
        if (response.status =="1"){
            location.reload();
        }else{
            alert(response.data)
        }
    }

    $('#remove-enrol').click(function(){
         $.ajax({
            type: 'POST',
            url: "/remove_enrol_person",
            data: {'id': $(this).attr('data')},
            dataType: "text",
            success: function(resultData) { onResponse(resultData); }
        });

    });

    $('#remove-camera').click(function(){
        $.ajax({
            type: 'POST',
            url: "/remove_camera",
            data: {'id': $(this).attr('data')},
            dataType: "text",
            success: function(resultData) { onResponse(resultData); }
        });
    });

    $("#enrol-submit").click(function(){
        form = $(this).closest("form");
        $.ajax({
            type: 'POST',
            url: "/enrol",
            data: form.serialize(),
            dataType: "text",
            success: function(resultData) { onResponse(resultData); }
        });
    });

    $("#add-camera").click(function(){

        form = $(this).closest("form");
        $.ajax({
            type: 'POST',
            url: "/add_camera",
            data: form.serialize(),
            dataType: "text",
            success: function(resultData) { onResponse(resultData); }
        });

    });
});
