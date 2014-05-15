// JS for creating tables based on user selectedPIDs



// server-side table manipulation for PID managing
$(document).ready(function(){	
	$('#example').DataTable( {		
	    bserverSide: true,	    	    	    	    	    	    
	    ajax: {	        
	        url: 'http://162.243.93.130/cgi-bin/php_dt.php',
	        type: 'POST'
	    }
	} );	
});
