$(function(){
	$('#btnRun').click(function(){

		$("#loaderDiv img").css("display","block");
		$("#result").removeClass("alert alert-danger alert-success");
		$("#result").html();
		//document.getElementById("loaderDiv").style.display="none";

        var fd = new FormData();
          var file_data = $('input[type="file"]')[0].files; // for multiple files
          for(var i = 0;i<file_data.length;i++){
              fd.append("file_"+i, file_data[i]);
              var size = file_data[i].size/1024/1024;
              size=Math.round(parseFloat(size));
              if (size > 3)
              {
                alert ("File size : " + file_data[i].name + " should be less than 2 Mb.");
                return;
              }
      }

	    var host_ip = $("#host_ip").val();
		var host_user = $("#host_user").val();
		var cloud_type = $("input[name='cloud_type']:checked").val();
		if (host_ip == "" || host_user == "" || cloud_type == ""){
		 	$("#result").removeClass("alert");
		 	$("#result").addClass("alert alert-danger");
		 	$("#result").html("Please Provide Mandatory Fields...");
			return
		 }

		if ($("input[name='createcluster']:checked").val() === undefined) {
			$("#result").removeClass("alert");
		 	$("#result").addClass("alert alert-danger");
		 	$("#result").html("Please Select Cluster Create Options...");
			return
		}
		fd.append("host_ip",$("#host_ip").val());
		fd.append("host_user",$("#host_user").val());
		fd.append("host_password",$("#host_password").val());
		fd.append("gui_user_name",$("#gui_user_name").val());
		fd.append("gui_user_password",$("gui_user_password").val());
		fd.append("tclevel",$("#tclevel").val());
		fd.append("tctype",$("#tctype").val());

		var reuse_cluster_name = $("#reuse_cluster_name").val();
		if (reuse_cluster_name != "") {
			fd.append("reuse_cluster_name",reuse_cluster_name);
			var target_cluster_name = $("#target_cluster_name").val();
			if (target_cluster_name != "") {
				fd.append("target_cluster_name",target_cluster_name);
			}
		}

		fd.append("node_count",$("#node_count").val());
		fd.append("disk_size",$("#disk_size").val());
		fd.append("cloud_type",$("input[name='cloud_type']:checked").val());
		fd.append("createcluster",$("#createcluster").val());
		fd.append("execution_type",$("#execution_type").val());
		fd.append("app_type",$("input[name='app_type']:checked").val());
		fd.append("email",$("#email").val());
		fd.append("cluster_type",$("input[name='cluster_type']:checked").val());

		if ($("input[name='precleanup']:checked").val() === undefined) {
			fd.append("precleanup","");
		}
		else {
			fd.append("precleanup",$("input[name='precleanup']:checked").val());
		}
		if ($("input[name='cleanup']:checked").val() === undefined) {
			fd.append("cleanup","");
		}
		else {
			fd.append("cleanup",$("input[name='cleanup']:checked").val());
		}
		if ($("input[name='target']:checked").val() === undefined) {
			fd.append("target","");
		}
		else {
			fd.append("target",$("input[name='target']:checked").val());
		}

		fd.append("access_key",$("#access_key").val());
		fd.append("secret_key",$("#secret_key").val());
		fd.append("region_name",$("#region_name").val());
		fd.append("subnet",$("#subnet").val());

		fd.append("keystone",$("#keystone").val());
		fd.append("openstack_username",$("#openstack_username").val());
		fd.append("openstack_password",$("#openstack_password").val());
		fd.append("project_name",$("#project_name").val());

		//fd.append("total_nodes",$("#total_nodes").val());
		//fd.append("disk_size",$("#disk_size").val());
		//fd.append("disk_type",$("#disk_type").val());
		//fd.append("disk_count",$("#disk_count").val());

		fd.append("aws_options",$("#aws_options").val());
		fd.append("openstack_options",$("#openstack_options").val());

		fd.append("customdata",$("#customdata").val());

		$.ajax({
			url: '/checkConnection',
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
				var href = $(location).attr('href','dashboard');
				setTimeout(function() {window.location = href}, 5000);
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


	$('#rerun').click(function(){
		$("#loaderDiv img").css("display","block");
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
			url: '/startRun',
			data: fd,
            contentType: false,
            processData: false,
            type: 'POST',
			success: function(response){
				console.log(response);
				obj = JSON.parse(response);
				$("#result").removeClass("alert alert-danger");
				$("#result").html(obj.html);
				$("#result").addClass("alert alert-success");
				var href = $(location).attr('href','dashboard');
				setTimeout(function() {window.location = href}, 5000);
			},
			error: function(error){
				console.log(error);
				$("#result").removeClass("alert");
			 	$("#result").addClass("alert alert-danger");
			 	$("#result").html("Trying Rerun , but getting error...");
			}
		});

	});

});
