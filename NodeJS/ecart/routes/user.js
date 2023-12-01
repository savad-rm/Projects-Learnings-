var express = require('express');
var router = express.Router();
var productHeleper=require('../helpers/product-helpers')


/* GET home page. */
  router.get('/', function(req, res, next) {
    productHeleper.getAllProducts().then((products)=>{
      res.render('user/view-products', { products });
    })
  });

  router.get('/login',(req,res)=>{
    res.render('user/login')
  })

  router.get('/signup',(req,res)=>{
    res.render('user/signup')
  })

  router.post('/signup',(req,res)=>{
    
  })


module.exports = router;
