var emailinput = document.getElementById('email');
emailinput.addEventListener('input', function() {
    var inputvalue = emailinput.value;
    if (inputvalue === '') {
        emailinput.innerText = 'email@company.com';
    } 
});

var errormsg = document.getElementById('error');
var submitButton = document.getElementById ('submit');

submitButton.addEventListener('click', function(event) {
    var emailvalue = emailinput.value;
    if (emailvalue === ''|| emailvalue.indexOf('@') === -1) {
        errormsg.style.display = 'block';
        emailinput.classList.add('error-input');
    } else {
        errormsg.style.display = 'none';
        emailinput.classList.remove('error-input');
        localStorage.setItem("userInput", emailinput.value);
       
        window.location.href = "thanks.html";
    }
});



