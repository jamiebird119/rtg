$(document).ready(function () {
  $("#pickyDate").datepicker();
});

$("#pickyDate").datepicker({
  onSelect: function (dateText, inst) {
    var dateAsString = dateText; //the first parameter of this function
    var dateAsObject = $(this).datepicker("getDate"); //the getDate method
    print(dateText);
  },
});

console.log("hello")