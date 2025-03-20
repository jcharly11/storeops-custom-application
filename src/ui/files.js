
let baseItems = []
var localItems = []

const file = "/var/environment/storeops-custom-application/local-environment-vars.txt"
const ui_file = "/var/environment/storeops-custom-application/ui-local-environment-vars.txt" 
 
let getEnvironmentVariablesFromBaseFilePromise = function getVariablesData(){
    return new Promise((resolve, reject) => {
        cockpit.file(file).read()
        .then((content, tag) => {
            if(content){
              console.log("reading file finish")
              resolve(content);
            }
        }).catch(error => {
            reject('Can not read local file')
        });
    
    
    
      });
    };

let getEnvironmentVariablesFromLocalFilePromise = function getVariablesData(){
      return new Promise((resolve, reject) => {
          cockpit.file(ui_file).read()
          .then((content, tag) => {
          
            resolve(content);
              
          }).catch(error => {
              console.log(error)
              reject('Can not read UI file')
          });
      
      
      
        });
      };   
      
 
