$(document).ready(function () {
  $(".sidenav").sidenav();

  $(".datepicker").datepicker({
    selectMonths: true,
    format: "yyyy-mm-dd",
  });

  $("input.autocomplete").autocomplete({
    data: {
      "Atlanta Hawks": "/static/assets/logos/Hawks.gif",
      "Boston Celtics": "/static/assets/logos/Celtics.gif",
      "Brooklyn Nets": "/static/assets/logos/Nets.gif",
      "Charlotte Hornets": "/static/assets/logos/Hornets.gif",
      "Chicago Bulls": "/static/assets/logos/Bulls.gif",
      "Cleveland Cavaliers": "/static/assets/logos/Cavaliers.gif",
      "Dallas Mavericks": "/static/assets/logos/Mavericks.gif",
      "Denver Nuggets": "/static/assets/logos/Nuggets.gif",
      "Detroit Pistons":"/static/assets/logos/Pistons.gif",
      "Golden State Warriors": "/static/assets/logos/Warriors.gif",
      "Houston Rockets": "/static/assets/logos/Rockets.gif",
      "Indiana Pacers": "/static/assets/logos/Pacers.gif",
      "Los Angeles Clippers": "/static/assets/logos/Clippers.gif",
      "Los Angeles Lakers": "/static/assets/logos/Lakers.gif",
      "Memphis Grizzlies": "/static/assets/logos/Grizzlies.gif",
      "Miami Heat":"/static/assets/logos/Heat.gif",
      "Milwaukee Bucks": "/static/assets/logos/Bucks.gif",
      "Minnesota Timberwolves":"/static/assets/logos/Timberwolves.gif",
      "New Orleans Pelicans": "/static/assets/logos/Pelicans.gif",
      "New York Knicks": "/static/assets/logos/Knicks.gif",
      "Oklahoma City Thunder": "/static/assets/logos/Thunder.gif",
      "Orlando Magic": "/static/assets/logos/Magic.gif",
      "Philadelphia 76ers": "/static/assets/logos/76ers.gif",
      "Phoenix Suns": "/static/assets/logos/Suns.gif",
      "Portland Trail Blazers": "/static/assets/logos/Blazers.gif",
      "Sacramento Kings": "/static/assets/logos/Kings.gif",
      "San Antonio Spurs": "/static/assets/logos/Spurs.gif",
      "Toronto Raptors": "/static/assets/logos/Raptors.gif",
      "Utah Jazz": "/static/assets/logos/Jazz.gif",
      "Washington Wizards": "/static/assets/logos/Warriors.gif",
    },
  });
});

function sendMail(myform) {
  emailjs.init("user_5EZSkDLP3C5SHi2nuzTfw");
  emailjs
    .send("gmail", "template_LYsBkwyA", {
      reply_to: myform.reply_to.value,
      from_name: myform.from_name.value,
      message_html: myform.message_html.value,
    })
    .then(
      function (response) {
        console.log("SUCCESS", response);
      },
      function (error) {
        console.log("FAILED", error);
      }
    );
  return false; // To block from loading a new page
}
