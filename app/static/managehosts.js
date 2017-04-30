$(function(){

	$(".addData li").click(function(){
		var index = $(this).index();
		$(".addDataBox > div.item").eq(index).show().siblings().hide();

	});

	$(".showDBBtn").click(function(){
		console.log('aaa');
		$(".showDBContent").show().siblings().hide();
	});

	$("#removeBtn").click(function(){
		$.ajax({
			type:"GET",
			url:"/managehost",
			data:{"action":"removealldata"},
			dataType:"json",
			success:function(data){
				$("#resultMessage").text(data.result)
				$("#confirm").modal({
					keyboard : true,
					show : true
				});

				
				console.log(data);
			}
		});
	});


	$(".addDataBox > .item .queryBtn").click(function(){
		var item = $(this).parents(".input-group");
		var queryData = item.find("input").val();
		var type = item.find("input").attr("name");
		$(".showResultBox h2").text("已经将爬取任务加入后台..")
		$.ajax({
			type: "GET",
			url: "/managehost",
			data:{'action':'query','type':type,'params':queryData},
			dataType: 'json',
			success: function(data){
				console.log(data);
				$(".showResultBox").show();
				if(data.error){
					$(".showAccackResult").html("<p>[ERROR]: "+ data.error +"</p>")
				}else{
					$(".showAccackResult").html("<p> 爬取结果"+ data.result +"</p>")
				}
			}
		});
	});


});