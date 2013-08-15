// show the trial list
function result_content (nct)
  { var sout = new String()
    for (var k in nct)
      { // rank
	sout += '<tr><td class="rank">' + nct[k][1] +'</td>';
	// title
	// sout += '<td class="title"><a href="http://clinicaltrials.gov/ct2/show/' + nct[k][0]+ '" target="_blank">' + nct[k][2] + '</a>';
	sout += '<td class="title"><a href="http://haotianyong.appspot.com/cluster_gov?/ct2/show/' + nct[k][0]+ '" target="_blank">' + nct[k][2] + '</a>';
	// condition
	sout += '<table class="ct_detail"><tr><td id="dtitle"> Condition: </td><td id="dvalue">' + nct[k][3] + '</td></tr></table></tr>';
      }
    return sout
  }


// function to output the search results
function show_results(data, tsearch) 
  { sout = '<table id="search_table">';
    sout += result_content (data.nct);
    // page navigation
    sout += '<tr><td colspan="3"><p id="nav_search">'
    first = parseInt(data.nct[0][1]);
    last = parseInt(data.nct[data.nct.length-1][1]);
    np = parseInt(data.npag);
    // previous
    if (np > 1)
      sout += '<span id="rprev" class="nav_page"> Previous Page (' + (first-20) + ' - ' + (last-20) + ')</span>';
    else
      sout += '<span> Previous Page </span>'
    // current
    sout += '<span id="rshow"> Showing (' + first + ' - ' + last + ')</span>'
    // next
    pmax = Math.ceil(parseInt(data.n.replace(',',''))/20);
    if (np+1 <= pmax)
      sout += '<span id="rnext" class="nav_page"> Next Page (' + (first+20) + ' - ' + (last+20) + ')</span>'
    else
      sout += '<span> Next Page </span>'
    sout += '</p></td></tr></table>';
    $("#results").html(sout); 
    
    // navigation clicks
    $('#rprev').bind('click', function() 
      { if (tsearch == 'advanced')
          advanced_search(parseInt(data.npag)-1);
        else
          search(parseInt(data.npag)-1);
	$(document).scrollTop(0);
      });

    $('#rnext').bind('click', function() 
      { if (tsearch == 'advanced')
          advanced_search(parseInt(data.npag)+1);
        else
          search(parseInt(data.npag)+1);
	$(document).scrollTop(0);
      });

    $('.filter_link').bind('click', function() 
      { tag_cloud_filtering (tsearch); });
  }


// tag cloud filtering
function tag_cloud_filtering (tsearch)
 { $("#search_form").hide();
   $('#header_results').hide();
   $('.filter').hide();
   $('#results').hide();
   $('.loader').show();
   $('.tag_type').removeClass ('selected');
   if (tsearch == 'advanced')
    { var form_args = $(adv_search).serializeArray();
      qlabel = $('#qlabel').text();
      var qlabel = {"name": "qlabel", "value": qlabel};
      form_args.push(qlabel);
      $.getJSON($SCRIPT_ROOT + '/_advs_tag_cloud', 
		form_args, function (data) { tagcloud_visualization (data)});
    }
   else
      $.getJSON($SCRIPT_ROOT + '/_tag_cloud', 
	       { stxt: $('input[name="search_text"]').val()}, function (data) { tagcloud_visualization (data)});
 }


// visualize tagcloud
function tagcloud_visualization (data)
 { tag_cloud (data);
   $('.loader').hide();
   $('#filter_header_results').html($('#header_results').html())
   $('#filter_header_results').show();
   $('#inc').addClass ('selected');
   $('#all').addClass ('selected');
   add_tag_type_click (data.nct)
   add_tag_role_click (data.nct)
   $('#filter_results').empty();
   $('#filter_results').show();
 }


// add action to the tag-type buttons
function add_tag_type_click (nct)
 { ltag = format_selected_tags ($('#selected_tags').html());
   $('.tag_type').unbind ('click');
   $('.tag_type').bind ('click', function() 
	{ sel = $('.tag_type.selected').attr('id');
	  if (sel != $(this).attr('id'))
	   { $("#tag_cloud").html('<div class="loader"><span class="tagcloud"></span><span class="tagcloud"></span><span class="tagcloud"></span></div>');
	     $.post ($SCRIPT_ROOT + '/_refine_tagcloud', 
	      { nct: String(nct),
		tag: ltag,
		ttag: $(this).attr('id'),
		trole: $('#tag_role .selected').attr('id')
	      }, function (data) 
		  { $('.tag_type').removeClass ('selected');
		    $('#' + data.tgrp).addClass ('selected');
		    $("#tag_cloud").empty()
		    $("#tag_cloud").jQCloud(format_tags(data.tags,data.nct), {width:630, height:280}); 
		  }, 'json');
	   }
      });
 }


// add action to the tag-role buttons
function add_tag_role_click (nct)
 { ltag = format_selected_tags ($('#selected_tags').html());
   $('.trole').unbind ('click');
   $('.trole').bind ('click', function() 
	{ sel = $('.trole.selected').attr('id');
	  if (sel != $(this).attr('id'))
	   { $("#tag_cloud").html('<div class="loader"><span class="tagcloud"></span><span class="tagcloud"></span><span class="tagcloud"></span></div>');
	     $.post ($SCRIPT_ROOT + '/_refine_tagcloud', 
	      { nct: String(nct),
		tag: ltag,
		ttag: $('#tag_category .selected').attr('id'),
		trole: $(this).attr('id')
	      }, function (data) 
		   { $('.trole').removeClass ('selected');
		     $('#' + data.trole).addClass ('selected');
		     $("#tag_cloud").empty()
		     $("#tag_cloud").jQCloud(format_tags(data.tags,data.nct), {width:630, height:280}); 
		   }, 'json');
	   } 
	});
 }



// function to search
function search (np)
{ $('#results').hide();
  $('.loader').show() 
  $.getJSON ($SCRIPT_ROOT + '/_ctgov_search', 
    { stxt: $('input[name="search_text"]').val(),
      npag: np
    }, function (data) 
          { // format query
	    fquery = data.q.replace(/&/g,'&amp');
	    fquery = fquery.replace(/</g,'&lt');
	    fquery = fquery.replace(/>/g,'&gt');
	    tsearch = 'regular';
	    sout = '<p class="recap"> Found <span class="drecap">' + data.n + '</span> clinical trials for: <span id="qlabel" class="drecap">' + data.q + '<span></p>';
	    $('.loader').hide()
	    $('#results').show()
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


// document
$(document).ready(function() 
 { $('#adv_search_detail').hide();
   $('#tag_cloud_container').hide();
   $('#filter_results').hide();
   $('#filter_header_results').hide();
   $('.loader').hide();
   $('#search_text').focus();
   
   // round corners
   $('#tc_box').corner('left');
   $('#tag_selection').corner('right');
   $('#header').corner('top');
   $('#navigation').corner('bottom');
   $('#footer').corner();
   $('.sbutton').corner('5px');

   // search
   $('#search_button').bind('click', 
     function() 
       { search (1); 
	 $(document).scrollTop(0);
       });
   
   $('#search_text').live ("keypress", function(e) 
     {  if (e.keyCode == 13) 
          { search (1); 
	    $(document).scrollTop(0);
            return false;
          }
     });

   $('.field_text').live ("keypress", function(e) 
     {  if (e.keyCode == 13) 
          { advanced_search(1);
	    $(document).scrollTop(0);
            return false;
          }
     });

   // advanced search
   $('#advsearch_button').click(function()
     { $("#search_form").hide();
       $('#header_results').hide();
       $('#results').hide();
       $("#adv_search_detail").show();
       var input = $('input[name="search_text"]').val();
       $('#first_focus').val(input);
     });

   $('.asearch').click (function()
     { advanced_search(1);
       $(document).scrollTop(0);
     });

   // close advanced search form and return
   $('#back_button').click(function()
     { $("#adv_search_detail").hide();
       $("#search_form").show();
       $('#header_results').show();
       $('#results').show();
     });

   
   // close tag cloud
   $('#close_tag_cloud').bind('click',
     function()
       { // empty and hide the cloud
	 $("#tag_cloud_container").hide();
	 $("#tag_cloud").empty();
	 $("#selected_tags").empty();
	 $("#filter_results").hide();
	 $("#filter_header_results").hide();
	 // empty and show results
	 $("#search_form").show();
	 $.getJSON ($SCRIPT_ROOT + '/_clean', function (data)
		    { $("#results").show();	 
		      $("#header_results").show();	 
		      $(".filter").show();	 
		      $(document).scrollTop(0);
		      $("#search_form").show();
		    }); 
       });

 });   

