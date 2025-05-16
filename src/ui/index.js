const submitButton = document.getElementById("submit-button");
const container = document.getElementById("container");

let fileId = []
const file = "/var/environment/storeops-basic-custom-application/local-environment-vars.txt"
const tempFile = "/tmp/local-environment-vars.txt"

let getEnvironmentVariablesPromise = function getVariablesData(){
    return new Promise((resolve, reject) => {
        cockpit.file(file).read()
        .then((content, tag) => {
            if(content){
    
              resolve(content);
            }
        }).catch(error => {
            reject('Rejected')
        });
    
    
    
      });
    };
let restartApplicationPromise = function resterApplication() {
      console.log("starting promise")
      return new Promise((resolve, reject) => {
        http = cockpit.http({
          "address": "localhost",
          "headers": {
               
          },
          "port": 8005,
          
      });
        request = http.get("/restart")
        console.log(request)
        request.then((data) => { 
    
          resolve(data)
        
        }).catch((error) => {console.log(error);});   
          
      });
    };

$(document).ready(function() {
      getEnvironmentVariablesPromise().then((data) => { 
          
             let dataContent = data.split("\n")
             dataContent.forEach(element => {
               if(element){
              
                 data = element.split("=")
                 value = data[0].replace("export ", "")

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
              }
              
            });
             
           
           }).catch((error) => {
             console.log(error);
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
   });

}
function copyFile(){
  cockpit.spawn(["/usr/bin/cp", tempFile, file]).then((data) => { 
 
    console.log(data);
    restartApp()
  
  }).catch((error) => {
    console.log(error);
  });  

  
   
}


function restartApp() {
  
  // restartApplicationPromise().then((data) => { 
  //   let result = JSON.parse(data)
  //   console.log(result);
  
  // }).catch((error) => {
  //   console.log(error)
    
  // });  

  restartCustomApplication()
  window.alert("Upgrade complete")
   
}

function restartCustomApplication(){
  cockpit.spawn(["sh","restart.sh", "1"]).then((data) => { 
    console.log(data);
  }).catch((error) => {
    console.log(error);
  });  
   
}

function changeMQTTStatus(enable){
  cockpit.spawn(["mqttt_enable.sh", enable]).then((data) => { 
    console.log(data);
  }).catch((error) => {
    console.log(error);
  });  
   
}

submitButton.addEventListener("click",  setEnvironmentVariables)

      
      