// function add(num1,num2,callback){
//     let err=false
//     if(num1==0){
//         err=false
//     }
//     callback(num1+num2,err)
// }
// function multiply(num1,num2,callback){
//     callback(num1*num2)
// }

// function div(num1,num2,callback){
//     callback(num1/num2)
// }

// add(10,20,(sum,err)=>{
//     if(err){
//         console.log("First number is zero")
//     }
//     else{
//         console.log(sum)
//         multiply(sum,sum,(product)=>{
//         console.log(product)
//         div(product,10,(result)=>{
//             console.log(result)
//         })
//         })
//     }
// })



// function add(num1,num2){
//         return new Promise((resolve,reject)=>{
//            if(num1==0){
//             reject("Error")
//            }
//             resolve(num1+num2) 
//         })
// }

// function mul(num1,num2){
//     return new Promise((resolve,reject)=>{
//        if(num1==0){
//         reject("Error")
//        }
//         resolve(num1*num2) 
//     })
// }

// function div(num1,num2){
//     return new Promise((resolve,reject)=>{
//        if(num1==0){
//         reject("Error")
//        }
//         resolve(num1/num2) 
//     })
// }

// add(10,20).then((sum)=>{
//     console.log(sum)
//     return mul(sum,sum)
// }).then((product)=>{
//     console.log(product)
//     return div(product,10)
// }).then((result)=>{
//     console.log(result)
// })
// .catch((err)=>{
//     console.log(err)
// })



const Promise=require('promise')
const {resolve,reject}=require('promise')

function getName(){
    return new Promise((resolve,reject)=>{
        setTimeout(( )=>{
            resolve('Abs')
        },3000)
    })
}

function getMobile(){
    return new Promise((resolve,reject)=>{
        setTimeout(( )=>{
            resolve('76575785787')
        },2000)
    })
}

// Promise.all([getName(),getMobile()]).then((result)=>{
//     console.log(result)
// })


async function getUser(){
    let name=await getName()
    console.log(name)
    let mobile=await getMobile()
    console.log(mobile)
    
}

getUser()