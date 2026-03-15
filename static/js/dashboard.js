// Handle menu clicks properly
$(".menu > ul > li > a").on("click", function (e) {

  const parentLi = $(this).parent("li");
  const subMenu = parentLi.children(".sub-menu");

  // CASE 1: Menu has submenu → toggle only
  if (subMenu.length) {
    e.preventDefault(); // stop navigation ONLY for submenu
    parentLi.toggleClass("active");
    subMenu.slideToggle();

    parentLi.siblings().removeClass("active");
    parentLi.siblings().children(".sub-menu").slideUp();
  }

  // CASE 2: Normal menu (NO submenu) → allow navigation
  else {
    $(".menu > ul > li").removeClass("active");
    parentLi.addClass("active");
    // NO preventDefault here → href WILL work
  }
});

// Sidebar toggle
$(".menu-btn").click(function () {
  $(".sidebar").toggleClass("active");
});
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const icon = document.querySelector(".menu-btn i");

    sidebar.classList.toggle("collapsed");

    // Change icon direction
    if (sidebar.classList.contains("collapsed")) {
        icon.classList.remove("ph-caret-left");
        icon.classList.add("ph-caret-right");
    } else {
        icon.classList.remove("ph-caret-right");
        icon.classList.add("ph-caret-left");
    }
}
function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("collapsed");
}
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const icon = document.querySelector(".menu-btn i");

    sidebar.classList.toggle("collapsed");

    if (sidebar.classList.contains("collapsed")) {
        icon.classList.remove("ph-caret-left");
        icon.classList.add("ph-caret-right");
    } else {
        icon.classList.remove("ph-caret-right");
        icon.classList.add("ph-caret-left");
    }
}