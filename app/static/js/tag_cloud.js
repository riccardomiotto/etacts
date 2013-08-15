// function to output the search results
function show_filter_results(data) 
  { sout = '<table id="search_table">';
    sout += result_content (data.nct);
    // page navigation
    sout += '<tr><td colspan="3"><p id="nav_search">'
    np = parseInt(data.npag);
    sfirst = (np-1)*20 + 1;
    slast = np * 20;
    // previous
    if (np > 1)
      sout += '<span id="frprev" class="nav_page"> Previous Page (' + (sfirst-20) + ' - ' + (slast-20) + ')</span>';
    else
      sout += '<span> Previous Page </span>'
    // current
    sout += '<span id="rshow"> Showing (' + sfirst + ' - ' +slast + ')</span>'
    // next
    pmax = Math.ceil(parseInt(data.n.replace(',',''))/20);
    if (np+1 <= pmax)
      sout += '<span id="frnext" class="nav_page"> Next Page (' + (sfirst+20) + ' - ' + (slast+20) + ')</span>'
    else
      sout += '<span> Next Page </span>'
    sout += '</p></td></tr></table>';
    sout += '</table>'
    $("#filter_results").html(sout); 
    
    // navigation clicks
    $('#frprev').bind('click', function() 
      { $('#filter_results').hide();
	$('.loader').show();
	$(document).scrollTop(0);  
	ltag = format_selected_tags($('#selected_tags').html());
	$.post ($SCRIPT_ROOT + '/_turn_fresult', 
	    { tag: ltag, 
	      nct: String(data.onct),
	      npag: (np-1)}, function (data) 
                { $('#filter_results').show();
		  $('.loader').hide() 
		  show_filter_results (data);
		}, 'json');
      });

    $('#frnext').bind('click', function() 
      { $('#filter_results').hide();
	$('.loader').show();
	$(document).scrollTop(0);  
	ltag = format_selected_tags($('#selected_tags').html());
	$.post ($SCRIPT_ROOT + '/_turn_fresult', 
	    { tag: ltag, 
	      nct: String(data.onct),
	      npag: (np+1)}, function (data) 
                { $('#filter_results').show();
		  $('.loader').hide() 
		  show_filter_results (data);
		}, 'json');
      });
  }


// output the tag cloud of tags
function tag_cloud (data)
 { ftags = format_tags (data.tags, data.nct);
   $("#tag_cloud").jQCloud(ftags, {width:640, height:280});
   $("#tag_cloud_container").show();
 }


// format tags for the cloud
function format_tags (tags, nct)
{ ftags = new Array ();
  for (var i=0;i<tags.length; i++)
  { t = tags[i][0]
    if (t.charAt(3) == ':')
    { t = t.substring(4); }
      var ct = {text:t, weight:parseFloat(tags[i][1]), html:{class: 'cloud_label', value: tags[i][0]}, 
	      handlers:{click:function() { refine_results($(this).attr('value'), true, nct); }}};
    ftags[i] = ct
  }
  return ftags;
}


// filter search results (add = false is remove)
function refine_results (tag, add, nct)
  { // update tag selection
    stags = $('#selected_tags').html();
    t = tag;
    if (tag.charAt(3) == ':')
      { pfx = tag.substring(0,3);
        t = tag.substring (4);
        if (pfx == 'inc')
          { t = '<span id="prefix">inclusion:</span> ' + t; }
        if (pfx == 'exc')
          { t = '<span id="prefix">exclusion:</span> ' + t; }
      }
    if (add == true)
      { stags += '<p class="stag" id="' + tag + '">' + t + '</p>'; }
    else
      { stags = stags.replace ('<p class="stag" id="' + tag + '">' + t + '</p>', ''); }
    $('#selected_tags').html(stags);
    // format tag selection for the server
    ltag = format_selected_tags (stags);
    // tag removal
    $('.stag').click(function () { refine_results ($(this).attr('id'), false, nct); });
    $('#filter_results').hide();
    $('.loader').show();
    // processing
    $.post ($SCRIPT_ROOT + '/_refine_search', 
	    { tag: ltag, 
	      nct: String(nct),
	      npag: 1,
	      ttag: $('.tag_type.selected').attr('id'),
	      trole: $('#tag_role .selected').attr('id')
	    }, function (data) 
                { sout = '<p class="recap"> Left <span class="drecap">' + data.n + '</span> clinical trials for: <span id="qlabel" class="drecap">' + data.q + '<span></p>';
		  $('#filter_header_results').html(sout)
		  $("#tag_cloud").empty()
		  $("#tag_cloud").jQCloud(format_tags(data.tags,data.onct), {width:640, height:280});
		  add_tag_type_click (data.onct)
		  $('#filter_results').show();
		  $('.loader').hide();
		  if (parseInt(data.nct.length) > 0)
		    { show_filter_results (data); }
		  else
		  { $('#filter_results').empty (); }
		}, 'json');
  }


// convert the selected tags for server processing
function format_selected_tags (htag)
 { var rx = /<p class="stag" id="(.*?)">{1}/
   tags = '';
   while (match = rx.exec(htag))
    { tags = tags + match[1] +';';
      htag = htag.replace (match[0],''); 
    } 
   return tags.substring (0,tags.length-1);
 }

	   

