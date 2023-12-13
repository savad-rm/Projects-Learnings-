

function calculate(num1,num2, callback){
    console.log("App started")
    const a=num1
    const b=num1
    const c = a + b
    console.log(c)
    callback()
}

calculate(5,6,function(){
    console.log("App closed")
})