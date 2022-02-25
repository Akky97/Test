function login_into() {
var name= {
"db": "clickbima",
"username": "click@click.com",
"password": "123456"
}
$.ajax({
url: "https://bimabachat.in/api/auth/get_tokens",
method: "POST",
dataType: 'json',
contentType: "text/plain",
async:false,
data:JSON.stringify(name),
success: function (data) {
console.log(data.access_token);
localStorage.setItem('access',data.access_token)
if (data.response ==200){
getURL();

}
}

});
}

function getURL() {
$.ajax({
url: "https://bimabachat.in/api/faq?filters=[('infodata','=','Diabetes')]",
method: "GET",
dataType: 'json',
contentType: "text/plain",
async:false,
headers:{"access-token":localStorage.getItem('access')},
data:JSON.stringify(name),
success: function (data) {
console.log(data);
data1 =data.results;
console.log(data1.length,"Data1")
var htm ='';
for(var i=0;i< data1.length;i++)
{
    if(i == 0){
     var col = 'in';
     }else{
     var col = '';
     }
    htm += '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion" href="#panel'+i+'" ><i class="glyphicon glyphicon-plus"/>'+data1[i].question+' </a></h4></div><div id="panel'+i+'" class="panel-collapse collapse '+ col +' "  ><div class="panel-body"> '+ data1[i].answer+'</div></div></div>';


}
 console.log(htm);
 $('#accordion').html(htm);
} });

}

$( '.accordion-toggle').click(function() {
   $(this).find("li").toggleClass('fa-minus-circle')
});