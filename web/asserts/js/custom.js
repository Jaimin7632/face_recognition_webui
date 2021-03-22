  $(document).ready(function() {

    function onResponse(response){
        console.log(response)
        if (response.status =="1"){
            location.reload();
        }else{
            alert(response.data)
        }
    }

    $('.remove-enrol').click(function(){
         $.ajax({
            type: 'POST',
            url: "/remove_enrol",
            data: {'id': $(this).attr('data')},
            mimeTypes:"text",
            cache: false,
            success: function(resultData) { onResponse(resultData); }
        });

    });

    $('.remove-camera').click(function(){
        $.ajax({
            type: 'POST',
            url: "/remove_camera",
            data: {'id': $(this).attr('data')},
            mimeTypes:"text",
            cache: false,
            success: function(resultData) { onResponse(resultData); }
        });
    });

    $("#enrol-submit").click(function(){

        form = $(this).closest("form");
        var formdata = new FormData(form[0]);
        $.ajax({
            type: 'POST',
            url: "/enrol",
            data: formdata,
            mimeTypes:"multipart/form-data",
            contentType: false,
            cache: false,
            processData: false,
            success: function(resultData) {
            onResponse(resultData); }
        });
    });

    $("#add-camera").click(function(){

        form = $(this).closest("form");
        $.ajax({
            type: 'POST',
            url: "/add_camera",
            data: form.serialize(),
            mimeTypes:"text",
            cache: false,
            success: function(resultData) { onResponse(resultData); }
        });

    });

    $(".enrol-person-entry").click(function(){

        form = $(this).closest("form");
        $.ajax({
            type: 'POST',
            url: "/enrol_person_entry",
            data: form.serialize(),
            mimeTypes:"text",
            cache: false,
            success: function(resultData) { onResponse(resultData); }
        });

    });

    $(".update_enrolled_person").click(function(){

        form = $(this).closest("form");
        $.ajax({
            type: 'POST',
            url: "/update_enrolled_person",
            data: form.serialize(),
            mimeTypes:"text",
            cache: false,
            success: function(resultData) { onResponse(resultData); }
        });

    });
});
