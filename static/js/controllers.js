'use strict';

/**
 * The root beratedApp module.
 *
 * @type {beratedApp|*|{}}
 */
var beratedApp = beratedApp || {};

/**
 * @ngdoc module
 * @name beratedControllers
 *
 * @description
 * Angular module for controllers.
 *
 */
beratedApp.controllers = angular.module('beratedControllers', ['ui.bootstrap']);

/**
 * @ngdoc controller
 * @name MyProfileCtrl
 *
 * @description
 * A controller used for the My Profile page.
 */
beratedApp.controllers.controller('MyProfileCtrl',
    function ($scope, $log, oauth2Provider, HTTP_ERRORS) {
        $scope.submitted = false;
        $scope.loading = false;

        /**
         * The initial profile retrieved from the server to know the dirty state.
         * @type {{}}
         */
        $scope.initialProfile = {};

        /**
         * Candidates for the genders select box.
         * @type {string[]}
         */
        $scope.genders = [
            {'type': 'NOT_SPECIFIED', 'text': "Not Specified"},
            {'type': 'FEMALE', 'text': "Female"},
            {'type': 'MALE', 'text': "Male"},
        ];
        
        /**
         * Initializes the My profile page.
         * Update the profile if the user's profile has been stored.
         */
        $scope.init = function () {
            var retrieveProfileCallback = function () {
                $scope.profile = {};
                $scope.loading = true;
                gapi.client.berated.getProfile().
                    execute(function (resp) {
                        $scope.$apply(function () {
                            $scope.loading = false;
                            if (resp.error) {
                                // Failed to get a user profile.
                            } else {
                                // Succeeded to get the user profile.
                                $scope.profile.displayName = resp.result.displayName;
                                $scope.profile.gender = resp.result.gender;
                                $scope.profile.zipCode = resp.result.zipCode;
                                $scope.profile.birthDate = resp.result.birthDate;
                                $scope.initialProfile = resp.result;
                            }
                        });
                    }
                );
            };
           /*
            if (!oauth2Provider.signedIn) {
                var modalInstance = oauth2Provider.showLoginModal();
                modalInstance.result.then(retrieveProfileCallback);
            } else {
                retrieveProfileCallback();
            }
           */
        };

        /**
         * Invokes the berated.saveProfile API.
         *
         */
        $scope.saveProfile = function () {
            $scope.submitted = true;
            $scope.loading = true;
            gapi.client.berated.saveProfile($scope.profile).
                execute(function (resp) {
                    $scope.$apply(function () {
                        $scope.loading = false;
                        if (resp.error) {
                            // The request has failed.
                            var errorMessage = resp.error.message || '';
                            $scope.messages = 'Failed to update a profile : ' + errorMessage;
                            $scope.alertStatus = 'warning';
                            $log.error($scope.messages + 'Profile : ' + JSON.stringify($scope.profile));
						/*
                            if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                                oauth2Provider.showLoginModal();
                                return;
                            }
                         */
                        } else {
                            // The request has succeeded.
                            $scope.messages = 'The profile has been updated';
                            $scope.alertStatus = 'success';
                            $scope.submitted = false;
                            $scope.initialProfile = {
                                displayName: $scope.profile.displayName,
                                gender: $scope.profile.gender,
                                zipCode: $scope.profile.zipCode
                            };

                            $log.info($scope.messages + JSON.stringify(resp.result));
                        }
                    });
                });
        };
    })
;

/**
 * @ngdoc controller
 * @name CreateRatingCtrl
 *
 * @description
 * A controller used for the Create Ratings page.
 */
beratedApp.controllers.controller('CreateRatingCtrl',
    function ($scope, $log, oauth2Provider, HTTP_ERRORS) {
    
        /**
         * The rating object being edited in the page.
         * @type {{}|*}
         */
        $scope.rating = $scope.rating || {};
        $scope.rating.ratedName = "";
        $scope.rating.ratedType = "";
        
        /**
         * Holds the default values for the input candidates for ratedTypes select.
         * @type {string[]}
         */
        $scope.ratedTypes = [
            'Person',
            'Product',
            'Business',
            'Place',
            'Other',
        ];
        
         $scope.ratingValues = [
            '1',
            '2',
            '3',
            '4',
            '5',
        ];
    
        // initialization functionality
        // in case we've been redirected here, we want to set form fields from the url
    	//$log.info("in CreateRatingCtrl");

		var data = window.location.href;
		//$log.info("data 1? " + data);
		if(data) {
		  if(data.indexOf("?") >= 0) {
		    var p = data.split('?');
		    data = p[1];
		    data=data.split('&');
		    //$log.info("data 2? " + data);
		    		    
		    for(var i=0; i<data.length; i++){
		        var tmp=data[i].split('=');
		        //$log.info("tmp " + tmp);
		        if (tmp[0] == "ratedName")
		            $scope.rating.ratedName = tmp[1].replace("%20", " "); // TODO: replaces first %20 only
		        if (tmp[0] == "ratedType") {		            
		            var val = tmp[1].replace("%20", " ").trim();
		            //$log.info("val " + val);
		            for (var j = 0; j < $scope.ratedTypes.length; j++) {
    				   if ( val == $scope.ratedTypes[j])
		                   $scope.rating.ratedType = $scope.ratedTypes[j];		
		             }            
		           }
		    	}
            } // if data indexOf
		} // if data


        
        /**
         * Tests if $scope.rating is valid.
         * @param ratingForm the form object from the create_rating.html page.
         * @returns {boolean|*} true if valid, false otherwise.
         */
        $scope.isValidRating = function (ratingForm) {
            return true;
        }

        /**
         * Invokes the berated.createRating API.
         *
         * @param ratingForm the form object.
         */
        $scope.createRating = function (ratingForm) {
            $log.info('entered createRating');
            
            if (!$scope.isValidRating(ratingForm)) {
                return;
            }

            $scope.loading = true;
            $log.info($scope.loading + ' : ' + $scope.loading);
            gapi.client.berated.createRating($scope.rating).
                execute(function (resp) {
                    $scope.$apply(function () {
                        $scope.loading = false;
                        if (resp.error) {
                            // The request has failed.
                            var errorMessage = resp.error.message || '';
                            $scope.messages = 'Failed to create a rating : ' + errorMessage;
                            $scope.alertStatus = 'warning';
                            $log.error($scope.messages + ' rating : ' + JSON.stringify($scope.rating));
                  /*
                            if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                                oauth2Provider.showLoginModal();
                                return;
                            }
                   */
                        } else {
                            // The request has succeeded.
                           // $scope.messages = 'The rating has been created';
                            //$scope.alertStatus = 'success';
                            $scope.submitted = false;
                            $scope.rating = {};
                            //$log.info($scope.messages + ' : ' + JSON.stringify(resp.result));
                        }
                    });
                });
        };
    });

/**
 * @ngdoc controller
 * @name ShowRatingsCtrl
 *
 * @description
 * A controller used for the Show Ratings page.
 */
beratedApp.controllers.controller('ShowRatingsCtrl', function ($scope, $log, oauth2Provider, HTTP_ERRORS) {

});

/**
 * @ngdoc controller
 * @name BrowseRatingsCtrl
 *
 * @description
 * A controller used for the Browse Ratings page.
 */
beratedApp.controllers.controller('BrowseRatingsCtrl', function ($scope, $log, oauth2Provider, HTTP_ERRORS) {
    
    /**
     * Holds the status if the query is being executed.
     * @type {boolean}
     */
    $scope.submitted = false;

    $scope.selectedTab = 'ALL';
    
    /**
	 * The rating object being edited in the page.
	 * @type {{}|*}
	 */
	$scope.canned = $scope.canned || {};
	$scope.canned.ratedCategory = "";
	$scope.canned.radioItem = "All";
	$scope.canned.ratedSortByItem = "Rating";
	$scope.canned.ratedName = "";
	$scope.canned.ratedLimit = "100";
	$scope.ratedCategories = [
	        'Any',
            'Person',
            'Product',
            'Business',
            'Place',
            'Other',
        ];
    
    $scope.ratedSortByItems = [
        "High",
        "Name",
        "Num"
    ]

    /**
     * Holds the filters that will be applied when browseRatings is invoked.
     * @type {Array}
     */
     $scope.filters = [];  
     $scope.canned_types = [];
     $scope.canned_radios = [];
     $scope.canned_names = [];
     $scope.canned_sortbys = [];
     $scope.canned_limits = [];
    
    $scope.cannedFiltereableFields = [
      {enumValue: 'RATED_TYPE', displayName: 'ratedType(Person,Product,Business,Place,Other)'},
      {enumValue: 'LIMIT', displayName: 'limit(0=show all)'},
      {enumValue: 'RATED_NAME', displayName: 'ratedName'},
      {enumValue: 'SORT_BY', displayName: 'sortBy(High,Low,Name,Num)'}
    ]

    $scope.filtereableFields = [
        {enumValue: 'RATED_NAME', displayName: 'ratedName'},
        {enumValue: 'SORT_BY', displayName: 'sortBy(High,Low,Name,Num)'}, 
    ]

    /**
     * Possible operators.
     *
     * @type {{displayName: string, enumValue: string}[]}
     */
    $scope.operators = [
        {displayName: '=', enumValue: 'EQ'},
        {displayName: '>', enumValue: 'GT'},
        {displayName: '>=', enumValue: 'GTEQ'},
        {displayName: '<', enumValue: 'LT'},
        {displayName: '<=', enumValue: 'LTEQ'},
        {displayName: '!=', enumValue: 'NE'}
    ];

    /**
     * Holds the ratings currently displayed in the page.
     * @type {Array}
     */
    $scope.browse = [];

    /**
     * Sets the selected tab to 'ALL'
     */
    $scope.tabAllSelected = function () {
        $scope.selectedTab = 'ALL';
       /*
        if (!oauth2Provider.signedIn) {
            oauth2Provider.showLoginModal();
            return;
        }
      */
        $scope.browseRatings();
    };

    /**
     * Adds a filter and set the default value.
     */
    $scope.addFilter = function (item) {
        $log.info("addFilter, ratedType ", item)
        $scope.filters.push({
            field: $scope.filtereableFields[0],
            operator: $scope.operators[0],
            value: item
        })
    };
    
    $scope.setRatedType = function (item) {
        $log.info("setRatedType, ratedType ", item)
        $scope.clearFilters();
        $scope.canned_types = []; // reset on each callback
        if (item != "Any") {
	        $scope.canned_types.push({
            field: $scope.cannedFiltereableFields[0], // RATED_TYPE
            operator: $scope.operators[0],
            value: item
           });   
       } 
    };
   
    
    // replaces setRatedLimit
    $scope.setRatedLimit = function(item) {
       $log.info("setting canned.ratedLimit to ", item);
       $scope.canned_limits = [];
       $scope.canned.ratedLimit = item;
       $scope.canned_limits.push({
            field: $scope.cannedFiltereableFields[1], // LIMIT
            operator: $scope.operators[0],
            value: item
       });   
    }
    
    $scope.setRatedSortByItem = function(item) {
       $log.info("setting canned.ratedSortByItem to ", item);
       $scope.canned_sortbys = [];
       $scope.canned.ratedSortByItem = item;
       $scope.canned_sortbys.push({
            field: $scope.cannedFiltereableFields[3], // SORT BY
            operator: $scope.operators[0],
            value: item
       });   
    }
    
    $scope.setRatedName = function(item) {
       $log.info("setting canned.ratedName to ", item);
       $scope.canned_names = [];
       $scope.canned.ratedName = item;
       if (item != "") {
	       $scope.canned_names.push({
                field: $scope.cannedFiltereableFields[2], // RATED_NAME
                operator: $scope.operators[0],
                value: item
	       });   
	   }
    }

    /**
     * Clears all filters.
     */
    $scope.clearFilters = function () {
        $scope.filters = [];
    };

    /**
     * Removes the filter specified by the index from $scope.filters.
     *
     * @param index
     */
    $scope.removeFilter = function (index) {
        if ($scope.filters[index]) {
            $scope.filters.splice(index, 1);
        }
    };
    
    /**
     * Toggles the status of the offcanvas.
     */
    $scope.toggleOffcanvas = function () {
        $scope.isOffcanvasEnabled = !$scope.isOffcanvasEnabled;
    };
    
    /**
    *  Callback from table row
    */
    $scope.go = function (item) {
        $log.info("in browseRatings.go");
        $log.info(item);
        var ratedType = item.ratedType;
        var ratedName = item.ratedName;
        // go to createRating page with these fields filled in
        // so the user only has to add their own rating and submit
        window.location = "#/berated/create?ratedName=" + ratedName + "&ratedType= " + ratedType;
    };

    /**
     * Namespace for the pagination.
     * @type {{}|*}
     */
    $scope.pagination = $scope.pagination || {};
    $scope.pagination.currentPage = 0;
    $scope.pagination.pageSize = 20;
    /**
     * Returns the number of the pages in the pagination.
     *
     * @returns {number}
     */
    $scope.pagination.numberOfPages = function () {
        return Math.ceil($scope.browse.length / $scope.pagination.pageSize);
    };

    /**
     * Returns an array including the numbers from 1 to the number of the pages.
     *
     * @returns {Array}
     */
    $scope.pagination.pageArray = function () {
        var pages = [];
        var numberOfPages = $scope.pagination.numberOfPages();
        for (var i = 0; i < numberOfPages; i++) {
            pages.push(i);
        }
        return pages;
    };
    
    /**
     * Invokes the berated.browseRatings API.
     */
    $scope.browseRatings = function (ratedName) {
        // clear the filters to be sent
        var sendFilters = {
            filters: []
        }
        $scope.pagination.currentPage = 0; // reset to page one on all searches
        
        // handle (optional) ratedName search selection
        if (ratedName != "") {
           $log.info("setting ratedName to ", ratedName);
           $scope.setRatedName(ratedName);
        }
        else {
           $log.info("re-setting ratedName to empty");
           $scope.setRatedName("");
        }
        
        // handle (optional) ratedLimit search selection
        if ($scope.canned.ratedLimit != "") {
           $log.info("setting ratedLimit to ", $scope.canned.ratedLimit);
           $scope.setRatedLimit($scope.canned.ratedLimit);
        }
        else {
          $log.info("re-setting ratedLimit to 100");
           $scope.setRatedLimit("100");
        }
	    
	    // honor the (required) ratedType search selection
        $log.info("canned_types = ", $scope.canned_types);
        if ($scope.canned_types.length > 0) {
           for (var i = 0; i < $scope.canned_types.length; i++) {
	            var filter = $scope.canned_types[i];
	            if (filter.field && filter.operator && filter.value) {
	                sendFilters.filters.push({
	                    field: filter.field.enumValue,
	                    operator: filter.operator.enumValue,
	                    value: filter.value
	                });
	            }
	        }
	    }
	        
	    // handled the (optional) sortby search selection
        $log.info("canned_sortbys = ", $scope.canned_sortbys);
        if ($scope.canned_sortbys.length > 0) {
           for (var i = 0; i < $scope.canned_sortbys.length; i++) {
	            var filter = $scope.canned_sortbys[i];
	            if (filter.field && filter.operator && filter.value) {
	                sendFilters.filters.push({
	                    field: filter.field.enumValue,
	                    operator: filter.operator.enumValue,
	                    value: filter.value
	                });
	            }
	        }
	    }
	    
	    // handled the (optional) name search selection
        $log.info("canned_names = ", $scope.canned_names);
        if ($scope.canned_names.length > 0) {
           for (var i = 0; i < $scope.canned_names.length; i++) {
	            var filter = $scope.canned_names[i];
	            if (filter.field && filter.operator && filter.value) {
	                sendFilters.filters.push({
	                    field: filter.field.enumValue,
	                    operator: filter.operator.enumValue,
	                    value: filter.value
	                });
	            }
	        }
	    }
	    
	    // handled the (optional) limit search selection
        $log.info("canned_limits = ", $scope.canned_limits);
        if ($scope.canned_limits.length > 0) {
           for (var i = 0; i < $scope.canned_limits.length; i++) {
	            var filter = $scope.canned_limits[i];
	            if (filter.field && filter.operator && filter.value) {
	                sendFilters.filters.push({
	                    field: filter.field.enumValue,
	                    operator: filter.operator.enumValue,
	                    value: filter.value
	                });
	            }
	        }
	    }
 
        $log.info("sendFilters " + sendFilters.filters);
        $scope.loading = true;
        gapi.client.berated.browseRatings(sendFilters).
            execute(function (resp) {
                $scope.$apply(function () {
                    $scope.loading = false;
                    if (resp.error) {
                        // The request has failed.
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'query failed : ' + errorMessage;
                        $scope.alertStatus = 'warning';
                        $log.error($scope.messages + ' filters : ' + JSON.stringify(sendFilters));
                    } else {
                        // The request has succeeded.
                        $scope.submitted = false;
                        //if (sendFilters["filters"].length == 0)
                        //    $scope.messages = 'Without filters, this view displays some of the things that have been rated today';
                        //else
                        //    $scope.messages = 'Query succeeded, yo : ' + JSON.stringify(sendFilters);
                        //$scope.alertStatus = 'success';
                        //$log.info($scope.messages);

                        $scope.browse = [];
                        angular.forEach(resp.items, function (browse) {
                            $scope.browse.push(browse);
                        });
                        //$log.info("scope browse " + $scope.browse);
                        //$log.info("browse length " + $scope.browse.length);
                    }
                    $scope.submitted = true;
                });
            });
    };
    
});


/**
 * @ngdoc controller
 * @name RootCtrl
 *
 * @description
 * The root controller having a scope of the body element and methods used in the application wide
 * such as user authentications.
 *
 */
beratedApp.controllers.controller('RootCtrl', function ($scope, $location, oauth2Provider) {

    /**
     * Returns if the viewLocation is the currently viewed page.
     *
     * @param viewLocation
     * @returns {boolean} true if viewLocation is the currently viewed page. Returns false otherwise.
     */
    $scope.isActive = function (viewLocation) {
        return viewLocation === $location.path();
    };

    /**
     * Returns the OAuth2 signedIn state.
     *
     * @returns {oauth2Provider.signedIn|*} true if siendIn, false otherwise.
     */
    $scope.getSignedInState = function () {
        return oauth2Provider.signedIn;
    };

    /**
     * Calls the OAuth2 authentication method.
     */
    $scope.signIn = function () {
    /*
        oauth2Provider.signIn(function () {
            gapi.client.oauth2.userinfo.get().execute(function (resp) {
                $scope.$apply(function () {
                    if (resp.email) {
                        oauth2Provider.signedIn = true;
                        $scope.alertStatus = 'success';
                        $scope.rootMessages = 'Logged in with ' + resp.email;
                    }
                });
            });
        });
      */
    };

    /**
     * Render the signInButton and restore the credential if it's stored in the cookie.
     * (Just calling this to restore the credential from the stored cookie. So hiding the signInButton immediately
     *  after the rendering)
     */
    $scope.initSignInButton = function () {
        gapi.signin.render('signInButton', {
            'callback': function () {
                jQuery('#signInButton button').attr('disabled', 'true').css('cursor', 'default');
                if (gapi.auth.getToken() && gapi.auth.getToken().access_token) {
                    $scope.$apply(function () {
                        oauth2Provider.signedIn = true;
                    });
                }
            },
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'scope': oauth2Provider.SCOPES
        });
    };

    /**
     * Logs out the user.
     */
    $scope.signOut = function () {
        oauth2Provider.signOut();
        $scope.alertStatus = 'success';
        $scope.rootMessages = 'Logged out';
    };

    /**
     * Collapses the navbar on mobile devices.
     */
    $scope.collapseNavbar = function () {
        angular.element(document.querySelector('.navbar-collapse')).removeClass('in');
    };

});


/**
 * @ngdoc controller
 * @name OAuth2LoginModalCtrl
 *
 * @description
 * The controller for the modal dialog that is shown when an user needs to login to achive some functions.
 *
 */
beratedApp.controllers.controller('OAuth2LoginModalCtrl',
    function ($scope, $modalInstance, $rootScope, oauth2Provider) {
        $scope.singInViaModal = function () {
        /*
            oauth2Provider.signIn(function () {
                gapi.client.oauth2.userinfo.get().execute(function (resp) {
                    $scope.$root.$apply(function () {
                        oauth2Provider.signedIn = true;
                        $scope.$root.alertStatus = 'success';
                        $scope.$root.rootMessages = 'Logged in with ' + resp.email;
                    });

                    $modalInstance.close();
                });
            });
          */
        };
    
 });

/**
 * @ngdoc controller
 * @name DatepickerCtrl
 *
 * @description
 * A controller that holds properties for a datepicker.
 */
beratedApp.controllers.controller('DatepickerCtrl', function ($scope) {
    $scope.today = function () {
        $scope.dt = new Date();
    };
    $scope.today();

    $scope.clear = function () {
        $scope.dt = null;
    };

    // Disable weekend selection
    $scope.disabled = function (date, mode) {
        return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
    };

    $scope.toggleMin = function () {
        $scope.minDate = ( $scope.minDate ) ? null : new Date();
    };
    $scope.toggleMin();

    $scope.open = function ($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened = true;
    };

    $scope.dateOptions = {
        'year-format': "'yy'",
        'starting-day': 1
    };

    $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'shortDate'];
    $scope.format = $scope.formats[0];
});

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');

    for(var i = 0; i < hashes.length; i++)
        {
         hash = hashes[i].split('=');
         vars.push(hash[0]);
         vars[hash[0]] = hash[1];
         }

     return vars;
}
