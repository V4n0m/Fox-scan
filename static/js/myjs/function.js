String.prototype.format=function(){
  if(arguments.length==0) return this;
  for(var s=this, i=0; i<arguments.length; i++)
    s=s.replace(new RegExp("\\{"+i+"\\}","g"), arguments[i]);
  return s;
};

var taskid_dict = new Array();

var ChildDemo = "<p></p><table width='100%' class='insert-tab{2}'>" +
             "<tbody><tr><th width='15%'><i class='require-red'>*</i>Domain: </th>" +
            "<td><input type='text' id='' value='{0}' size='85' name='keywords' class='common-text'></td>" +
            "</tr>" +
            "<tr><th width='15%'><i class='require-red'>*</i>Operator: </th><td>" +
            "<button class='btn btn-primary btn6 mr10' onclick=\"WatchStatus('{1}')\">status</button>" +
            "<button class='btn btn-primary btn6 mr10' onclick=\"StopTask('{1}')\">STOP</button>" +
            "</td></tr></tbody></table>";

function setSelectUserNo(radioObj){
    var radioCheck= $(raioObj).val();
    if("True"==radioCheck){
        $(radioObj).attr("checked",false);
        $(radioObj).val("False");
    }else{
        $(radioObj).attr("checked", true);
        $(radioObj).val("True");
    }
}

function AppendChildStatus(data, obj){
    var child = ChildDemo.concat();
    $.each(data, function(n, value){
        if (taskid_dict.indexOf(value['taskid']) > -1){
            return false;
        }
        if (value['success'] == 1){
            obj.append(child.format(value['target'], value['taskid'], " red_table"));
        }else{
            obj.after(child.format(value['target'], value['taskid'], ""));
        }

        taskid_dict.push(value['taskid']);
    });
}


function ajaxGetjson(obj){
    $.ajax({
        url  : '/action/showtask?action=refresh',
        dataType : "json",
        success : function (jdata) {
            AppendChildStatus(jdata, obj);
        }
    });
}

function STOPALL() {
    taskid = "";
    for (var i =0;i<taskid_dict.length;i++){
        taskid += taskid_dict[i] + ",";
    }
    alert(taskid);
    $.post({
        url  : "/action/stoptask",
        data : {"taskidlist":tasid},
        success : function(result){
            data = JSON.parse(result);
            if (data['status'] == true){
                alert("ok");
            }
        }
    })
}