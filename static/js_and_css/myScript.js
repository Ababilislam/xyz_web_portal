// JavaScript Document
var my_url='https://127.0.0.1:8000/touries/'
//var my_url='https://touries.com/';



// ------------------------------------------------

$(function() {

//<!--	   country-->
	 var country_show="";  
	  
	 $.ajax({
		  //url: 'http://touries.com/default/country_list',
		  url: my_url+'default/country_list',
		  success: function(country) {
			country_show=country
				
		  }
		});
		$('input#country').focus(function() {
			var country_list = country_show.split(',');
			$( "input#country" ).autocomplete({	
				source: country_list
				
			
		 });
	  }); 
		$('input#country').keyup(function(){
			var country_code=".";
			country_code=$("#country").val()
			if (country_code==""){
				$("#city").val('');
			}
			
	  }); 
	   
}); 



////Get country code based on city
$(function() {
//<!--All city list-->
var city_all="";
var temp_city_array ;
var myarray = new Array();
myarray[0] = new Array(2); // Make the first element an array of two elements 
var city_list;
 $.ajax({
	  //url: 'http://touries.com/default/city_all',
	  url: my_url+'default/city_all',
	  success: function(city) {
		city_all=city		
	  }
	});
	
$('input#city').blur(function() {
		var city_code=$("#city").val()	
		var city_all_string;
		temp_city_array = city_all.split(':');
		 if (city_code!=''){
			for(i = 0; i < temp_city_array.length; i ++)
			{
				  myarray[i] = temp_city_array[i].split(';');
				  myarray[i][1] = myarray[i][1].replace(/\]/g,'');  
				  myarray[i][0] = myarray[i][0].replace(/\[/g,'');   
			  	if(myarray[i][1]==city_code){
						$("#country").val(myarray[i][0]);
						
				  }	
			  }	
			}  				
		
	  });

	

	   
}); 


$(function() {
//<!--All city list-->
var city_all="";
var temp_city_array ;
var myarray = new Array();
myarray[0] = new Array(2); // Make the first element an array of two elements 
var city_list;
 $.ajax({
	  //url: 'http://touries.com/touries/default/city_all',
	  url: my_url+'default/city_all',
	  success: function(city) {
		city_all=city		
	  }
	});
	
	
var city_show=""; 
$('input#city').focus(function() {
var country_code=$("#country").val()	
var city_all_string;
var start_flag=0;	
temp_city_array = city_all.split(':');
for(i = 0; i < temp_city_array.length; i ++)
{
	  myarray[i] = temp_city_array[i].split(';');
	  myarray[i][1] = myarray[i][1].replace(/\]/g,'');  
	  myarray[i][0] = myarray[i][0].replace(/\[/g,'');   
	  
	  if (country_code!=''){
	  
		  if(myarray[i][0]==country_code){
				if (start_flag==0){
					city_all_string=myarray[i][1];
					start_flag=1;
				}
				else{
					city_all_string=city_all_string+","+myarray[i][1];
				}
		  }	
	  }
	  else{
			if (start_flag==0){
				city_all_string=myarray[i][1];
				start_flag=1;
			}
			else{
				city_all_string=city_all_string+","+myarray[i][1];
			}
	  }
}   
			var city_list = city_all_string.split(',');
			$( "input#city" ).autocomplete({	
				source: city_list
		 });
	  }); 
	   
}); 

$(function() {
	 var city_show=""; 
		$('input#hotel_name').focus(function() {
		  var country_code=$("#country").val()	
		  var city_code=$("#city").val()
		  $.ajax({	
			  //url:  "http://touries.com/default/hotel_list?country="+country_code+"&city="+city_code,
			  url:  my_url+"default/hotel_list?country="+country_code+"&city="+city_code,
			  success: function(hotel) {
			  hotel_show=hotel
			  }
		  });
			var hotel_list = hotel_show.split(',');
			$( "input#hotel_name" ).autocomplete({	
				source: hotel_list
			
		 });
	  });  
});	





//=================datepicker================

$(function() {
	$( "#datepicker" ).datepicker({
		//showOn: "both",
		numberOfMonths: 2,
		dateFormat: "dd-mm-yy",
		//onSelect: insertDepartureDate,
		firstDay: 1,
		minDate: '0Y', maxDate: '+1Y'
	});
});


//<!--check out-->
  
$(function() {
	$( "#datepicker_out" ).datepicker({
		//showOn: "both",
		numberOfMonths: 2,
		dateFormat: "dd-mm-yy",
		//onSelect: insertDepartureDate,
		firstDay: 1,
		minDate: '0Y', maxDate: '+1Y'
	});
});




//<!--set out date based on nights-->

function sale_days() {
   var dateAdjust=$("#sel_days").val();   
   if (dateAdjust.match('^(0|[1-9][0-9]*)$')){
	   if ((dateAdjust.length>2) || (dateAdjust>30)){
	    $("#sel_days").val('');
        $('#datepicker_out').val('');
	   }
	   else{
		   var firstDate = new Date($('#datepicker').datepicker("getDate"));
		   var current_date= new Date();
		   current_time = current_date.getTime();
		   days=(firstDate.getTime()-current_time)/(1000*60*60*24);
		   if(days < 0){
			var add_day = 1;
			}else{
			 var add_day = 2;
			}
		   days=parseInt(days);
		   $('#datepicker_out').datepicker("option" , "minDate" , days + add_day );
		   $('#datepicker_out').datepicker("option" , "maxDate" , days+29);
		   dateAdjust=parseInt(dateAdjust);
		   var secondDate = new Date(firstDate.getFullYear(), firstDate.getMonth(), firstDate.getDate()+ dateAdjust);
		   $('#datepicker_out').datepicker('setDate', secondDate);
	   }
   }
   else{
   	$("#sel_days").val('');
    $('#datepicker_out').val('');
   
   }
};

function sale_days_in() {
   var dateAdjust=$("#sel_days").val(); 
	sale_days();
   
}

$(document).ready(function() {
var myDate = new Date();
var prettyDate =myDate.getDate()+ '-' +(myDate.getMonth()+1) + '-' + myDate.getFullYear();
$("#datepicker").val(prettyDate);
var dateAdjust=30;
var firstDate = new Date($('#datepicker').datepicker("getDate"));
var current_date= new Date();
current_time = current_date.getTime();
days=(firstDate.getTime()-current_time)/(1000*60*60*24);
if(days < 0){
var add_day = 1;
}else{
 var add_day = 2;
}
days=parseInt(days);
$('#datepicker_out').datepicker("option" , "minDate" , days + add_day );
$('#datepicker_out').datepicker("option" , "maxDate" , days+29);
dateAdjust=parseInt(dateAdjust);
var secondDate = new Date(firstDate.getFullYear(), firstDate.getMonth(), firstDate.getDate()+ dateAdjust);

$('#datepicker_out').bind('change', function(){
    var d1 = $('#datepicker').datepicker('getDate');
    var d2 = $('#datepicker_out').datepicker('getDate');
    var diff = 0;
    if (d1 && d2) {
            diff = Math.floor((d2.getTime() - d1.getTime()) / 86400000); // ms per day
    }
    
  $("#sel_days").val(diff);
});


$('#datepicker').bind('change', function(){
   var dateAdjust=30;
   var firstDate = new Date($('#datepicker').datepicker("getDate"));
   var current_date= new Date();
   current_time = current_date.getTime();
   days=(firstDate.getTime()-current_time)/(1000*60*60*24);
   if(days < 0){
	var add_day = 1;
	}else{
	 var add_day = 2;
	}
   days=parseInt(days);
   $('#datepicker_out').datepicker("option" , "minDate" , days + add_day );
   $('#datepicker_out').datepicker("option" , "maxDate" , days+29);
   dateAdjust=parseInt(dateAdjust);
   var secondDate = new Date(firstDate.getFullYear(), firstDate.getMonth(), firstDate.getDate()+ dateAdjust);
   
    var d1 = $('#datepicker').datepicker('getDate');
    var d2 = $('#datepicker_out').datepicker('getDate');
    var diff = 0;
    if (d1 && d2) {
            diff = Math.floor((d2.getTime() - d1.getTime()) / 86400000); // ms per day
    }
});

});

//===============================



		
		
//<!--=======================combo box end=============-->	
	

//<!-- slider-->

$(function() {
	var max_p=$( "#price_max" ).val();
	var min_p=$( "#price_min" ).val();
	
	var max_p=max_p;
	var min_p=min_p;
	$( "#slider-range" ).slider({
		range: true,
		min: 5000,
		max: max_p,
		values: [ min_p, max_p ],
		slide: function( event, ui ) {
			$( "#price" ).val( ui.values[ 0 ] );
			$( "#price_end" ).val( ui.values[ 1 ] );
			$( "#price_div" ).text( "BDT" + ui.values[ 0 ] + " - BDT" + ui.values[ 1 ]  );
			
		}
	});
	$( "#price" ).val( $( "#slider-range" ).slider( "values", min_p ) );
	//$( "#price" ).val( min_p );
	$( "#price_end" ).val(max_p );
	
	//$( "#price_div" ).text( $( "#slider-range" ).slider( "values", 0) );
});

 
//<!--================================-->	
//<!--==============saerch table show============-->


function search_table() {
	jQuery('#search_table').show();
	jQuery('#filter_table').hide();
};
function filter_table() {
	jQuery('#search_table').hide();
	jQuery('#filter_table').show();
};

//<!--========================================-->



//<!--====================Start form validation====================-->

//$(document).ready(function() {
//	var text ='';
//	$(required_field).css({ 'color': '#A20000', 'font-size': '16px' ,'font-family':'' , 'font-style':'','font-weight':''});;
//	$("#required_field").html(text);
//	$("#btn_search").click(function() 
//        {
//			var valid_country=$("#country").val();
//			var valid_city=$("#city").val();
//			var valid_check_in=$("#datepicker").val();
//			var valid_check_out=$("#datepicker_out").val();
//			var valid_rooms=$("#rooms").text();
//			if (valid_country=='') 
//			{
//            	text=text + '<div >Counrty</div> '
//				$("#required_field").html(text);
//			}
//			if (valid_city=='') 
//			{
//				text=text + '<div >city</div> '
//            	$("#required_field").html(text);
//			}
//			
//			if (valid_check_out=='') 
//			{
//				text=text+ '<div >Checkin</div> ' + '<div >Checkout</div> '
//            	$("#required_field").html(text);
//			}
//			if (valid_rooms<1) 
//			{
//            	text=text + '<div >room</div> '
//				$("#required_field").html(text);
//			}
//			
//			if ((valid_country!='') && (valid_city!='') && (valid_check_in!='') && (valid_check_out!='') && (valid_rooms>0))
//			{
//				$("form#form1").submit(); 
//			}
//			text ='';
//		
//        });
//	
//});
 // ==================================================================





