(function($) {
	$.fn.userautocomplete = function(options) {

		var username_input = $( this );

		var no_results_indicator = $("#" + username_input.attr('id') +  "_no_results");

		username_input.focusout(function(){
			no_results_indicator.hide();
			username_input.val('');
		});

		username_input.typeahead({
			source: function(input_value, process){

				$.ajax({
					type: "GET",
					url: options.url,
					dataType: "json",
					cache: false,
					data: {
						"searchtext": input_value
					},
					success: function (data) {

						if (data.length == 0){
							no_results_indicator.show();
						}
						else {
							no_results_indicator.hide();
							process(data);
						}
					},
					error: function(){
						
					}
				});
			}, 
			afterSelect : function(item){

				if (options.hasOwnProperty("afterSelect") && typeof(options.afterSelect) == 'function'){
					options.afterSelect(item);
				}
			},
            autoSelect: false,
			minLength: 3,
			delay: 300
		}); 
	}
}(jQuery));
