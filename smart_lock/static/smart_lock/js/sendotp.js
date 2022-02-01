$(function(){
	$('#sendbtn').click(function(){
		$.ajax({
			url: 'send_otp',
			type: 'GET',
			success:function(response){
				console.log(3)
				console.log(response);
				alert("OTP sent successfully!")
			},
			error: function(error){
				console.log(error);
				alert("Fail to send OTP");
			}
		});
	});
});



