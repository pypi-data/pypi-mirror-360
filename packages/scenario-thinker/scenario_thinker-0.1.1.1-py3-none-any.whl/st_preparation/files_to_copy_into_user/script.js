
document.addEventListener("DOMContentLoaded", function() {
    colorChange()
  });

  function saveSelection() {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        return selection.getRangeAt(0);
    }
    return null;
}

function restoreSelection(range) {
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
}

function colorChange(){
    let inputDiv = document.getElementById("input-text")

    let textValue = inputDiv.innerText.trim()
        .replaceAll("Feature:", "<br/><span style='color: purple; font-weight: 600'>\nFeature:</span>")
        .replaceAll("Scenario:", "<br/><span style='color: purple; font-weight: 600'>\nScenario:</span>")
        .replaceAll("Given", "<br/><span style='color: red; font-weight: 600'>\nGiven</span>")
        .replaceAll("When", "<br/><span style='color: blue; font-weight: 600'>\nWhen</span>")
        .replaceAll("Then", "<br/><span style='color: green; font-weight: 600'>\nThen</span>")
        .replace("<br/>", "")
    const range = saveSelection();
        
    inputDiv.innerHTML = textValue
}

function addFile(element){
    let file = element.files[0]
    if (file) {
        var reader = new FileReader();
        reader.readAsText(file, "UTF-8");
        reader.onload = function (evt) {
            document.getElementById("input-text").innerHTML = evt.target.result;
            colorChange()
            element.value = ""
        }
        reader.onerror = function (evt) {
            document.getElementById("input-text").innerHTML = "error reading file";
            element.value = ""
        }
    }
}
function sendScenarioToPython(){
    // let file = document.getElementById("input-text").innerText
    document.getElementById('output-text').innerText = "";
    // let heh = setInterval(interval_for_ping, 1000);
    generated_scenario("heh")

}

function interval_for_ping(){
    fetch('http://localhost:5000/which_line_now') 
    .then(response => response.text())
    .then(data => {
        document.getElementById('response').innerText = `Server Response: ${data}`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function generated_scenario(intervalID){
    document.getElementById('error-container').style.display = "none";
    llm_type = document.getElementById('llm').value

    let inputData = document.getElementById("input-text").innerText
    console.log(inputData)
    fetch('http://localhost:5000/get_scenario',{
        method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input_data: inputData, llm_type: llm_type })
    })
    .then(response => response.text())
    .then(data => {
        data2 = JSON.parse(data)
        console.log(data2[0])
        console.log(data2[1])
        console.log("hihi\n\n\n")

        document.getElementById('output-text').innerText = data2[0];
        if(data2[1] != ""){
            document.getElementById('error-text').innerText = data2[1];
            document.getElementById('error-container').style.display = "block";
        }
        hljs.highlightElement(document.getElementById('output-text'));
        clearInterval(intervalID)
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(
        document.getElementById('response').innerText = ""
    );
}

function download(filename) {
    let text = document.getElementById("output-text").innerText
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
  
    element.style.display = 'none';
    document.body.appendChild(element);
  
    element.click();
  
    document.body.removeChild(element);
  }