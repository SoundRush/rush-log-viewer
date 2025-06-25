function fetchData() {
  $.getJSON("/data", function (data) {
    if (data.error) {
      $("#table-container").html('<p class="error">' + data.error + "</p>");
    } else {
      let rows = "";
      data.table.forEach((row) => {
        rows += `
                        <tr>
                            <td>${row.timestamp}</td>
                            <td>${row.event_type}</td>
                            <td>${row.message}</td>
                        </tr>
                    `;
      });
      $("#table-body").html(rows);
    }
  });

  const timestamp = new Date().getTime();
  $("#graph").attr("src", "/image?t=" + timestamp);
}

setInterval(fetchData, 5000);
$(document).ready(fetchData);
