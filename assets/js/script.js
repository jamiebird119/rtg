 $(document).ready(function () {
        $("#pickyDate").datepicker({
          dateFormat: "yy-mm-dd",
          onSelect: function (dateText) {
            urlFor = '{{ url_for("search_schedule", date="fakeDate") }}'.replace(
              "fakeDate",
              dateText
            );
            $.ajax({
              type: "POST",
              url: urlFor,
              success: function (result) {
                data = JSON.parse(result);
                write = "";
                for (i in data) {
                  write += `<h3> ${data[i]["home"]} vs ${data[i]["away"]}
            </h3>
            <button onclick="rate_game(${data[i]["id"]})"> Rate That Game! </button>
            <div id=${data[i]["id"]}></div>
            `;
                }
                document.getElementById("results").innerHTML = write;
              },
              error: function (error) {
                console.log(error);
              },
            });
          },
        });
      });
      
      function rate_game(id) {
        console.log("running")
        url_game = '{{ url_for("search_update", id="fakeId") }}'.replace(
          "fakeId",
          id
        );
        $.ajax({
          type: "POST",
          url: url_game,
          success: function (result) {
            game_data = JSON.parse(result);
            var el = document.getElementById(id);
            var rating = Number(
              0.015 *
                (game_data["home"]["score"] + game_data["away"]["score"]) +
                math.abs(
                  game_data["home"]["score"] - game_data["away"]["score"]
                ) +
                0.06 * game_data["lead_changes"]
            );
            el.innerHTML = `<h1> ${rating} </h1>`;
          },
          error: function (error) {
            console.log(error);
          },
        });
      }