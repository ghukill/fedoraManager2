// JS for creating tables based on user selectedPIDs

// server-side table manipulation for PID managing
$(document).ready(function(){			
	$('#example').DataTable( {		
	    "serverSide": true,
		"sAjaxSource": 'http://162.243.93.130/cgi-bin/php_dt.php'				    
	} );	
});
