const submitButton = document.getElementById("submit-button" );
const refreshButton = document.getElementById("refresh-button" );
const clearButton= document.getElementById("clear-button" );
const fileInput = document.getElementById("file-xls-input");
const tableBody = document.getElementById("table-visualizer-container");
const tableEPCSBody = document.getElementById("table-visualizer-container-epcs");
var total_regs=0
var total_regs_unknown=0 
var type_events=[]
var type_events_count=[]


let getKnowEPCSPromise = function getEpcKnow() {
  console.log("starting promise")
  return new Promise((resolve, reject) => {
    http = cockpit.http({
      "address": "localhost",
      "headers": {
           
      },
      "port": 8005,
      
  });
    request = http.get("/api/events/inventory")
    console.log(request)
    request.then((data) => { 

      
      resolve(data)
    
    }).catch((error) => {console.log(error);});   
      
  });
};


let getUnKnowEPCSPromise = function getEpcUnKnow() {
  console.log("starting promise")
  return new Promise((resolve, reject) => {
    http = cockpit.http({
      "address": "localhost",
      "headers": {
           
      },
      "port": 8005,
      
  });
    request = http.get("/api/events/unknown")
    console.log(request)
    request.then((data) => { 
      resolve(data)
    }).catch((error) => {console.log(error);});   
  });
};


let postDBDataPromise = function postLocalData(dataMaster) {
  console.log("starting promise")
  return new Promise((resolve, reject) => {
    
    http = cockpit.http({
      "address": "localhost",
      "headers": {
           
      },
      "port": 8005,
      
  });

  post = http.post("/api/events/datamaster",dataMaster, ["Content-Type: application/json"])
  console.log(post)
  post.then((data) => { 

    resolve(data)
  
  }).catch((error) => {console.log(error);});   
      
  });
};


let clearDataPromise = function postLocalData() {
  console.log("starting promise clear")
  return new Promise((resolve, reject) => {
    
    http = cockpit.http({
      "address": "localhost",
      "headers": {
           
      },
      "port": 8005,
      
  });

  post = http.post("/api/events/clear_data", ["Content-Type: application/json"])
  console.log(post)
  post.then((data) => { 

    resolve(data)
    refreshDataSources()
  
  }).catch((error) => {console.log(error);});   
      
  });
};


let DeleteDatamasterPromise = function deleteDatamaster() {
  console.log("starting promise delete")
  return new Promise((resolve, reject) => {
    
    http = cockpit.http({
      "address": "localhost",
      "headers": {
           
      },
      "port": 8005,
  });

  post = http.post("/api/events/delete_datamaster", ["Content-Type: application/json"])
  console.log(post)
  post.then((data) => { 

    resolve(data)
  
  }).catch((error) => {console.log(error);});   
      
  });
};


$(document).ready(function() {
 /////////////////PROMESA 1 GET
 
 getKnowEPCSPromise().then((data) => { 
        let result = JSON.parse(data)
        total_regs= Object.keys(result).length
        type_events_count=[]
        result.forEach(item => { 
          type_events_count.push(item.sku)
          generateVisualizer(item.epc, item.timestamp, item.alarm_type, item.description, item.image)
        })
        var tableEvents= $('#know-epcs').DataTable();
        $('#know-epcs').DataTable({
          retrieve: true
        });
        tableEvents.order([0, 'desc']).draw();
        
      
      }).catch((error) => {
        console.log(error);
      });  
      
 getUnKnowEPCSPromise().then((data) => { 
        console.log(data);
        let result = JSON.parse(data)
        total_regs= Object.keys(result).length
        result.forEach(item => { 
          generateVisualizerNoDB(item.epc, item.timestamp, item.alarm_type)
        })
        var tableUnknown= $('#unknow-epcs').DataTable();
        $('#unknow-epcs').DataTable({
          retrieve: true
        });
        tableUnknown.order([0, 'desc']).draw();
        
        
      }).catch((error) => {
        console.log(error);
      });  
      
     autoRefresh()
    
  });
 




function generateVisualizer(epc, timestamp, alarm_type, description, image){
  var tableEvents= $('#know-epcs').DataTable();
    if(image==undefined){
      image='no image'
    }
    if(description==undefined){
      description=''
    }
   
    if(image.length > 100 ){
      image='<img src='+image+'>'
    }else{
      image='no image'
    } 
    
    tableEvents.row.add([timestamp,alarm_type,description,image]).draw(false);
}

function generateVisualizerNoDB(epc, date, type_alarm){
    var tableEvents= $('#unknow-epcs').DataTable();
    tableEvents.row.add([date,type_alarm,epc]).draw(false);
}

 function generateSummary(){
  var child_events=""
  var events_container=document.getElementById("row-event");
  events_container.innerHTML="";

  var types = localStorage.getItem("type_events").split(',');
  

  var unique_values = types.filter((value, index, arr) => index === arr.indexOf(value))

  unique_values.forEach(type => { 
    total_events= type_events_count.filter(x => x==type).length
    child_events+= "<div class='child-event'><h5>"+type+"</h3><h6>"+total_events+"</h4></div>"
  })
  events_container.innerHTML= child_events;
  document.getElementById("total-events").innerHTML=total_regs+total_regs_unknown
  document.getElementById("total-events-unknown").innerHTML=total_regs_unknown
}

function refreshDataSources(){  
  console.log("Refreshing data")
  
  var tableUnknown= $('#unknow-epcs').DataTable();
  var tableEvents= $('#know-epcs').DataTable();
  
  tableUnknown.clear().draw();
  tableEvents.clear().draw();

  getKnowEPCSPromise().then((data) => { 
    let result = JSON.parse(data)
    total_regs= Object.keys(result).length
    type_events_count=[]
    result.forEach(item => {
      type_events_count.push(item.sku) 
      generateVisualizer(item.epc, item.timestamp, item.alarm_type, item.description, item.image)
      
    })
      


    getUnKnowEPCSPromise().then((data) => { 
      let result_unknown = JSON.parse(data)
      total_regs_unknown= Object.keys(result_unknown).length
      result_unknown.forEach(item => { 
      generateVisualizerNoDB(item.epc, item.timestamp, item.alarm_type)
          
    })
          
      }).catch((error) => {
      console.log(error);
      });
    }).catch((error) => {
      console.log(error);
    });
    
    generateSummary()
}

 
function importFile() { 
    const file = document.getElementById("file-xls-input").files[0];
    var reader = new FileReader();
    type_events=[]
    localStorage.setItem("type_events", "");
    reader.addEventListener('load', function (e) {
        /////delete datamaster db before insert
        DeleteDatamasterPromise().then((data) => { 

          console.log(data)
        
        }).catch((error) => {console.log(error);});   



        let csvdata = e.target.result; 
        let data = csvdata.split("\n")
        data.forEach(function(element) {
          if(element){
            let data = element.split(",")
            type_events.push(data[0])
            var product= {
              sku: data[0],
              epc: data[1],
              description: data[2],
              image: "data:image/jpeg;base64," + data[4]
            }
            console.log(product)
            postDBDataPromise(product).then((data) => { 

              console.log(data)
            
            }).catch((error) => {console.log(error);});   
          
          }
          
      });
      localStorage.setItem("type_events", type_events);
    });
    reader.readAsBinaryString(file);
    setTimeout(function(){refreshDataSources()}, 1000);
    
}  
 
function clearData(){
  clearDataPromise().then((data) => { 
    var events_container=document.getElementById("row-event");
    events_container.innerHTML="";
    type_events_count=[]
    total_regs=0
    total_regs_unknown=0
    document.getElementById("total-events").innerHTML=total_regs
    document.getElementById("total-events-unknown").innerHTML=total_regs_unknown
    refreshDataSources()
  
  }).catch((error) => {console.log(error);});   
}

function autoRefresh(){
  var actual_regs= total_regs
  var actual_regs_unknown= total_regs_unknown
  var updateRegs=false

  getKnowEPCSPromise().then((data) => { 
    let result= JSON.parse(data)
    total_regs= Object.keys(result).length
    type_events_count=[]
    result.forEach(item => {
      type_events_count.push(item.sku) 
    })

    if(total_regs>actual_regs){
      updateRegs=true
    }
    getUnKnowEPCSPromise().then((data) => { 
      let result= JSON.parse(data)
      total_regs_unknown= Object.keys(result).length
      if(total_regs_unknown>actual_regs_unknown){
        updateRegs=true
      }
      
      if(updateRegs==true){
        refreshDataSources()
      }

      }).catch((error) => {
        console.log(error);
      });  
    }).catch((error) => {
      console.log(error);
    });


    
}

refreshButton.addEventListener("click",  refreshDataSources)
submitButton.addEventListener("click",  importFile)
clearButton.addEventListener("click", clearData)
window.setInterval(autoRefresh, 3000)
