function testMatch() {
    var formData = new FormData(document.getElementById('addmatch'))
    console.log(formData)
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        console.log(this.responseText)
        document.getElementById('presubmit_result').innerHTML = this.responseText;
        document.getElementById('presubmit_result').hidden = false;
      }
    };
    xhttp.open('POST', 'presubmit', true);
    //xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    // xhttp.send("a=1&b=2");
    xhttp.send(formData)
    // alert("boom")
}
