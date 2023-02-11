$(document).ready(function() {

  $(".box").on("click", function() {
    $(this).siblings().toggleClass("hidden");
    $(this).toggleClass("full");
    $(".captionBox").toggleClass("hiddenText");
    $(this).children().animate({
      opacity: "1"
    }, 500, function() {});
  });

   $(".boxl1").on("click", function() {
   window.location.href="/shop";
  });
     $(".box22").on("click", function() {
   window.location.href="/shop";
  });


   $(".boxl2").on("click", function() {
   window.location.href="/pro_cat/Plushies";
  });

   $(".boxl3").on("click", function() {
   window.location.href="/pro_cat/Handmade";
  });

  $(".boxl4").on("click", function() {
   window.location.href="/pro_cat/Swag";
  });



    $(".boxl5").on("click", function() {
   window.location.href="/pro_cat/Axolotls";
  });





  if ($(window).width() < 768) {
    $(".box").on("click", function() {
      $("#gridGallery").toggleClass("mobileFunction");
    });
  }

  if ($(window).width() >= 768) {

    $(".box2").hover(function() {
      $(this).siblings().toggleClass("opacity");
    });

  }

  $(".horizontal").click(function() {
    $(this).toggleClass("full");
    $(".captionBox").toggleClass("hiddenText");
    $(this).children().animate({
      opacity: "1"
    }, 500, function() {});
  });

  $(".horizontal").hover(function() {
    $(this).siblings().toggleClass("opacity");
  });

});