// JS for creating tables based on user selectedPIDs

var table_handle = "";

function paintTable(username){

	table_handle = $('#example').DataTable( {		
	    "serverSide": true,			    	    
		"ajax": 'http://162.243.93.130/cgi-bin/php_simple.php',		
		"columns": [
			{ 	"searchable": true, 
				"name":"id" 
			},
			{ 	"searchable": true, 
				"name":"PID" 
			},
		    { 	"searchable": true, 
		    	"name":"username"		    	
		    },
		    {
		    	"name":"status",
		    	"visible":false
		    }		    
		  ],
		"rowCallback": function( row, data, displayIndex ) {
            if ( data[3] == "selected" ) {            	
                $(row).addClass('selected');                
            }
        }
	} );

	// filter only the user
	table_handle.columns(2).search(username).draw();	

	// selects rows
	$('#example tbody').on('click', 'tr', function () {	  		
	    // OLD
	    // var id = $(this).children()[0].innerHTML;    
	    // var index = $.inArray(id, selected);
	    // if ( index === -1 ) {
	    //     selected.push( id );
	    // } else {
	    //     selected.splice( index, 1 );
	    // }
	    // $(this).toggleClass('selected');

	    // NEW
	    var id = $(this).children()[0].innerHTML;	    
		$.ajax({
			url: "/PIDRowUpdate/"+id+"/update_status/toggle",			
			}).done(function() {
			$(this).toggleClass('selected');
			table_handle.draw();			
		});
	} );
 
    // $('#button').click( function () {
    //     alert( table.rows('.selected').data().length +' row(s) selected' );
    // } );
}

function s_all_true(){
	
}

function s_all_false(){

} 

function s_del(){
	
}