var express = require('express');
// const {render}=require('../app')
var router = express.Router();
var productHeleper=require('../helpers/product-helpers')

/* GET users listing. */
router.get('/', function(req, res, next) {
  productHeleper.getAllProducts().then((products)=>{
    res.render('admin/view-products',{products,admin:true})
  })
});

router.get('/add-product',function(req,res){
  res.render('admin/add-product')
})
router.post('/add-product',(req,res)=>{
  productHeleper.addProduct(req.body,(id)=>{
    let image=req.files.Image
    image.mv('./public/product-images/'+id+'.jpg',(err)=>{
      if(!err){
        res.render("admin/add-product")
      }else{
        console.log(err)
      }
    })
  })
})

module.exports = router;
