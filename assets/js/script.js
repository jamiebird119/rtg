$(document).ready(function () {
    $("#datepicker").datepicker({
        showAnim: "slide",
        prevText: "click for previous months",
        nextText: "click for next months",
        duration: "slow",
        onSelect: function () {
            var dateTime = new Date($("#datepicker").datepicker("getDate"));

            var strDateTime = dateTime.getDate() + "/" + (dateTime.getMonth() + 1) + "/" + dateTime.getFullYear();

            getSchedule(strDateTime);
        }
    });
});