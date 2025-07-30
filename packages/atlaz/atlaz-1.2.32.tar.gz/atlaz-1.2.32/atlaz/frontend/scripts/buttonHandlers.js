document.addEventListener("DOMContentLoaded", function() {
    const applyButton = document.getElementById("apply-button");
    if (applyButton) {
      applyButton.addEventListener("click", function() {
        fetch("http://127.0.0.1:5050/api/apply_changes", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        })
          .then(response => response.json())
          .then(data => {
            if (data.status === "success") {
              alert("Changes applied successfully!");
            } else {
              alert("Error applying changes: " + (data.message || "Unknown error"));
            }
          })
          .catch(err => {
            console.error("Error applying changes:", err);
            alert("Error applying changes (check console).");
          });
      });
    }
  });
  

  const rejectButton = document.getElementById('reject-button')
  if (rejectButton) {
    rejectButton.addEventListener('click', function() {
        fetch("http://127.0.0.1:5050/api/remove_files", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        })
          .then(response => response.json())
          .then(data => {
            if (data.status === "success") {
              alert("Changes rejected");
            } else {
              alert("Error rejecting changes: " + (data.message || "Unknown error"));
            }
          })
          .catch(err => {
            console.error("Error rejecting changes:", err);
            alert("Error rejecting changes (check console).");
          });
    });
  }
//     }