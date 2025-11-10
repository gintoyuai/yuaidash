(function($) {
    'use strict';
	//Header Search
	if($('.search-box-outer').length) {
		$('.search-box-outer').on('click', function() {
			$('body').addClass('search-active');
		});
		$('.close-search').on('click', function() {
			$('body').removeClass('search-active');
		});
	}
	
	// Mobile Menu
    $('.mobile-menu nav').meanmenu({
        meanScreenWidth: "991",
        meanMenuContainer: ".mobile-menu",
        meanMenuOpen: "<span></span> <span></span> <span></span>",
        onePage: false,
    });	

    // sticky
    var wind = $(window);
    var sticky = $('#sticky-header');
    wind.on('scroll', function () {
        var scroll = wind.scrollTop();
        if (scroll < 100) {
            sticky.removeClass('sticky');
        } else {
            sticky.addClass('sticky');
        }
    });

    // Loder  //
    $(function () {
      $('body').addClass('loaded');
    });


      // testimonial Active
      $('.hero-active').owlCarousel({
        loop: true,
        autoplay: true,
		smartSpeed: 2500,
        autoplayTimeout: 6500,
        dots:false,
        nav:true,
        margin: 30,
        navText: ["next", "prev"],
        responsive: {
			320: {
                items: 1
            },
			480: {
                items:1
            },
            600: {
                items: 1
            },
            768: {
                items: 1
            },
            992: {
                items: 1
            },
            1000: {
                items: 1
            },
            1920: {
                items: 1
            }
        }
    })  


     // project Active
     $('.project_list').owlCarousel({
        loop: true,
        autoplay: true,
		smartSpeed: 1500,
        autoplayTimeout: 2800,
        dots: true,
        nav: false,
        margin: 30,
        navText: ["<i class='bi bi-arrow-right''></i>", "<i class='bi bi-arrow-left''></i>"],
        responsive: {
            0: {
                items: 1
            },
            768: {
                items: 2
            },
            992: {
                items: 2
            },
            1000: {
                items: 3
            },
            1920: {
                items: 5
            }
        }
    }) 

// project Active
    $('.project_item').owlCarousel({
        loop: true,
        autoplay: true,
        smartSpeed: 1500,
        autoplayTimeout: 2800,
        dots:false,
        nav:true,
        margin: 30,
        navText: ["<i class='bi bi-arrow-left''></i>", "<i class='bi bi-arrow-right''></i>"],
        responsive: {
            0: {
                items: 1
            },
            768: {
                items: 2
            },
            992: {
                items: 3
            },
            1000: {
                items: 3
            },
            1920: {
                items: 4
            }
        }
    }) 


// testimonial Active
    $('.brand_list').owlCarousel({
        loop: true,
        autoplay: true,
		smartSpeed: 1500,
        autoplayTimeout: 2800,
        dots: false,
        nav: false,
        navText: ["<i class='bi bi-chevron-left''></i>", "<i class='bi bi-chevron-right''></i>"],
        responsive: {
			320: {
                items: 1
            },
			480: {
                items: 2
            },
            600: {
                items: 2
            },
            768: {
                items: 3
            },
            992: {
                items: 3
            },
            1000: {
                items: 4
            },
            1920: {
                items: 5
            }
        }
    })  



    // testimonial Active
    $('.testi_list').owlCarousel({
        loop: true,
        autoplay: true,
		smartSpeed: 1500,
        autoplayTimeout: 2800,
        dots: false,
        nav: false,
        margin: 30,
        navText: ["<i class='bi bi-chevron-left''></i>", "<i class='bi bi-chevron-right''></i>"],
        responsive: {
			320: {
                items: 1
            },
			480: {
                items:1
            },
            600: {
                items: 1
            },
            768: {
                items: 2
            },
            992: {
                items: 2
            },
            1000: {
                items: 3
            },
            1920: {
                items: 3
            }
        }
    })  

      // testimonial Active
      $('.testi_inner').owlCarousel({
        loop: true,
        autoplay: true,
		smartSpeed: 1500,
        autoplayTimeout: 2800,
        dots:true,
        nav:false,
        margin: 30,
        navText: ["<i class='bi bi-chevron-left''></i>", "<i class='bi bi-chevron-right''></i>"],
        responsive: {
			320: {
                items: 1
            },
			480: {
                items:1
            },
            600: {
                items: 1
            },
            768: {
                items: 2
            },
            992: {
                items: 2
            },
            1000: {
                items: 2
            },
            1920: {
                items: 2
            }
        }
    })  
  
    /*---------------------
    WOW active js 
    --------------------- */
    new WOW().init();


    //curseer animation

    var curser = document.querySelector(".curser");
    var curser2 = document.querySelector(".curser2");

    document.addEventListener("mousemove", function(e){
        curser.style.cssText = curser2.style.cssText = "left: " + e.clientX + "px; top: " + e.clientY + "px;";
    });


    // counterUp
    $('.counter').counterUp({
        delay: 10,
        time: 1000
    });
	
	/*  Cart Plus Minus Button
    /*----------------------------------------*/
    $('.ctnbutton').on('click', function () {
        var $button = $(this);
        var oldValue = $button.parent().find('input').val();
        if ($button.hasClass('inc')) {
            var newVal = parseFloat(oldValue) + 1;
        } else {
            // Don't allow decrementing below zero
            if (oldValue > 1) {
                var newVal = parseFloat(oldValue) - 1;
            } else {
                newVal = 1;
            }
        }
        $button.parent().find('input').val(newVal);
    });

	
	 // Venubox

    $('.venobox').venobox({

        numeratio: true,

        infinigall: true

    });
	/*--------------------------
     scrollUp
    ---------------------------- */
    $.scrollUp({
        scrollText: '<i class="fa fa-angle-up"></i>',
        easingType: 'linear',
        scrollSpeed: 900,
        animation: 'fade'
    })

    // accordion js
        jQuery(document).ready(function($) {
            "use strict";

            $(".accordion > li:eq(0) a").addClass("active").next().slideDown();

            $(".accordion a").click(function (j) {
                var dropDown = $(this).closest("li").find("p");

                $(this).closest(".accordion").find("p").not(dropDown).slideUp();

                if ($(this).hasClass("active")) {
                    $(this).removeClass("active");
                } else {
                    $(this).closest(".accordion").find("a.active").removeClass("active");
                    $(this).addClass("active");
                }

                dropDown.stop(false, true).slideToggle();

                j.preventDefault();
            });

        });




        $(document).ready(function(){
        $('#bar1').barfiller({ duration: 7000 });
        $('#bar2').barfiller({ duration: 7000 });
        $('#bar3').barfiller({ duration: 7000 });
        });

        
        $(window).on('scroll', function () {
            var scrolled = $(window).scrollTop();
            if (scrolled > 300) $('.go-top').addClass('active');
            if (scrolled < 300) $('.go-top').removeClass('active');
        });

        $('.go-top').on('click', function () {
            $("html, body").animate({
                scrollTop: "0"
            }, 1200);
        });

        // table tabs
        
        $(document).ready(function() { 

        (function ($) { 
            $('.tab ul.tabs').addClass('active').find('> li:eq(0)').addClass('current');
            
            $('.tab ul.tabs li a').click(function (g) { 
                var tab = $(this).closest('.tab'), 
                    index = $(this).closest('li').index();
                
                tab.find('ul.tabs > li').removeClass('current');
                $(this).closest('li').addClass('current');
                
                tab.find('.tab_content').find('div.tabs_item').not('div.tabs_item:eq(' + index + ')').slideUp();
                tab.find('.tab_content').find('div.tabs_item:eq(' + index + ')').slideDown();
                
                g.preventDefault();
            } );
        })(jQuery);

    });

    // Sidebar
    
    "use strict";
        jQuery(document).ready(function (o) {
            0 < o(".offset-side-bar").length &&
                o(".offset-side-bar").on("click", function (e) {
                    e.preventDefault(), e.stopPropagation(), o(".cart-group").addClass("isActive");
                }),
                0 < o(".close-side-widget").length &&
                    o(".close-side-widget").on("click", function (e) {
                        e.preventDefault(), o(".cart-group").removeClass("isActive");
                    }),
                0 < o(".navSidebar-button").length &&
                    o(".navSidebar-button").on("click", function (e) {
                        e.preventDefault(), e.stopPropagation(), o(".info-group").addClass("isActive");
                    }),
                0 < o(".close-side-widget").length &&
                    o(".close-side-widget").on("click", function (e) {
                        e.preventDefault(), o(".info-group").removeClass("isActive");
                    }),
                o("body").on("click", function (e) {
                    o(".info-group").removeClass("isActive"), o(".cart-group").removeClass("isActive");
                }),
                o(".xs-sidebar-widget").on("click", function (e) {
                    e.stopPropagation();
                }),
                0 < o(".xs-modal-popup").length &&
                    o(".xs-modal-popup").magnificPopup({
                        type: "inline",
                        fixedContentPos: !2,
                        fixedBgPos: !0,
                        overflowY: "auto",
                        closeBtnInside: !2,
                        callbacks: {
                            beforeOpen: function () {
                                this.st.mainClass = "my-mfp-slide-bottom xs-promo-popup";
                            },
                        },
                    });
            });

        // Sidebar
        jQuery(document).ready(function () {
            $('.nav-btn a i').on('click', function () {
                $('.xs-sidebar-group').addClass('isActive');
            });

            $('.xs-overlay').on('click', function () {
                $('.xs-sidebar-group').removeClass('isActive');
            });
            
            $('.close-side-widget').on('click', function () {
                $('.xs-sidebar-group').removeClass('isActive');
        });
    });

          /* Portfolio Isotope---case study*/
          $('.image_load').imagesLoaded(function () {

            if ($.fn.isotope) {
                
                var $portfolio = $('.image_load');
        
                $portfolio.isotope({
                    itemSelector: '.grid-item',
                    filter: '*',
                    resizesContainer: true,
                    layoutMode: 'masonry',
                    transitionDuration: '0.8s'
                });
        
                $('.menu-filtering li').on('click', function () {
                    $('.menu-filtering li').removeClass('current_menu_item');
                    $(this).addClass('current_menu_item');
                    var selector = $(this).attr('data-filter');
                    $portfolio.isotope({
                        filter: selector,
                    });
                });
        
            }
        });

     
    
})(jQuery);

