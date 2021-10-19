// This ensures that your function is called once after all the DOM elements of the page are ready to be used.
$(document).ready(function(){
  
    // This function automatically uses the returned json from backend and shows list, but 
    // We just have to make sure whatever we are trying to return will be in `value` key
    $("#autocomplete-input").autocomplete({
      source: "/get_movies/",
      minLength: 2,
      select: function (event, ui) {
        $("#movieID").val(ui.item.id);
      }

    });


  // Get input field
	const inputField = document.getElementById('autocomplete-input');  // Or we can use: document.querySelector() 
	
	const inputHandler = function(e) {
    // If input field is blank then disable it
    if(e.target.value == ""){
      $('#search_button').attr('disabled', true);
    }
    else{
      $('#search_button').attr('disabled', false);
    }
  }
  // Now at input field we are adding this function, so it will check whether value in input field is filled or not
  // then only `Search` button will be enabled
  inputField.addEventListener('input', inputHandler);


  // When Search button is clicked
  $('#search_button').on('click', function(event) {
  	// First check input field is empty or not
  	const inputField = document.getElementById('autocomplete-input');
  	if(inputField.value == "" ) {
  		return;
  	}
    // event.preventDefault();
    var movieID = $('#movieID').val();
    console.log(movieID);
    if (movieID=="") {
      $('.results').css('display','none');
      $('.wrong_movie').css('display','block');
      $('#autocomplete-input').val('');
      swal("Selected movie is not in our database", "Please select a movie from dropdown!", "warning");
    }
    else {
      get_movie_details(movieID);
    }
  });
});


// Get movie related info and recommended movies for given movie Id
function get_movie_details(movie_id) {
    const url = '/recommend/?movie=' + movie_id;
    $("#loading").fadeIn();
    $.ajax({
      type:'GET',
      url: url,
      dataType: 'html',
      success: function(response){
        // When results are sucessfully fetched then display it
        $('.results').html(response);
        $('#autocomplete-input').val('');
        // Remove loader
        $("#loading").delay(500).fadeOut();
        $(window).scrollTop(0);
        $('#search_button').attr('disabled', true);
      },
      error: function(){
        // Remove loader
        $("#loading").fadeOut();
        // Make input box empty
        $('#autocomplete-input').val('');
        $('#movieID').val('');
        // Display alert 
        swal("Internal Server Error!", "Cannot fetch results right now", "error");
      },
    });
}