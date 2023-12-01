var express = require('express');
var router = express.Router();
// var MongoClient=require('mongodb').MongoClient
// var Server=require('mongodb').Server, assert = require("assert")
const { MongoClient, ServerApiVersion } = require("mongodb");
var uri='mongodb://127.0.0.1:27017'

const client = new MongoClient(uri,  {
  serverApi: {
      version: ServerApiVersion.v1,
      strict: true,
      deprecationErrors: true,
  }
}
);

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title:'Express'});
});

router.post('/submit',function(req,res){
  console.log(req.body)
  async function run() {
    try {
      await client.connect();
      console.log('Database connected');
      client.db('smp').collection('user').insertOne(req.body)
      
      // Add your database operations here
    
    } catch (error) {
      console.error('Error connecting to the database:', error);
    } finally {
      // await client.close();
      // console.log('Database connection closed');
    }
   
  }
  run()
  res.send('got it')
})


module.exports = router;
