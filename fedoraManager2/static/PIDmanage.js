// JS for creating tables based on user selectedPIDs

// server-side table manipulation for PID managing
$(document).ready(function(){
	console.log("firing!");
	$('#example').DataTable( {
		// processing: true,
	    serverSide: true,
	    ajax: {
	        url: 'http://162.243.93.130:5001/PIDmanage_data',
	        type: 'POST'
	    }
	} );	
});
