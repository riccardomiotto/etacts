// advanced search function
function advanced_search(np)
 { $('#adv_search_detail').hide();
   $("#search_form").show();
   $('.loader').show();
   // array of objects of search form values and npag value
   var form_args = $(adv_search).serializeArray();
   for (var i=0; i<3; i++)
   { s = 'State' + (i+1);
     fs = 'f' + s.toLowerCase();
     var it = {'name':fs, 'value': $('#' + s + ' option:selected').html().replace(' &nbsp;', '')};
     form_args.push(it);
     c = 'Country' + (i+1)
     fc = 'fcntry' + (i+1)
     var it = {'name':fc, 'value': $('#' + c + ' option:selected').html().replace(' &nbsp;', '')};
     form_args.push(it);
   }
   var page = {'name': 'npag', 'value': np};
   form_args.push(page);
   $.getJSON($SCRIPT_ROOT + '/_adv_search', form_args, function(data)
     { tsearch = 'advanced';
       var input = $('input[name="term"]').val();
       $('#search_text').val(input);
       sout = '<p class="recap"> Found <span class="drecap">' + data.n + '</span> clinical trials for: <span id="qlabel" class="drecap">' + data.q + '<span></p>';
       $('.loader').hide();
       $("#header_results").show();
       $('#results').show();
       nres = parseInt(data.n.replace(',',''));
       if (nres > 0) 
         { if (nres > 1 && nres <= 25000)
	     sout += '<p class="filter"> Result Filtering: <span id="tfilt" class="filter_link"> Eligibility Criteria Tag Cloud </span> </p>';
	   else
	     { if (nres > 25000)
		 sout += '<p class="filter"> Result Filtering: <span id="tfilt" class="filter_na"> Eligibility Criteria Tag Cloud NOT Available (resulting trials must be less than 25,000)</span></p>';
             }
	   $("#header_results").html(sout);
           show_results(data, tsearch);
	 }
       else
        { $("#header_results").html(sout);
          $('#results').empty();
        }
     });
  }
