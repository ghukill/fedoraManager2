// JS for creating tables based on user selectedPIDs

var selected = [];

$(document).ready(function(){		
	
	$('#example').dataTable( {		
	    "serverSide": true,		
	    "searchCols":[
	    	null,
	    	{"search":"smalluser", "escapeRegex":false}
	    ],
		"ajax": 'http://162.243.93.130/cgi-bin/php_simple.php',		
		"rowCallback": function( row, data, displayIndex ) {
            if ( $.inArray(data[0], selected) !== -1 ) {
                $(row).addClass('selected');
                console.log("fired");
            }
        }
	} );	

	// Working pretty nice!
	$('#example tbody').on('click', 'tr', function () {	        
	    var id = $(this).children()[0].innerHTML;    
	    var index = $.inArray(id, selected);
	    if ( index === -1 ) {
	        selected.push( id );
	    } else {
	        selected.splice( index, 1 );
	    }
	    $(this).toggleClass('selected');
	} );

	// simple click example
	// $('#example tbody').on('click', 'tr', function () {
 //        var name = $('td', this).eq(0).text();
 //        alert( 'You clicked on '+name+'\'s row' );
 //    } );

	// click selected
	    // $('#example tbody').on( 'click', 'tr', function () {
	    //     $(this).toggleClass('selected');
	    // } );
	 
	    // $('#button').click( function () {
	    //     alert( table.rows('.selected').data().length +' row(s) selected' );
	    // } );

});

