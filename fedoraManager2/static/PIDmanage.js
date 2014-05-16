// JS for creating tables based on user selectedPIDs

$(document).ready(function(){			
	$('#example').DataTable( {		
	    "serverSide": true,		
		"ajax": 'http://162.243.93.130/cgi-bin/php_simple.php',						
	} );	
});

