function add_educational_row() {
    var table = document.getElementById('educational_details');
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    var row_id = table.rows[rowCount-1].id;
    row.id = row_id.substring(0,3)+(parseInt(row_id.substring(3))+1).toString();
    var colCount = table.rows[2].cells.length;
    var a=0;
    for(var i=0; i<colCount; i++) {
        var newcell	= row.insertCell(i);

        newcell.innerHTML = table.rows[2].cells[i].innerHTML;

        var id_name = newcell.children[0].name.substring(0,newcell.children[0].name.lastIndexOf("_")+1) + row.id.substring(3);
        newcell.children[0].name = id_name;
        newcell.children[0].id = id_name;
    }
}

function add_experience_row() {
    var table = document.getElementById('experience_details');
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    var row_id = table.rows[rowCount-1].id;
    row.id = row_id.substring(0,3)+(parseInt(row_id.substring(3))+1).toString();
    var colCount = table.rows[2].cells.length;
    var a=0;
    for(var i=0; i<colCount; i++) {
        var newcell	= row.insertCell(i);

        newcell.innerHTML = table.rows[2].cells[i].innerHTML;

        var id_name = newcell.children[0].name.substring(0,newcell.children[0].name.lastIndexOf("_")+1) + row.id.substring(3);
        newcell.children[0].name = id_name;
        newcell.children[0].id = id_name;
    }
}
function edudeleteRow(x) {
    try {
        var table = document.getElementById('educational_details');
        var rowCount = table.rows.length;
        if(rowCount==3){
            table.children[0].setAttribute("style", "display:none;");
        }
        var row_index = x.parentElement.parentElement.rowIndex;
        table.deleteRow(row_index);

    }catch(e) {
        alert(e);
    }
}
function expdeleteRow(x) {
    try {
        var table = document.getElementById('experience_details');
        var rowCount = table.rows.length;
        if(rowCount==3){
            table.children[0].setAttribute("style", "display:none;");
        }
        var row_index = x.parentElement.parentElement.rowIndex;
        table.deleteRow(row_index);

    }catch(e) {
        alert(e);
    }
}