// This ensures that your function is called once after all the DOM elements of the page are ready to be used.
$(document).ready(function(){
  
    // This function automatically uses the returned json from backend and shows list, but 
    // We just have to make sure whatever we are trying to return will be in in  `value` key
    $("#autocomplete-input").autocomplete({
      source: "/movies/get_movies/",
      // select: function (event, ui) { //item selected
      //   console.log(ui.item);
      //   AutoCompleteSelectHandler(event, ui)
      // },
      minLength: 2,
      select: function (event, ui) {
        $("#movieID").val(ui.item.id);
        // console.log($("#hide1").val());
      }

    });

  // Read: https://tarekraafat.github.io/autoComplete.js/#/usage?id=_2-script
  // const autoCompleteJS = new autoComplete({
  //   selector: "#autoComplete",
  //   placeHolder: "Search for Movie...",
  //   data: {
  //       src: movie_titles,
  //       // cache: true,
  //   },
  //   resultsList: {
  //       element: (list, data) => {
  //           if (!data.results.length) {
  //               // Create "No Results" message element
  //               const message = document.createElement("div");
  //               // Add class to the created element
  //               message.setAttribute("class", "no_result");
  //               // Add message text content
  //               message.innerHTML = `<span>Found No Results for "${data.query}"</span>`;
  //               // Append message element to the results list
  //               list.prepend(message);
  //           }
  //       },
  //       noResults: true,
  //   },
  //   resultItem: {
  //       highlight: {
  //           render: true
  //       }
  //   }
  // });
  

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
  $('#search_button').on('click', function() {
  	// First check input field is empty or not
  	const inputField = document.getElementById('autocomplete-input');
  	if(inputField.value == "" ) {
  		return;
  	}
    var api_key = '7c12036c11aea87af9d938d331e8c107';
    var title = $('.movie').val();
    if (title=="") {
      $('.results').css('display','none');
      $('.fail').css('display','block');
    }
    else {
      get_movie_details(title);
    }
  });

  function get_movie_details(movie_title) {
    // https://api.themoviedb.org/3/find/tt0111161?api_key=7c12036c11aea87af9d938d331e8c107&external_source=imdb_id
    // https://api.themoviedb.org/3/movie/tt0111161?api_key=7c12036c11aea87af9d938d331e8c107
    // https://image.tmdb.org/t/p/original/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg
    const url = '/recommend/?movie=' + movie_title;
    $.ajax({
      type:'GET',
      url: url,
      success: function(movie_details){
        show_details(movie_details,arr,movie_title,my_api_key,movie_id);
      },
      error: function(){
        alert("API Error!");
        $("#loader").delay(500).fadeOut();
      },
    });
}

});

