
  // Get references to the input  and output
  var inputCVC = document.getElementById('CVC');
  var displayCVC = document.getElementById('displayCVC');
        inputCVC.maxLength = 3;

  // Add event listener to the input field
  inputCVC.addEventListener('input', function() {
    // Get the value from the input field
    var inputValue = inputCVC.value;

    if (inputValue === '') {
      displayCVC.innerText = '123'; // If empty, display '000'
    } else { 
    // Update the output with input value
    displayCVC.innerText = inputValue; // Use innerText instead of textContent
    }
  });

  var inputname = document.getElementById('cardname');
  var outputname = document.getElementById('displayname');

  inputname.addEventListener('input', function() {

    var inputValueName = inputname.value;

    if (inputValueName === '') {
      outputname.innerText = 'JANE APPLESEED';
    } else {
      outputname.innerText = inputValueName;
    }
  });

  var inputnumber = document.getElementById('cardnumber');
  var outputnumber = document.getElementById('displaynumber');
        inputnumber.maxLength = 16;
  inputnumber.addEventListener('input', function() {
    var inputValuenumber = inputnumber.value;
    // Add a space after every  4 characters
    var formattedNumber = inputValuenumber.replace(/(.{4})(?=.)/g, '$1 ').trim();
    if (formattedNumber === '') {
      outputnumber.innerText = '0000 0000 0000 0000';
    } else {
      outputnumber.innerText = formattedNumber;
    }
  });


  var inputmonth = document.getElementById('MM');
  var outputmonth = document.getElementById('displaymonth');
        inputmonth.maxLength = 2;
  inputmonth.addEventListener('input', function () {
    var inputValuemonth = inputmonth.value;
    if (inputValuemonth === '') {
      outputmonth.innerText = '00';
    } else {
      outputmonth.innerText = inputValuemonth
    }
  });

  var inputyear = document.getElementById('YY');
  var outputyear = document.getElementById('displayyear');
        inputyear.maxLength = 2;
  inputyear.addEventListener('input', function () {
    var inputValueyear = inputyear.value;
    if (inputValueyear === '') {
      outputyear.innerText = '00';
    } else {
      outputyear.innerText = inputValueyear
    }
  });


  var submitButton = document.getElementById ('submitButton');
  var errormsgyear = document.getElementById ('errordate');
  var errormsgyear2 = document.getElementById ('errordate2');
  var errormsgCVC = document.getElementById ('errormsgCVC');
  var errormsgnumber = document.getElementById ('errornumber');

  submitButton.addEventListener('click', function(event) {
    var inputValueyear = inputyear.value;
    if (inputValueyear === ''|| !/^\d+$/.test(inputValueyear)) {
      event.preventDefault();
      errormsgyear.style.display = 'block';
      inputyear.classList.add('error-input');
    } else {
      errormsgyear.style.display = 'none';
      inputyear.classList.remove('error-input');
    }
    var inputValuemonth = inputmonth.value;
    if (inputValuemonth === ''|| !/^\d+$/.test(inputValuemonth)) {
      event.preventDefault();
      errormsgyear2.style.display = 'block';
      inputmonth.classList.add('error-input');
    } else {
      errormsgyear2.style.display = 'none';
      inputmonth.classList.remove('error-input');
    }
    var inputValue = inputCVC.value;
    if (inputValue === ''|| !/^\d+$/.test(inputValue) || inputValue.length !== 3) {
      event.preventDefault();
      errormsgCVC.style.display = 'block';
      inputCVC.classList.add('error-input');
    } else {
      errormsgCVC.style.display = 'none';
      inputCVC.classList.remove('error-input');
    }
    var inputvaluecardnumber = cardnumber.value;
    if (inputvaluecardnumber === ''|| !/^\d+$/.test(inputvaluecardnumber) || inputvaluecardnumber.length !== 16) {
      event.preventDefault();
      errornumber.style.display = 'block';
      cardnumber.classList.add('error-input');
    } else {
      errornumber.style.display = 'none';
      cardnumber.classList.remove('error-input');
    }
    var inputvaluename = cardname.value;
    if (inputvaluename === ''|| !/^[a-zA-Z\s]+$/.test(inputvaluename)) {
      event.preventDefault();
      errorname.style.display ='block';
      cardname.classList.add('error-input');
    } else {
      errorname.style.display ='none';
      cardname.classList.remove('error-input');
    }

    var isValid = 
    errormsgyear.style.display === 'none' &&
    errormsgyear2.style.display === 'none' &&
    errormsgCVC.style.display === 'none' &&
    errornumber.style.display === 'none' &&
    errorname.style.display === 'none';
    var text = document.querySelector('.text');
    var text2 = document.querySelector('.text2');
    
    if (isValid) {
      text.style.display = 'none';
      text2.style.display = 'block';
    } else {
      text.style.display = 'block';
      text2.style.display = 'none';
    }

  });