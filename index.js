function processSend()
{
	var p = document.getElementById('phone').value;
	var m = document.getElementById('message').value;
	if(p =='')
	{
		alert('Nhap phone!');
		return;
	}
	if( m == '')
	{
		alert('Nhap tin nhan!');
		return;
	}
	urltoget = "http://sms.hotelducpho.com/process.php?phone="+ p + "&message=" + m
	//alert(urltoget);
	$.ajax({
		url: urltoget,
		data: '',
		type: 'GET',
		crossDomain: true,
		dataType: 'jsonp',
	});
}
function processData(result)
{
	alert(result);
	if(result == 1)
		alert('Send thanh cong');
}