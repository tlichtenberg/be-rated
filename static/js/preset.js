// preset.js  Copyright 2009-2014 by Richard L. Trethewey - All Rights Reserved
// Permission is granted to use this code as long as this copyright notice
// is left intact.  For more information, see http://www.rainbodesign.com/pub/

// Get the query string contents from the page URL used by removing the "?"
//var query = location.search.substr(1);



var  search_pattern = '\\+';
var  search_flags = 'g';
var  search_reg_exp = new RegExp(search_pattern, search_flags);

function populate(formName) {
  var data = window.location.href;
  var p = data.split('?');
  data = p[1];
  var params=data.split('&');
   console.log("params: " + params);
  if (data) {						// Was there a query string?
   //var params = data.split('&');				// Yes!  Split them up
   var theForm = findForm(formName);			// Locate the form with the correct name/ID
   console.log("theForm: " + formName + " = " + theForm);
    if (theForm != null) {				// Did we find the form?
     for (q=0; q<params.length; q++) {
      xy = params[q].split("=");			// Split the command into name/value pair
      paramName = xy[0];
      newValue = unescape(xy[1].replace(search_reg_exp, ' '));	// translate query string
      console.log("newValue = " + newValue);

       if (theForm.elements[paramName]) {		// does named element exist?

       console.log(paramName + ' ' + theForm.elements[paramName] + ' ' + theForm.elements[paramName].type);

       switch(theForm.elements[paramName].type) {
        case 'text':					// type = "text"
        case 'hidden':					// type = "hidden"
	    case 'textarea':				// <textarea>
        case 'email':					// type = "email"
        case 'search':					// type = "search"
        case 'url':					    // type = "url"
        case 'number':					// type = "number"
        case 'range':					// type = "range"
          theForm.elements[paramName].value = newValue;
          //theForm.elements[paramName].ng-model = "rating." + newValue;
          console.log(theForm.elements[paramName].value); // it's setting the value, but the field is still empty!
        break;

        case 'select-one':				// <select>
		  theOption = theForm.elements[paramName];
		   max = theOption.length;
		   for (i = 0; i < max; i++) {
		    if (theOption.options[i].value == newValue) { theOption.options.selectedIndex = i; }
		   }  // end for i
	    break;

        case undefined:					// type = "radio" (really 'nodeList')
			if (theForm.elements[paramName]) {		// double-check this element exists
			  theOption = theForm.elements[paramName];
			  max = theOption.length;
			  for (i = 0; i < max; i++) {
			   if (theOption[i].value == newValue) { theOption[i].checked = true; }
			  }  // end for i
			 } // endif exists
         break;

        case 'checkbox':				// type="checkbox"
	          theForm.elements[paramName].checked = true;
	    break;

       } // end switch
      } // endif theForm.elements[paramName]
    } // end for q
   } // endif {theForm)
 } // endif (query)
} // end populate()

function findForm(theForm) {
formElement = null;
if (document.getElementById(theForm)) {			// try ID first
 formElement = document.getElementById(theForm);
  } else {
 for (i=0; i<document.forms.length; i++) {
  if (document.forms[i].name == theForm) { formElement = document.forms[i]; break; }
 } // endFor
} // endif document.getElementById
return formElement;
} // end findForm

