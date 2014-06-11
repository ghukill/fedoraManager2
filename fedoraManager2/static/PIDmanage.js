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
		    },
		    {
		    	"name":"actions",
		    	"title":"actions",		    	
		    	"render":function (data,type,row){		    				    		
		    		return "<a href='#' onclick='del_row("+row[0]+"); return false;'>remove</a>";
		    	}		    	
		    }	    
		  ],
		searchCols: [
	        null,
	        null,	        
	        { sSearch: username },
	        null,
	        null
	    ],	    
		"rowCallback": function( row, data, displayIndex ) {
            if ( data[3] == "selected" ) {            	
                $(row).addClass('selected');                
            }
        },
        start:1
	} );
	
	// LEAVE FOR REFERENCE, searchCols WORKING ABOVE PER BUG FIX IN DATATABLES
	// filter only the user
	// https://datatables.net/forums/discussion/comment/61834#Comment_61834
	// table_handle.columns(2).search(username).draw();	

	// selects row
	$('#example tbody').on('click', 'tr', function () {
	    var id = $(this).children()[0].innerHTML;	    
		$.ajax({
			url: "/PIDRowUpdate/"+id+"/update_status/toggle",			
			}).done(function() {
			$(this).toggleClass('selected');
			var cpage = table_handle.page();
			console.log(cpage);
			table_handle.draw();								
			$("a.paginate_button.current").click();					
		});
	} );


 
    // $('#button').click( function () {
    //     alert( table.rows('.selected').data().length +' row(s) selected' );
    // } );
}

// delete row
function del_row(id){	
	$.ajax({
		url: "/PIDRowUpdate/"+id+"/delete/delete",			
		}).done(function() {
			$(this).toggleClass('selected');
			table_handle.draw();			
		});
}	