$(function(){
	$('#save').click(function(){

		$("#result").removeClass("alert alert-danger alert-success");
		$("#result").html();

	    var host_ip = $("#hostname").val();
		var host_user = $("#username").val();
		var host_password = $("#password").val()
		var pattern = $("#pattern").val()
		if (host_ip == "" || host_user == "" || host_password == ""){
		 	$("#result").removeClass("alert");
		 	$("#result").addClass("alert alert-danger");
		 	$("#result").html("Please Provide Mandatory Fields...");
			return
		 }

		var fd = new FormData();

		fd.append("host_ip",host_ip);
		fd.append("host_user",host_user);
		fd.append("host_password",host_password);
		fd.append("pattern",pattern);

		$.ajax({
			url: '/addCronJob',
			data: fd,
            contentType: false,
            processData: false,
            type: 'POST',
			success: function(response){
				console.log(response);
				obj = JSON.parse(response);
				if (obj.result == 'failure') {
					$("#result").removeClass("alert");
				 	$("#result").addClass("alert alert-danger");
				 	$("#result").html(obj.html);
					return
				}
				$("#result").removeClass("alert alert-danger alert-success");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-success");
				$('#example1').DataTable().ajax.reload();
			},
			error: function(error){
				console.log(error);
				obj = JSON.parse(error);
				$("#result").removeClass("alert alert-danger alert-success");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-danger");
			}
		});
	});

	$('#store').click(function(){

		$("#result").removeClass("alert alert-danger alert-success");
		$("#result").html();

	    var host_ip = $("#ahostname").val();
		var host_user = $("#ausername").val();
		var host_password = $("#apassword").val()
		var key = $("#key").val()
		if (host_ip == "" || host_user == "" ){
		 	$("#result").removeClass("alert");
		 	$("#result").addClass("alert alert-danger");
		 	$("#result").html("Please Provide Mandatory Fields...");
			return
		 }

		var fd = new FormData();

		fd.append("host_ip",host_ip);
		fd.append("host_user",host_user);
		fd.append("host_password",host_password);
		fd.append("host_key",key);

		$.ajax({
			url: '/addHost',
			data: fd,
            contentType: false,
            processData: false,
            type: 'POST',
			success: function(response){
				console.log(response);
				obj = JSON.parse(response);
				if (obj.result == 'failure') {
					$("#result").removeClass("alert");
				 	$("#result").addClass("alert alert-danger");
				 	$("#result").html(obj.html);
					return
				}
				$("#result").removeClass("alert alert-danger alert-success");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-success");
				$('#example2').DataTable().ajax.reload();
			},
			error: function(error){
				console.log(error);
				obj = JSON.parse(error);
				$("#result").removeClass("alert alert-danger alert-success");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-danger");
			}
		});
	});

	$('#kill').click(function(){
		var id = $("input[name='id']:checked").val();
		if (id === undefined) {
			$("#result").removeClass("alert alert-danger alert-success");
			$("#result").html("Please select Id.");
			$("#result").addClass("alert alert-danger");
			return
		}

		$("#loaderDiv img").css("display","block");
		$("#result").removeClass("alert alert-danger alert-success");
		$("#result").html();

		var fd = new FormData();
		fd.append("task_id",id);

		$.ajax({
			url: '/deleteProcess',
			data: fd,
            contentType: false,
            processData: false,
            type: 'POST',
			success: function(response){
				console.log(response);
				obj = JSON.parse(response);
				if (obj.result == 'failure') {
					$("#result").removeClass("alert");
				 	$("#result").addClass("alert alert-danger");
				 	$("#result").html(obj.html);
					return
				}
				$("#result").removeClass("alert alert-danger");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-success");
				$('#example1').DataTable().ajax.reload();
				window.setTimeout(function(){window.location.reload()}, 5000);
			},
			error: function(error){
				console.log(error);
			}
		});

	});

	$('#poweron').click(function(){
		var id = $("input[name='id']:checked").val();
		if (id === undefined) {
			$("#result").removeClass("alert alert-danger alert-success");
			$("#result").html("Please select Id.");
			$("#result").addClass("alert alert-danger");
			return
		}

		$("#loaderDiv img").css("display","block");
		$("#result").removeClass("alert alert-danger alert-success");
		$("#result").html();

		var fd = new FormData();
		fd.append("task_id",id);

		$.ajax({
			url: '/poweron',
			data: fd,
            contentType: false,
            processData: false,
            type: 'POST',
			success: function(response){
				console.log(response);
				obj = JSON.parse(response);
				if (obj.result == 'failure') {
					$("#result").removeClass("alert");
				 	$("#result").addClass("alert alert-danger");
				 	$("#result").html(obj.html);
					return
				}
				$("#result").removeClass("alert alert-danger");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-success");
				$('#example1').DataTable().ajax.reload();
				window.setTimeout(function(){window.location.reload()}, 5000);
			},
			error: function(error){
				console.log(error);
			}
		});

	});

    $('#refresh').click(function(){

		$("#loaderDiv img").css("display","block");
		$("#result").removeClass("alert alert-danger alert-success");
		$("#result").html();

		var fd = new FormData();

		$.ajax({
			url: '/refresh',
			data: fd,
            contentType: false,
            processData: false,
            type: 'POST',
			success: function(response){
				console.log(response);
				obj = JSON.parse(response);
				if (obj.result == 'failure') {
					$("#result").removeClass("alert");
				 	$("#result").addClass("alert alert-danger");
				 	$("#result").html(obj.html);
					return
				}
				$("#result").removeClass("alert alert-danger");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-success");
				$('#example1').DataTable().ajax.reload();
				window.setTimeout(function(){window.location.reload()}, 5000);
			},
			error: function(error){
				console.log(error);
			}
		});

	});


	$('#delete').click(function(){
		var id = $("input[name='id']:checked").val();
		if (id === undefined) {
			$("#result").removeClass("alert alert-danger alert-success");
			$("#result").html("Please select Id.");
			$("#result").addClass("alert alert-danger");
			return
		}

		$("#loaderDiv img").css("display","block");
		$("#result").removeClass("alert alert-danger alert-success");
		$("#result").html();

		var fd = new FormData();
		fd.append("task_id",id);

		$.ajax({
			url: '/deleteData',
			data: fd,
            contentType: false,
            processData: false,
            type: 'POST',
			success: function(response){
				console.log(response);
				obj = JSON.parse(response);
				$("#result").removeClass("alert alert-danger alert-success");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-success");
				$('#example1').DataTable().ajax.reload();
				window.setTimeout(function(){window.location.reload()}, 1000);
			},
			error: function(error){
				console.log(error);
			}
		});


	});

	$('#deleteConfig').click(function(){
		var id = $("input[name='id']:checked").val();
		if (id === undefined) {
			$("#result").removeClass("alert alert-danger alert-success");
			$("#result").html("Please select Id.");
			$("#result").addClass("alert alert-danger");
			return
		}
		var fd = new FormData();
		fd.append("task_id",id);

		$.ajax({
			url: '/deleteConfig',
			data: fd,
            contentType: false,
            processData: false,
            type: 'POST',
			success: function(response){
				console.log(response);
				obj = JSON.parse(response);
				$("#result").removeClass("alert alert-danger alert-success");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-success");
				$('#example1').DataTable().ajax.reload();
				window.setTimeout(function(){window.location.reload()}, 1000);
			},
			error: function(error){
				console.log(error);
			}
		});


	});




});
