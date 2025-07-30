
get_all_existing_methods()
function get_all_existing_methods(){
    fetch('http://localhost:5000/get_methods') 
    .then(response => response.text())
    .then(data => {

        // document.getElementById("list").innerHTML = "<"
        console.log(data)
        data2 = JSON.parse(data)
        // console.log(data2)
        // console.log(data[0][0])
        // console.log(data.length)
        // console.log(data[0].length)
        document.getElementById("list").innerHTML = ""

        for (let i = 0; i < data2.length; i++) {
            document.getElementById("list").innerHTML += edit_card_html(data2[i][0], data2[i][1], data2[i][2])
        }
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(
        // document.getElementById('response').innerText = ""
    );
}

function show_card_html(command, python_script, id){
    console.log(python_script)
    console.log(python_script)
    console.log(JSON.stringify(python_script))
    return `
            <div id="card-${id}" class="card">
                <p>ID: ${id}</p>  
                <p><strong>Command: </strong><br/> "${command}"</p>  
                <p><strong>Python script: </strong><br/> ${python_script}</p>
                <a onclick='edit_card("${command}", '${JSON.stringify(python_script)}', ${id})' style='color: green'> Edit</a>
                <a onclick='delete_method(${id})' style='color: red'>Delete</a>
            </div>`
}

function show_card(command, python_script, id){
    let element = document.getElementById(`card-${id}`)
    element.outerHTML = edit_card_html(command, python_script, id)

}

function edit_card(command, python_script, id){
    let element = document.getElementById(`card-${id}`)
    element.outerHTML = edit_card_html(command, python_script, id)
    // let oldHTML = card(command, python_script, id)
    // element.outerHTML = 
}

function edit_card_html(command, python_script, id){
    return `
            <form onsubmit="updateMethod(event, ${id})" id="card-${id}" class="card">
                <p>ID: ${id}</p>  
                <p><strong>Command: </strong></p>
                <textarea name="Text0" cols="40" rows="1" class="w-70">${command}</textarea>
                <p><strong>Python script: </strong></p>
                <textarea name="Text1" cols="40" rows="5" class="w-70">${python_script}</textarea>
                <button type="submit" style='color: green'> Save</button>
                <button onclick='delete_method(${id})' style='color: red'>Delete</button>
            </form>`
}

async function updateMethod(event, id){
    event.preventDefault();
    let value_sent = {
        command: event.target.elements[0].value,
        python_script: event.target.elements[1].value
    }

    console.log(value_sent)
    await fetch(`http://localhost:5000/update_method/${id}`,{
        method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(value_sent)
    })
    .then(response => response.text())
    .then(data => {
        // show_card(value_sent.command, value_sent.python_script, id)
    })
    .catch(error => {
        console.error('Error:', error);
    })

    await fetch('http://localhost:5000/get_methods') 
    .then(response => response.text())
    .then(data => {

        // // console.log(data)
        // data2 = JSON.parse(data)
        // document.getElementById("list").innerHTML = ""

        // for (let i = 0; i < data2.length; i++) {
        //     document.getElementById("list").innerHTML += edit_card_html(data2[i][0], data2[i][1], data2[i][2])
        // }
    })
    .catch(error => {
        console.error('Error:', error);
    })
}


function cancelEditing(element, oldHTML){
    element.outerHTML = oldHTML
}
async function add_new_command(event){
    event.preventDefault();
    console.log(event)
    // event.preventDefault();
    // console.log(event.target.elements.command.value) // from elements property
    console.log(event.target.command.value)
    console.log(event.target.python_script.value)
    let value_sent = {
        command: event.target.command.value,
        python_script: event.target.python_script.value
    }
    // return false
    // let inputData = document.getElementById("input-text").innerText


    // console.log(inputData)
    await fetch('http://localhost:5000/add_method',{
        method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(value_sent)
    })
    .then(response => response.text())
    // .then(data => {
    //     document.getElementById('output-text').innerText = data;
    //     // hljs.highlightElement(document.getElementById('output-text'));
    //     clearInterval(intervalID)
    // })
    .catch(error => {
        console.error('Error:', error);
    })

    await fetch('http://localhost:5000/get_methods') 
    .then(response => response.text())
    .then(data => {

        // console.log(data)
        data2 = JSON.parse(data)
        document.getElementById("list").innerHTML = ""

        for (let i = 0; i < data2.length; i++) {
            document.getElementById("list").innerHTML += show_card_html(data2[i][0], data2[i][1], data2[i][2])
        }
    })
    .catch(error => {
        console.error('Error:', error);
    })

    return false;
}

async function delete_all_commands(event){
    event.preventDefault();
    await fetch('http://localhost:5000/delete_all_methods',
    {
        method: 'DELETE'
    })
    .then(response => response.text())
    // .then(data => {
    //     document.getElementById('output-text').innerText = data;
    //     // hljs.highlightElement(document.getElementById('output-text'));
    //     clearInterval(intervalID)
    // })
    .catch(error => {
        console.error('Error:', error);
    })

    await fetch('http://localhost:5000/get_methods') 
    .then(response => response.text())
    .then(data => {

        // console.log(data)
        data2 = JSON.parse(data)
        document.getElementById("list").innerHTML = ""

        for (let i = 0; i < data2.length; i++) {
            document.getElementById("list").innerHTML += show_card_html(data2[i][0], data2[i][1], data2[i][2])
        }
    })
    .catch(error => {
        console.error('Error:', error);
    })

    return false;
}

async function delete_method(id){
    await fetch(`http://localhost:5000/delete_method/${id}`,
    {
        method: 'DELETE'
    }) 
    .then(response => response.text())
    .then(data => {
        // get_all_existing_methods()
        document.getElementById(`card-${id}`).classList.add("card-eliminate")
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(
        // document.getElementById('response').innerText = ""
    );

    await new Promise(r => setTimeout(r, 1000));

    await fetch('http://localhost:5000/get_methods') 
    .then(response => response.text())
    .then(data => {

        // // console.log(data)
        // data2 = JSON.parse(data)
        // document.getElementById("list").innerHTML = ""

        // for (let i = 0; i < data2.length; i++) {
        //     document.getElementById("list").innerHTML += show_card_html(data2[i][0], data2[i][1], data2[i][2])
        // }
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(
        // document.getElementById('response').innerText = ""
    );
}