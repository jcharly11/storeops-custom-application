const submitButton = document.getElementById("submit-button");
const container = document.getElementById("container");
const errorMessage = document.getElementById("alert");
errorMessage.style.visibility = 'hidden'
const errorMessageText = document.getElementById("message");
errorMessageText.style.visibility = 'hidden'
let fileId = []

$(document).ready(function() {
  getEnvironmentVariablesFromBaseFilePromise().then((base) => { 
    console.log("Response promise")
    var baseData = base
    console.log(baseData)
    console.log("*************")
    if (baseData) {
      let baseContent = baseData.split("\n")
      baseContent.forEach(element => {
          if(element){
            baseItems.push(element) 
         }
     })};
  
     getEnvironmentVariablesFromLocalFilePromise().then((local) => { 
      console.log("Response promise")
      var localData = local
      console.log(localData)
      console.log("*************")
      if (localData) {
        localContent = localData.split("\n")
        localContent.forEach(element => {
          if(element){
            console.log(element);
            localItems.push(element)
   
          }

       
     });
    }
     console.log("***############****")
     console.log(baseItems.length)
     console.log(localItems.length)
     if(baseItems.length > localItems.length){ //NEW ITEMS IN BASE FILES FROM DEPLOY
        printUI(baseItems)
     }else{
      printUI(localItems)
     }
  
       
     
     }).catch((error) => {
       console.log(error);
      // alertError("Error getting data file base")
  
     }); 
     
    

   
   }).catch((error) => {
     console.log(error);
     alertError("Error getting data file base")

   });  
   
  

  

     
         
});


function setEnvironmentVariables(){
  replaceContent = ""
  fileId.forEach(element => {

    value = document.getElementById(element).value
    nline = "export "+  element + "=" + value + "\n"
    console.log(nline)
    replaceContent += nline 

  })
  console.log(replaceContent)
   cockpit.file(tempFile).replace(replaceContent)
   .then((content, tag) => {
    console.log(content)
    copyFile()
   
    
    
   }).catch(error => {
       console.log(error)
       message = error.message + "\n" +"Please turn to administrative access"
       window.alert(message)
   });

}
function copyFile(){
  cockpit.spawn(["/usr/bin/cp", tempFile, ui_file]).then((data) => { 
 
    console.log(data);
    restartCustomApplication()
  
  }).catch((error) => {
    console.log(error);
  });  

  
   
}
function restartCustomApplication(){
  
  cockpit.spawn(["sh","/var/scripts/storeops-custom-application/restart_custom_app.sh", true]).then((data) => { 
    console.log(data);
    window.alert("Upgrade complete")
  }).catch((error) => {
    console.log(error);
  });  
}
function printUI(content){
  console.log("******printUI*******");
  content.forEach(element => {
      
    data = element.split("=")
    value = data[0].replace("export ", "")

    if (value == "MQTT_SECURE_CONNECTION"){
      
      separator = document.createElement("hr")
      separator.className = 'dashed'
        container.appendChild(document.createElement("br"))
        container.appendChild(document.createElement("br"))
        container.appendChild(separator) 
        container.appendChild(document.createElement("br"))
        container.appendChild(document.createElement("br"))
    }

    var divName = document.createElement('div');
    divName.className='divName'
    
    var divValue = document.createElement('div');
    divValue.className = 'divValue'


    divName.innerHTML = value
    container.appendChild(divName);
    

    var input = document.createElement("input");
    input.type = "text";
    input.id =value;
    fileId.push(value)
    input.value = data[1].replace(/'/g,"")

    divValue.appendChild(input)


    container.appendChild(divValue);
    container.appendChild(document.createElement("br"))
    container.appendChild(document.createElement("br"))
    container.appendChild(document.createElement("hr")) 
    

  });   
 
}
submitButton.addEventListener("click",  setEnvironmentVariables)

      