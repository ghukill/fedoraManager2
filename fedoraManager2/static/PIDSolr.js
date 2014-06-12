// javascript for /PIDSolr data tables

// table handle
var table_handle = "";

// paint table
function paintTable(json_output){
	table_handle = $('#PIDtable').DataTable({
		"data":json_output,
		"columns": [
			{ 	"searchable": true, 
				"name":"PID" 
			},
			{ 	"searchable": true, 
				"name":"dc_title",
				"render":function (data,type,row){		    				    		
		    		return "<a target='_blank' href='http://digital.library.wayne.edu/digitalcollections/item?id="+row[0]+"'>"+row[1]+"</a>";
		    	} 
			}
		  ],
	});	
}

