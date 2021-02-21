var static = "{{url_for('static',filename='')}}";
$("#includedContent").load(static+"src/video_feed.html");

$('.nav li').click(function(){
  page = $(this).attr('id');
  if (page.includes('.html')){
  $("#includedContent").load(static+"src/"+page);
  }else{
     $("#includedContent").load(page);
  }
});

$('.remove-enrol').click(function(){
   $.post("/remove_enrol_person", {'id': $(this).attr('data')},function(data, status){
        alert(data.data);
        //$("#img").attr('src', 'data:image/jpg;base64,'+String(data.data));
      });
});

$(".enrol-submit").click(function(){
    form = $(this).closest("form");;
    $.post('/enrol/', form.serialize(),
        function(returnedData){
             //console.log(returnedData);
             alert(returnedData.data);
         });
});