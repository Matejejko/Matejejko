

document.getElementById("form").addEventListener("submit", function(event) {
    var selectedValue = document.querySelector('input[name="radio"]:checked').value;
    localStorage.setItem("selectedValue", selectedValue);
});

