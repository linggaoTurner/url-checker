//once focus on input text box, remove warning textz
$('#searchText').focus(function(){$('#searchDomain').find("p").eq(0).html("")});

$('#searchText').keypress(function (e) {
 var key = e.which;
 if(key == 13)  // the enter key code
  {
    searchName()
    return false
  }
});
searchable = false;
$('#searchText').on('change',  function(){
  if($('#searchText').val()!="")
  {
    $("#searchBtn").attr('class', 'btn btn-primary');
    searchable = true;
  }
  else {
    $("#searchBtn").attr('class', 'btn btn-primary disabled');
    searchable = false;
  }
});

$('#searchBtn').click(function(e){
  e.preventDefault();
  searchName()
});

function searchName()
{
  if(searchable)
  {
    $.ajax({
      url:$('#searchDomain').attr('action'),
      type: 'POST',
      csrfmiddlewaretoken: '{{ csrf_token }}',
      data: {'name':$('#searchText').val()},


      success: function(result) {

        if(result.success == false)
        {
          $('#searchDomain').find("p").eq(0).html(result.message);
        }
        else{
          window.location.replace('/logs')
        }


      },
      error: function(result) {
          $('#searchDomain').find("p").eq(0).html(result);
        }

    });
  }
}
